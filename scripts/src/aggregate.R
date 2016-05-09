#!/usr/bin/env Rscript

library(stringr)
library(magrittr)

help="Aggregate a table

Usage: aggregate.R [options] COLUMNS FUN [FILE|-]

COLUMNS       By which columns the output should be grouped. Separate columns
              by '+' signs. Avoid whitespace or use \"...\". Example: src+pos
FUN           The function(s) which should be used to summarize the data. 
              
              If multiple summarys shall be performed, separate the functions
              by ';'
--sep SEP     [Default: TAB] Character which separates columns of input
--dec DEC     [Default: .] The used decimal point character
"

ARG_SPEC=
"name   nargs   default
sep     1       NA
dec     1       NA
"

ACCEPTED_FUNCTIONS = list(
    count =    function(col)     length(col)
    sum =      function(col)     sum(as.numeric(col))
    mean =     function(col)     mean(as.numeric(col))
    max =      function(col)     max(as.numeric(col))
    min =      function(col)     min(as.numeric(col))
    n.equals = function(col,val) sum(as.character(col) == val)
    n.true =   function(col)     sum(as.logical(col))
    n.false =  function(col)     sum(!as.logical(col))
)

args = commandArgs(TRUE)
columns=args[1]
funs=args[2]
str_c("out=aggregate( . ~ ",columns,",data=in,fun=function(x))

parse.arguments = function


# Aggregation
# ===========




# Object accessor and creator methods
# =======================

# Creates a new object containing a a=f(x,y) representation
fundesc = function(col,fun,args){
    return(list(col=col,
                fun=fun,
                args=args)
    )
}

column = function(obj){
    return(obj$col)
}
funname = function(obj){
    return(obj$fun)
}
arguments = function(obj){
    return(obj$arg)
}

# Utility functions
# =================

format = function(string,...){
    a = list(...)
    for(n in names(a)){
        string = str_replace_all(string, fixed(str_c("{",n,"}")), a[[n]])
    }
    return(string)
}



# Argument parsing
# ================


# Parses strings of the form col1[+col2+...]
parse.aggregate.arg = function(string){
    spl = str_trim(string) %>% 
          str_split("[:blank:]*\\+[:blank:]*") %>% 
          .[[1]]
    return(spl)
}

# Parses strings of the form [col=]fun([arg1[,...]])
parse.fun.arg = function(string){
    format_error = function() stop(string, "is of wrong format!")

    string %>% str_trim()

    ### SPLIT col=fun(a1,a2)
    ### Variables: a ----> b ----> c --> args
    ###               col     fun
    # Split off col: col | fun(a1,a2)
    a = str_split(string,"=")[[1]] %>% str_trim()
    if(length(a) > 2) format_error()
    # Format 'call(args)'
    if(length(a) == 1){
        col=""
        b = a[1]
    # Format 'col=call(args)'
    }else{
        col = a[1]
        b = a[2]
    } 

    # Split fun | a1,a2 |
    b = str_split(b,"[()]")[[1]] %>% str_trim()
    if(length(b) != 3 || b[3] != "") format_error()

    fun = b[1]

    # Split a1 | a2
    c = str_split(b[2],",")[[1]] %>% str_trim()

    # Format f(a,b,) is illegal, fun() is not
    if(length(c) > 1 && any(c == "")) format_error()

    # return character(0) in case of input [col=]fun()
    args = c[c != ""]

    ### FORMAT CHECKS

    # No whitespace in any part of the command allowed
    if(any(str_detect(c(col,fun,args),"[:blank:]"))) format_error()

    return(fundesc(col=col,fun=fun,args=args))
}

# Parses string X[; Y[;...]] and processes X,Y,... with parse.fun.arg
parse.fun.cmdline = function(cmdline){
    split = cmdline %>% 
            str_split(";") %>% 
            .[[1]] %>% 
            str_trim() %>%
            .[. != ""] %>%
            as.list

    return(lapply(split,parse.fun.arg))
}

###################################################################
# Ad-hoc argument parser. Should be replaced by docopt when docopt
# accepts --arg "a b c" style arguments
###################################################################

usageError = function() stop("Invalid command line, use --help for usage info")
printHelpAndExit = function(){
    cat(help,"\n")
    quit(status=0)
}

parseArgs = function(argv=commandArgs(TRUE),spec=ARG_SPEC,n.mandatory=0){
    # Optional arguments:
    # Set all argument values to default
    argValues=spec$default
    names(argValues) = spec$name
    argValues = parseDefault(argValues)
    # Munge away argv, strarting from first element until the first argument
    # which doesn't start on --... is encountered
    while(str_sub(argv[1],1,2) == "--" && length(argv) != 0){
        # Opt name
        opt = str_sub(argv[1],3)
        if(opt == "help") printHelpAndExit()

        if(!(opt %in% names(argValues))) usageError()
        argv = argv[-1]
        # Number of needed additional values
        nparm = subset(spec,name==opt)[,"nparam"]
        if(nparm > length(argv)) usageError()
        # This is a --flag without additional values
        if(nparm == 0){
            argValues[[opt]] = TRUE
        # This parameter needs additional values
        }else{
            argValues[[opt]] = argv[1:nparm]
            argv = argv[-(1:nparm)]
        }
    }
    # Mandatory arguments:
    if(length(argv) != n.mandatory) usageError()
    mandatory = argv

    return(list(mnd=mandatory,opt=argValues))
}

parseDefault = function(string){
    string = as.list(string)
    for(i in 1:length(string)){
    # If TRUE, FALSE, NA or a number, convert
        if(str_detect(string[[i]],"^(TRUE|FALSE|NA)$") ||
           str_detect(string[[i]],"^([+-]?[0-9]+(\\.[0-9]+)?([eE][0-9]+)?)$")){
           string[[i]] = eval(parse(text=string[[i]]))
        }
    }
    return(string)
}
###############################################################
# End Ad-hoc argument parser
###############################################################

# Script starting point
# =====================

# Don't run if this script is source()d and not executed from the shell
if(!exists("TEST") && !interactive()){
    args = parseArgs(cmda,spec=ARG_SPEC,n.mandatory=2)
    cmda <- commandArgs(TRUE)
    options(error=traceback)
    main(args)
}

# vim: tw=80

