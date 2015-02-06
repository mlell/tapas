#!/usr/bin/env Rscript

library(methods)
library(docopt)
suppressPackageStartupMessages(library(dplyr))
library(magrittr)

help="Usage: sens-spec.R RUN_AGG"

args=docopt(help)

run.stats = args$`RUN_AGG`

#run.stats = "all.agg"

# These reads should map back to their origin genome
mapped.org = "uspemito"

run.stats = read.table(run.stats,header=TRUE) %>% tbl_df()

should_map_orgs = filter(run.stats, correct.mapping) %>% 
                  .[["org"]] %>% unique() %>% as.character()
should_map_orgs
all_orgs = union(levels(run.stats[["org"]]),levels(run.stats[["torg"]]))
all_orgs
shouldnot_map_orgs = setdiff(all_orgs,should_map_orgs)

shouldnot_map_orgs

# Sensitivity
# ===========

# Fates of all reads which should map correctly 
true.pos = group_by(run.stats, run) %>%
                filter(torg == org)
true.pos
n.true.pos = true.pos %>% summarize(count=sum(count))


# How many of the true positives are actually mapped? (Test positive)
test.pos = group_by(true.pos, run) %>%
    filter(org == mapped.org, correct.mapping & high.quality) 

n.test.pos = test.pos %>% summarize(count = sum(count))

sensitivity = merge(n.true.pos, n.test.pos, 
                    by="run", suffixes=c(".true",".test")) %>%
    mutate(sensitivity = count.test/count.true)

# Specificity
# ===========

# How many reads are negative control reads
true.neg = group_by(run.stats,run) %>%
    filter( torg != mapped.org)

test.neg = group_by(true.neg, run) %>%
    filter( (org != mapped.org) | (org == mapped.org & !high.quality) )
    
n.true.neg = true.neg %>% summarize(count = sum(count))
n.test.neg = test.neg %>% summarize(count = sum(count))

specificity = merge(n.true.neg, n.test.neg, 
                    by="run", suffixes=c(".true",".test")) %>%
    mutate(specificity = count.test/count.true, run)

performance = merge(sensitivity, specificity, 
                    by="run", suffixes=c(".sens", ".spec"))

# Output
# ======
write.table(performance, file="", sep="\t", dec=".", quote=FALSE, 
            row.names=FALSE)



