---
title:
  - Glossary
---

Some terms are explained here, which are used in the rest of the
manual and may have a special meaning:

~table: A text table is the most widely used data format in this
project. It is a simple text file, where the columns are separated by
a special character. Usually this is a tabulator (tab) character, but
sometimes space-separated tables are also used. 

~FASTA record: A FASTA record is a block in a fasta file which is
delimited by two > signs. It consists of the following parts:
 
 1)  The header line: >.................(line end). 
    a) The FASTA identifier, which is the first 'word' of the header
       line. E.g. in a header line 
       
    >A1 Felis catus genome ID:012345...
        
        the FASTA identifier is 'A1'.
    b) The FASTA record description: All the text between identifier
       and line end. 
 2) Biological sequence data, IUPAC one-character-code. Should not be wider 
    than 80 characters and may contain whitespace.
    E.g. nucleotides: ACCTCTCTACCT...

~FASTA identifier: -> FASTA record

~FASTA description: -> FASTA record

~file offset: This is the
distance in bytes from the beginning of a file. The first character of
a file has the offset 0.

~offset: -> file offset

~i-based index: An index is i-based if it starts counting with
number i. For example, the mapping position (pos) field of a SAM file 
is a 1-based index. If the position 1 is written there, the read maps
to the first base of the genome. Conversely, if the index were
0-based,
the first base of the genome would be referenced with the number 0.

~0-based: -> i-based index

~1-based: -> i-based index

~standard input: Many commands expect input on this stream. Input can
be provided either by typing into the console, by using the < operator
to provide input from a file or by the | operator, which forwards the
content on standard output of a previous command to standard input of
this command. Refer to the "Redirection" section of your shell for
more information.

~standard output: All output a command writes is by default redirected
to the standard output or standard error streams. Per convention,
standard output is used for the results of the program, whereas
standard error is used for status and error messages. Content on
standard output can be written in a file by using the > operator or
redirected to standard input of another command by using the |
operator. Standard error output can be redirected to a file using the
2> operator. Consult the "Redirection" section of your shell for more
information. 

~standard error: -> standard output

~command line argument: a value which is written on the command line
behind the name of the program which shall be invoked. They are
forwarded to the program and influence it. The valid parameters of a
program are described in the program's manual. (often accessible via
the `--help` command line argument. 

~command line switch: -> command line argument



