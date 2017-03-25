library(feather)
library(dplyr)
library(forecast)
library(reshape2)
library(ggplot2)
library(plotly)
library(mlr)
library(glmnet)

firstStartDate = as.Date("2011-01-01")
endDate = as.Date("2016-04-18")
target = "IGC.GOI"


## Read the datasets
harmonisedData =
    read_feather("harmonised_data.feather") %>%
    data.frame() %>%
    mutate(date = as.Date(date, "%Y-%m-%d")) %>%
    .[order(.$date), ] %>%
    mutate(articleSentiment = magnitude * polarity)

topicVariables =
    harmonisedData %>%
    colnames %>%
    `[`(., !. %in% c("id", "date", "magnitude", "polarity"))


priceData =
    read.csv("data/igc_goi.csv", stringsAsFactors = FALSE) %>%
    mutate(date = as.Date(DATE, "%m/%d/%Y"), DATE = NULL) %>%
    na.omit %>%
    subset(date > firstStartDate & date < endDate)


## This basically shows that there is no need to predict the other
## variables. The trend is practically the same.
pricePlot = 
    melt(priceData, id.var = "date") %>%
    ggplot(data = ., aes(x = date, y = value, col = variable)) +
    geom_line()
ggplotly(pricePlot)


## Add smoothing to the wheat
decomposed = 
    priceData %>%
    subset(., select = c("date", target)) %>%
    with(., stl(ts(.[, 2], freq = 261), s.window = "periodic")) %>%
    `[[`(1) %>%
    data.frame

decomposed %>%
    cbind(date = priceData$date, ., original = priceData[[target]]) %>%
    melt(., id.vars = "date") %>%
    ggplot(data = ., aes(x = date, y = value, col = variable)) +
    geom_line()



## Process the sentiments

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


## Create response
##
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




## benchmark =
##     model.df %>%
##     subset(., select = c("response", target), date < cutoffDate) %>%
##     with(., lm(response ~ ., data = .)) %>%
##     predict(., model.df)


## benchmark2 =
##     model.df %>%
##     subset(., select = -date, date < cutoffDate) %>%
##     with(., lm(response ~ ., data = .)) %>%
##     predict(., model.df)


## model =
##     model.df %>%
##     subset(., select = -date, date < cutoffDate) %>%
##     {
##         xvars = as.matrix(.[, -1])
##         yvar = as.matrix(.[, 1])
##         cv.glmnet(xvars, yvar)
##     }

## minLambda = model$lambda.min
## modelCoef = coef(model, s = minLambda)
## predicted = cbind(1, as.matrix(model.df[, -c(1, 2)])) %*%
##     as.matrix(modelCoef)


## Helper function for model building and testing.
shiftPrediction = function(x, shift){
    c(rep(NA, shift), x[1:(length(x) - shift)])
}

mlrModelBuilder = function(data, model){
    task = makeRegrTask(data = data, id = "prediction",
                        target = "response")
    learner = makeLearner(model)
    model = train(learner, task)
    predict(model, task = task) %>%
        data.frame %>%
        subset(select = response, drop = TRUE)
}

mlrModelBuilder = function(data_train, data_test, model){
    task = makeRegrTask(data = data_train, id = "prediction",
                        target = "response")
    learner = makeLearner(model)
    model = train(learner, task)
    predict(model,
            newdata = rbind(data_train, data_test)) %>%
        data.frame %>%
        subset(select = response, drop = TRUE)
}

## Build and benchmark various model

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
