#!/usr/bin/env Rscript


help="
Plot how many reads from which origin have mapped to which origin.

Usage: plot-read-fate.R [options] ORIGIN MAPPED_TO CORRECT_MAP COUNT PLOT_FILE [INFILE|-]

INFILE            Input file; If missing or - read from standard input.
                  This file must contain column headers and be tab-separated.
                  
                  Example INFILE (header names are specified in other parameters)

                  ─────────────────────────────────── 
                  true_orig  map_orig  correct  count
                  fcatus     fcatus    TRUE     112
                  fcatus     fcatus    FALSE    19
                  fcatus     clupus    FALSE    100
                  fcatus     *         FALSE    44
                  clupus     fcatus    FALSE    20
                  clupus     *         FALSE    88
                  ─────────────────────────────────── 


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

COL_OKMATCH = "#d4fa2c"
COL_MISMATCH = "#ff592d"

main = function(argv){
    args = parse.args(argv)
    inputfile = args$INFILE
    origincol = args$ORIGIN
    mappedcol = args$MAPPED_TO
    corrmapcol= args$CORRECT_MAP
    countcol  = args$COUNT
    qcol      = args$HQ_COL
    plotfile  = args$PLOT_FILE
    format    = tolower(args$FORMAT)

    tab = read.table(file=ifelse(inputfile=="-",stdin(),inputfile),
                     sep = "\t", dec=".", header = TRUE, row.names = NULL)

    # All columns which are not NA
    cols = c(origincol,mappedcol,corrmapcol,countcol,qcol) 
    cols = cols[!is.na(cols)] 

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
    createPlot(tab)
    dev.off()

    return(invisible(NULL))
}

createPlot = function(stat, relative=TRUE){

    # Count of references which reads can be mapped to (actual mappings)
    # --> plot columns
    # Includes * = not mapped
    rnames = unique(stat$rname)
    n.rname = length(rnames)
    trnames = unique(stat$trname)
    n.trname=length(trnames)

    n.reads = sum(stat$count)

    # Fraction of reads per true origin 
    stat$frac = stat$count / sum(stat$count)

    # Subdivide plotting region
    # - subplots with organism annotation
    n.plotrows = n.trname + 1 # plus annotation
    n.plotcols = n.rname + 2 # plus total read bar and annotation

    mat = matrix(1:(n.plotrows*n.plotcols),ncol=n.plotcols,byrow=F)
    #     org ann.  total read bar  main plot region
    w = c(lcm(2),  lcm(0.4),       rep(1,n.rname)    )

    #     target ann.  main plot region
    h = c(lcm(1),      rep(1,n.trname)  )

    # -legend area
    m = max(mat)
    mat = cbind(mat, 0) # free area
    mat = cbind(mat, m+1) # legend
    #        free area  legend
    w = c(w, lcm(0.5),  lcm(2.2))

    layout( mat , widths = w , heights = h) 

    
    # Plot.
    for( plotcol in 1:n.plotcols ){  
        for( plotrow in 1:n.plotrows ){
            c.trname = trnames[plotrow-1]
            c.rname = rnames[plotcol-2]

            # Number of reads that will be plotted in this row
            n.this.true.src = sum(subset(stat, trname == c.trname)$count)
            n.this.map.src = sum(subset(stat, rname == c.rname)$count)

            
            # Top left cell: Draw legend for column and row annotations
            if( plotcol == 1 && plotrow == 1){
                par(mar=c(0.2,0.2,0.2,0.2))
                plot.new() 
                lines(c(1,0),c(0,1))
                xpd = par("xpd")
                par(xpd=NA)
                text(0.1,0.1,"origin",adj=0)
                text(0.7,0.6,"target",adj=0)
                par(xpd=xpd)

            }else if( plotcol <= 2  && plotrow <= 1){
                # Empty plot
                plot.new() 

            # Draw column annotations: map target organisms
            }else if( plotrow == 1){
                par(mar=c(0.2,0.2,0.2,0.2))
                plot.new() 
                # Print true organism names
                par(usr=c(0,1,0,1))
                if(c.rname == "*"){
                    text( 0.5,0.2, labels="(not mapped)")
                }else{
                    text( 0.5,0.2, labels=c.rname)
                }

            # Draw row annotations: read origin organisms
            }else if( plotcol == 1){
                par(mar=c(0.2,0.2,0.2,0.2))
                plot.new() 
                # Print mapping target names
                par(usr=c(0,1,0,1))
                text(1,0.6,labels=c.trname, adj=1)
                text(1,0.4,adj=1,labels=
                     sprintf("(%d reads)",n.this.true.src),cex=0.7)

            # Draw a column of black bars which indicate which fraction the 
            # reads of the respective row take of all reads
            }else if( plotcol == 2){
                par(mar=c(0.2,0.2,0.2,0.4))
                plot.new() 
                # Plot bars with total read amounts per organism 
                fract = n.this.true.src / n.reads
                par(usr=c(0,1,0,1))
                draw.bg("#EFEFEF")
                rect(xleft=0,ybottom=0,xright=1,ytop=fract,col="black")
                text(0,0,labels=sprintf("%d",n.this.true.src))

            # Draw bars denoting fractions of reads mapped from specific origin
            # to specifict target
            }else{
                par(mar=c(0.2,0,0.2,0))
                plot.new() 
                # Plot read fractions mapped/unmapped/mismapped
                draw.bg("#EFEFEF")
                d = subset(stat, trname == c.trname & rname == c.rname)
                # Relative count compared to all reads of this true origin (in
                # current iteration)
                d$count = d$count / n.this.true.src

                plot.percentage.axis(plotcol-2 == n.rname)
                draw.mapping(d)
            }
        }
    }

    
    # Plot the legend
    plot.new()
    par(usr=c(1,0,1,0))
    legend("topleft",
           fill=c(COL_OKMATCH,COL_MISMATCH,"black","black"),
           density=c(NA,NA,NA,40),
           legend=c("correct","mismatch","fract. total","low qual."),
           bty="n")


}

# Draw an axis showing ticks at 0, 15, 50, 75 and 100%
# Draw white grid lines at same positions
# printLabels: logical scalar
plot.percentage.axis = function(printLabels){
    # Ticks outside of plot
    if(printLabels){
        par(mgp=c(2,0.3,0))
        axis(4,at=seq(0,1,0.25), col=NA,col.ticks="#efefef",
             tck=-0.05, labels=seq(0,100,25), 
             cex.axis=0.6,las=1)
        par(mgp=c(2,1.2,0))
        axis(4,at=0.5, col=NA, labels="%", cex.axis=0.6,las=1)
    }

    # Grid lines
    axis(4,at=seq(0,1,0.25), col=NA,col.ticks="white",
         labels=NA,tck=1,lwd=0.5)

}

# Fill plot background
draw.bg = function(color){
    u = par()$usr
    rect(u[1], u[3], u[2], u[4], col=color, border=NA)
}

# Draw a stacked bar, representing fractions of reads of a certain
# origin organism which are mapped correctly or incorrectly to a certain target
# organism
# d: data.frame with columns 'correct.match' (logical), 'high.quality'(logical),
#    'count' (fraction (float) between 0 and 1)'
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

    if(ok.match.hq > 0){
    rect( xleft=XL, xright=XR, ybottom=y.cum.1, ytop=y.cum.2, col=COL_OKMATCH)
    }

    if(ok.match.lq > 0){
    rect( xleft=XL, xright=XR, ybottom=y.cum.2, ytop=y.cum.3, col=COL_OKMATCH)
    rect( xleft=XL, xright=XR, ybottom=y.cum.2, ytop=y.cum.3, density=10)
    }

    if(mismatch.lq > 0){
    rect( xleft=XL, xright=XR, ybottom=y.cum.3, ytop=y.cum.4, col=COL_MISMATCH)
    rect( xleft=XL, xright=XR, ybottom=y.cum.3, ytop=y.cum.4, density=10)
    }

    if(mismatch.hq > 0){
    rect( xleft=XL, xright=XR, ybottom=y.cum.4, ytop=y.cum.5, col=COL_MISMATCH)
    }
    
}

# Open a graphics device of the specified file format
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
    while(length(argv) > 0 && substr(argv[1],1,2) == "--" ){
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


