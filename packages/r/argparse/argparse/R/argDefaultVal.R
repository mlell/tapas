argDefaultVal <-
function(argName, expectedArgs){
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
