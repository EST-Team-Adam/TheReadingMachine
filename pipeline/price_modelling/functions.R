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
