#!/usr/bin/env Rscript
library("Quartet")
library("ape")

args = commandArgs(trailingOnly=TRUE)

test_tree <- ape::read.tree(file=args[1])
comp_trees <- ape::read.tree(file=args[2])

statuses <- SingleTreeQuartetAgreement(comp_trees, test_tree)
print(QuartetDivergence(statuses, similarity = FALSE))
