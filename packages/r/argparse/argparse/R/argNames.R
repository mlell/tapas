argNames <-
function(expectedArgs){
    stopifnot( "expectedArgs" %in% class(expectedArgs))
    return(names(expectedArgs))
}
