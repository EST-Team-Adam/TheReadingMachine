library(dplyr)
library(mlr)

getHarmonisedData = function(){
    ## Query the data
    dataSourceTable = 'HarmonisedData'
    statement = paste0('SELECT * FROM ', dataSourceTable)
    harmonisedData = dbGetQuery(con, statement)
    harmonisedData
}


transformHarmonisedData = function(harmonisedData){
    ## Transformation
    transformedData = 
        harmonisedData %>%
        mutate(date = as.Date(date, "%Y-%m-%d"))
    colnames(transformedData) = gsub("[[:space:]]", "_", colnames(transformedData))
    transformedData
}

getTopicVariables = function(){
    ## Set topic variable columns
    topicVariables =
        dbGetQuery(con, "PRAGMA table_info(NoposTopicModel)") %>%
        subset(., select = name, subset = name != "id") %>%
        unlist(., use.names = FALSE)
    topicVariables
}


getPriceData = function(){
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
    priceData
}



transformPriceData = function(priceData, forecastPeriod = 90, targetVariable){
    ## Smooth the data using stl
    decomposed = 
        priceData %>%
        subset(., select = c("date", targetVariable)) %>%
        with(., stl(ts(.[, 2], freq = 261), s.window = "periodic")) %>%
        `[[`(1) %>%
        data.frame

    response.df = data.frame(date = priceData$date,
                             response = 
                                 c(decomposed$trend[(forecastPeriod + 1):
                                                    (length(decomposed$trend))],
                                   rep(NA, forecastPeriod)))
    na.omit(response.df)
}

dailyAggregation = function(transformedData){
    transformedData %>%
        subset(., select = -id) %>%
        group_by(date) %>%
        summarise_each(funs(mean))
}


createModelData = function(responseData, explainData){
    model.df =
        responseData %>%
        merge(., explainData, all = FALSE, by = "date") %>%
        subset(., select = -date)
    model.df
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
