#!/usr/bin/env Rscript

args = commandArgs(TRUE)
plot.name=args[1]

d = scan("stdin")

pdf(plot.name,4,3)
# skip header
hist(d)
dev.off()
