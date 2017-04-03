#!/usr/bin/env Rscript
library(docopt)
library(ggplot2)
library(gridExtra)
doc="Usage: preview.R MUT_TAB OUTPUT_FILE

Plot the mutation probabilities specified in the given MUT_TAB
"
#f="data/gen/mut-param/GS136.tab"
main <- function(argv){
    args=docopt(doc=doc, args=argv)
    
    t <- read.table(args[['MUT_TAB']], header=TRUE, row.names=NULL, 
                    sep="", dec='.', stringsAsFactors=FALSE)

    x1 <- c(1,20)
    x2 <- c(20,1)

    d <- function(range, tab, strand){
        out <- list()
        x <- range[1]:range[2]
        for(l in 1:nrow(tab)){
            f <- t[l,"factor"]
            p <- t[l,"geom_prob"]
            i <- t[l,"intercept"]
            s <- t[l,"strand"]
            if(! s %in% c(3,5)) stop("strand must be 3 or 5!")
            if(s == strand){
                out[[l]] <- f*dgeom(x-1,p=p)+i
            }
            else{
                out[[l]] <- rep(i,length(x))
            }
        }

        outdf=do.call(data.frame,out)

        colnames(outdf) <- paste0("y",1:length(out))
        outdf = stack(outdf)
        outdf$x <- rep(x,length(out))
        colnames(outdf)[colnames(outdf)=="ind"] <- "row"
        colnames(outdf)[colnames(outdf)=="values"] <- "prob"
        #outdf$i <- rep(seq_along(out), each=length(out[[1]]))
        return(outdf)

    }
    data_3 = d(x1,t,3)
    data_5 = d(x1,t,5)

    p5 <- ggplot(data_5) + aes(x=x,y=prob,fill=row,color=row) + geom_area()+
        ylim(0,1) + scale_fill_discrete(guide="none")+ 
        scale_color_discrete(guide="none")
    p3 <- ggplot(data_3) + aes(x=x,y=prob,fill=row,color=row) + geom_area()+
        scale_x_reverse() + ylim(0,1) +
        scale_color_discrete(guide="none")

    pdf(args$OUTPUT_FILE, w=5,h=3)
    grid.arrange(p5, p3, ncol=2, nrow=1)
    dev.off()

}

main(commandArgs(TRUE))


