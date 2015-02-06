\name{arglist}
\alias{arglist}
%- Also NEED an '\alias' for EACH other topic documented here.
\title{
Return a list of named arguments and flags converted to boolean named arguments. }
\description{
Reads in the command line argument vector and parses. Converts key=value pairs to 
list entries containing a 2-element vector with key and value. Converts --flag arguments
to flag=TRUE and proceeds as with key-value pairs.

Prints a help message and stops on flags --help and -h
}

\usage{
arglist()
}
%- maybe also 'usage' for other objects documented here.
\details{
%%  ~~ If necessary, more details than the description above ~~
}
\value{
[[1]]
[1] "key1" "val1"

[[2]]
[1] "key2" "val2"

[[3]]
[1] "flag" "TRUE"

...

}
\references{
%% ~put references to the literature/web site here ~
}
\author{
Moritz Lell
}
\note{
%%  ~~further notes~~
}

%% ~Make other sections like Warning with \section{Warning }{....} ~

\seealso{
%% ~~objects to See Also as \code{\link{help}}, ~~~
}
\examples{
##---- Should be DIRECTLY executable !! ----
##-- ==>  Define data, use random,
##--	or do  help(data=index)  for the standard data sets.

## The function is currently defined as
function () 
{
    args = commandArgs(trailing = TRUE)
    args = .transformFlags(args)
    a = strsplit(args, split = "=")
    if (!all(unlist(lapply(a, length)) == 2)) {
        stop("All Arguments must be of the form --flag or name=value!")
    }
    return(a)
  }
}
