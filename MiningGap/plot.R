
# load libraries
require(ggplot2)
require(mgcv)
require(reshape2)

# Load data, and make sure x is increasing
d <- read.table('NMsg.csv',header=T,sep=',')
d <- d[order(d$DaysBeforeAfterRelationship),]

# plot something similar to original graph
ggplot(data=d,aes(x=DaysBeforeAfterRelationship,
   y=NumberOfTimelinePosts)) +
   geom_point() + 
   stat_smooth(method = "gam", formula = y ~ s(x))

# What would individuals generating posts
# as a Poisson process with a given intensity
# look like around 100 days before forming
# a relationship, right before forming a relationship,
# and long after a relationship is formed?
earlyIntensity <- mean(
   d[d$DaysBeforeAfterRelationship >= -100 &
   d$DaysBeforeAfterRelationship < -80,
   'NumberOfTimelinePosts'])
print(earlyIntensity)
nearIntensity <- mean(
   d[d$DaysBeforeAfterRelationship >= -20 &
     d$DaysBeforeAfterRelationship < 0,
   'NumberOfTimelinePosts'])
print(nearIntensity)
afterIntensity <- mean(
   d[d$DaysBeforeAfterRelationship >= 80 &
     d$DaysBeforeAfterRelationship < 100,
   'NumberOfTimelinePosts'])
print(afterIntensity)
set.seed(2315531)
density <- data.frame(NumberOfTimelinePosts=0:10)
density$nearCounts <- dpois(
   density$NumberOfTimelinePosts,
   lambda=nearIntensity)
density$afterCounts <- dpois(
   density$NumberOfTimelinePosts,
   lambda=afterIntensity)
dm <- melt(density,
   id.vars=c('NumberOfTimelinePosts'),
   variable.name='group',
   value.name='density')
ggplot(data=dm) +
   geom_bar(stat='identity',position='dodge',
      aes(x=NumberOfTimelinePosts,y=density,fill=group)) +
  scale_x_continuous(breaks=density$NumberOfTimelinePosts)
print(dm[dm$NumberOfTimelinePosts==4,])
##    NumberOfTimelinePosts       group    density
## 5                      4  nearCounts 0.05957193
## 16                     4 afterCounts 0.05019702

# If the original data was generated from
# independent individuals with slowly varying
# Poisson intensity, then we could estimate the
# degree of aggregation to see the mean^2/variance
# ration in the plot.
odd <- 2*(1:(dim(d)[[1]]/2))-1
varEst <- sum((d[odd,'NumberOfTimelinePosts']
   -d[odd+1,'NumberOfTimelinePosts'])^2)/(2*length(odd))
print(varEst)
## [1] 2.289848e-05
meanEst <- mean(d$NumberOfTimelinePosts)
print(meanEst)
## [1] 1.599492
kEst <- meanEst/varEst
print(kEst)
## [1] 69851.47
