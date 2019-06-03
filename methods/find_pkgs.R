
#' @param obj object to inspect
#' @param pkg_list packates to consider
#' @param show_details character, if not NULL show details of decision around this package
#' @return vector of suggested packages
#'
suggested_packages <- function(obj, pkg_list = .packages(), show_details = NULL) {
  force(obj)
  force(pkg_list)

  base_packages <- c("stats", "graphics", "grDevices", "utils", "datasets", "methods", "base", "")
  base_classes <- c("data.frame", "numeric", "character", "factor", "integer", "logical",
                    "list", "")

  #' @param obj object to inspect
  #' @return charater vector of classes of object and contained objects
  #'
  get_involved_classes <- function(obj) {
    if(is.null(obj)) {
      return(character(0))
    }
    cl <- class(obj)
    if(is.list(obj)) {
      sub_cl <- lapply(obj, get_involved_classes)
      sub_cl <- unlist(sub_cl, recursive = TRUE, use.names = FALSE)
      sub_cl <- unique(sub_cl)
      cl <- unique(c(cl, sub_cl))
    }
    cl
  }

  #' @param cl class name
  #' @return character vector of interesting S3 methods
  #'
  get_interesting_methods <- function(cl) {
    m <- methods(class = cl)
    t <- attr(m, "info")
    mthds <- rownames(t)[as.character(t$from)!='']
    mthds <- mthds[endsWith(mthds, paste0(".", cl))]
    generics <- substr(mthds, 1, nchar(mthds) - (nchar(cl) + 1))
    d <- data.frame(class = cl,
                    methods = mthds,
                    generics = generics,
                    stringsAsFactors = FALSE)
    d$package <- character(nrow(d))
    for(i in seq_len(nrow(d))) {
      tryCatch({
        d$package[[i]] <- getNamespaceName(environment(getS3method(d$generics[[i]], class=d$class[[i]])))
      },
      error = function(e) { invisible(NULL) }
      )
    }
    d
  }


  # build a data.frame of class and interesting methods
  cl_list <- get_involved_classes(obj)
  cl_list <- setdiff(cl_list, base_classes)
  mthds <- lapply(cl_list, get_interesting_methods)
  mthds <- do.call(rbind, mthds)
  mthds <- mthds[!(mthds$package %in% base_packages), , drop = FALSE]

  # build a data.frame of non-base attached packages and methods
  attached_pkgs <- setdiff(pkg_list, base_packages)

  reasons <- mthds[mthds$package %in% attached_pkgs, , drop = FALSE]
  rownames(reasons) <- NULL
  hits <- reasons[, c("class", "package")]
  hits <- unique(hits)
  rownames(hits) <- NULL
  result <- sort(unique(hits$package))
  if(length(show_details)>0) {
    explain <- reasons[reasons$package %in% show_details, , drop = FALSE]
    rownames(explain) <- NULL
    attr(result, "explain") <- explain
  }
  result
}






