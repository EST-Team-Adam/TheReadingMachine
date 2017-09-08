library(dplyr)
library(mlr)

getHarmonisedData = function(){
    ## Query the data
    dataSourceTable = 'HarmonisedData'
    statement = paste0('SELECT * FROM ', dataSourceTable)
    harmonisedData = dbGetQuery(con, statement) %>%
        mutate(date = as.Date(date, "%Y-%m-%d"))
    harmonisedData
}


transformHarmonisedData = function(harmonisedData, forecastPeriod,
                                   topicVariables, filterCoef = 1){
    transformedData =
        harmonisedData %>%
        ## HACK (Michael): This is temporary as there is some problem with
        ##                 commodity tagging. All the commodity are not
        ##                 tagged and thus they are identical
        ##                 variables. This results in unreliable
        ##                 prediction.
        subset(., select = -c(grep("contain", colnames(.)))) %>%
        mutate(response = lead(GOI, forecastPeriod))

    ## Perform decay
    transformedData[topicVariables] =
        stats::filter(transformedData[topicVariables],
                      filterCoef, method = "recursive", side = 1) * filterCoef

    transformedData
}

getTopicVariables = function(){
    ## Set topic variable columns
    topicVariables =
        dbGetQuery(con, "PRAGMA table_info(TopicModel)") %>%
        subset(., select = name, subset = name != "id") %>%
        unlist(., use.names = FALSE) %>%
        gsub(" ", "_", .)

    # This is to account for the positive and negative sentiments for each topic
    topicVariables = paste0(rep(topicVariables, each = 2), c("_neg", "_pos"))
    topicVariables
}


getPriceData = function(){
    dataSourceTable = 'PriceIGC'
    statement = paste0('SELECT * FROM ', dataSourceTable)
    priceData = dbGetQuery(con, statement) %>%
        mutate(date = as.Date(date, "%Y-%m-%d"))
    priceData
}

buildDatasets = function(completeData, forecastPeriod, holdoutPeriod){
    predictionData = completeData[is.na(completeData[[responseVariable]]), ]
    modelData = completeData[!is.na(completeData[[responseVariable]]), ]
    trainData = modelData[1:(NROW(modelData) - holdoutPeriod), ]
    testData = modelData[(NROW(modelData) - holdoutPeriod + 1):NROW(modelData), ]
    cutoffDate = max(trainData$date) + forecastPeriod
    list(predictionData = predictionData,
         trainData = trainData,
         testData = testData,
         cutoffDate = cutoffDate)
}


trainBagElasticnet = function(trainData, testData, predictionData,
                              modelVariables,
                              sampleRate = 10/length(modelVariables),
                              responseVariable, bootstrapIteration,
                              smoothPrediction, forecastPeriod,
                              alpha = 1, nfold = 10, s = "lambda.min",
                              verbose = TRUE){

    ## Initialise variables
    totalVariableCount = length(modelVariables)
    completeData = Reduce(rbind, x = list(trainData, testData, predictionData))
    predictions = matrix(NA, nr = NROW(completeData), nc = bootstrapIteration)
    coefficients = matrix(0, nr = totalVariableCount + 1, nc = bootstrapIteration)
    rownames(coefficients) = c("(Intercept)", modelVariables)
    varCount = rep(NA, bootstrapIteration)
    coefCount = rep(NA, bootstrapIteration)
    cvMin = rep(NA, bootstrapIteration)


    ## Bootstrap sample for model
    for(i in 1:bootstrapIteration){
        ## The minimum number of variable used is 2 and the max is the whole set.
        baggingSize = min(totalVariableCount, round(rexp(1, sampleRate)) + 2)
        baggingVariable = sample(modelVariables, baggingSize)
        currentModel = cv.glmnet(as.matrix(trainData[, baggingVariable]),
                                 trainData[[responseVariable]],
                                 nfold = nfold,
                                 standardize = FALSE,
                                 alpha = alpha)

        ## Update the prediciton matrix
        predictions[, i] = c(predict(currentModel,
                                     newx = as.matrix(completeData[baggingVariable],
                                                      s = s)))

        ## Update the coefficient matrix
        currentCoef = coef(currentModel)
        coefficients[currentCoef@Dimnames[[1]][currentCoef@i], i] = currentCoef@x[currentCoef@i]

        ## Update the variable and coefficient count
        varCount[i] = length(baggingVariable)
        coefCount[i] = length(currentCoef@x[currentCoef@i])
        cvMin[i] = min(currentModel$cvm)
    }

    ## Weight the model and coef based on cross-validation error
    baggingWeights = (1/cvMin)/sum(1/cvMin)

    ## Calculate prediction
    weightedPrediction = (predictions %*% baggingWeights)
    if(smoothPrediction){
        weightedPrediction = lowess(1:length(weightedPrediction),
                                    weightedPrediction,
                                    f = forecastPeriod/length(weightedPrediction))$y
    }

    finalPrediction = data.frame(date = completeData$date + forecastPeriod,
                                 prediction = weightedPrediction)

    ## Calculate the weighted coefficients
    weightedCoef = c(coefficients %*% baggingWeights)
    names(weightedCoef) = rownames(coefficients)

    ## Print basic summary
    if(verbose){
        avgVariable = mean(varCount)
        avgCoefCount = mean(coefCount)
        cat("Average variables sampled in each bootstrap: ", avgVariable, "\n")
        cat("Average number of coefficients in each model: ", avgCoefCount, "\n")
        cat("Top 10 variable by coefficient size: \n")
        print(tail(sort(abs(weightedCoef)), 10))
    }
    
    list(prediction = finalPrediction, coef = weightedCoef)
}

plotPrediction = function(completePrediction,
                          priceData, cutoffDate, dateVar = "date"){
    prediction.df =
        completePrediction %>%
        merge(., priceData, all = TRUE, by = dateVar) %>%
        mutate(`GOI Trend` = lowess(date, GOI, f = 0.05)$y) %>%
        melt(., id.var = dateVar)

    tickDates = c(as.Date(paste0(unique(substring(prediction.df$date, 1, 4)), "-01-01")),
                  cutoffDate,
                  max(prediction.df$date))
    ggplot(data = prediction.df, aes(x = date, y = value, col = variable)) +
        geom_line() +
        geom_vline(xintercept = as.numeric(cutoffDate), linetype = "dashed") +
        scale_x_date(breaks = tickDates) +
        expand_limits(y = 0) + 
        theme(axis.text.x = element_text(angle = 45, hjust = 1))
}
