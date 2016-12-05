dataframe_aggregator <- function(df_original,date1,date2) {

#wheat1 <- wheat[wheat$date >= date1 & wheat$date <= date2,]
df1<-df_original[df_original$Date >= date1 & df_original$Date <= date2,]
names <- colnames(df1)

df2 <- data.frame(aggregate(df1$Filtered ~ df1$Date, data=df1, FUN=mean ))                   
colnames(df2) <- c('Date','Filtered')

return(df2)
}

dataframe_assembler <- function(df2,date1,date2, wheat) {

names <- colnames(df2)
df3 <- data.frame(semi_join(df2,wheat,by=names[1]) , semi_join(wheat,df2,by=names[1])[2]) 
wheat1 <- wheat[wheat$Date >= date1 & wheat$Date <= date2,]

return(df3)

}