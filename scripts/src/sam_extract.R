#!/usr/bin/env Rscript

#library(methods) # docopt
#library(docopt) # Buggy: splits "..." enclosed arguments
library(magrittr) # %>% and %<>% pipe operators
library(stringr)
#library(dplyr)

# Create data.frames with string columns, not factor columns
options(stringsAsFactors = FALSE)

help="
Usage: mapping-stat.R [options] SAM-FILE

This script needs the UNIX `cut` utility and the `gunzip` utility, if gzip'ed
files should be read.

Generate a table, where each row corresponds to one read line in the input SAM
file, which contains several columns filled with informations from read names 
and mapping, which is saved in the SAM file.

Options
=======

Mandatory
---------

SAM-FILE               Mapping which shall be evaluated. 


Input interpretation
--------------------

--pattern PATTERN      [Default: {src}_{start}] Specify which data
                       is coded in the read name. {Braced} names are matched
                       as regex [A-Za-z0-9]+. See below for which fields are
                       mandatory. 

--regex                The value of --pattern is specified using standard regex 
                       syntax. No interpretation of {...} patterns is performed.
                       Named capture groups must be specified in the regex whose
                       names are used as field names (see below).
                       Example: (?<src>[A-Z]+)_(?<start>[0-9]+)

--collate CPATTERN     Specify that a output column should be generated
                       using multiple placeholders, as used in --pattern. 

                       Example:
                       --pattern {org}_{chr}_{start} --collate src={org}-{chr}

                       This generates four columns, `org`, `chr`, `start`, 
                       containing the information extracted from the respective
                       parts of the read name, and `src`, containing the values
                       of `org` and `chr`, concatenated by a dash.

                       Multiple tags can be specified this way, by separating
                       multiple CPATTERNs by commmas (avoid spaces!): 
                       a={a}_{b},b={c}-{d}

--sam-fields FIELDS    Prints the specified fields from the SAM file.
                       FIELDS is a comma-separated list of names as 
                       specified in the SAM specification, Section 1.4.

--gz                   The input SAM file is gzip'ed

## Miscellaneous

--test                 Run unit tests.

The pattern string is converted to a regular expression
=======================================================

{...} are converted to named capture groups (?<name>REGEX) (see --pattern for 
details). For each named capture group, one column is printed containing the
value of the respective groups.

Therefore, regular expressions in the pattern are valid. Use --regex
to disable {...} field conversion altogether and use a regex-only pattern.
Then, you need to define a named capture group for each column you want to be
generated out of the read names.

"

# Unfortunately, docopt doesn't support arguments with spaced parameter, like
# --opt "a b c" by now (Sep-2015). Therefore, a custom argument parser has to be
# used, which is implemented at the end of the script
ARG_SPEC = read.table(header=TRUE, row.names=NULL,na.strings="",text=
"name       nparam  default
pattern     1       NA
sam-fields  1       NA
regex       0       FALSE
collate     1       NA
gz          0       FALSE
test        0       FALSE
")

# These names are from the SAM specification
SAM.COLS = c("qname","flag","rname","pos","mapq",
             "cigar","rnext","pnext","tlen","seq","qual")

main = function(args){
    # Parse command line arguments:
    # Bug in docopt
    #args = docopt(help)

    # Which fields from the SAM file shall be printed as-is?
    sam.fields = args$opt$`sam-fields`
    # Pattern how to extract true origin and mapping of a read out of its name
    pattern= args$opt$pattern
    is.regex = args$opt$regex

    # Optional read source collating
    collate = args$opt$collate

    # Whether to read a gzip'ed SAM file
    gz = args$opt$gz

    # Parse {...} strings
    if(!is.regex){
        pattern = parse.pattern.to.regex(pattern)
    }

    # Convert the input sam file to a data.frame, sequence and quality strings
    # are not needed.
    # The column names of the resulting data.frame match those in the official
    # SAM file specification
    sam = readSAM(args$mnd[1], gz)

    # This will be the output data.frame. 
    readInfo = data.frame(row.names=1:nrow(sam))

    if(!is.na(pattern)){
        new.cols = parse.read.name(sam$qname, pattern)
        readInfo = append.disjoint.df(readInfo,new.cols)
    }

    # Parse --sam-fields
    if(!is.na(sam.fields)){
        # Convert argument string to character vector
        printedSAMFields = parse.sam.fields.arg(sam.fields)
        # Add specified SAM fields to output
        new.cols = data.frame(sam[,printedSAMFields])
        colnames(new.cols) = printedSAMFields
        readInfo = append.disjoint.df(readInfo,new.cols)
    }

    # If additional information is supposed to be generated from multiple 
    # placeholders (--collate), do it now.
    if(!is.na(collate)){
        collate_args = parse.spaced.arg(collate)
        for(newReadInfoName in names(collate_args)){
            newReadInfoFmt  = collate_args[newReadInfoName]
            newReadInfoData = data.frame(gen.column(readInfo,newReadInfoFmt))
            colnames(newReadInfoData) = newReadInfoName

            readInfo = append.disjoint.df(readInfo,newReadInfoData)
        }
    }

    # Print table
    write.table(readInfo,file=stdout(), sep="\t", quote=FALSE, row.names=FALSE)

    return(invisible(NULL)) 
}

# Append colums of the specified data frames and throw an error
# if column names would be duplicated, an error is thrown. 
append.disjoint.df = function(df1, df2){
    cnames.or.names = function(df){
        n = colnames(df)
        if(is.null(n)){
               n = names(df)
        }
        return(n)
    }
    names.df1 = cnames.or.names(df1)
    names.df2 = cnames.or.names(df2)
    if(any(names.df2 %in% names.df1)){
        n = names.df2[names.df2 %in% names.df1]
        stop("Error: the field name(s) ",n," have been specified more than once!")
    }
    return(data.frame(df1,df2))
}

parse.sam.fields.arg = function(arg){
    printedSAMFields = str_split(arg,",")[[1]] %>%
        str_trim()
    
    # Error if non-existant field names are specified by the user
    illegalSAMFields = printedSAMFields[!(printedSAMFields %in% SAM.COLS)]
    if(length(illegalSAMFields)>0){
        stop("The specified field(s) ",illegalSAMFields," are not valid according",
             " to the SAM specification!")
    }

    return(printedSAMFields)
}

test_rows.are.equal = function(){
    df=function(text) read.table(text=text,header=TRUE,row.names=NULL)
    d = df(
    "a  b
     1  2
     2  2")
    f = df(
    "a  b
     1  2
     2  x")
    a = rows.are.equal(d,f)
    b = c(TRUE,FALSE)
    return(identical(a,b))
}

# Returns a vector of logical indicating rowwise identity of df1 and df2
rows.are.equal = function(df1, df2){
    eq = NULL
    for(col in 1:ncol(df1)){
        eq = cbind(eq,df1[,col] == df2[,col])
    }
    out = apply(eq,1,all)
    return(out)
}

# t: Table generated from SAM file (function readSAM)
stat = function(t, qthres){
    # check actual mapping positions for identity to true location
    t$correct.match = ( t$pos  == t$tstart ) & 
                      ( t$trname == t$rname  )
    t$high.quality = t$mapq >= qthres

    true_genomes = unique(t$trname)
    map_genomes  = unique(t$rname)

    # Add "*" for "read not mapped" as used in SAM specification
    map_genomes = union(map_genomes,"*")

    # Count of genes will be in column named 'qname'
    a = aggregate( qname ~ trname + rname + correct.match + high.quality
                 , data=t, FUN=length)
    # Rename column qname to count
    names(a)[names(a) == "qname"] = "count"

    # All possible read (non-)mappings to all references
    x = expand.grid(trname=true_genomes,rname=map_genomes,
                    correct.match=c(TRUE,FALSE),high.quality=c(TRUE,FALSE))

    m = merge(x=a, y=x, all.y=TRUE)

    # Replace all NAs with 0
    m$count[is.na(m$count)] = 0

    return(m)
}


readSAM = function(f,gz=FALSE){
    if(!gz){
        cut_call=sprintf("cut -f1-%d %s",length(SAM.COLS),f)
    }else{
        cut_call=sprintf("gunzip -c %s | cut -f1-%d",f,length(SAM.COLS))
    }
    t = read.table(pipe(cut_call),comment.char="@",sep="\t", fill=TRUE, 
                   stringsAsFactors=FALSE)
    # Split off optional tags
    t = t[,1:length(SAM.COLS)]
    colnames(t) = SAM.COLS

    return(t)
}

test_parse.read.name = function(){
    p = parse.pattern.to.regex("{origin}_{start}_.*")
    a = parse.read.name(c("Hum_234_567","Bac_334_556","*_0_0"),p)
    b = data.frame(origin = c("Hum","Bac","*"), 
                   start = c("234","334","0"))
    return ( all(a == b) )
}
parse.read.name = function(rnames, regex){
    matches = regexpr(pattern=regex, text=rnames, perl=TRUE)
    capture.names = attr(matches,"capture.names")
    capture.start = attr(matches,"capture.start")
    capture.len = attr(matches,"capture.length")
    capture.end = capture.start + capture.len - 1
    # Don't include unnamed capture groups in result columns
    field.names = colnames(capture.start) %>% {.[. != ""]}
    # One list element per pattern component, e.g. ...{src}...
    substrings = lapply(field.names,
           function(name)
               substr(rnames,
                      start= capture.start[,name],
                      stop  = capture.end[,name]))
    names(substrings) = field.names
    return( as.data.frame( substrings))

}

test_parse.pattern.to.regex = function(){
    x = parse.pattern.to.regex("{test1}_{test2}")
    y = "(?<test1>[[:alnum:]*]+)_(?<test2>[[:alnum:]*]+)"
    return(x == y)
}
# Converts {...} to (?<...>[[:alnum:]]+)
parse.pattern.to.regex = function(pattern){
    gsub("\\{([[:alnum:]]+)\\}","(?<\\1>[[:alnum:]*]+)",pattern)
}

test_regex.cluster1 = function(){
    x = regex.cluster(c("a-1_100","a-2_100","b-1_200","b-2_200"),
                      regex="^([a-z]+)",group=1)
    y = c("a","a","b","b")
    return(all(x == y))
}
test_regex.cluster2 = function(){
    x = regex.cluster("a-1_100", regex="^([a-z]+)", group=1)
    y = "a"
    return(all(x == y))
}
regex.cluster = function(v, regex, group=1){
    m = regexpr(text=v, pattern=regex, perl=T)
    group.start = attr(m,"capture.start")[,group]
    group.len = attr(m,"capture.length")[,group]
    group.end = group.start + group.len - 1
    group.str = substr(v, start=group.start, stop=group.end)
    return(group.str)
}

test_gen.column = function(){
    d = data.frame(org=rep("abc",4), chr=c("a","a","b","b"))
    x = gen.column(d, fmt="{org}_{chr}")
    y = c("abc_a","abc_a","abc_b","abc_b")
    return(all(x == y))
}
gen.column = function(df, fmt){
    s = str_extract_all(string=fmt, pattern="\\{[A-z0-9_\\.-]+\\}")[[1]]
    lengths = str_length(s)
    placeholders = unique(str_sub(s,2,lengths-1))
    missing_placeholders = placeholders[!placeholders %in% colnames(df)]
    if(length(missing_placeholders) > 0){
        stop("You have used the placeholder(s)",s,", but no data could be extracted",
             "for them from the read names")
    }
    for( p_name in placeholders){
        p_fmt = str_c("{",p_name,"}")
        fmt = str_replace_all(fmt, fixed(p_fmt), df[,p_name]) 
    }
    return(fmt)
}

test_parse.spaced.arg = function(){
    a = parse.spaced.arg("a={a}_{b} b={c}={d}")
    b = c(a="{a}_{b}", b="{c}={d}")
    return(identical(a,b))
}
parse.spaced.arg = function(string){
    str_split(string,pattern="[:space:]+")[[1]] %>% 
        str_split(pattern="=", n=2) -> 
        split
    
    names = sapply(split, getElement, 1)    
    fmt = sapply(split, getElement, 2)    
    return(setNames(fmt,names))
}

# Unit test functions
# ===================


printf = function(...) cat(sprintf(...))

# Expects string. Returns whether that string is an existing function name
is.function_ = function(f) is.function(eval(parse(text=f)))

test = function(){
    n.failed = 0
    for(e in ls(globalenv())){
        if(substr(e,1,5) == "test_" & is.function_(e)){
            r = eval(parse(text=e))()
            if(!r) {
                n.failed = n.failed+1
                printf("Test % 15s failed\n",e)
            }
        }
    }
    printf("%d tests have failed.\n",n.failed)
}

# Command line argument parsing
# =============================

usageError = function(...) stop(...)

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
        argv = argv[-1]

        if(opt == "help") printHelpAndExit()

        if(!(opt %in% names(argValues))) usageError("Unknown option",opt)

        # Number of needed additional values
        nparm = subset(spec,name==opt)[,"nparam"]
        if(nparm > length(argv)) usageError("Wrong number of parameters for --",opt)

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
    if(length(argv) != n.mandatory) usageError("Wrong number of mandatory arguments")
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

# Script starting point
# =====================
cmda <- commandArgs(TRUE)

if(length(cmda)>0 && "--test" %in% cmda){
    test()
}else{
    options(error=traceback)
    args = parseArgs(cmda,spec=ARG_SPEC,n.mandatory=1)
    # tryCatch... : Only print error message if error occurs, no additional info
    tryCatch(expr=
        main(args)
    , error=function(...){
        cat(geterrmessage(),"\n",file=stderr())
    })
}

# vim: tw=80


