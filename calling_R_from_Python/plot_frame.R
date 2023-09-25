
library(ggplot2)


plt_frame <- function(d) {
  ggplot(data = d, mapping = aes(x = x, y = y)) +
    geom_point()
}
