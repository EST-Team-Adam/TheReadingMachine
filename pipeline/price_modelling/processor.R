library(RSQLite)
library(dplyr)
library(forecast)
library(reshape2)
library(ggplot2)
source("controller.R")

########################################################################
## Initialisation
########################################################################

## HACK (Michael): This first date is due to the fact that sentiment
##                 score were vastly different prior and after
##                 2013. Prior to 2013, the sentiment has mean clsoe
##                 to 0, while after 2013, the mean of sentiments has
##                 risen to approximately 0.25.
firstStartDate = as.Date("2013-01-01")
endDate = as.Date("2016-04-18")
target = "IGC.GOI"
forecastPeriod = 90

########################################################################
## Read the data
########################################################################

## connect to the sqlite file
dataDir = Sys.getenv("DATA_DIR")
dbName = "/the_reading_machine.db"
fullDbPath = paste0(dataDir, dbName)
con = dbConnect(drv=SQLite(), dbname=fullDbPath)


harmonisedData =
    getHarmonisedData() %>%
    ## HACK (Michael): This is temporary as there is some problem with
    ##                 commodity tagging. All the commodity are not
    ##                 tagged and thus they are identical
    ##                 variables. This results in unreliable
    ##                 prediction.
    subset(., select = -c(grep("contain", colnames(.))))
topicVariables = getTopicVariables()
priceData = getPriceData()

########################################################################
## Transform the data for modelling
########################################################################

transformedData = transformHarmonisedData(harmonisedData)
aggregatedData = dailyAggregation(transformedData) %>%
    subset(., subset = date > firstStartDate)
responseData = transformPriceData(priceData, forecastPeriod = forecastPeriod, targetVariable = target)


for(i in topicVariables){
    aggregatedData[i] = cumsum(scale(aggregatedData[i]))
}


########################################################################
## Create the final model data
########################################################################

complete.df =
    createModelData(responseData = responseData, explainData = aggregatedData)



########################################################################
## Model to select best model
########################################################################


bestModelName = mlrModelSelector(data = complete.df,
                                 testPeriod = 180,
                                 models =  c("regr.lm", "regr.glmnet", "regr.cvglmnet"))


## bestModelName = "regr.glmnet"

########################################################################
## Prediction
########################################################################

## Re-fit full data with best model
bestLearner = makeLearner(bestModelName)
task = makeRegrTask(data = complete.df, id = "prediction", target = "response")
bestModel = train(bestLearner, task = task)


prediction.df = 
    aggregatedData %>%
    subset(., select = -date) %>%
    ## subset(., select = grep("wheat", colnames(.), value = TRUE)) %>%
    ## mutate(date = as.numeric(date)) %>%
    predict(bestModel, newdata = .) %>%
    `$`(data) %>%
    cbind(date = aggregatedData$date, .) %>%
    mutate(date = date + forecastPeriod) %>%
    mutate(prediction = lowess(date, response, f = 90/length(response))$y) %>%
    subset(., select = -response) %>%
    ## mutate(smootehdPrediction = lowess(date, prediction, f = 90/length(prediction))$y) %>%
    merge(., priceData, all.y = TRUE, by = "date") %>%
    ## rename(prediction = response) %>%
    melt(., id.var = "date")

ggplot(data = prediction.df, aes(x = date, y = value, col = variable)) +
    geom_line()

getSortedCoef(bestModel)

