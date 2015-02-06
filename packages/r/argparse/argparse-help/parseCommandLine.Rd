\name{parseCommandLine}
\alias{parseCommandLine}
%- Also NEED an '\alias' for EACH other topic documented here.
\title{
Parse command line using type and default value information
}
\description{
Reads in the command line arguments using \code{argparse}. Converts values according to their
expected type and fills in default values of missing optional arguments.
}
\usage{
parseCommandLine(expectedArgs)
}
%- maybe also 'usage' for other objects documented here.
\arguments{
  \item{expectedArgs}{
  Description of expected arguments, as parsed by \code{parseExpectedArgs}.
}
}
\details{
%%  ~~ If necessary, more details than the description above ~~
}
\value{
List: keys named like expected arguments, values are their values.
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
}
