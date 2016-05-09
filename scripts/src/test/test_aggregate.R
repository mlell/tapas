#!/usr/bin/Rscript
library(testthat)

source("aggregate.R")

test_that("--fun argument a=b(c,d) is split correctly",{
    arg = "a=b(c,d)"
    parsed = parse.fun.arg(arg)
    expect_equal(column(parsed), "a")
    expect_equal(funname(parsed), "b")
    expect_equal(arguments(parsed), c("c","d"))
})

test_that("FUN parsing accepts count()",{
    p = parse.fun.arg("count()")
    expect_equal(column(p), "")
    expect_equal(funname(p), "count")
    expect_equal(arguments(p), character())
})
test_that("--fun arg parsing can deal with whitespace",{
    arg = c("a =b(c,d)","a = b(c,d)", 
            "a= b( c, d)","a=b (c,d )")
    for(i in arg){
        parsed = parse.fun.arg(arg)
        expect_equal(column(parsed), "a")
        expect_equal(funname(parsed), "b")
        expect_equal(arguments(parsed), c("c","d"))
    }
})
test_that("illegal formats of FUN argument are rejected",{
    expect_error(parse.fun.arg("a=a(b,c)=x"))
    expect_error(parse.fun.arg("a=a(b,c)(x)"))
    expect_error(parse.fun.arg("a=a(b(x),c)"))
    expect_error(parse.fun.arg("a x=a(b,c)"))
    expect_error(parse.fun.arg("a x=a(b,c)"))
    expect_error(parse.fun.arg("a=a x(b,c)"))
    expect_error(parse.fun.arg("a=a(b,c x)"))
    expect_error(parse.fun.arg("a=a(b,c) x"))
})
test_that("FUN argument can deal with 3-part and 2-part arguments",{
    p1 = parse.fun.arg("a(b,c)")
    expect_equal(column(p1), "")
    p2 = parse.fun.arg("d=a(b,c)")
    expect_equal(column(p2),"d")
})

test_that("FUN argument accecpts multiple functions",{
    p = parse.fun.cmdline("a=fun(x,y); b = fun2();")
    pa = parse.fun.arg("a=fun(x,y)")
    pb = parse.fun.arg("b=fun2()")
    expect_equal(column(p[[1]]), column(pa))
    expect_equal(funname(p[[1]]), funname(pa))
    expect_equal(arguments(p[[1]]), arguments(pa))
})

test_that("{...} replacement by format() works",{
    a = "{a} {b}"
    expect_equal(format(a,a=1), "1 {b}")
})

test_that("aggregate columns argument is parsed correctly.",{
    expect_equal(parse.aggregate.arg("col1+col2"),c("col1","col2"))
    expect_equal(parse.aggregate.arg("col1"),c("col1"))
    expect_equal(parse.aggregate.arg("col1 + col2"),c("col1","col2"))
})

