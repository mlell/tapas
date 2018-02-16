#!/usr/bin/env RScript

help="
Usage: setup_r_check_dependencies [PACKAGENAME]...

For each PACKAGENAME, print a line whether the package is found and 
can be loaded without errors.
"

pkgs = commandArgs(TRUE)

all.ok = TRUE
not.found = c()
damaged = c()

for(p in pkgs){
    loc = find.package(p,quiet=TRUE)    
    if(length(loc) == 0){
        cat(sprintf("%s NOT FOUND.\n",p))
        not.found = c(not.found, p)
        all.ok = FALSE
    }else{
        loadable = suppressPackageStartupMessages(
            require(p, quiet=TRUE, character.only=TRUE)
        )
        if(!loadable){
            all.ok = FALSE
            damaged = c(damaged, p)
        }
        cat(sprintf("%s FOUND and %s (%s)\n",
            p, 
            if(loadable) "LOADABLE" else "NOT LOADABLE",
            loc))
    }
}

if(length(not.found)>0){
    cat('#>## Install the following R packages: ',toString(not.found),'\n')
    cat('#> \n')
}
if(length(damaged)>0){
    cat('#>## The following R packages threw an ERROR DURING LOADING: \n')
    cat('#>##\n')
    cat('#>##   ',toString(damaged),'\n')
    cat('#>##\n')
    cat('#>## This may be due to the package itself or one of its dependencies\n')
    cat('#>## Load them using `library(...)` in an interactive R session \n')
    cat('#>## and check the error messages.\n')
    cat('#> \n')
}

if(all.ok) quit(status=0)
if(!all.ok) quit(status=1)
