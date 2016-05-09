#!/usr/bin/env Rscript

`%notin%` <- function(a,b) ! a%in%b

args <- commandArgs(trailing=TRUE)
if(length(args) < 3){
    cat("
    Usage: merge_organisms.sh (READ_TAB | -) BY ORGANISM_TAB [A=B ...]

    Look up additional information by looking up values of BY in
    ORGANISM_TAB and append them to READ_TAB.

    Details
    =======

    READ_TAB must have a column called BY, whose values correspond
    to the first column of ORGANISM_TAB.

    READ_TAB may be - in which case the table is read from standard 
    input.

    The first column in ORGANISM_TAB may not have duplicated values

    An arbitrary number of A=B expressions may follow, which rename columns
    stemming from ORGANISM_TAB: Column A is renamed to B.

    Values of the column BY may also be *, which indicates a read that 
    is not mapped. All values which would otherwise be imported from 
    ORGANISM_TAB get replaced by * then.


    Example
    =======
    
    Given the files

    ─── reads.tab ────────────────────────────────
    orig    read         correct
    A1      sample_21    TRUE
    A2      sample_10    FALSE
    A2      sample_0     FALSE
    ret     sample_5     FALSE 
    ──────────────────────────────────────────────

    ─── organisms.tab ─────
    record  organism
    A1      volpertinger
    A2      volpertinger
    A3      volpertinger
    B1      volpertinger
    B2      volpertinger
    ret     retli
    ───────────────────────

    the call 
       
        merge_organisms.R reads.tab orig organisms.tab

    yields

    ───────────────────────────────────────────
    orig    read         correct  organism
    A1      sample_21    TRUE     volpertinger
    A2      sample_10    FALSE    volpertinger
    A2      sample_0     FALSE    volpertinger
    ret     sample_5     FALSE    retli
    ───────────────────────────────────────────

    ")
    quit(status=1)
}
readTab <- function(fn){
    if(fn == "-") fn <- "stdin"
    read.table(fn, header=TRUE, row.names=NULL, stringsAsFactors=FALSE,
               comment.char="")
}

read_tab <- readTab(args[1])
by <- args[2]
organism_tab <- readTab(args[3])


renames <- args[-(1:3)]
renames <- strsplit(renames,"=")
if(any(sapply(renames,length) != 2)) 
    stop("illegal column rename rule specified. Must be A=B")


old_cn <- colnames(organism_tab)
new_cn <- colnames(organism_tab)
for(r in renames){
    # First column may not be renamed
    if((old_cn == r[1])[1]) stop("First column may not be renamed")
    # Rename column named r[1] to r[2]
    new_cn[old_cn == r[1]] <- r[2]
}
colnames(organism_tab) <- new_cn

# Put an asterisk (*) if a read is not mapped
organism_tab <- rbind(organism_tab, rep('*',ncol(organism_tab))) 

# There may be no duplicated keys in second input
if(any(duplicated(organism_tab[,1])))
    stop("There must not be any duplicated value in the first",
         " column of ORGANISM_TAB")

# There may be no keys (chromosome names) missing in second input
read_tab_keys <- unique(read_tab[,by])
organism_keys <- unique(organism_tab[,1])
missing_keys <- read_tab_keys[read_tab_keys %notin% organism_keys]
if(length(missing_keys) > 0)
    stop("The following chromosome names have no organism specified: ",
         paste(missing_keys,collapse=", "))

# Get information for the true organisms
o <- merge(read_tab, organism_tab, 
            by.x=by, by.y=1, all.x=TRUE)


write.table(o, file=stdout(), row.names=FALSE, sep="\t", quote=FALSE)


