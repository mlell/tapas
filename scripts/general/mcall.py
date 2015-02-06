#!/usr/bin/env python
import argparse
# Local module
import subprocess as sp
import traceback
import os.path as path
import os
import errno
import threading as t
import sys
import datetime
from time import time,gmtime,sleep
import signal
import queue as qu



helpText="""\
Evaluate a list of calls, in parallel.

The calls are expected, separated by newline, on the standard input
or, if specified, an input file.

Note that the command is evaluated via a shell, therefore shell-specific
features like piping, output redirection etc. can be used.

Thus, using output redirection (... > OUTPUTFILE ) is the
way to specify output files if the executed program prints on 
standard output. The shell features available 
depend on which shell python uses. On linux, this is /bin/sh.

"""
# ======= Constants ===============================

SHELL = "/bin/sh"

# ======= Global variables ========================

# Whether Ctrl-C has been received and spawning new threads should
# be stopped
sigint = False

# Prevent two threads from logging at the same time. See log function
log_lock=t.Lock()

# Controls maximum number of threads
# Initialized in main()
#semaphore = None 

# List of started threads. Threads are added when they 
# are started and the main thread doesn't exit before 
# all of these threads have ended.
subthread_list = []
open_files = []

job_queue = qu.Queue()
msg_queue = qu.Queue()
err_queue = qu.Queue()

class EOI:
    pass
END_OF_INPUT = EOI()

# ====== Main program logic ===========================

def main():
    global status, sigint
    try:
        # Invoke handle_sigint if Ctrl-C is pressed
        signal.signal(signal.SIGINT, handle_sigint)

        # Set up argument parser
        args = create_argument_parser().parse_args()

        # Initialize status object
        status = Status()
        if(args.status):
            def statusDaemon():
                while True:
                    sys.stderr.write(status.status())
                    sys.stderr.write("\r")
                    sys.stderr.flush()
                    sleep(1)

            global statusTimer
            statusTimer = t.Thread(target=statusDaemon, daemon=True)
            statusTimer.start()

        # Register time logger if requested
        if args.log_time[0]:
            if args.log_time[0] == "-":
                timelog_file = sys.stdout
            else:
                timelog_file = open(args.log_time[0],"wt")
                open_files.append(timelog_file)

            def logTime(jobid, event):
                if event == "complete":
                    deltatime = status.endTimes[jobid] - status.startTimes[jobid]
                    timelog_file.write("\t".join([str(i) for i in [
                        jobid, status.exitCodes[jobid], deltatime]]))
                    timelog_file.write("\n")
                    timelog_file.flush()

            status.listeners.append(logTime)

        # Register verbose logger if requested
        if args.verbose:
            def verbose_log(jobid,event):
                if event == "queued" or event == "started":
                    log("Job {} {}".format(jobid,event))
                elif event == "complete":
                    deltatime = status.endTimes[jobid] \
                              - status.startTimes[jobid]
                    log(("Job {} finished. Exit code: {}. "+
                            "Running time {:02.0f}:{:02.0f}:{:04.2f}").
                        format(jobid, status.exitCodes[jobid],
                            *(human_time(deltatime))
                            ))

            status.listeners.append(verbose_log)
                    
        # Determine maximum count of threads
        nthreads = int(args.threads[0])
        record_sep = args.sep[0] if not args.sep0 else "\0"

        workers = []
        for i in range(0,nthreads):
            w = t.Thread(target= workerThread,
                    kwargs= dict(worker_id= i,jobQueue= job_queue))
            workers.append(w)
            w.start()

        # Read calls from STDIN or input file, if specified
        if args.cmdfile == "-":
            input_stream = sys.stdin
        else:
            input_stream = open(args.cmdfile[0],"rt")
            open_files.append(input_stream)


        jobid=0
        if record_sep:
            input_generator = line_delimited_records(input_stream,record_sep)
        else:
            input_generator = input_stream

        try:
            while True:
                #input = sys.stdin.readline().rstrip()
                input = next(input_generator)
                if input: 
                    execute_call(jobid,input)
                else: log("Job {} has no commands.".format(i))
                jobid += 1
        except StopIteration:
            pass


        for w in workers:
            queue_end_of_input(jobid)
            jobid += 1

        job_queue.join()

        if sigint: raise KeyboardInterrupt


    except KeyboardInterrupt as e:
        # Ctrl-C pressed
        print("Main: KeyboardInterrupt",file=sys.stderr)
        return -2
    except Exception as e:
        # Error in the script occurred
        sigint = True

        if args.debug :
            traceback.print_exc()
        else:
            print(e,file=sys.stderr)
        return 1
    finally:
        try:
            if(args.status):
                print(status.status(), file=sys.stderr)
        except:
            pass

        for f in open_files:
            f.close()

    return 0

def line_delimited_records(stream,sep,join="\n"):
    """Reads in the input stream linewise and chunks it into records
    `sep` determines the end of a record. `join` specify the character to
    separate the lines of one record. Using the newline char for `sep`
    equals standard line-by-line records"""

    # End of input has been reached: return last record and exit
    stop = False

    def getRecord(stream,sep,join="\n"):
        nonlocal stop
        output=[]
        while True:
            line = next(stream,None)
            if not line:
                stop = True
            if (not line) or (line.strip() == sep) : 
                return(join.join(output))
            output.append(line)

    while not stop:
        yield getRecord(stream,sep,join)

# def execute_call(call_index,call):
#         # Exit if Ctrl-C has been received
#         if sigint: sys.exit(-2)
#         # Set up a new Thread
#         T = SemaphoreSubprocessThread()
#         T.init( call , semaphore, subprocess_id=call_index)
#         # Register the thread as subthread
#         subthread_list.append(T)
#         # Launch Thread executing current command
#         T.start()

def execute_call(call_index,call):
    global job_queue, status
    job = Job(call_index,call)
    job_queue.put(job)
    status.reportQueued(jobid=call_index)

def queue_end_of_input(call_index):
    global job_queue
    job = Job(call_index,END_OF_INPUT)
    job_queue.put(job)


# ======== Subthread class ============================
class Job:
    def __init__(self,id,cmdline):
        self.id = id
        self.cmdline = cmdline
    def __repr__(self):
        return "Job {:d}: {}".format(self.id,self.cmdline)

def workerThread(worker_id,jobQueue):
    global status,sigint
    job = None
    returncode = None
    while True:
        try:
            # Wait for job and check whether the program is interrupted regulary
            while not job:
                if(sigint): raise KeyboardInterrupt
                try:
                    job = jobQueue.get(block=True,timeout=1)
                except qu.Empty:
                    pass

            if job.cmdline is END_OF_INPUT: 
                sys.exit(0)

            status.reportStarted(jobid=job.id)

            # Call subprocess
            returncode = None
            process = sp.Popen(SHELL, stdin=sp.PIPE, stdout=sp.PIPE,
                                stderr=sp.PIPE)
            out,err = process.communicate(input=job.cmdline.encode())

            if out: print(out.decode(),end="")
            if err: print(err.decode(),end="",file=sys.stderr)

            returncode = process.returncode


        except KeyboardInterrupt:
            sys.exit(-2)
        finally:
            if job:
                jobQueue.task_done()
            if job and (job.cmdline is not END_OF_INPUT):
                status.reportComplete(jobid=job.id, code=returncode)
            job = None




# ======== Utility functions ==========================

def create_argument_parser():
    p = argparse.ArgumentParser(description=helpText
               , formatter_class=argparse.RawDescriptionHelpFormatter)

    p.add_argument( "--cmdfile","-c", nargs=1, help=\
    """A plain text file containing the command template and a table of 
    parameters, as described above""", default="-")

    p.add_argument( "--debug", action="store_true", help=\
    "Print the stack trace when an error occurs" )

    p.add_argument( "--threads", "-t", nargs=1
                  , default=[1], type=int, help=\
    """Number of subprocesses that should be started simultaneously.
    Note that subprocesses can execute parallel calls on their own.""" )
    p.add_argument( "--status", action="store_true", help=\
    """Prints a status line at STDERR indicating how many processes have been 
    executed.""" )

    p.add_argument( "--sep", "-s", nargs=1, default=[""], type=str, help=\
    """Separator which indicates the beginning of a new record. Each record
    is executed by an independent job. The default value 
    (newline character,\\n) equals line-per-line execution""" )

    p.add_argument( "--sep0", "-0", action="store_true", help=\
    """Use the null character (\\0) as a command separator instead of
    the newline character. Can't be used together with --sep.""" )

    p.add_argument( "--log-time", nargs=1 , default=[None], type=str, help=\
    """Write a log to the specified file. A value of - writes to standard
    output.""" )

    p.add_argument( "--verbose", action="store_true", 
            help="""Print more information during program run.""")
    return p

# Set a global flag that program should be aborted.
def handle_sigint(signum, frame):
    global sigint
    sigint = True
    delete_all_jobs()

def delete_all_jobs():
    global job_queue
    try:
        while(True):
            job_queue.get_nowait()
            job_queue.task_done()
    except qu.Empty:
        pass

def log(msg):
    sys.stdout.write("{}: {}\n".format(
        datetime.datetime.now().strftime("%Y-%M-%d %H:%M:%S"),
        msg))
    sys.stdout.flush()

def human_time(secs):
    m,s = divmod(secs,60)
    h,m = divmod(m,60)
    s = round(s,2)
    return (h,m,s)


# ======= Status object ===============================

class Status:
    def __init__(self):
        self.lock = t.Lock()
        self.queued = 0
        self.started = 0
        self.complete = 0
        self.failed = 0
        self.listeners = []
        self.startTimes = {}
        self.endTimes = {}
        self.exitCodes = {}

    def status(self):
        return "{} queued, {} started, {} complete, {} failed."\
            .format(self.queued,self.started,self.complete,self.failed)

    def reportQueued(self, jobid):
        with self.lock:
            self.queued += 1
            self.statusChanged(jobid,"queued")

    def reportStarted(self, jobid):
        with self.lock:
            self.queued -= 1
            self.started += 1
            self.startTimes[jobid] = time()
            self.statusChanged(jobid,"started")

    def reportComplete(self, jobid, code):
        with self.lock:
            self.started -= 1
            if code == 0: 
                self.complete += 1
            else:
                self.failed += 1
            self.endTimes[jobid] = time()
            self.exitCodes[jobid] = code
            self.statusChanged(jobid, "complete")

    def statusChanged(self,jobid,event):
        for l in self.listeners:
            l(jobid,event)




# ======= Main function launcher ======================

if __name__ == "__main__": 
    return_code = main()
    sys.exit(return_code)

