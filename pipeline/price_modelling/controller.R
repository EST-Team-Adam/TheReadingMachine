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
        dbGetQuery(con, "PRAGMA table_info(TopicModel)") %>%
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

trainStackElasticnet = function(trainData, testData, regularisation, modelVariables,
                           sampleRate = 10/length(modelVariables),
                           responseVariable, bootstrapIteration,
                           smoothPrediction, forecastPeriod,
                           alpha = 1){

    ## Initialise variables
    totalVariableCount = length(modelVariables)
    completeData = rbind(trainData, testData)
    predictions = matrix(NA, nr = NROW(completeData), nc = bootstrapIteration)
    coefficients = matrix(0, nr = totalVariableCount + 1, nc = bootstrapIteration)
    rownames(coefficients) = c("(Intercept)", modelVariables)
    varCount = c()
    coefCount = c()
    cvMin = c()


    # Bootstrap sample for model
    for(i in 1:bootstrapIteration){
        baggingSize = min(totalVariableCount, round(rexp(1, sampleRate)) + 2)
        baggingVariable = sample(modelVariables, baggingSize)
        currentModel = cv.glmnet(as.matrix(trainData[, baggingVariable]),
                                 trainData[[responseVariable]],
                                 nfold = 10,
                                 standardize = FALSE,
                                 alpha = alpha)

        ## Update the prediciton matrix
        predictions[, i] = c(predict(currentModel,
                              newx = as.matrix(completeData[baggingVariable],
                                               s = "lambda.min")))

        ## Update the coefficient matrix
        currentCoef = coef(currentModel)
        coefficients[currentCoef@Dimnames[[1]][currentCoef@i], i] = currentCoef@x[currentCoef@i]

        ## Update the variable and coefficient count
        varCount = c(varCount, length(baggingVariable))
        coefCount = c(coefCount, length(currentCoef@x[currentCoef@i]))
        cvMin = c(cvMin, min(currentModel$cvm))
    }

    ## Weight the model and coef based on cross-validation error
    baggingWeights = (1/cvMin)/sum(1/cvMin)

    ## Calculate prediction
    finalPrediction = (predictions %*% baggingWeights)
    if(smoothPrediction){
        finalPrediction = lowess(1:length(finalPrediction),
                                 finalPrediction,
                                 f = forecastPeriod/length(finalPrediction))$y
    }

    ## Calculate the weighted coefficients
    weightedCoef = c(coefficients %*% baggingWeights)
    names(weightedCoef) = rownames(coefficients)

    avgVariable = mean(varCount)
    avgCoefCount = mean(coefCount)
    cat("Average variables sampled in each bootstrap: ", avgVariable, "\n")
    cat("Average number of coefficients in each model: ", avgCoefCount, "\n")
    cat("Top 10 variable by coefficient size: \n")
    print(tail(sort(abs(weightedCoef)), 10))
    
    list(prediction = finalPrediction, coef = weightedCoef)
}

plotPrediction = function(completeData, forecastPeriod, completePrediction,
                          priceData, cutoffDate, dateVar = "date"){
    prediction.df =
        data.frame(date = completeData$date + forecastPeriod,
                   prediction = completePrediction) %>%
        merge(., priceData, all = TRUE, by = dateVar) %>%
        mutate(`GOI Trend` = lowess(date, GOI, f = 0.05)$y) %>%
        melt(., id.var = dateVar)

    tickDates = c(as.Date(paste0(unique(substring(prediction.df$date, 1, 4)), "-01-01")),
                  cutoffDate,
                  max(prediction.df$date))
    ggplot(data = prediction.df, aes(x = date, y = value, col = variable)) +
        geom_line() +
        geom_vline(xintercept = as.numeric(cutoffDate)) +
        scale_x_date(breaks = tickDates) +
        theme(axis.text.x = element_text(angle = 45, hjust = 1))
}
