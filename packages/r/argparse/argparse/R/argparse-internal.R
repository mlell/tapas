.coerce <-
function(val, as){
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
.getFlagIndices <-
function(args){
    return(which(substr(args,0,2)=="--"))
}
.transformFlags <-
function(args){
    ind=.getFlagIndices(args)
    flagNames=substring(args[ind],3)
    args[ind]=paste0(flagNames,"=TRUE")
    return(args)
}
