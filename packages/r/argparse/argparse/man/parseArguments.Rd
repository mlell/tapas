\name{parseArguments}
\alias{parseArguments}
%- Also NEED an '\alias' for EACH other topic documented here.
\title{
Invoke argument parser for a given textual description of expected arguments
}
\description{
Top-Level function. Expects a table like this as string:

\code{
a | numeric   | <>    | Help text for a
b | character | abc   | Help text for b
c | logical   | FALSE | Help text for c
d | numeric   | 1     | Help text for d}

}
\usage{
parseArguments(expectedArgumentText)
}
%- maybe also 'usage' for other objects documented here.
\arguments{
  \item{expectedArgumentText}{
String forming a table with 4 columns: name, type, default value or <> if mandatory, Help text.
}
}
\details{
%%  ~~ If necessary, more details than the description above ~~
}
\value{
Nested list of class "expectedArguments". Contains one item per argument, each item containing
4 sub-items named name, type, val, help.
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
function (expectedArgumentText) 
{
    return(parseCommandLine(parseExpectedArgs(expectedArgumentText)))
  }
}
