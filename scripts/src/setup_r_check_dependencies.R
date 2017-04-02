#!/usr/bin/env RScript


pkgs = commandArgs(TRUE)

for(p in pkgs){
    loc = find.package(p,quiet=TRUE)    
    if(length(loc) == 0){
        cat(file=stderr(),sprintf("Package %s NOT FOUND.\n",p))
    }else{
        loadable = suppressPackageStartupMessages(
            require(p, quiet=TRUE, character.only=TRUE)
        )
        cat(file=stderr(),sprintf("Package %s CAN %sbe loaded from %s\n",
            p, 
            if(!loadable) "NOT " else "", 
            loc))
    }
}
