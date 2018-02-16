#!/usr/bin/env Rscript

if(!file.exists("scan_r_dependencies.R")){
    stop("Error: Change the working directory to the enclosing folder of this script")
}
if(options("repos") == "@CRAN@"){
    options(repos = "https://cloud.r-project.org")
}
p <- packrat:::dirDependencies("../src")
deps <- tools::package_dependencies(p, recursive = TRUE)
deps <- lapply(deps, rev) # Dependencies must come before top-level pkgs
deps <- unique(c(unlist(deps),p))

availPkgs <- available.packages()
insPkgs <- installed.packages()
partofR <- insPkgs[substr(insPkgs[,"License"],1,9) == "Part of R","Package"]
deps <- setdiff(deps, partofR)
ret <- availPkgs[deps, c("Package","Version")]
ret <- as.data.frame(ret, stringsAsFactors = FALSE)
colwd <- lapply(ret, function(col) max(nchar(as.character(col))))
ret <- mapply(ret, colwd, FUN = function(col,n) format(col,width=n,justified='left'))

ret <- apply(ret, 1, paste0, collapse = " ")
cat(ret, sep='\n')
