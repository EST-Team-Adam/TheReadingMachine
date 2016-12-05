timestamp_to_date<-function(df) {

date <- as.Date(as.POSIXlt(df_original$Timestamp, origin="1970-01-01"))
df<-cbind(date, df)

}

wheat_date<-function(wheat) {

wheat$date <- as.Date(wheat$date, format = "%m/%d/%Y")

}
