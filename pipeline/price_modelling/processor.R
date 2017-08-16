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


topicVariables = getTopicVariables()
priceData = getPriceData()
complete.df =
    getHarmonisedData() %>%
    ## HACK (Michael): This is temporary as there is some problem with
    ##                 commodity tagging. All the commodity are not
    ##                 tagged and thus they are identical
    ##                 variables. This results in unreliable
    ##                 prediction.
    subset(., select = -c(grep("contain", colnames(.)))) %>%
    mutate(date = as.Date(date, "%Y-%m-%d")) %>%
    rename(response = SGOI)



for(i in topicVariables){
    complete.df[i] = cumsum(scale(aggregatedData[i]))
}


########################################################################
## Model to select best model
########################################################################


bestModelName =
    complete.df %>%
    select(., -date) %>%
    mlrModelSelector(data = .,
                     testPeriod = 180,
                     models =  c("regr.lm", "regr.glmnet", "regr.cvglmnet"))

########################################################################
## Prediction
########################################################################

## Re-fit full data with best model
bestLearner = makeLearner(bestModelName)
task = complete.df %>%
    select(., -date) %>%
    makeRegrTask(data = , id = "prediction", target = "response")
bestModel = train(bestLearner, task = task)


prediction.df = 
    complete.df %>%
    subset(., select = -date) %>%
    predict(bestModel, newdata = .) %>%
    `$`(data) %>%
    cbind(date = complete.df$date, .) %>%
    mutate(date = date + forecastPeriod) %>%
    mutate(prediction = lowess(date, response, f = 90/length(response))$y) %>%
    subset(., select = -c(response, truth)) %>%
    merge(., priceData, all = TRUE, by = "date") %>%
    melt(., id.var = "date")

ggplot(data = prediction.df, aes(x = date, y = value, col = variable)) +
    geom_line()

getSortedCoef(bestModel)

