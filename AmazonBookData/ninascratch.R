# Random questions to answer:
# average rank by:  average rating, total reviews (should be correlated?)
#                   publisher type, price
# same for units sold
#

# subset to the ones where sales aren't na

dsold = subset(d, !is.na(Daily.Units.Sold))

ggplot(dsold, aes(x=Sale.Price)) + geom_density() + scale_x_log10()
ggplot(dsold, aes(x=Total.Reviews)) + geom_density() + scale_x_log10()
ggplot(dsold, aes(x=Average.Rating)) + geom_density() 
ggplot(dsold, aes(x=Daily.Units.Sold)) + geom_density() + scale_x_log10()

publisherType = c('Indie', 'Small/Med', 'Amazon', 'Big5', 'Single.Author')

publisherCode = with(dsold, 1*Indie.Publisher+2*Small.or.Medium.Publisher+3*Amazon.Publsher+
                       4*Big.Five.Publisher+5*Uncategorized.Single.Author.Publisher)
dsold$publisherType=publisherType[publisherCode]

dfic = subset(dsold, Genre.Fiction==1 | FictionampLiterature==1)

freqTab = table(dfic$publisherType)/dim(dfic)[1]
ggplot(as.data.frame(freqTab), aes(x=Var1, y=Freq)) + geom_bar(stat="identity") + xlab("publisherType")

qmin = function(x) {quantile(x, 0.05)}
qmax = function(x) {quantile(x, 0.95)}
q25 = function(x) {quantile(x, 0.25)}
q75 = function(x) {quantile(x, 0.75)}

# change these graphs to fake a boxplot where the box section covers the central 50%
# and the lines the central 90% 


comparisonPlot = function(dframe, y) {
  ggplot(dframe, aes_string(x="publisherType", y=y)) +
    stat_summary(fun.ymin=qmin, fun.ymax=qmax, geom="linerange") + 
    stat_summary(fun.y=median, fun.ymin=q25, fun.ymax=q75, geom="crossbar", fill="gray")
}

# big five most expensive
comparisonPlot(dfic, "Sale.Price")

# big five gets most reviews
comparisonPlot(dfic, "Total.Reviews")

# amazon published sell best
comparisonPlot(dfic, "Daily.Units.Sold")

# somewhat mirror sales (not surprising)
comparisonPlot(dfic, "Daily.Author.Revenue")

comparisonPlot(dfic, "Daily.Gross.Sales")

# also do a regression of sales vs. pub, reviews, ratings

library(mgcv)
fmla = as.formula("Daily.Units.Sold ~ publisherType +
                        s(Sale.Price) + s(Total.Reviews) + s(Average.Rating)")

include = dfic$Daily.Units.Sold <= qmax(dfic$Daily.Units.Sold)
dfic_clip = dfic[include,]

model = gam(fmla, data=dfic_clip)  # those who sold < 146 units/day (covers 95% of the data)

#
# Amazon published did best, indies did next best. ratings appear significant
#
# > summary(model)
# 
# Family: gaussian 
# Link function: identity 
# 
# Formula:
#   Daily.Units.Sold ~ publisherType + s(Sale.Price) + s(Total.Reviews) + 
#   s(Average.Rating)
# 
# Parametric coefficients:
#   Estimate Std. Error t value Pr(>|t|)    
# (Intercept)                  40.586      1.349  30.075  < 2e-16 ***
#   publisherTypeBig5           -10.759      1.555  -6.921 4.78e-12 ***
#   publisherTypeIndie           -6.493      1.481  -4.384 1.18e-05 ***
#   publisherTypeSingle.Author  -16.773      1.590 -10.550  < 2e-16 ***
#   publisherTypeSmall/Med      -19.340      1.465 -13.199  < 2e-16 ***
#   ---
#   Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1
# 
# Approximate significance of smooth terms:
#   edf Ref.df      F p-value    
# s(Sale.Price)     7.289  8.192  37.13  <2e-16 ***
#   s(Total.Reviews)  6.340  7.394 228.04  <2e-16 ***
#   s(Average.Rating) 3.539  4.306  51.53  <2e-16 ***
#   ---
#   Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1
# 
# R-sq.(adj) =   0.23   Deviance explained = 23.1%
# GCV score = 812.49  Scale est. = 810.58    n = 9437

# extract the terms

sx = predict(model, type="terms")
# > summary(sx)
# publisherType     s(Sale.Price)     s(Total.Reviews) s(Average.Rating)
# Min.   :-19.340   Min.   :-24.013   Min.   :-9.228   Min.   :-8.4991  
# 1st Qu.:-19.340   1st Qu.: -3.990   1st Qu.:-8.300   1st Qu.:-3.1921  
# Median :-10.759   Median : -1.266   Median :-5.673   Median :-0.1852  
# Mean   :-12.496   Mean   :  0.000   Mean   : 0.000   Mean   : 0.0000  
# 3rd Qu.: -6.493   3rd Qu.:  2.220   3rd Qu.: 1.555   3rd Qu.: 2.5521  
# Max.   :  0.000   Max.   : 11.469   Max.   :72.353   Max.   :12.2955  

# terms needs to be a data frame, predict returns a matrix
# the xstr needs to be continuous, or else the plotting doesn't work quite right
# (and analysis, I think) doesn't work quite right.
analyzeS = function(xstr, ystr, data, terms, nonlin=T) {
  if(nonlin) {
    termstr = paste("s(",xstr, ")", sep='')
  } else {termstr = xstr}
  
  xdata = data[[xstr]]
  ydata = data[[ystr]]
  sdata = terms[[termstr]]
  
  meanY = mean(ydata)
  maxS = max(sdata)
  minS = min(sdata)
  maxdelta = max(maxS, abs(minS)) # max should really always be positive, min always negative
  maxRelChange = maxdelta/meanY
  
  plt = ggplot(data.frame(x=xdata, sx=sdata+meanY), aes(x=x,y=sx)) +
    geom_line() + geom_rug(sides="b") + xlab(xstr) + ylab(ystr)
  
  print(plt)
  list(center = meanY, max.rel.change = maxRelChange, avg.rel.change = sd(sdata)/meanY)
}


#
# mean unit sales = 28.09028
#
analyzeS("Sale.Price", "Daily.Units.Sold", dfic_clip, as.data.frame(sx))
# $max.rel.change
# [1] 0.8548462
# $avg.rel.change
# [1] 0.2044394

analyzeS("Total.Reviews", "Daily.Units.Sold", dfic_clip, as.data.frame(sx))
# $max.rel.change
# [1] 2.575726
# $avg.rel.change
# [1] 0.4912535

analyzeS("Average.Rating", "Daily.Units.Sold", dfic_clip, as.data.frame(sx))
# $max.rel.change
#[1] 0.4377132
#$avg.rel.change
# [1] 0.1607792

# hmm. still not that good. underpredicts for the high sellers, still
df = data.frame(actual=dfic_clip$Daily.Units.Sold, pred=predict(model))
ggplot(df, aes(y=actual, x=pred)) +
  geom_point(alpha=0.5) + geom_line(aes(y=pred)) + geom_smooth()

ggplot(df, aes(x=pred, y=(pred-actual))) + geom_point(alpha=0.5) +geom_smooth()

ggplot(df, aes(x=actual, y=(pred-actual))) + geom_point(alpha=0.5) +geom_smooth()

df2 = data.frame(actual=dfic_clip$Daily.Units.Sold, pred=predict(model.lm))
ggplot(df2, aes(x=pred, y=(pred-actual))) + geom_point(alpha=0.5) +stat_smooth(method="lm")

ggplot(df2, aes(x=pred, y=(pred-actual))) + geom_point(alpha=0.5) + geom_smooth()

with(df, sqrt(mean((actual-pred)^2)) )
# [1] 28.43723 -- not too different from the linear.

model.lm = lm("Daily.Units.Sold ~ publisherType + Sale.Price + Total.Reviews + Average.Rating",
              data=dfic_clip)
lm(formula = "Daily.Units.Sold ~ publisherType + Sale.Price + Total.Reviews + Average.Rating", 
   data = dfic_clip)

# somewhat consistent findings on the publisher type.
# Residuals:
#   Min       1Q   Median       3Q      Max 
# -240.685  -18.554  -10.518    3.954  132.964 
# 
# Coefficients:
#   Estimate Std. Error t value Pr(>|t|)    
# (Intercept)                 4.502e+01  1.948e+00  23.110  < 2e-16 ***
#   publisherTypeBig5          -9.527e+00  1.572e+00  -6.060 1.41e-09 ***
#   publisherTypeIndie         -7.311e+00  1.528e+00  -4.785 1.74e-06 ***
#   publisherTypeSingle.Author -1.861e+01  1.635e+00 -11.387  < 2e-16 ***
#   publisherTypeSmall/Med     -2.333e+01  1.507e+00 -15.487  < 2e-16 ***
#   Sale.Price                 -9.155e-01  1.239e-01  -7.388 1.61e-13 ***
#   Total.Reviews               2.354e-02  7.992e-04  29.447  < 2e-16 ***
#   Average.Rating             -6.028e-01  3.066e-01  -1.966   0.0493 *  
#   ---
#   Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1
# 
# Residual standard error: 29.89 on 9429 degrees of freedom
# Multiple R-squared:  0.1518,  Adjusted R-squared:  0.1512 
# F-statistic: 241.1 on 7 and 9429 DF,  p-value: < 2.2e-16

ggplot(data.frame(actual=dfic_clip$Daily.Units.Sold, pred=predict(model.lm)), aes(x=actual, y=pred)) +
  geom_point(alpha=0.5) + geom_line(aes(y=actual))

x = dfic_clip$Total.Reviews
y = as.data.frame(sx)[["s(Total.Reviews)"]] + 28.09028
tmp = data.frame(Total.Reviews=x, sTotal.Reviews=y)

ggplot(tmp, aes(x=Total.Reviews, y=sTotal.Reviews)) + geom_line() + 
  geom_rug(sides="b") + ylab("Daily.Units.Sold") + coord_cartesian(xlim=c(0,5000))
