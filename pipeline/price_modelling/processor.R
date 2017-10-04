library(RSQLite)
library(dplyr)
library(forecast)
library(reshape2)
library(ggplot2)
library(glmnet)
source("controller.R")

########################################################################
## Initialisation
########################################################################

## connect to the sqlite file
dataDir = Sys.getenv("DATA_DIR")
dbName = "/the_reading_machine.db"
fullDbPath = paste0(dataDir, dbName)
con = dbConnect(drv=SQLite(), dbname=fullDbPath)
topicVariables = getTopicVariables()

## initial parameters
forecastPeriod = 180
holdoutPeriod = 2
filterCoef = 1
regularisation = "lambda.min"
responseVariable = "response"
sampleRate = 10/length(topicVariables)
bootstrapIteration = 50
alpha = 1


########################################################################
## Data Extraction and processing
########################################################################

## Get raw data
priceData = getPriceData()
complete.df =
    getHarmonisedData() %>%
    transformHarmonisedData(., forecastPeriod = forecastPeriod,
                            filterCoef = filterCoef, topicVariables = topicVariables)

## Create train and test set
datasets = buildDatasets(completeData = complete.df,
                         forecastPeriod = forecastPeriod,
                         holdoutPeriod = holdoutPeriod)



########################################################################
## Model training and prediction
########################################################################


## Train the model and make prediction
model = with(datasets,
             trainBagElasticnet(trainData = trainData,
                                testData = testData,
                                predictionData = predictionData,
                                modelVariables = topicVariables,
                                responseVariable = "response",
                                sampleRate = sampleRate,
                                bootstrapIteration = bootstrapIteration,
                                smoothPrediction = TRUE,
                                forecastPeriod = forecastPeriod,
                                alpha = alpha,
                                s = regularisation))

## Plot the prediction
plotPrediction(completePrediction = model$prediction,
               priceData = priceData[, c("date", "GOI")],
               cutoffDate = datasets$cutoffDate)
