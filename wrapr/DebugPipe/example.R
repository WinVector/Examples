
library("dplyr")
library("wrapr")

source("fns.R")

d <- data_frame(x=1:5, z=1)




fn(d)

fnB(d)

fnL(d)



my_db <- dplyr::src_sqlite(":memory:", 
                           create = TRUE)
d2 <- dplyr::copy_to(my_db, d)



fnB(d2)


devtools::install_github("WinVector/replyr")
library("replyr")



fnE(d2)

fnP(d, 'z', 'q', 'x')



df <- DebugFnW(as.name('lastError'), fnP)

df(d2, 'z', 'q', 'x')

do.call(lastError$fn_name, lastError$args)


