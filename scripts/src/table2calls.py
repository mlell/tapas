#!/usr/bin/env python
import sys
import csv
import argparse
import shlex
import re

description="""Usage: tablecalls.py [options] TAB SCRIPT

Print calls which set variables defined in a table and execute a
specified script afterwards. For each table row one call of SCRIPT
is printed, setting the appropriate environment variables beforehand.
"""

epilog="""
==========================================================================

Details:

This tools generates calls of the sort
    
    ────────────────────────────
    (var1=abc var2=def SCRIPT);
    (var1=xyz var2=ijk SCRIPT);
    (var1=123 var2=456 SCRIPT);
    ────────────────────────────

This kind of calls executes `SCRIPT` with the variables `var1` and `var2` 
being set as environment variables. The `SCRIPT` can then use the means
of its programming language to access the values of `var1` and `var2`. 

For example, if `SCRIPT` is a shell script, this is as easy as accessing
`${var1}` and `${var2}`, respectively. Python scripts can use the 
`os.environ['var1']` function. See the documentation of your programming
language to find out how to access environment variables.

Note that variables which are made environment variables by the calling
shell are visible to all called programs and scripts, and are therefore
propagated here as well. This may lead to subtle bugs if a variable which
is thought to be unset is set. Therefore this program writes checks for
all variables to be unset at the beginning of the script. This behaviour
can be disabled.


Example input to this tool: 
===========================
    
    ───── example.tab ──────
    index    var1   b
    1       1       5.12  
    2       1       14.3
    3       2       2.00
    ───────────────────────

The call 

    `table2calls.py example.tab ./myscript.sh` 
    
results in the following output:

    ─────────────────────────────────────────────
    (index=1 var1=1 b=5.12 ./myscript.sh);
    (index=2 var1=1 b=14.3 ./myscript.sh);
    (index=3 var1=2 b=2.00 ./myscript.sh);
    ─────────────────────────────────────────────
"""

def parseArguments():
    p = argparse.ArgumentParser(description=description, epilog=epilog,
                                formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument('TAB', help=
        "Text table with variable values to translate into calls")
    p.add_argument('SCRIPT', help=
        "Program or script which is to be executed")
    p.add_argument('--const', type=str, nargs = 2, action = 'append', 
        metavar=['NAME' 'VALUE'], default = [], help=
        "In addition to the variables in TAB, set a variable called NAME "+\
        "with the value VALUE. This is handy to forward constant values, "+\
        "like file paths from the main analysis script to SCRIPT")
    #p.add_argument('--omit', default="<>", metavar="<>",
    #            help=
    #    "Character sequence in TAB which indicates a certain\n" +
    #    "variable shall not be set")
    # This is disabled because the output needs to be executable per line
    # in parallel
    #p.add_argument('--no-variable-checks', action='store_true', default=False,
    #                help=
    #    "Do not print shell code to check for conflicting\n" +
    #    "environment variables")

    return p.parse_args()

# Return a string to use to start a program, setting environment variables 
# in advance
def program(program, **variables):
    # Generate string "var1=a var2=b ..."
    variableString = ["{}={}".format(shlex.quote(varname),
                                     shlex.quote(varval))
                       for varname,varval 
                       in variables.items()]

    variableString = " ".join(variableString)

    return variableString + " " + shlex.quote(program)


def main(argv):
    args = parseArguments()

    # Disabled: Can introduce sublte bugs into the generated script because
    # it can not be checked automatically that a variable omitted via
    # this function is not set as an environment variable at calling time.
    # ---
    # Write command line arguments into variables
    # null_val=args.omit

    # Disable because output needs to be executable per line in parallel
    #print_variable_checks = not args.no_variable_checks
    print_variable_checks = False

    # Read table lines
    with open(args.TAB,"rt") as fd:
        dr = csv.DictReader(fd, delimiter='\t')
        lines = [line for line in dr]

    # Make dictionary of constants
    consts = {name:val for name,val in args.const}

    # Attention: these names are unquoted (use shlex.quote before 
    # using in shell calls)
    variableNames = lines[0].keys() if lines else []
    constantNames = consts.keys()
    allNames = list(variableNames) + list(constantNames)
    dupNames = set(e for e in allNames if allNames.count(e) > 1)
    if(len(dupNames) > 0):
        raise ValueError("Duplicate variable names: "+", ".join(dupNames))

    # Check if any constant names contain illegal characters
    illegalConsts = \
            [e for e,n in enumerate(constantNames, start = 1)
             if not re.match("^[a-zA-Z_]+[a-zA-Z0-9_]*$", n)]
    # Check if any variable names contain illegal characters
    illegalVariables = \
            [e for e,n in enumerate(variableNames, start = 1)
             if not re.match("^[a-zA-Z_]+[a-zA-Z0-9_]*$", n)]
    if illegalVariables or illegalConsts: 
        l = len(illegalVariables) if illegalVariables else len(illegalConsts)
        raise ValueError(("{}{} {}: Illegal name: Names must "+ \
            "be alphanumerical or underscores and must not start with "+\
            "a number.").format(
                "Variable" if illegalVariables else "Constant",
                "s" if l > 1 else "",
                 ", ".join(str(x) for x in (
                          illegalVariables if illegalVariables 
                          else illegalConsts))))

    surroundingCode = VariableChecks(variableNames) \
                      if print_variable_checks \
                      else EmptyCM()

    with surroundingCode:
        # Print out a line for each input row, first setting
        # variables, then executing the script.
        # A subshell is used to prevent the scripts from influencing
        # each other
        for row in lines:
            row.update(consts)
            print(program(args.SCRIPT, **row))


class VariableChecks:
    "Context Manager which prints variable checks"

    def __init__(self,variableNames,outputFile=sys.stdout):
        self.variableNames = variableNames
        self.outputFile = outputFile

    def _print(self,string): print(string,file=self.outputFile)
    def _printList(self,l): self._print("\n".join(l))

    def __enter__(self):
        """Return a series of shell commands to throw an error if any of 
        the variables specified in `variableNames` are set (sic!)"""

        # This returns code for the shell 'sh'
        if self.variableNames: 
            # A function which display an error message
            commands = [
            '# Assert that none of the variables is already set',
            '_varisset="";',
            'function _varisseterror(){',
            '  echo "Environment variable(s) $1 need(s) to be unset '+ 
                     'but is set" >&1 ',
            '}']
            for v in self.variableNames:
                v = shlex.quote(v)
                # Code which writes "v" to _varisset if variable v is set
                commands.append((
                    'if [ ! -z ${{{varname}+isset}} ]; '+
                    'then _varisset="${{_varisset}}{varname} "; '+
                    'fi')
                    .format(varname=v))

            # Code which displays an error if any of the checked variables 
            # was found to be set
            commands.extend([
                'if [ ! -z "${_varisset}" ]; then _varisseterror "${_varisset}"',
                'else',
                '',
                '# Section with calls to input script starts here'])

            # Print all the code
            self._printList(commands)


    def __exit__(self,type,value,traceback):
        # Close the if-else structure from __enter__
        if self.variableNames:
            self._printList(['','fi'])

class EmptyCM:
    def __enter__(self): pass
    def __exit__(self,type,value,traceback):  pass


if __name__ == "__main__": main(sys.argv)
