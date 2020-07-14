#n <- 20
#d <- data.frame(x1=rnorm(n),x2=rnorm(n))
#d$y <- with(d,x1+2*x2>3*rnorm(n))
#write.table(d,file='dGLMdat.csv',quote=F,sep=',',row.names=F)
#d <- read.table(file='dGLMdat.csv',header=T,sep=',')
d <- read.table(file='http://www.win-vector.com/dfiles/glmLoss/dGLMdat.csv',header=T,sep=',')
m <- glm(y~x1+x2,data=d,family=binomial(link='logit'))
summary(m)
d$s <- predict(m,type='response')
sum(with(d,2*(s-y)))
sum(with(d,2*(s-y)*x1))
sum(with(d,2*(s-y)*x2))
sum(with(d,2*(s-y)*s*(1-s)))
sum(with(d,2*(s-y)*s*(1-s)*x1))
sum(with(d,2*(s-y)*s*(1-s)*x2))
grad <- c(sum(with(d,2*(s-y)*s*(1-s))),sum(with(d,2*(s-y)*s*(1-s)*x1)),sum(with(d,2*(s-y)*s*(1-s)*x2)))
f <- function(a,b,c) {
   s <- function(x) { 1/(1+exp(-x)) }
   v <- s(a + b*d$x1 + c*d$x2)
   d <- v-d$y
   sum(d*d)
}
g <- function(w) { f(m$coefficients[1]-w*grad[1],m$coefficients[2]-w*grad[2],m$coefficients[3]-w*grad[3]) }
opt <- optimize(g,interval=c(-20,20))
w  <- opt$minimum
m$coefficients
c(m$coefficients[1]-w*grad[1],m$coefficients[2]-w*grad[2],m$coefficients[3]-w*grad[3])
sum(with(d,(y-s)*(y-s)))
f(m$coefficients[1],m$coefficients[2],m$coefficients[3])
f(m$coefficients[1]-w*grad[1],m$coefficients[2]-w*grad[2],m$coefficients[3]-w*grad[3])
d

