
fn <- function(x) {
  res <- x %>% 
    mutate(., zz = 2*z) %>%
    mutate(., qq = 2*q) %>%
    mutate(., tt = 2*x)
  res
}

fnB <- function(x) {
  x ->.; 
    mutate(., zz = 2*z) ->.;
    mutate(., qq = 2*q) ->.;
    mutate(., tt = 2*x) -> res
  res
}

fnE <- function(x) {
  x %->%.; 
    mutate(., zz = 2*z) %->%.;
    mutate(., qq = 2*q) %->%.;
    mutate(., tt = 2*x) -> res
  res
}


fnP <- function(x, v1, v2, v3) {
  let(c(V1=v1, V2=v2, V3=v3), {
    x %->%.; 
      mutate(., zz = 2*V1) %->%.;
      mutate(., qq = 2*V2) %->%.;
      mutate(., tt = 2*V3) -> res
  })
  res
}


