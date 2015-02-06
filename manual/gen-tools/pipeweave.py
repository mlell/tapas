#!/usr/bin/env python3

#import docopt
import sys
import subprocess as sp
import threading as th
import io
import re

ENCODING = 'utf-8'
#PROMPT = ">> "
PROMPT = "bash-4.3$ "
probeCommand = "echo 'pipeweave-ready'"
#probeCommand = r"disp(sprintf('\npipeweave-ready'))"
probeResponse = "pipeweave-ready"

exitCommand="exit"

outl_src_begin="```{.sh}"
outl_src_end="```"
outl_out_begin="```{.output}"
outl_out_end="```"

def status(text):
    print(text,file=sys.stderr)


def main(argv):

    mode = "subprocess"
    #mode = "pipe"
    verbose = False
    try:
        if(mode == "subprocess"):
            status("start command")
            childp = sp.Popen(argv[1], shell=True, stdin=sp.PIPE, 
                    stdout=sp.PIPE, bufsize=0)
            status("...started")

            send_int = io.TextIOWrapper(childp.stdin,encoding=ENCODING)
            recv_int = io.TextIOWrapper(childp.stdout,encoding=ENCODING)
        else:
            
            recv_int = open(argv[1],"rt")
            send_int = open(argv[2],"wt")

        fd_text = sys.stdin
        fd_print = sys.stdout

        chunks = []
        state = "text"

        sendProbe(send_int)

        welcomemsg = readToPrompt(recv_int)
        #print(welcomemsg)

        chunk_i=1
        while True:
            line = fd_text.readline()
            if not line: break

            if state == "text":
                if line.rstrip() == "```{.sh}":
                    state = "code"
                else:
                    fd_print.write(line)

            if state == "code":
                codechunk = readCodeChunk(fd_text)
                printCodeSource(codechunk, fd_print)
                print("Chunk #{}".format(chunk_i), file=sys.stderr)
                if verbose:
                    for line in codechunk:
                        sys.stderr.write("    "+line)

                chunk_i += 1
                for line in codechunk:
                    send_int.write(line)

                sendProbe(send_int)

                response = readToPrompt(recv_int)
                response = filterInterpreterOutput(response)

                # Prevent text feedback from commands send to the
                # interpreter if the interpreter sends its input
                # to standard output.
                printCodeOutput(response, fd_print)

                state = "text"

        print(exitCommand, file=send_int)
        send_int.flush()
    finally:
        try:
            send_int.close()
            recv_int.close()
        except IOError:
            pass



def printCodeSource(lines, print_stream):
    print(outl_src_begin)
    for l in lines: print(l.rstrip(), file=print_stream)
    print(outl_src_end)

def printCodeOutput(lines, print_stream):
    print(outl_out_begin)
    for l in lines: print(l.rstrip(), file=print_stream)
    print(outl_out_end)

def filterInterpreterOutput(lines):
    output = []
    for l in lines:
        while l.startswith(PROMPT):
            l = l[len(PROMPT):]
        output.append(l)

    return output



def readCodeChunk(stream):
    chunk = []
    while True:
        l = stream.readline()
        if not l or l.rstrip() == "```":
            return chunk
        chunk.append(l)

def sendProbe(send_stream):
    print(probeCommand,file=send_stream)
    send_stream.flush()

def readToPrompt(stream):
    output = []
    while True:
        line = stream.readline()
        if not line or line.rstrip() == probeResponse:
            return output
        output.append(line)



# def readToPrompt(stream):
#     print("readToPrompt",file=sys.stderr)
#     output = []
#     while True:
#         sio = StringIO
#         c = stream.read(1)
#         if c: barr.append(c[0])
#         print(from_iprt(c),end="",file=sys.stderr)
# 
#         if barr[-len(PROMPT):] == PROMPT or not c:
#             ostr = from_iprt(barr[:-len(PROMPT)])
#             output.append(ostr)
# 
#         if not c: break
# 
#     return output






if __name__ == "__main__": main(sys.argv)
