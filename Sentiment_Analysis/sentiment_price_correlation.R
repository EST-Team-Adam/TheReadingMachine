## PACKAGES ##
library(dplyr)
library(fANCOVA)
library(FKF)
library(lmtest)
library(tseries)

## CLEAR ALL ##
rm(list=ls())
gc()
source("kalman_filter.r")
source("dataframe_manipulator.r")

## DATA LOADING ##
commodities<-read.csv("igc_goi.csv")
wheat<-data.frame(commodities$DATE, commodities$Wheat)
colnames(wheat) <- c('Date', 'Wheat')
df_original<-read.csv("df.csv",sep=';')
 
# Date conversion #
wheat$Date <- as.Date(wheat$Date,origin="1900-01-01")
df_original$Date <- as.Date(df_original$Date)#,format = "%d/%m/%y")  # Modified Version
#df_original$Date <- as.Date(df_original$Date)  # Unmodified Version format = "%y/%m/%d"

df_original <- df_original[order(df_original$Date),]
#non_zero <- df_original$Compound[!(df_original$Compound==0)]   # take just non-zero observations

# Kalman Filter #
y <- df_original$Compound
     filtered_sentiment <- kalman_filter(y)
        df_original$Filtered_Sentiment <- ts(filtered_sentiment[[1]]$att[1, ], start = start(filtered_sentiment[[2]]), frequency = frequency(filtered_sentiment[[2]]))

# DataFrame building #
date1 <- as.Date("2010-01-01")  #2010-06-01
date2 <- as.Date("2016-11-25")  #2016-05-25

         df2 <- dataframe_aggregator(df_original,date1,date2)
         df <- dataframe_assembler(df2,date1,date2, wheat)

# Normal CCF #

ccf(df$Filtered,df$Wheat, main = "Filtered Sentiment & Wheat Price Index CCF", ylab = "CCF", xlab = "Lags")

adf.test(df$Filtered, k=ar(df$Filtered, ordermax=5,aic=TRUE)$order)
adf.test(df$Wheat, k=ar(df$Wheat, ordermax=5,aic=TRUE)$order)

# Plots #

t <- c(1:length(df$Date))
par(mar = c(5, 4, 4, 4) + 0.3)  # Leave space for z axis
  plot(t, df$Filtered, type = "l", col="red", ylab = "Filtered Sentiment, Wheat Price Index", xlab = "Observation") # first plot
    abline(lm(df$Filtered ~ t),col="red",lty = c(2))
par(new = TRUE)
  plot(t, df$Wheat, type = "l", axes = FALSE, bty = "n", xlab = "", ylab = "")
    abline(lm(df$Wheat ~ t),col="black",lty = c(2))
    axis(side=4, at = pretty(range(df$Wheat)))
par(xpd=TRUE)
  legend("bottomleft", inset=c(0.25,0),c("Filtered Sentiment","Wheat Price","Filtered Sentiment LM","Wheat Price LM"),col=c('red','black'), lty =    c(1,1,2,2))
 
# ScatterPlot
plot(df$Wheat,df$Filtered,ylab = "Filtered Sentiment", xlab = "Wheat Price Index", main = "IGC Wheat Price and Filtered Sentiment Scatterplot")
   abline(lm(df$Filtered ~ df$Wheat),col="red",lty = c(2))
   legend("topright",c("Linear Model"),col=c('red'), lty = c(2))