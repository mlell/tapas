#!/usr/bin/env Rscript

library(stringr)
library(magrittr)

help="
Plot how many reads from which origin have mapped to which origin.

Usage: plot-read-fate.R [options] ORIGIN MAPPED_TO CORRECT_MAP COUNT PLOT_FILE [INFILE|-]

INFILE            Input file; If missing or - read from standard input.
                  This file must contain column headers and be tab-separated.

ORIGIN            This specifies the column which states the reads' true origin. 

MAPPED_TO         This specifies the column which states to where the reads have been mapped.

CORRECT_MAP       The name of a column containing TRUE/FALSE indicating if the reads were
                  mapped to the correct position.

COUNT             The name of the column specifying how many reads a category, defined
                  by the aforementioned column, contains.

PLOT_FILE         The filename of the plot to be generated.

--quality HQ_COL  Plot the amount of reads which map with low quality. A column must be
                  specified containing TRUE (reads which map with high quality) or 
                  FALSE (reads which map with low quality).

--format F        Image format of the plot. Allowed: pdf or png. [Default: pdf]
"

options(stringsAsFactors=FALSE)

main = function(argv){
    args = parse.args(argv)
    inputfile = args$INFILE
    origincol = args$ORIGIN
    mappedcol = args$MAPPED_TO
    corrmapcol= args$CORRECT_MAP
    countcol  = args$COUNT
    qcol      = args$HQ_COL
    plotfile  = args$PLOT_FILE
    format    = str_to_lower(args$FORMAT)

    tab = read.table(file=ifelse(inputfile=="-",stdin(),inputfile),
                     sep = "\t", dec=".", header = TRUE, row.names = NULL)

    # All columns which are not NA
    cols = c(origincol,mappedcol,corrmapcol,countcol,qcol) %>% { .[!is.na(.)] }
    invalid_cols = cols[!cols %in% colnames(tab)]
    if(length(invalid_cols) > 0){
        stop("The column(s) ",invalid_cols," are non-existant!")
    }



    # Check for correct format of columns
    if(mode(tab[,countcol]) != "numeric"){
        stop("The specified count column contains non-numeric data")
    }
    if(mode(tab[,corrmapcol]) != "logical"){
        stop("The column CORRECT_MAP contains non-boolean (TRUE/FALSE) data!")
    }
    if(!is.na(qcol) && (mode(tab[,qcol]) != "logical")){
        stop("The column HQ_COL contains non-boolean (TRUE/FALSE) data!")
    }

    cols =  c(origincol, mappedcol, corrmapcol,      countcol)
    names = c("trname",  "rname",   "correct.match", "count")
    if(!is.na(qcol)) {
        cols =  c(cols,  qcol)
        names = c(names, "high.quality")
    }

    tab = tab[,cols]
    colnames(tab) = names

    open.graphics.device(plotfile, format)
    # locally-defined plot function
    plot(tab)
    dev.off()

    return(invisible(NULL))
}

plot = function(stat){

    # Count of references which reads can be mapped to (actual mappings)
    # --> plot columns
    # Includes * = not mapped
    rnames = unique(stat$rname)
    n.rname = length(rnames)
    trnames = unique(stat$trname)
    n.trname=length(trnames)

    # Fraction of reads per true origin (. is replaced by LHS of %>%)
    stat$frac = stat$count %>% {./sum(.)}

    # Subdivide plotting region
    mat = matrix(1:(n.trname*n.rname),ncol=n.rname,byrow=T)
    w = rep(1,n.rname)
    #h = stat$frac
    h = rep(1,n.trname)
    layout( mat , widths=w , heights = h) 

    par(oma=c(0,6,3,0))
    # Plot
    for( row in 1:n.trname ){  # Plot rows
        c.trname = trnames[row]
        # Number of reads that will be plotted in this column
        n.this.true.src = sum(subset(stat, trname == c.trname)$count)

        for( col in 1:n.rname ){ # Plot columns
            c.rname = rnames[col]
            par(mar=c(0.2,0.2,0.2,0.2))
            plot.new()
            box()
            # Data relevant to this iteration
            d = subset(stat, trname == c.trname & rname == c.rname)
            # Relative count compared to all reads of this true origin (in
            # current iteration)
            d$count %<>% divide_by(n.this.true.src)

            draw.mapping(d)
        }
    }
    par(new=TRUE)
    # Remove `layout()` subdivision
    par(fig=c(0,1,0,1))
    par(plt=c(0,1,0,1))
    # Reversed y axis
    par(usr=c(0,n.rname,n.trname,0))
    par(las=1)
    axis(side=2,line=0,at=(1:n.trname)-0.5, label=trnames,tick=FALSE)
    axis(side=3,line=0,at=(1:n.rname)-0.5,label=rnames, tick=FALSE)
}

draw.mapping = function(d){
    # If no quality column is specified --> all high quality
    if(is.null(d$high.quality)) d$high.quality = rep(TRUE, nrow(d))

    XL = 0
    XR = 1
    ok.match.hq = subset(d,  correct.match  &  high.quality)$count
    ok.match.lq = subset(d,  correct.match  & !high.quality)$count
    mismatch.lq = subset(d, !correct.match  & !high.quality)$count
    mismatch.hq = subset(d, !correct.match  &  high.quality)$count
    if(length(ok.match.hq) == 0) ok.match.hq = 0
    if(length(ok.match.lq) == 0) ok.match.lq = 0
    if(length(mismatch.hq) == 0) mismatch.hq = 0
    if(length(mismatch.lq) == 0) mismatch.lq = 0

    y.cum.1 = 0
    y.cum.2 = y.cum.1 + ok.match.hq
    y.cum.3 = y.cum.2 + ok.match.lq
    y.cum.4 = y.cum.3 + mismatch.lq
    y.cum.5 = y.cum.4 + mismatch.hq

    col.ok  = "#d4fa2c"
    col.mis = "#ff592d"

    if(ok.match.hq > 0){
    rect( xleft=XL, xright=XR, ybottom=y.cum.1, ytop=y.cum.2, col=col.ok)
    }

    if(ok.match.lq > 0){
    rect( xleft=XL, xright=XR, ybottom=y.cum.2, ytop=y.cum.3, col=col.ok)
    rect( xleft=XL, xright=XR, ybottom=y.cum.2, ytop=y.cum.3, density=10)
    }

    if(mismatch.lq > 0){
    rect( xleft=XL, xright=XR, ybottom=y.cum.3, ytop=y.cum.4, col=col.mis)
    rect( xleft=XL, xright=XR, ybottom=y.cum.3, ytop=y.cum.4, density=10)
    }

    if(mismatch.hq > 0){
    rect( xleft=XL, xright=XR, ybottom=y.cum.4, ytop=y.cum.5, col=col.mis)
    }
    
}

open.graphics.device = function(file, format){
    w = 4
    h = 3
    dpi=75
    if(tolower(format) == "pdf"){
        pdf(file,width=w,height=h)
    }else if(tolower(format) == "png"){
        png(file, width=w*dpi, height=h*dpi)
    }else{
        stop("Unsupported plot format:", format)
    }
}


parse.args = function(argv){
    a = list()
    a$FILE = "-"
    a$ORIGIN = NA
    a$MAPPED_TO = NA
    a$HQ_COL = NA
    a$FORMAT = "pdf"
    while(length(argv) > 0 && str_sub(argv[1],1,2) == "--" ){
        x = argv[1]
        argv = argv[-1]
        if( x == "--help"){
            cat(help)
            quit(status=0)
        }else if( x == "--quality"){
            a$HQ_COL = argv[1]
            argv = argv[-1]
        }else if( x == "--format" ){
            a$FORMAT = argv[1]
            argv = argv[-1]
        }else{
            stop("Unknown option ",x,", use --help for info")
        }
    }
    if(!(length(argv) %in% c(5,6))) stop("Wrong command line format; use --help for info")
    a$ORIGIN = argv[1]
    a$MAPPED_TO=argv[2]
    a$CORRECT_MAP=argv[3]
    a$COUNT = argv[4]
    a$PLOT_FILE = argv[5]
    if(length(argv) == 6){
        a$INFILE=argv[6]
    }
    return(a)
}


main(commandArgs(TRUE))


