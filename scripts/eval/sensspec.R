#! /usr/bin/env Rscript

library(methods)
library(magrittr)
#suppressPackageStartupMessages(
#    library(dplyr))
library(docopt)

help = "
Usage: sensspec.R [options] INPUT_FILE SHOULD_MAP

Calculates the sensitivity and specificity of mapping runs. 

INPUT_FILE is a TAB-separated table with lists amounts of reads satisfying the
values of the other columns. It can be obtained by aggregating the output of
sam-extract.R. The following columns are needed:

* t.org:    True origin of the reads
* m.org:    Genome the reads have been mapped to. Per default, * means
            'not mapped'
* correct:  Whether the reads have been 
* count:    Number of reads satisfying the values of the other columns.

Example of INPUT_FILE below.

SHOULD_MAP is a comma-separated list of values in the column t.org.
Pay attention not to include any whitespace in SHOULD_MAP!

All lines containing one of the values listed here in their t.org columns 
are expected to sum up to the total number of reads which are expected to be
mapped. This means all organisms for which references to map to were provided
to the mapper must be included here.

All lines containing values in t.org which are not listed in SHOULD_MAP
are considered to stand for reads that are not supposed to map, negative 
controls to assess the specificity of a mapper.


Options:

--c-torg CN     [Default: t.org]   Column name of the true origin column 
--c-morg CN     [Default: m.org]   Column name of the 'mapped to' column 
--c-correct CN  [Default: correct] Column name of the 'mapped correctly' column
--c-count CN    [Default: count]   Column name of the read count column 
--s-nomap CN    [Default: *]       String representing 'not mapped'


Example for INPUT_FILE:

t.org     m.org     correct   count
ecoli     ecoli     TRUE      1000
ecoli     ecoli     FALSE     300
ecoli     bsubt     FALSE     100
ecoli     *         FALSE     200
bsubt     bsubt     TRUE      500
bsubt     ecoli     FALSE     120
bsubt     *         FALSE     200
ecoli     ecoli     TRUE      900
ecoli     ecoli     FALSE     100
...

"

#pr <- Sys.getenv("pr")
#setwd(paste0(pr,"/data/gen/cat_mappings/bwa/1"))
args <- docopt(doc=help)
correct_col <- args$"--c-correct"
torg_col    <- args$"--c-torg"
morg_col    <- args$"--c-morg"
count_col   <- args$"--c-count"
# This symbol means 'not mapped'
org_null    <- args$"--s-nomap"

in.filename <- args$"INPUT_FILE"
org_should_map  <- strsplit(args$"SHOULD_MAP", ",")[[1]]

colnames = readLines(in.filename,1) %>% strsplit("\t") %>% .[[1]]
needed.colnames = c(correct_col, torg_col, morg_col, count_col)
missing = ! needed.colnames %in% colnames
missing = needed.colnames[missing]
                       
if(length(missing) > 0){
    stop("The input table misses one or more mandatory columns: ",
         paste0(missing,collapse=","))
}

t <- read.table(file=in.filename,sep="\t", header=TRUE, row.names = NULL)

# Rename input columns to t.org, m.org, ... , respectively
# ddplyr syntax is way clearer if the column names are hard-coded.
#t %<>% select_(.dots = setNames(
#            c(torg_col,morg_col, correct_col, count_col),
#            c("t.org","m.org","correct","count")))

#all_organisms <- union(t$m.org, t$t.org)
all_organisms <- union(t[[morg_col]], t[[torg_col]])

# org_should_map <- 
#    t %>% filter(correct) %>% select(t.org) %>% .[[1]] %>%
#        unique() %>% as.character()
org_should_not_map <- setdiff(all_organisms, org_should_map)

#org_should_not_map
#org_should_map

# Senstitivity
# ============

# Reads which should map, and their actual fate
#should_map <- filter(t, t.org %in% org_should_map )
#should_map <- t[t$t.org %in% org_should_map, ]
should_map <- t[t[[torg_col]] %in% org_should_map, ]

#n_should_map <- summarize(should_map, count = sum(count))
n_should_map <- sum(should_map[[count_col]])

# Which of the reads that should map are actually mapped?
#n_actual_map <- filter(should_map, correct == TRUE) %>%
                #select(run, count)
n_actual_map <- sum(ifelse(
                    should_map[[correct_col]], 
                    should_map[[count_col]], 
                    0))

sensitivity <- data.frame(map.true=n_should_map, map.actl=n_actual_map, 
                     sensitivity=n_actual_map/n_should_map)

#sensitivity %<>% #group_by(run) %>%
#                transmute(sensitivity = count.actl / count.true,
#                          correct.true = count.true, 
#                          correct.actl = count.actl)



# Specificity
# ===========

#should_not_map <- filter(t, t.org %in% org_should_not_map)
should_not_map <- t[t[[torg_col]] %in% org_should_not_map, ]

#n_should_not_map <- group_by(should_not_map) %>%
#                    #select(run, count) %>%
#                    summarize(count = sum(count))
n_should_not_map <- sum(should_not_map[[count_col]])

#actual_not_map <- filter(should_not_map, m.org == org_null)

#n_actual_not_map <- group_by(actual_not_map) %>%
#                    summarize(count = sum(count))
n_actual_not_map <- sum(ifelse(
                        should_not_map[[morg_col]] == org_null, 
                        should_not_map[[count_col]], 
                        0))

#specificity <- merge(n_should_not_map, n_actual_not_map, by="run",
                     #suffixes=c(".true",".actl"))
#specificity %<>% #group_by(run) %>%
#                 rename( nomap.true = count.true,
#                         nomap.actl = count.actl) %>%
#                 transmute(specificity = nomap.actl/nomap.true,
#                           nomap.true, nomap.actl)

specificity <- data.frame(nomap.true=n_should_not_map,
                     nomap.actl=n_actual_not_map,
                     specificity = n_actual_not_map / n_should_not_map)
performance <- cbind(sensitivity, specificity)
performance[,"bcr"] <- 
    ( performance[,'sensitivity'] + 
      performance[,'specificity'] ) / 2
 
write.table(performance, file=stdout(), sep="\t", row.names=FALSE,
            quote=F)



