printHelp <-
function(expectedArgs){
    print(do.call(rbind,expectedArgs))
    cat("\n\n")
    cat(attr(expectedArgs,"helpText"))
}
