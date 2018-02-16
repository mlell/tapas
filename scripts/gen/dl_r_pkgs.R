#!/usr/bin/env Rscript
args <- commandArgs(TRUE)

deptabfile = "r_deps.txt"
dest = "../lib/r-src"

while(length(args) != 0 && substr(args,1,2) == "--"){
    if(args[1] == "--"){
        args <- args[-1]
        break
    }else if(args[1] == "--help"){
        cat(
"Usage: dl_r_pkgs [--deplist DEPLIST] [--dest DESTDIR]

Download an R souce package into the TAPAS R library source package.

This tool is only needed by developers if a new R package version
needs to be distributed along with TAPAS.

--deplist DEPLIST:  
          A file name which contains a two-column table of R package
          names and versions for download.

--dest DEST:
          A directory where to put the downloaded files.

", file=stderr())
        q("no")
    } else if(args[1] == "--dest"){
        dest = args[2]
        args = args[-2:-1]
    } else if(args[1] == "--deplist"){
        deptabfile = args[2]
        args = args[-2:-1]
    }else{
        cat("Error: Invalid parameter ",args[1],". See --help.")
        q("no", status = 127)
    }
}

# --- End of argument parsing ---------------------------------------------
if(!file.exists("dl_r_pkgs.R")){
    cat("Error: Set working directory to directory of this script!")
    q("no",status = 1)
}

dlPkgVer <- function(pkgname, ver, destdir, skipExisting = TRUE){
    pkgfile <- paste0(pkgname,"_",ver,".tar.gz")
    pkgpath <- file.path(destdir, pkgfile)
    url <- paste0(options("repos"), "/src/contrib/", pkgfile)
    if(!file.exists(pkgpath) || !skipExisting){
        download.file(url, destfile = pkgpath)
    }else{
        message("Skip ",pkgfile," (exists already)")
    }
    return(pkgpath)
}

if(options("repos") == "@CRAN@"){
    options(repos = "https://cloud.r-project.org")
}
deptab <- read.table(deptabfile, row.names = NULL, header = FALSE, stringsAsFactors = FALSE)
for(row in seq_len(nrow(deptab))){
    dlPkgVer(deptab[row,1], deptab[row,2], dest)
}

