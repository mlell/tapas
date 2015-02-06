#!/usr/bin/Rscript

# Fits a geometric distribution with additional factor to 
# the given values

library(argparse)

usage="
Usage
=====
    fit_geom.R [data={- | filename}] [plot=filename]  ...
"
expArgs="
data      | character | -     | input data, newline separated. -: STDIN
plot      | character | NA    | file for the fitting plot (PDF)
pstart    | numeric   | 0.1   | start value for p
fstart    | numeric   | 1     | start value for f
tstart    | numeric   | 0     | start value for t
plower    | numeric   | 1e-5  | minimum value for p
pupper    | numeric   | 1     | maximum value for p
flower    | numeric   | 0     | minimum value for f
fupper    | numeric   | Inf   | maximum value for f
tlower    | numeric   | 0     | minimum value for t
tupper    | numeric   | Inf   | maximum value for t
overwrite | logical   | FALSE | whether to overwrite files
print     | logical   | FALSE | whether to print the course of optimization
title     | character | NA    | title to print on the plot, NA -> no title
no-legend | logical   | FALSE | whether to hide the legend
no-params | logical   | FALSE | whether to hide the numerical parameter values on the plot
ofmt      | character | NA    | String specifying a desired output format. See help for info
"

help="
Purpose
=======

Determines parameters to fit a geometric distribution \"with factor\"
to the given values. The parameters and some statistics are printed
and a plot showing the accuracy of the fit can be created.

The values are fitted to the following formula:
    
    y(x) = f * dgeom(x, p)

where 
geom(x, p) is the geometric distribution density function, 
x is its parameter \"number of trials\",
p is its parameter \"probability of success\" and
f is a floating point number.

The fitting algorithm needs starting values of the two parameters 
f and p. The values of the parameters pstart= and fstart= are used
for this purpose.

To fit the function, the root mean square deviation of the data to
the function is minimized.

If a filename for plot= is given, a plot in PDF format is saved
which shows the data in comparison to the 

Input
=====

All parameters are expected to be of the form name=value (no
no whitespace around = )

Data input
----------

The values must be provided in the form 

    n_1 n_2 ... n_n
    n_(n+1) ...
    ...

That is, values separated by spaces or newlines. 
(without the leading whitespace)

The read data is expected to be the y-values for x=1,2,3,..., in this
order. Values for x are not expected to be mentioned explicitly in
the input.

"

# === Main function ======================================

main = function(){
    cmda=commandArgs(trailing=TRUE)
    if(length(cmda) > 0){
       if(cmda[1]=="-h"){
           printHelp(long=FALSE)
           q("no")
       }else if(cmda[1] == "--manual"){
           printHelp(long=TRUE)
           q("no")
       }
    }
    a = parseArguments(expArgs)

    # Read data from STDIN or file
    #data=readData(ifelse(a$data=="-", stdin(), a$data))
    data=readData.raw(a$data)

    if( length(data) < 2 ) stop("Can't fit: Not enough data received!")

    o = optim(par=c(prob=a$pstart,fac=a$fstart,t=a$tstart)
            , lower=c(a$plower,a$flower,a$tlower)
            , upper=c(a$pupper,a$fupper,a$tupper)
            , method="L-BFGS-B"
            , fn=squared.err.geomDist
            , data=data,
            , print=a$print)

    printFitInfo(data=data,          fac=o$par["fac"]
               , prob=o$par["prob"], t=o$par["t"]
               , format=a$ofmt)

    if(!is.na(a$plot)){
        saveFittingPlot(file=a$plot,      data=data
                      , fac=o$par["fac"], prob=o$par["prob"]
                      , t=o$par["t"]
                      , overwrite=a$overwrite
                      , title=a$title,
                      , plot.params=! a$`no-params`
                      , legend=! a$`no-legend`)
    }

}

# === Auxilliary Functions ===========================

# Read in space and/or newline-separated data
# file: connection object to read data from
readData.raw = function(file){
    stopifnot(!is.null(file))
    out=NULL
    if(file != "-" ){ # Input is a file
        if(!file.exists(file)){ # Don't overwrite
            stop("File ",file," does not exist!")
        }
        out=scan(file=file
                  , what=double()
                  , comment.char="#"
                  , quiet=TRUE)
    }else{ # Input is TTY (STDIN)
        f=file("stdin")
        t= scan(text=readLines(f)
             , what=double()
             , comment.char="#"
             , quiet=TRUE)
        close(f)
        out=t
    }
    return(out)
}


# Function to be fitted to:
#     fac * dgeom(x, prob) + t
# x     = number of failures before first success
# prob  = success probability
# fac   = scaling factor
# dgeom = geometric distr. density function
# t     = constant to be added (baseline)
fgeom = function(x,fac,prob,t){
    ifelse(x < 1, NaN,
    fac * dgeom(x=x-1,prob=prob)) + t
}

# Calulate the root mean squared sum of differences
# between the data (dat.x, dat.y) and the values
# of f(dat.x). Further arguments are forwarded to f.
squared.abs.error = function(dat.x, dat.y , f, ...){
    sqrt( sum( ( f(dat.x,...) - dat.y )^2 ))
}

# Calculate the root mean squared sum of absolute deviation
# between the and the values of fgeom (defined above)
# data is assumed to be a one-dimensional vector holding
# the y-values for x=1,2,3,...
# par is assumed to be a named vector holding the parameters
# for fgeom: prob and fac.
# all x for which data[x] == 0 are neglected.
squared.err.geomDist = function(data,par,print=FALSE){
    prob=par["prob"]
    fac=par["fac"]
    t=par["t"]
    x=seq_along(data)
# Uncomment when using relative deviation
# Prune data points for data[x] == 0
 #   prune.i = which(data==0)
 #  print(prune.i)
 #  if(length(prune.i)>0){
 #      data = data[-prune.i]
 #      x = x[-prune.i]
 #  }
    e=squared.abs.error(dat.x=x,   dat.y=data, f=fgeom
                      , prob=prob, fac=fac,    t=t)
    # When optimization progress should be printed
    if(print){
        printf=function(...){cat(sprintf(...))}
        printf("f=%.5g; p=%.5g; t=%.5g -> e_RMS=%.3g\n",fac,prob,t,e)
    }
    return(e)
}

# Save a plot superposing the input data with the fitted function,
# and the distance between the two. Saved in PDF format
saveFittingPlot = function(file, data, fac, prob, t
                         , width=5, height=3, overwrite=FALSE
                         , title=NA, plot.params=TRUE
                         , legend=TRUE){
    if( (!overwrite) && file.exists(file))
        stop("File ",file," exists and won't be overwritten!")
    p=sprintf # Function name alias
    x=1:length(data)
    d=data.frame(
         data=data
       , geomY=fgeom(x=x, fac=fac, prob=prob, t=t))
    d$err= abs(d$data - d$geomY )
    
    pdf(file,width=width,height=height)
    par(mfcol=c(2,1))

    topmar=ifelse(is.na(title),0,2)
    par(mar=c(.5,4,0,0),oma=c(2,0,topmar,0),las=1)
    matplot (x=x, y=d,type="l", lty=1,axes=FALSE
           , col=c("black","blue","red"),ylab=NA,xlab=NA)
    box()
    axis(2)
    intAxis = function(){
        axis(1, at=prettyInt(range=par()$usr[1:2],nticks=25),
             labels=FALSE,tck=-.03)
    }
    intAxis()
    axis(1,labels=FALSE)

    xlim=par("usr")[1:2]
    if(plot.params){
        mtext(side=3,line=-1, at=mean(xlim),adj=0.5,text="f*dgeom(x,p)+t")
        mtext(side=3,line=-1, at=xlim[2],adj=1,text=p("f = %.3g",fac))
        mtext(side=3,line=-2, at=xlim[2],adj=1,text=p("p = %.3g",prob))
        mtext(side=3,line=-3, at=xlim[2],adj=1,text=p("t = %.3g",t))
        mtext(side=3,line=-4, at=xlim[2],adj=1,
        text=p("max. err. = %.2g",max(d$err)))
    }

    matplot (x=x, y=d,type="b",pch=1, lty=1, cex=.5
           , col=c("black","blue","red")
           , log="y",ylab=NA,xlab=NA)

    intAxis()
    mtext(side=1,adj=0,text=" log",line=-1)
    mtext(side=1,adj=1,line=0,at=xlim[2],text="x")
    if(legend){
        legend("topright",lty=1,col=c("black","blue","red")
             , legend=c("data","fit","err"), bty="n")
    }
    if(!is.na(title)){
        mtext(text=title, side=3, line=1, adj=0,outer=TRUE,cex=1.2)
    }
    dev.off()
    invisible(NULL)
}

# Like R function pretty, but never use steps<1
prettyInt = function(range, nticks,...){
    pretty(range, max(max(range)-min(range), nticks),...)
}

printFitInfo = function(data, fac, prob,t
                      , format=NA){
    x=1:length(data)
    geomY=fgeom(x=x, fac=fac, prob=prob,t=t)
    err=abs(data - geomY )

    max.err = max(err)
    i.max.e = which(err == max.err) # possibly multiple results
    p.max.e = max(max.err/data[i.max.e]*100)

    e.rms=sqrt(mean(err^2))
    #p.e.rms=sqrt(mean((err/data)^2))*100 # RMS percentage?

    o=function(...){cat(...);cat("\n")}
    #o(sprintf("factor: %.8g",fac))
    #o(sprintf("geometric_parameter: %.8g",prob))
    #o(sprintf("y_intercept: %.8g",t))
    #o(sprintf("max.err.: %.4g (%.1f%%)",max(err), p.max.e))
    # No percentage as of now, b/c i don't know whether that
    # would have any statistically justified meaning
    #o(sprintf("RMS.err.: %.5g ",max(e.rms)))
    if(is.na(format)){
        o("#fac   geom.p   t       err.max   err.max.%   err.rms")
        o(sprintf(
          "%.8g %.8g %.8g %.4g %.1f %.5g"
          , fac,prob,t,max(err),p.max.e,max(e.rms)))
    }else{
        fmtout=lapply(   list(factor=fac,          f=fac
                            , geomprob=prob,       p=prob
                            , intercept=t,         t=t
                            , max.err=max.err,     me=max.err
                            , p.max.err=p.max.e,   pme=p.max.e
                            , rms.max.err=max(e.rms)
                            , erms=       max(e.rms))
                      , formatC ,digits=8, width=1, format="g")
        o(formatOutput(format.string=format, values=fmtout))
    }
}

# formatOutput("{valA}Text {valB}", list(valA=1,valB="C"))
#    --> 1Text C
formatOutput = function(format.string,values){
    v.names=names(values)
    for(n in v.names){
        format.string=gsub(pattern=paste0("\\{",n,"}"), repl=values[n],
                           x=format.string)
    }
    return(format.string)
}



# Print long or short help and exit.
printHelp = function(long=FALSE){
    catnl=function(...){cat(...);cat("\n")}
    if(!long){
        catnl(usage)
        catnl("Fit a geometric distribution with forefactor to ",
              "given data.")
        catnl("use --manual for complete help.")
    }else{
        catnl(usage)
        catnl(help)
        catnl("Parameters")
        catnl("==========")
        catnl()
        catnl(expArgs)
    }
}

main()




# vim: tw=70
