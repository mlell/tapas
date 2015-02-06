mandatoryArguments <-
function(eargs){
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
