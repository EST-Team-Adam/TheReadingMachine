library(dplyr)
library(mlr)

getHarmonisedData = function(){
    ## Query the data
    dataSourceTable = 'HarmonisedData'
    statement = paste0('SELECT * FROM ', dataSourceTable)
    harmonisedData = dbGetQuery(con, statement)
    harmonisedData
}


getTopicVariables = function(){
    ## Set topic variable columns
    topicVariables =
        dbGetQuery(con, "PRAGMA table_info(NoposTopicModel)") %>%
        subset(., select = name, subset = name != "id") %>%
        unlist(., use.names = FALSE) %>%
        gsub(" ", "_", .)
    topicVariables
}


getPriceData = function(){
    dataSourceTable = 'PriceIGC'
    statement = paste0('SELECT * FROM ', dataSourceTable)
    priceData = dbGetQuery(con, statement) %>%
        mutate(date = as.Date(date, "%Y-%m-%d"))
    priceData
}


mlrModelSelector = function(data, testPeriod, models){
    modelSample = NROW(data)
    trainIndex = 1:(modelSample - testPeriod)
    testIndex = (modelSample - testPeriod + 1):modelSample
    
    task = makeRegrTask(data = data, id = "prediction", target = "response")
    learnerList = lapply(models, makeLearner)
    modelList = lapply(learnerList, function(x) train(x, task = task, subset = trainIndex))
    testPred = lapply(modelList, function(x) predict(x, task = task, subset = testIndex))
    bestModelIndex = which.min(unlist(lapply(testPred, performance)))
    bestModel = models[bestModelIndex]
    bestModel
}

getSortedCoef = function(model){
    coef = coef(model$learner.model, s = 0.01)
    coef.df = data.frame(variable = rownames(coef), coef = 0)
    coef.df[coef@i + 1, 'coef'] = coef@x
    arrange(coef.df, coef)
}
