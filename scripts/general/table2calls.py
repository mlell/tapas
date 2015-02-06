#!/usr/bin/env python
import sys
import csv
from docopt import docopt
import shlex

doc="""Usage: tablecalls.py [--omit O] TAB SCRIPT 

Print calls which set variables defined in a table and execute a
specified script afterwards. For each table row one line printed.

Options:
========

    --omit O  [Default: <>] If a table cell has this value, the 
              corresponding variable is unset in that line.

Details:
========

The calls are enclosed in parentheses, in order to make the shell spawn
a subshell, preventing interaction of the commands with each other, 
e.g. by setting variables. Setting variables in a parent shell from a subshell
is not possible in a straightforward manner.

However, variables defined in the calling shell are visible to subshells.

A value of '<>' results in the corresponding variable being unset so that
it holds no values when the child script is sourced. Such variables
are explicitly unset in the subshell, guaranteeing they will be without
value when the child script (argument SCRIPT) is called, even if they are
defined in the calling shell.

Refer to the bash manual for more information.


Testing for unset variables in bash
-----------------------------------

Note that when writing the SCRIPT to execute, the substitution pattern
${var:+value} in bash can be of great use.

This results in `value` being printed if `var` is set, if `var` is unset,
nothing is printed:

    ───── example.sh ───────────────────────────

    # set a value for a, while b remains unset
    a=123 
    echo hello ${a:+-a $a} ${b:+-b $b}

    ────────────────────────────────────────────

If executed like this:

    ./example.sh

Output is:

    ────────────────────────

    hello -a 123

    ────────────────────────


Example input to this tool: 
===========================
    
    ───── example.tab ──────
    index    var1   b
    1       1       5.12  
    2       1       14.3
    3       2       <>
    ───────────────────────

The call `tablecalls.py example.tab myscript.sh` results in 
the following output:

    ─────────────────────────────────────────────
    (index=1;var1=1;b=5.12;source myscript.sh);
    (index=2;var1=1;b=14.3;source myscript.sh);
    (index=3;var1=2;unset b;source myscript.sh);
    ─────────────────────────────────────────────


"""

# Set the bash commands used to perform various tasks:
# -------------------------------------------------------

# Command to use when deleting a variable
unset = lambda var: "unset {}".format(shlex.quote(var))

# Command to use when setting a variable
set_var = lambda name, value: "{}={}".format( shlex.quote(name), 
                                               shlex.quote(value)) 
# Command to use when sourceing a script (execute in same
# shell, no subshell)
source = lambda script: "source {}".format(shlex.quote(script))

# String to use when invoking a subshell
subshell = lambda *args : "(" +"; ".join(args) +");"

# --------------------------------------------------------

def main(argv):
    args=docopt(doc=doc,argv=argv[1:])

    null_val=args["--omit"]

    # Read table lines
    with open(args["TAB"],"rt") as fd:
        dr = csv.DictReader(fd, delimiter='\t')
        lines = [line for line in dr]

    # Print out a line for each input row, first setting
    # variables, then executing the script.
    # A subshell is used to prevent the scripts from influencing
    # each other
    for row in lines:
        commands = []
        for fname,fval in row.items():
            if(fval==null_val): 
                commands.append(unset(fname))
            else:
                commands.append(set_var(fname,fval))

        commands.append(source(args["SCRIPT"]))

        print(subshell(*commands))



if __name__ == "__main__": main(sys.argv)
