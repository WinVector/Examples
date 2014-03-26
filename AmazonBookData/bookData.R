
# load libraries
require('gam')
require('ggplot2')
require('gdata')
require('RCurl')

# Data: http://authorearnings.com/wp-content/uploads/2014/02/Amazon-US-Kindle-bestsellers-anon-snapshot-20140207-v8.xlsx
# Found at: http://authorearnings.com/reports/the-50k-report/

# do <- read.xls('Amazon-US-Kindle-bestsellers-anon-snapshot-20140207-v8.xlsx',
#   sheet=2,pattern='Sold by',stringsAsFactors=F,as.is=T)
do <- read.xls('http://authorearnings.com/wp-content/uploads/2014/02/Amazon-US-Kindle-bestsellers-anon-snapshot-20140207-v8.xlsx',
   sheet=2,pattern='Sold by',stringsAsFactors=F,as.is=T)
d <- do
colnames(d) <- gsub('\\.\\.+','',colnames(do))
numCols <- c('Daily.Units.Sold', 'Daily.Gross.Sales', 
   'Daily.Amazon.Revenue', 'Daily.Publisher.Revenue', 
   'Daily.Author.Revenue')
for (col in numCols)  { 
   d[,col] <- as.numeric(gsub(',','',d[,col]))
}
stateCols <- c('Indie.Publisher', 'Small.or.Medium.Publisher',
   'Amazon.Publsher', 'Big.Five.Publisher',
   'Uncategorized.Single.Author.Publisher', 'Nonfiction',
   'Genre.Fiction', 'FictionampLiterature', 'Children.s.Books',
   'ComicsampGraphic.Novels', 'Foreign.Language')
for (col in stateCols) {
   d[is.na(d[,col]),col] <- 0
}

dsub <- subset(d,Small.or.Medium.Publisher==1 & 
   Indie.Publisher==0 &
   Genre.Fiction==0 & FictionampLiterature==0 &
   Children.s.Books==0 &
   ComicsampGraphic.Novels==0 &
   Nonfiction==1 & Foreign.Language==0)

model <- gam(Daily.Units.Sold ~ s(Total.Reviews) + s(Average.Rating) + s(Sale.Price),data=dsub)
print(summary(model))

ggplot(data=dsub) + geom_density(aes(x=Average.Rating))
plot(model,ask=T)
save(list=ls(),file='amazonBookData.Rdata')


model2 <- gam(log(Daily.Units.Sold) ~ s(Total.Reviews) + s(Average.Rating) + s(Sale.Price),data=dsub)
print(summary(model2))

summary(dsub$Daily.Units.Sold)
ggplot(data=dsub) + geom_density(aes(x=log(Daily.Units.Sold)))
ggplot(data=subset(dsub,Daily.Units.Sold<=20)) + geom_bar(aes(x=Daily.Units.Sold),binwidth=1)



