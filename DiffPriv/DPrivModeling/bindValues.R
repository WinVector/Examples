#' Copy arguments into env and re-bind any function's lexical scope to bindTargetEnv
#' 
#' Used to send data along with a function in situations such as parallel execution 
#' (when the global environment would not be available).
#' 
#' @param bindTargetEnv environment to bind to
#' @param objNames additional names to lookup in parent environment and bind
bindToEnv <- function(...,bindTargetEnv=parent.frame(),objNames=c()) {
  # get names of variables used as ... aguments in function call
  dnames <- sapply(substitute(list(...))[-1],deparse)
  # get the values
  dvalues <- list(...)
  # makes sure there are no other named assignments
  if(!is.null(names(dvalues))) {
    stop("unexpected named assignments")
  }
  # merge in any value (non "=") assigments as names
  names(dvalues) <- dnames
  # now bind the values into environment
  # and switch any functions to this environment!
  for(var in names(dvalues)) {
    val <- dvalues[[var]]
    if(is.function(val)) {
      environment(val) <- bindTargetEnv
    }
    assign(var,val,envir=bindTargetEnv)
  }
  # same for any names from the parent environment
  if(!is.null(objNames)) {
    for(var in objNames) {
      val <- get(var,envir=parent.frame())
      if(is.function(val)) {
        environment(val) <- bindTargetEnv
      }
      assign(var,val,envir=bindTargetEnv)
    }
  }
}

