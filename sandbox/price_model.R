library(RSQLite)
library(dplyr)
library(forecast)
library(reshape2)
library(ggplot2)
source("functions.R")

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


## Query the data
dataSourceTable = 'HarmonisedData'
statement = paste0('SELECT * FROM ', dataSourceTable)
harmonisedData = dbGetQuery(con, statement)

## Transformation
transformedData = 
    harmonisedData %>%
    mutate(date = as.Date(date, "%Y-%m-%d")) %>%
    ## Drop the use onlyt the compound sentiment for now
    subset(., select=-c(positive_sentiment, neutral_sentiment, negative_sentiment))

## Set topic variable columns
topicVariables =
    dbGetQuery(con, "PRAGMA table_info(TopicModel)") %>%
    subset(., select = name, subset = name != "id") %>%
    unlist(., use.names = FALSE)



## TODO (Michael):
##
## 1. Load the igc data into the database
##
## 2. AUtomise the loading of the data
## 
priceDataPath = paste0(dataDir, "/igc_goi.csv")
priceData =
    read.csv(priceDataPath, stringsAsFactors = FALSE) %>%
    mutate(date = as.Date(DATE, "%m/%d/%Y"), DATE = NULL) %>%
    na.omit %>%
    subset(date > firstStartDate & date < endDate)


########################################################################
## Add smoothing to the wheat
########################################################################
decomposed = 
    priceData %>%
    subset(., select = c("date", target)) %>%
    with(., stl(ts(.[, 2], freq = 261), s.window = "periodic")) %>%
    `[[`(1) %>%
    data.frame


########################################################################
## Process the sentiments
########################################################################

topicScore = transformedData[topicVariables]
topicSentiment = topicScore * transformedData$compound_sentiment

weightedSentiment = cbind(date = transformedData[, c("date")],
                          topicSentiment)

summedSentiment =
    weightedSentiment %>%
    group_by(date) %>%
    summarise_each(funs(sum))



filledSentiment = 
    merge(summedSentiment,
          data.frame(date = seq(min(priceData$date),
                                max(priceData$date), 1)),
          by = "date", all.y = TRUE)
filledSentiment[is.na(filledSentiment)] = 0

cumSentiment =
    filledSentiment %>% {
    originalDates = .$date
    subset(., select = -date) %>%
        cumsum %>%
        cbind(date = originalDates, .)
}


smoothedSentiment =
    cumSentiment %>%
    {
        originalDates = .$date
        subset(., select = -date) %>%
            lapply(., FUN = function(x){
                smoothed = ses(x, alpha = 0.03,
                               initial = "simple")$fitted
                as.numeric(smoothed)
            }) %>%
            data.frame %>%
            cbind(date = originalDates, .)
    } 

########################################################################
## Create response
########################################################################

## The smoothed price in n days is our response as we want to see how
## well we can predict the general trend in the future.

forecastPeriod = 180

priceData$trend =
    decomposed$trend
priceData$response =
    c(decomposed$trend[(forecastPeriod + 1):
                            (length(decomposed$trend))],
      rep(NA, forecastPeriod))


complete.df =
    merge(priceData[, c("date", "response")],
          smoothedSentiment, all.x = TRUE, by = "date")
    ## NOTE (Michael): There seem to be problem with data prior to 2013.
    ## subset(., date > as.Date("2013-01-01"))

########################################################################
## Build models
########################################################################

testPeriod = 180
model.df = complete.df %>% na.omit
cutoffDate = max(model.df$date) - testPeriod

full = subset(model.df, select = -date)
fullIndex = as.numeric(rownames(full))
training = subset(model.df, select = -date, date < cutoffDate)
trainingIndex = as.numeric(rownames(training))
test = subset(model.df, select = -date, date >= cutoffDate)
testIndex = as.numeric(rownames(test))


models = c("regr.lm", "regr.glmnet", "regr.cvglmnet")
modelList = list()



modelList =
    lapply(models,
           function(x){
               mlrModelBuilder(data = full, subset = trainingIndex, model = x)
           })


names(modelList) = models
## modelList[["regr.arima"]] =
##     mlrModelBuilder(data = modelNodates.df,
##                     data_train = training[, c("response", target)],
##                     model = "regr.lm")

testPredList = lapply(modelList, function(x) predict(x$model, task = x$task, subset = testIndex))
(performList = lapply(testPredList, performance))


fullPredList = lapply(modelList, function(x) predict(x$model, task = x$task, subset = fullIndex))
pred.df = complete.df
pred.df$response[is.na(pred.df$response)] = 0
fullPredList = lapply(modelList,
                      function(x) predict(x$model, newdata = subset(complete.df, select = -date))




########################################################################
## Results
########################################################################

result.df = 
    lapply(fullPredList, function(x) x$data$response) %>%
    do.call(cbind, .) %>%
    data.frame(date = complete.df$date,
               response = priceData$response,
               price = priceData[target],
               .) %>%
    melt(., id.var = "date") %>%
    mutate(linewidth = ifelse(variable == "response", 1, 0.5)) %>%
    rename(model = variable)    



## result.df =
##     combinePrediction(list(lmNaiveBenchmark = lmNaiveBenchmark,
##                            lmComplete = lmComplete,
##                            lassoComplete = lassoComplete,
##                            lassoCV = lassoCV,
##                            newModel = newModel))


ggplot(result.df, aes(x = date, y = value, col = model,
                      size = linewidth)) +
    geom_line() +
    geom_vline(xintercept = as.numeric(cutoffDate),
               linetype = "longdash") +
    scale_size(range = c(0.8, 2), guide = FALSE) +
    ylim(c(0, 400))





## ########################################################################
## ## Prediction
## ########################################################################

## bestPrediction = 
##     smoothedSentiment %>%
##     subset(., select = -date, subset = date %in% priceData$date) %>%
##     ## subset(., select = -date) %>%    
##     predict(bestModel, newdata = .)

## plot(bestPrediction$data$response, type = "l")
## lines(priceData$response)
## lines(priceData[target])


## library(feather)
## oldHarmonisedData =
##     read_feather("../../data/harmonised_data.feather") %>%
##     data.frame() %>%
##     mutate(date = as.Date(date, "%Y-%m-%d")) %>%
##     .[order(.$date), ] %>%
##     mutate(articleSentiment = magnitude * polarity)

## ## This is for checking between the old and new sentiments.
## ##
## ##
## ## par(mfrow = c(3, 1))
## ## plot(priceData$date, priceData[[target]])
## ## ## plot(priceData$date[-1], diff(priceData$response))
## ## transformedData %>%
## ##     group_by(date) %>%
## ##     summarise(sent = mean(compound_sentiment)) %>%
## ##     subset(., date >= min(priceData$date)) %>%    
## ##     ## arrange(., date) %>%
## ##     ## mutate(sent = cumsum(sent)) %>%
## ##     plot
## ## abline(h = 0, col = "red")
## ## oldHarmonisedData %>%
## ##     group_by(date) %>%
## ##     summarise(sent = mean(articleSentiment)) %>%
## ##     subset(., date >= min(priceData$date)) %>%    
## ##     ## arrange(., date) %>%
## ##     ## mutate(sent = cumsum(sent)) %>%
## ##     plot
## ## abline(h = 0, col = "red")



########################################################################
## Process the sentiments
########################################################################



## topicScore = transformedData[topicVariables]
## topicSentiment = topicScore * transformedData$compound_sentiment

## weightedSentiment = cbind(date = transformedData[, c("date")],
##                           topicSentiment)

## summedSentiment =
##     weightedSentiment %>%
##     group_by(date) %>%
##     summarise_each(funs(sum))



## filledSentiment = 
##     merge(summedSentiment,
##           data.frame(date = seq(min(priceData$date),
##                                 max(priceData$date), 1)),
##           by = "date", all.y = TRUE)
## filledSentiment[is.na(filledSentiment)] = 0

## cumSentiment =
##     filledSentiment %>% {
##     originalDates = .$date
##     subset(., select = -date) %>%
##         cumsum %>%
##         cbind(date = originalDates, .)
## }


## smoothedSentiment =
##     cumSentiment %>%
##     {
##         originalDates = .$date
##         subset(., select = -date) %>%
##             lapply(., FUN = function(x){
##                 smoothed = ses(x, alpha = 0.03,
##                                initial = "simple")$fitted
##                 as.numeric(smoothed)
##             }) %>%
##             data.frame %>%
##             cbind(date = originalDates, .)
##     } 





## ########################################################################
## ## Prediction
## ########################################################################

## bestPrediction = 
##     smoothedSentiment %>%
##     subset(., select = -date, subset = date %in% priceData$date) %>%
##     ## subset(., select = -date) %>%    
##     predict(bestModel, newdata = .)

## plot(bestPrediction$data$response, type = "l")
## lines(priceData$response)
## lines(priceData[target])


## library(feather)
## oldHarmonisedData =
##     read_feather("../../data/harmonised_data.feather") %>%
##     data.frame() %>%
##     mutate(date = as.Date(date, "%Y-%m-%d")) %>%
##     .[order(.$date), ] %>%
##     mutate(articleSentiment = magnitude * polarity)

## ## This is for checking between the old and new sentiments.
## ##
## ##
## ## par(mfrow = c(3, 1))
## ## plot(priceData$date, priceData[[target]])
## ## ## plot(priceData$date[-1], diff(priceData$response))
## ## transformedData %>%
## ##     group_by(date) %>%
## ##     summarise(sent = mean(compound_sentiment)) %>%
## ##     subset(., date >= min(priceData$date)) %>%    
## ##     ## arrange(., date) %>%
## ##     ## mutate(sent = cumsum(sent)) %>%
## ##     plot
## ## abline(h = 0, col = "red")
## ## oldHarmonisedData %>%
## ##     group_by(date) %>%
## ##     summarise(sent = mean(articleSentiment)) %>%
## ##     subset(., date >= min(priceData$date)) %>%    
## ##     ## arrange(., date) %>%
## ##     ## mutate(sent = cumsum(sent)) %>%
## ##     plot
## ## abline(h = 0, col = "red")

########################################################################
## Old stuff from price_model.R
########################################################################

library(feather)
library(dplyr)
library(forecast)
library(reshape2)
library(ggplot2)


source("functions.R")

########################################################################
## Initialisation
########################################################################
firstStartDate = as.Date("2011-01-01")
endDate = as.Date("2016-04-18")
target = "IGC.GOI"

########################################################################
## Read the datasets
########################################################################

harmonisedData =
    read_feather("../../data/harmonised_data.feather") %>%
    data.frame() %>%
    mutate(date = as.Date(date, "%Y-%m-%d")) %>%
    .[order(.$date), ] %>%
    mutate(articleSentiment = magnitude * polarity)

topicVariables =
    harmonisedData %>%
    colnames %>%
    `[`(., !. %in% c("id", "date", "magnitude", "polarity"))


priceData =
    read.csv("../../data/igc_goi.csv", stringsAsFactors = FALSE) %>%
    mutate(date = as.Date(DATE, "%m/%d/%Y"), DATE = NULL) %>%
    na.omit %>%
    subset(date > firstStartDate & date < endDate)

########################################################################
## Add smoothing to the wheat
########################################################################
decomposed = 
    priceData %>%
    subset(., select = c("date", target)) %>%
    with(., stl(ts(.[, 2], freq = 261), s.window = "periodic")) %>%
    `[[`(1) %>%
    data.frame


########################################################################
## Process the sentiments
########################################################################

topicScore = harmonisedData[, 7:106]
topicSentiment = topicScore * harmonisedData$articleSentiment

weightedSentiment = cbind(date = harmonisedData[, c("date")],
                          topicSentiment)

summedSentiment =
    weightedSentiment %>%
    group_by(date) %>%
    summarise_each(funs(sum))



filledSentiment = 
    merge(summedSentiment,
          data.frame(date = seq(min(priceData$date),
                                max(priceData$date), 1)),
          by = "date", all.y = TRUE)
filledSentiment[is.na(filledSentiment)] = 0

cumSentiment =
    filledSentiment %>% {
    originalDates = .$date
    subset(., select = -date) %>%
        cumsum %>%
        cbind(date = originalDates, .)
}


smoothedSentiment =
    cumSentiment %>%
    {
        originalDates = .$date
        subset(., select = -date) %>%
            lapply(., FUN = function(x){
                smoothed = ses(x, alpha = 0.03,
                               initial = "simple")$fitted
                as.numeric(smoothed)
            }) %>%
            data.frame %>%
            cbind(date = originalDates, .)
    } 

########################################################################
## Create response
########################################################################

## The smoothed price in n days is our response as we want to see how
## well we can predict the general trend in the future.

forecastPeriod = 180
cutoffDate = as.Date("2015-01-01")
priceData$trend =
    decomposed$trend
priceData$response =
    c(decomposed$trend[(forecastPeriod + 1):
                            (length(decomposed$trend))],
      rep(NA, forecastPeriod))


model.df =
    merge(priceData[, c("date", "response", target)],
          smoothedSentiment, all.x = TRUE, by = "date")
    ## NOTE (Michael): There seem to be problem with data prior to 2013.
    ## subset(., date > as.Date("2013-01-01")) %>%
    ## na.omit

########################################################################
## Build models
########################################################################

lmNaiveBenchmark =
    model.df %>% {
        data_train =
            subset(., select = c("response", target),
                   date < cutoffDate) %>%
            na.omit
        data_test =
            subset(., select = c("response", target),
                   date >= cutoffDate)
        list(data_train = data_train, data_test = data_test)
    } %>%
    with(.,
         mlrModelBuilder(data_train = data_train,
                         data_test = data_test,
                         model = "regr.lm"))


lmComplete =
    model.df %>% {
        data_train =
            subset(., select = -date, date < cutoffDate) %>%
            na.omit
        data_test =
            subset(., select = -date, date >= cutoffDate)
        list(data_train = data_train, data_test = data_test)
    } %>%
    with(.,
         mlrModelBuilder(data_train = data_train,
                         data_test = data_test,
                         model = "regr.lm"))

lassoComplete =
    model.df %>% {
        data_train =
            subset(., select = -date, date < cutoffDate) %>%
            na.omit
        data_test =
            subset(., select = -date, date >= cutoffDate)
        list(data_train = data_train, data_test = data_test)
    } %>%
    with(.,
         mlrModelBuilder(data_train = data_train,
                         data_test = data_test,
                         model = "regr.glmnet"))


lassoComplete =
    model.df %>% {
        data_train =
            subset(., select = -date, date < cutoffDate) %>%
            na.omit
        data_test =
            subset(., select = -date, date >= cutoffDate)
        list(data_train = data_train, data_test = data_test)
    } %>%
    with(.,
         mlrModelBuilder(data_train = data_train,
                         data_test = data_test,
                         model = "regr.glmnet"))


lassoCV =
    model.df %>% {
        data_train =
            subset(., select = -date, date < cutoffDate) %>%
            na.omit
        data_test =
            subset(., select = -date, date >= cutoffDate)
        list(data_train = data_train, data_test = data_test)
    } %>%
    with(.,
         mlrModelBuilder(data_train = data_train,
                         data_test = data_test,
                         model = "regr.cvglmnet"))

newModel =
    model.df %>% {
        data_train =
            subset(., select = -date, date < cutoffDate) %>%
            na.omit
        data_test =
            subset(., select = -date, date >= cutoffDate)
        list(data_train = data_train, data_test = data_test)
    } %>%
    with(.,
         mlrModelBuilder(data_train = data_train,
                         data_test = data_test,
                         model = "regr.nnet"))

########################################################################
## Results
########################################################################

result.df =
    combinePrediction(list(lmNaiveBenchmark = lmNaiveBenchmark,
                           lmComplete = lmComplete,
                           lassoComplete = lassoComplete,
                           lassoCV = lassoCV,
                           newModel = newModel))


ggplot(result.df, aes(x = date, y = value, col = model,
                      size = linewidth)) +
    geom_line() +
    geom_vline(xintercept = as.numeric(cutoffDate),
               linetype = "longdash") +
    scale_size(range = c(0.8, 2), guide = FALSE) +
    ylim(c(0, 400))


## data.frame(variable = modelCoef@Dimnames[[1]],
##            coef = matrix(modelCoef)) %>%
##     arrange(., coef) %>%
##     subset(coef > 0) %>% {
##         print(.)
##         cat(paste0("Number of variables used: ", NROW(.), "\n"))
##     }

library(mlr)
library(glmnet)
## Helper function for model building and testing.
shiftPrediction = function(x, shift){
    c(rep(NA, shift), x[1:(length(x) - shift)])
}

## mlrModelBuilder = function(data, model){
##     task = makeRegrTask(data = data, id = "prediction",
##                         target = "response")
##     learner = makeLearner(model)
##     model = train(learner, task)
##     predict(model, task = task) %>%
##         data.frame %>%
##         subset(select = response, drop = TRUE)
## }

mlrModelBuilder = function(data, subset, model_name){
    task = makeRegrTask(data = data, id = "prediction",
                        target = "response")
    learner = makeLearner(model_name)
    model = train(learner, task, subset = subset)
    ## predict(model, newdata = data_test) %>%
    ##     data.frame %>%
    ##     subset(select = response, drop = TRUE)
    list(model = model, task = task)
}


combinePrediction = function(models){
    predictions =
        lapply(models,
               FUN = function(x)
                   shiftPrediction(x, shift = forecastPeriod)) %>%
        do.call(cbind, .)
    data.frame(date = model.df$date, response = priceData$trend) %>%
        cbind(., predictions) %>%
        melt(id.vars = "date") %>%
        mutate(linewidth = ifelse(variable == "response", 1, 0.5)) %>%
        rename(model = variable)
}
