#!/usr/bin/env Rscript

library(methods)
library(docopt)
suppressPackageStartupMessages(
library(dplyr))
library(ggplot2)
library(magrittr)
library(lazyeval)

help = "
Usage: plot_mapping_runs.R [options] TABLE X Y PLOT_NAME

Plot values of a measure of a mapper run for multiple mapper runs, grouping
runs with similar measure values to avoid overplotting.

For example, the sensitivity of multiple mapper runs can be plotted against 
the value of some parameter. If multiple mapper runs have a similar 
sensitivity, the dot on the plot corresponding to this sensitivity (y) and
parameter value (x) is enlargened. This is quite similar to a heat map, but
providing an additional means to distinguish by a third variable, namely
by assigning colors to the dots.

Mandatory arguments: 

TABLE            is the input table file. Tab-separated values.

X                is the name of the column whose values shall be plotted on
                 the x-axis of the plot

Y                is the name of the column whose values shall be plotted on
                 the y-axis of the plot

Options:

--color COLUMN   A column name whose column values shall be used to 
                 color the dots of the plot

--round DIGITS   Round all values of the chosen measure Y to DIGITS digits.
                 This is used to assign similar values of Y to the same group,
                 enlargening the corresponding dot on the graph and therefore 
                 avoiding overplotting.

--signif DIGITS  Round all values of the chosen measure Y to DIGITS 
                 *significant* digits, e.g. rounding 14, 1.4, 0.14 to one
                 significant digit yields 10, 1 and 0.1. Purpose is the same
                 as for the round parameter.
"


main = function(argv){
    args = docopt(doc=help, args=argv)
    checkArgumentSanity(args)

    # In cols, the column names are saved as R symbols, in args they are saved
    # as strings
    #cols <- new.env(parent=emptyenv())
    #for( n in c("--color","X","Y")){
    #    cols[[n]] <- if(is.null(args[[n]])) NULL
    #                 else as.name(args[[n]])
    #}


    t <- read.table(file=args$TABLE, row.names=NULL, header=TRUE)

    attach(args)
    `--round` %<>% as.numeric
    `--signif` %<>% as.numeric
    if(!is.null(round)){
        t[,Y] <- round(t[,Y], `--round`)
    }
    if(!is.null(args$signif)){
        t[,Y] <- signif(t[,Y], `--signif`)
    }
    detach(args)

    # This column name is needed to provide an input for the length
    # function in the subsequent aggregate function
    #firstcol <- as.name(colnames(t)[1])
    firstcol <- colnames(t)[1]
    # Generate formula for aggregate, substituting user-specified 
    # column names

    if(is.null(args$`--color`)){
        color <- "0"
    }else{
        color <- args$`--color`
    }

    f <- sprintf("cbind(.amount=%s) ~ %s + %s + %s",
                    firstcol, args$X, args$Y, color)
    f <- as.formula(f)

    #f <- as.formula(interp( 
    #        "cbind(.amount=FSTCOL ) ~ Y + COLOR + X",
    #        X=cols$X, Y=cols$Y, FSTCOL=firstcol, COLOR=cols$`--color`))

    a <- aggregate( f, FUN=length, data=t )

    # Convert the color column into factors to yield a discrete scale 
    # in ggplot
    if(!is.null(args$`--color`)) a[,args$`--color`] %<>% as.factor

    getYScale <- function(data, ...){
        if(mode(data) == "numeric") return(scale_y_continuous(...))
        else return( scale_y_discrete(...))
    }
    p <- ggplot(a) + 
        aes_string(x=args$X, y=args$Y, size=".amount", color=args$`--color`) +
        (
            if(mode(a[,args$X]) == "numeric") 
                 scale_y_continuous(name=args$Y)
            else scale_y_discrete(name=args$Y)
        )+
        scale_size_continuous("amount")+
        geom_point()

    ggsave(filename=args$PLOT_NAME, plot=p, device=pdf, width=5,height=2.5)
}

checkArgumentSanity = function(args){
    if(sum(!is.null(c(args$round, args$signif)))>1){
        stop("Only one option of --round, --signif can be specified!")
    }
}

main(commandArgs(TRUE))



