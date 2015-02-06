arglist <-
function(){
    args=commandArgs(trailing=TRUE)
    args=.transformFlags(args)
    a=strsplit(args,split="=")
    if(!all(unlist(lapply(a,length))==2)){
        stop("All Arguments must be of the form --flag or name=value!")
    }
    return(a)
}
