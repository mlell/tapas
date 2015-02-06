#!/usr/bin/Rscript

# Generate a set of numeric ranges with the following properties
# * Uniformly distributed across a given Range
# * Normal distributed in length, with P
# Author: Moritz Lell (2015-Feb-13)

# Get command line: Rscript <Scriptname> A B C ...
#                                       |------- ... --|


# Top-Level function. Expects a table like this as string:
# a | numeric   | <>    | Help text for a
# b | character | abc   | Help text for b
# c | logical   | FALSE | Help text for c
# d | numeric   | 1     | Help text for d
parseArguments = function(expectedArgumentText){
    return(parseCommandLine(parseExpectedArgs(expectedArgumentText)))
}


# Create a data structure specifying which arguments are accepted.
parseExpectedArgs=function(s,sep="|",expectedMark="<>",helpText=""){
    # Parse as data.frame
    tab=read.table(text=s, header=FALSE, sep=sep,
                   stringsAsFactors=FALSE, strip.white=TRUE)
    colnames(tab)=c("name","type","val","help")
    # Transcribe in list, one entry per argument
    if(any(tab$val == "NULL",na.rm=TRUE)) 
        stop("NULL is not allowed as default value for optional argument!")
    out=list()
    class(out)=c(class(out),"expectedArgs")
    for (i in 1:nrow(tab)){
        # Check for all FALSE defaults for flags
        if( ( tab[i,]$type  ==   "logical"      ) && 
            (! tab[i,]$val %in% c("FALSE","F"))   )
            stop("Default values of logical arguments may only be
                 FALSE!. Rewrite your argument name to no-[name] to
                 implement opt-out behaviour!")
        # Create one list entry per argument
        out[[tab$name[i]]] = as.list(tab[i,]) 
    }
    # Save placeholder for mandatory arguments
    attr(out,"expectedMark") = expectedMark
    attr(out,"helpText") = helpText
    return(out)
}

# Return the type of the argument with the given name.
argType = function(argName, expectedArgs){
    stopifnot( "expectedArgs" %in% class(expectedArgs))
    return( expectedArgs[[argName]]$type)
}

argNames = function(expectedArgs){
    stopifnot( "expectedArgs" %in% class(expectedArgs))
    return(names(expectedArgs))
}

.coerce = function(val, as){
    if(is.na(as) || is.null(as))
        stop("NA or NULL given as target type for coercion")
    if(as == "numeric")
        return(as.numeric(val))
    if(as == "character")
        return(as.character(val))
    if(as == "logical")
        return(as.logical(val))
    else
        stop("Only logical, character and numeric are allowed as argument
             types! Given: ",as)
}

# Return default value of Argument if it is optional, NULL otherwise.
argDefaultVal= function(argName, expectedArgs){
    stopifnot( "expectedArgs" %in% class(expectedArgs))
    stopifnot( mode(argName) == "character")
    val = expectedArgs[[argName]]$val
    if(is.null(val))
        return(NULL)
    if(is.na(val))
        return(NA)
    if(val == attr(expectedArgs,"expectedMark"))
        # Return NULL if the argument is mandatory
        val = NULL
    else
        # Return value with correct type otherwise
        val = .coerce(val=val,
                 as= argType(argName,expectedArgs))
    return(val)
}

# Return the names of all mandatory arguments
mandatoryArguments = function(eargs){
    stopifnot("expectedArgs" %in% class(eargs))
    # Placeholder value in case of mandatory argument
    em=attr(eargs,"expectedMark")
    # Create list of mandatory arguments
    mandIndices=unlist(lapply(eargs,function(arg){
        # Caution: NA == <x> yields NA, not TRUE or FALSE
        # => extra clause: return FALSE if default value == NA
        # NA is a default value => not mandatory argument
        (!is.na(arg$val)) && (arg$val == em)
    }))
    return(names(eargs)[mandIndices])
}

# Return the names of all optional arguments
optionalArguments = function(eargs){
    stopifnot("expectedArgs" %in% class(eargs))
    margs = mandatoryArguments(eargs)
    allargs=names(eargs)
    return( allargs[! allargs %in% margs])
}

arglist=function(){
    args=commandArgs(trailing=TRUE)
    args=.transformFlags(args)
    a=strsplit(args,split="=")
    if(!all(unlist(lapply(a,length))==2)){
        stop("All Arguments must be of the form --flag or name=value!")
    }
    return(a)
}

# Expects a character vector and returns element indices beginning
# with "--"
.getFlagIndices=function(args){
    return(which(substr(args,0,2)=="--"))
}

# Expects a character vector and translates strings of the form
# --Aaaa into Aaaa=TRUE
.transformFlags = function(args){
    ind=.getFlagIndices(args)
    flagNames=substring(args[ind],3)
    args[ind]=paste0(flagNames,"=TRUE")
    return(args)
}

parseCommandLine = function(expectedArgs){
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

printHelp = function(expectedArgs){
    print(do.call(rbind,expectedArgs))
    cat("\n\n")
    cat(attr(expectedArgs,"helpText"))
}



# vim: tw=70
