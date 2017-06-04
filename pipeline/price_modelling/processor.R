library(RSQLite)
library(dplyr)
library(forecast)
library(reshape2)
library(ggplot2)
source("controller.R")

########################################################################
## Initialisation
########################################################################
firstStartDate = as.Date("2011-01-01")
endDate = as.Date("2016-04-18")
target = "IGC.GOI"

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
aggregatedData = dailyAggregation(transformedData)
responseData = transformPriceData(priceData, forecastPeriod = 180, targetVariable = target)

########################################################################
## Create the final model data
########################################################################

complete.df = createModelData(responseData = responseData, explainData = aggregatedData)



########################################################################
## Model to select best model
########################################################################


bestModelName = mlrModelSelector(data = complete.df,
                                 testPeriod = 180,
                                 models =  c("regr.lm", "regr.glmnet", "regr.cvglmnet"))


########################################################################
## Prediction
########################################################################

## Re-fit full data with best model
bestLearner = makeLearner(bestModelName)
task = makeRegrTask(data = complete.df, id = "prediction", target = "response")
bestModel = train(bestLearner, task = task)


prediction.df = 
    aggregatedData %>%
    mutate(date = as.numeric(date)) %>%
    predict(bestModel, newdata = .) %>%
    `$`(data) %>%
    data.frame(date = aggregatedData$date, prediction = .) %>%
    merge(., priceData, all.y = TRUE, by = "date") %>%
    rename(prediction = response) %>%
    melt(., id.var = "date")


ggplot(data = prediction.df, aes(x = date, y = value, col = variable)) +
    geom_line()
