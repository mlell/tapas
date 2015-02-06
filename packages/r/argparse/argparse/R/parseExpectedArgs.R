parseExpectedArgs <-
function(s,sep="|",expectedMark="<>",helpText=""){
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
