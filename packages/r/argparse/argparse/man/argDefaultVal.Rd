\name{argDefaultVal}
\alias{argDefaultVal}
%- Also NEED an '\alias' for EACH other topic documented here.
\title{
Return default value of an optional argument
}
\description{
Given a parsed parameter table, returns the default value of the argument with the given name. Returns NULL 
if the named argument is mandatory.
}
\usage{
argDefaultVal(argName, expectedArgs)
}
%- maybe also 'usage' for other objects documented here.
\arguments{
  \item{argName}{
String with the argument name.
}
  \item{expectedArgs}{
parsed list of expected Arguments, as returned by parseExpectedArgs.
}
}
\details{
%%  ~~ If necessary, more details than the description above ~~
}
\value{
Default value, type of the named argument.
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
\code{\link{parseExpectedArgs}}, \code{\link{argType}}, \code{\link{argNames}}
}
\examples{
##---- Should be DIRECTLY executable !! ----
##-- ==>  Define data, use random,
##--	or do  help(data=index)  for the standard data sets.

## The function is currently defined as
function (argName, expectedArgs) 
{
    stopifnot("expectedArgs" \%in\% class(expectedArgs))
    stopifnot(mode(argName) == "character")
    val = expectedArgs[[argName]]$val
    if (is.null(val)) 
        return(NULL)
    if (is.na(val)) 
        return(NA)
    if (val == attr(expectedArgs, "expectedMark")) 
        val = NULL
    else val = .coerce(val = val, as = argType(argName, expectedArgs))
    return(val)
  }
}
