
library("dplyr")

source("fns.R")

d <- data_frame(x=1:5, z=3:7)










# There are a few issues with debugging pipelines:
#  1) The whole pipeline is one expression
#  2) Visibility of the intermediate results
#  3) Localizing operations in the presence of lazy evaluation
fn(d)

# Issues 1 & 2 can be addressed by use of 
# explicit dot notation and the Bizarro pipe
# "->;."
# http://www.win-vector.com/blog/2017/01/using-the-bizarro-pipe-to-debug-magrittr-pipelines-in-r/
fnB(d)

my_db <- dplyr::src_sqlite(":memory:", 
                           create = TRUE)
d2 <- dplyr::copy_to(my_db, d)

fnB(d2)

# Issue 3 (when it arises) 
# can be mitigate by using the 
# "eager landing pipe" %->%
# from the development version of replyr
# https://github.com/WinVector/replyr
devtools::install_github("WinVector/replyr")
library("replyr")

fnE(d2)


# This works (with some caveats)
# even in the presence of wrapr::let
# https://github.com/WinVector/wrapr
library("wrapr")
fnP(d, 'z', 'q', 'x')


# And for debug-wrapped functions we can 
# re-enter and inspect later.
df <- DebugFnW(as.name('lastError'), fnP)
df(d2, 'z', 'q', 'x')

do.call(lastError$fn_name, lastError$args)


