#!/usr/bin/env Rscript

# Default function to read input data
readInput_default = function(f){
    read.table(file=ifelse(f=="-","stdin",f),
        header=TRUE,stringsAsFactors=FALSE,sep=sep,
        comment.char="", row.names=NULL,dec=dec)
}

readInput_fread = function(f){
    # Unfortunately prints progress to stdout, therefore showProgress=FALSE
    fread(input = ifelse(f == "-", "cat /dev/stdin", f),
          header=TRUE, sep=sep, dec=dec, showProgress=FALSE)

}


args = commandArgs(TRUE)

# Parse arguments:
# Default options
sep = "\t"
na = "NA"
dec = "."
packages = character()
readInput = readInput_default

while(length(args) > 0 && substr(args[1],1,2) == "--"){
    opt = args[1]
    args = args[-1]
    if( opt == "--help" ){
        cat(
"Usage: pocketR.R [options] R-CODE [INPUT_FILE ...]

Read in tab separated values and save them as data.frame called `input`.
If multiple INPUT_FILEs are specified, a list of data.frames called
`inputs` is provided. The result of the computation (the value of the
last expression) is printed out as a text table.

Options:
--sep     Output separator. Default: TAB
--na      String to print if data is missing (NA). Default: NA
--dec     Character to use as decimal separator. Default: \".\"
--fread
          Use the fread function from the data.table package to read in
          the input data. This is faster but yields a data.table (and
          not a data.frame). Implies '--pkg data.table'. You can 
          specify a command instead of a file name. Then the output 
          of that command will be used. E.g. 'zcat table.tab'.  ")

        quit(status=0)
    }else if(opt == "--sep"){
        sep = args[1]
        args = args[-1]
    }else if(opt == "--dec"){
        dec = args[1]
        args = args[-1]
    }else if(opt == "--na"){
        na = args[1]
        args = args[-1]
    }else if(opt == "--pkg"){
        packages = union(packages, args[1])
        args = args[-1]
    }else if(opt == "--fread"){
        packages = union(packages, "data.table")
        readInput = readInput_fread      
    }else{
        stop("Unknown option ",opt," or incorrect number of parameters to preceeding option")
    }
}
if(length(args) < 1) stop("Incorrect command line! Use --help for info")

# String with R commands
cmd = args[1]

# Filenames of input files
files = args[-1]

# Load required packages
for(pkg in packages){
    suppressPackageStartupMessages(
        library(pkg, character.only=TRUE))
}

# Define main function signature. 
# If more than one input is provided, force user to use
# the input variable "inputs" (list of input data)
# If one input is provided, the variable "input" may be
# used, avoiding the repeated use of inputs[[1]]
if(length(files) > 1){
    fun_head = "function(inputs)"
}else{
    fun_head = "function(inputs,input=inputs[[1]])"
}

# Construct main function from user input
fun = eval(parse(text=paste0( fun_head,"{", cmd, "}" )))

# Read from standard input
if(length(files) == 0) files[1] = "-"

# Read input tables
inputs = lapply(files, readInput)

# Execute user-defined commands
output = fun(inputs)

printOutput <- function(output,file=stdout(),sep=sep,
                        dec=".",row.names=FALSE,quote=FALSE, ...){
    write.table(output,file=file,sep=sep,dec=dec,
                row.names=row.names,quote=quote, ...)
}

# Print result table
printOutput(output,file=stdout(),sep=sep,dec=".",
            row.names=FALSE,quote=FALSE, na=na)




