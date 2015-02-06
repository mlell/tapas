parseCommandLine <-
function(expectedArgs){
    stopifnot("expectedArgs" %in% class(expectedArgs))
    if("--help" %in% commandArgs(trailing=TRUE) ||
       "-h"     %in% commandArgs(trailing=TRUE)){
        printHelp(expectedArgs)
        stop("Help printed.")
    }
    `%not in%` = function(a,b) !a%in%b
    out=list()
    a=arglist()
    for(arg in a){
        argName=arg[[1]]
        if(! argName %in% argNames(expectedArgs))
            stop("Argument ",argName," is not expected.")
        argVal=arg[[2]]
        argType=argType(argName     = argName,
                        expectedArgs= expectedArgs)
        out[[arg[1]]]=.coerce(val=argVal, 
                              as=argType)
    }
    margs=mandatoryArguments(expectedArgs)
    oargs=optionalArguments(expectedArgs)
    missingMargs = margs[margs %not in% names(out)]
    if(length(missingMargs)>0)
        stop("Mandatory Argument(s) ",paste(missingMargs,sep=" ")," missing!")
        missingOargs = oargs[oargs %not in% names(out)]
    for(arg in missingOargs){
        out[[arg]] = argDefaultVal(argName=arg,
                                   expectedArgs=expectedArgs)
    }
    # Check mandatory arguments for validity
    for(a in margs){
        if(is.na(out[a]) || is.null(out[a])){
            stop("Mandatory argument ",a," has the illegal value ",
                 out[a],"!")
        }
    }
    return(out)
}
