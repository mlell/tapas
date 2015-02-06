optionalArguments <-
function(eargs){
    stopifnot("expectedArgs" %in% class(eargs))
    margs = mandatoryArguments(eargs)
    allargs=names(eargs)
    return( allargs[! allargs %in% margs])
}
