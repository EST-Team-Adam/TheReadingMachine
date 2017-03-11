library(feather)
library(dplyr)
library(forecast)
library(reshape2)
library(ggplot2)
library(plotly)


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
forecastPeriod = 90
cutoffDate = as.Date("2014-01-01")
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




benchmark = 
    model.df %>%
    subset(., select = c("response", target), date < cutoffDate) %>%
    with(., lm(response ~ ., data = .)) %>%
    predict(., model.df)


benchmark2 = 
    model.df %>%
    subset(., select = -date, date < cutoffDate) %>%
    with(., lm(response ~ ., data = .)) %>%
    predict(., model.df)

library(glmnet)
model = 
    model.df %>%
    subset(., select = -date, date < cutoffDate) %>%
    {
        xvars = as.matrix(.[, -1])
        yvar = as.matrix(.[, 1])
        cv.glmnet(xvars, yvar)
    }

modelCoef = coef(model, s = "lambda.min")
predicted = cbind(1, as.matrix(model.df[, -c(1, 2)])) %*%
    as.matrix(modelCoef)




with(model.df,
{
    plot(date, priceData$trend, col = "green", lwd = 2,
         ylim = c(0, 550))
    lines(date, model.df[, target], type = "l", lwd = 1)
    ## lines(date,
    ##       c(rep(NA, forecastPeriod),
    ##         response[1:(length(predicted) - forecastPeriod)]),
    ##       col = "green")
    lines(date,
          c(rep(NA, forecastPeriod),
            predicted[1:(length(predicted) - forecastPeriod)]),
          col = "steelblue")
    lines(date,
          c(rep(NA, forecastPeriod),
            benchmark[1:(length(predicted) - forecastPeriod)]),
          col = "red")
    lines(date,
          c(rep(NA, forecastPeriod),
            benchmark2[1:(length(predicted) - forecastPeriod)]),
          col = "pink")
    ## lines(date, benchmark, col = "red")
    ## lines(date, benchmark2, col = "pink")
    abline(v = cutoffDate, lty = 2)
})


data.frame(variable = modelCoef@Dimnames[[1]],
           coef = matrix(modelCoef)) %>%
    arrange(., coef) %>%
    subset(coef > 0) %>% {
        print(.)
        cat(paste0("Number of variables used: ", NROW(.), "\n"))
    }
    

