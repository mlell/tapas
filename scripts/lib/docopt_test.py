from docopt import docopt
import pdb

doc="""Usage: test [options] A

Options:
    --output <X> <Y>  Output.
"""

doc2="""Usage: test [--output X Y] A"""

args = docopt(doc)

print(args)

re.findall(r'\[default: +((.+?) +)+(.+?) *\]','[default: Ab cd]')
