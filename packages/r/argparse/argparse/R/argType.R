argType <-
function(argName, expectedArgs){
    stopifnot( "expectedArgs" %in% class(expectedArgs))
    return( expectedArgs[[argName]]$type)
}
