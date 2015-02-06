\name{parseExpectedArgs}
\alias{parseExpectedArgs}
%- Also NEED an '\alias' for EACH other topic documented here.
\title{
Parse textual information about expected variables.
}
\description{
Reads in a string forming a table. Returns a nested list of class "expectedArguments". 
Contains one item per argument, each item containing
4 sub-items named name, type, val, help.

}
\usage{
parseExpectedArgs(s, sep = "|", expectedMark = "<>", helpText = "")
}
%- maybe also 'usage' for other objects documented here.
\arguments{
  \item{s}{
  String forming a table: Example:
  \code{
a | numeric   | <>    | Help text for a
b | character | abc   | Help text for b
c | logical   | FALSE | Help text for c
d | numeric   | 1     | Help text for d}

}
  \item{sep}{
    Table column separator character
}
  \item{expectedMark}{
    Text in value column if the argument is mandatory. Default: <>.
}
  \item{helpText}{
    A text describing the program. This is shown in addition to the 
    argument specific help texts when the script is invoked with the --help or
    -h option.
}
}
\details{
%%  ~~ If necessary, more details than the description above ~~
}
\value{
see Description.
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
expectedArgs="
nreads        | numeric | <> | Number of reads to create
readlength    | numeric | <> | Average length of an individual read
readlength.sd | numeric | <> | Standard deviation of read lengths
start         | numeric | <> | start index
end           | numeric | <> | end index
seed          | numeric | NA | random number generator seed
"

eargs= parseExpectedArgs(expectedArgs)

}
