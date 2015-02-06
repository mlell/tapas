#!/usr/bin/env Rscript

library(methods)
library(docopt)
library(stringr)
library(magrittr)

help="Usage: param-anova.R [options] TAB MODEL

WARNING: This script currently performs no ANOVA but is a simple wrapper for
         fitting the linear model MODEL to the input table TAB.

TAB          Table containing the columns sensitivity and specificity, and 
             columns containing parameter values, which can be reference from 
             START_MODEL

MODEL        R formula. Don't use whitespace in the argument. (bug in docopt)

--anova           Perform ANOVA with the specified model

--as-factor COLS  Comma-separated list (no whitespace!) of column names that
                  should be treated as factors. Only columns that would be
                  interpreted as numeric by default need to be included here. 

--tab-out         Currently ignored!
                  Print the output in tabular format, for easier automatic
                  parsing.

--filter-pval P   Only anova! Don't print lines for any p-value bigger than P
" 

args = docopt(help)

f.performance = args$TAB
start.model = args$MODEL
cols.as.factor = args$`--as-factor`
tab.output = args$`--tab-out`
max.pval = args$`--filter-pval`
do.anova = args$`--anova`

performance = read.table(file=f.performance, header=TRUE)

if(!is.null(cols.as.factor)){
    cols.as.factor = str_split(cols.as.factor,",")[[1]] %>% str_trim
    print(cols.as.factor)
    for(c in cols.as.factor){
        performance[,c] = as.factor(performance[,c])
    }
}

#formula.sens = eval(parse(text=paste0("sensitivity~",start.model)))
#formula.spec = eval(parse(text=paste0("specificity~",start.model)))

formula = eval(parse(text=start.model))
vars.rhs = all.vars(parse(text=gsub("^.*~","",start.model)))

summary(performance[,vars.rhs])

output = function(x){
   if(tab.output) print.data.frame(x)
   else print(x)
}
filter_pval = function(anova, p){
    anova %>% subset(`Pr(>F)` <= p)
}

#cat("==== Sensitivity ====\n")
model = lm( formula , data=performance)
if(!do.anova){
    summary(model)
}else{
    m.anova = anova(model)
    if(!is.null(max.pval)){
        m.anova %<>% filter_pval(max.pval)
    }
    output(m.anova)
}
#cat("---- Coefficients ----\n")
#coef = coefficients(msens)
#print.data.frame(data.frame(coef=names(coef),val=coef,row.names=NULL),row.names=F)

#cat("---- ANOVA ----\n")
#output(anova.sens)



