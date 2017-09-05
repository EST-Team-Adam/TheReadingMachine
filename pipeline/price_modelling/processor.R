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

## initial parameters
forecastPeriod = 180
filterCoef = 1

## topicVariables = getTopicVariables()
topicVariables = paste0(rep(getTopicVariables(), each = 2), c("_neg", "_pos"))
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
    mutate(response = lead(GOI, forecastPeriod)) %>%
    na.omit


complete.df[topicVariables] = stats::filter(complete.df[topicVariables],
                                            filterCoef, method = "recursive", side = 1) * filterCoef



########################################################################
## Model training and prediction
########################################################################

holdoutPeriod = 365
train.df = complete.df[1:(NROW(complete.df) - holdoutPeriod), ]
test.df = complete.df[(NROW(complete.df) - holdoutPeriod + 1):NROW(complete.df), ]
cutoffDate = max(train.df$date) + forecastPeriod




model = trainStackElasticnet(trainData = train.df,
                             testData = test.df,
                             regularisation = regularisation,
                             modelVariables = topicVariables,
                             responseVariable = "response",
                             sampleRate = 10/length(topicVariables),
                             bootstrapIteration = 50,
                             smoothPrediction = TRUE,
                             forecastPeriod = forecastPeriod,
                             alpha = 1)

plotPrediction(completeData = complete.df,
               forecastPeriod = forecastPeriod,
               completePrediction = model$prediction,
               priceData = priceData[, c("date", "GOI")],
               cutoffDate = cutoffDate)

## NOTE (Michael): Also remove popular words and text processing in
##                 the word2vec exercise in the article processing.
