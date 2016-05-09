#!/usr/bin/env Rscript
library(methods)
library(docopt)

help=" Usage: exactmap.R [options] TRUE_INFO READ_MAPPINGS

Output: READ_TAB, with an added column called 'correct', which holds
a logical value whether a read has mapped correctly.

TRUE_INFO must be a tab-separated table like the following:

    ────────TRUE_INFO ────────
    name        record  start  
    sample_0    A2      498   
    sample_1    B2      4899  
    sample_2    X       3674  
    sample_3    B2      3616  
    sample_4    B1      3675  
    ...
    ──────────────────────────
    
READ_MAPPINGS must be a tab-separated table like the following.
The column 'mapq' is only required if the switch --qthresh is used.

    ──────── READ_MAPPINGS ────────────
    qname        rname   pos     mapq  
    sample_0     A2      3605    13
    sample_1     X       5965    25
    sample_2     X       3674    37
    sample_3     B2      3616    0
    sample_4     X       3196    0
    ...
    ───────────────────────────────────

Additional columns may be present and are ignored.

Options:
  --qthresh Q          Only consider reads as mapped which are >= Q as mapped.
  --organism-tab OTAB  Merge an additional table OTAB. The first two columns
                       of this table carry FASTA record names and the 
                       organism names they belong to, respectively.

"

# Read in a tab-separated text table
readTab <- function(file){
    read.table(file=file, header=TRUE, sep="\t", row.names=NULL, 
               stringsAsFactors=FALSE)
}

# Main script
main <- function(argv){
    # Parse cmdline arguments
    args <- docopt(doc=help, args=argv)
    # Read input data
    trueinfo <- readTab(args$TRUE_INFO)
    mappings <- readTab(args$READ_MAPPINGS)

    organism_tab <- args$`--organism-tab`
    if(!is.null(organism_tab)){
        organism_tab <- readTab(organism_tab)
        # All record names must be unique
        if(any(duplicated(organism_tab[,1]))){
            stop('At least one duplicated value in first column of ',
                 'OTAB (FASTA record -- organism) table')
        }
    }

    # Check validity of inputs
    if(!is.null(args$`--qthresh`)){
        qthresh <- as.numeric(args$`--qthresh`)
        if(is.na(qthresh)) stop('Integer must be supplied to --qthresh!')
    }else{
        qthresh <- 0
    }
    if("*" %in% trueinfo$record) 
        stop("No FASTA record may have name * because it interferes with
             SAM file format!")

    # This is the name of the mapq column if the input data contains this
    # column, else an empty vector
    qualcol <- intersect(colnames(mappings),'mapq')

    # Merge true and actual mapping information
    merged <- merge(trueinfo[,c('name','record','start')], 
                    mappings[,c('qname','rname','pos', qualcol )],
                    by.x='name', by.y='qname',all.y=TRUE)

    # There may be no missing information for any read, except reads
    # that are not mapped (rname == *)
    missing_information <- 
        unique(subset(merged, is.na(record) & rname != '*')$rname)
    missing_information <- setdiff(missing_information,'*')
    if(length(missing_information > 0))
        stop('There is missing information in TRUE_INFO for ',
             paste(missing_information,collapse=', '))
    
    # Mark correctly mapped reads. Generate a new column, correct
    # Reads whose map quality is below the threshold are considered
    # not correctly mapped
    merged$correct <- rep(FALSE, nrow(merged))
    merged <- within(merged,{

        correct[ rname == record & pos == start & rname != '*' ] <- TRUE

        if(qthresh > 0){
            correct[ mapq < qthresh ] <- FALSE
        }
    })

    # Remove unneeded columns
    merged <- merged[,c('name','rname','record',qualcol,'correct')]

    # Rename columns for descriptive output
    cn <- colnames(merged)
    cn[cn=='name']   <- 'read'
    cn[cn=='rname']   <- 'm.orig'
    cn[cn=='record']  <- 't.orig'
    cn[cn=='mapq']    <- 'mapq'
    cn[cn=='correct'] <- 'correct'
    colnames(merged) <- cn

    # Get organism information from FASTA record names stored in 
    # name (TRUE_INFO) and rname (READ_MAPPINGS)
    if(!is.null(organism_tab)){
        oldcn <- colnames(organism_tab)

        # Output columns with true information will have prefix 't.'
        colnames(organism_tab) <- paste0('t.',oldcn)
        # --- Get true organisms ---
        merged <- merge(merged, organism_tab,
                        by.x='t.orig', by.y=1, all.x=TRUE)


        # If true origin is * (== no chromosome but dummy read), change
        # true origin organism to * as well
        if(any(merged$t.orig == '*')) 
            merged$t.organism[merged$t.orig == '*'] <- '*'

        # --- Get organisms reads have been mapped to ---

        # Output columns with information from reference reads are actually
        # mapped to will have prefix 'm.'
        colnames(organism_tab) <- paste0('m.',oldcn)
        merged <- merge(merged, organism_tab,
                        by.x='m.orig', by.y=1, all.x=TRUE)

        # If read was not mapped (*), change m.organism to * as well
        if(any(merged$m.orig == '*')) 
            merged$m.organism[merged$m.orig == '*'] <- '*'
    }

    # Output: rename columns to expressive values and print.

    write.table(merged, sep='\t', quote=FALSE, row.names=FALSE)
}

main(commandArgs(trailing=TRUE))



