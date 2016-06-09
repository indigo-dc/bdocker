#!/usr/bin/python

import resource
import os
import signal


RUNNING_DIR = "/tmp"
LOCK_FILE = "pydaemond.lock"
LOG_FILE = "pydaemond.log"
MAX_FD = 1024


def log_writer(message,filename=LOG_FILE):
    fd = open(filename,"a")
    fd.write(message)


def signal_handler(sig,frame):
    if sig == signal.SIGHUP:
        log_writer("Caught SIGHUP (Hangup Signal)\n")
        return

    if sig == signal.SIGTERM:
        log_writer("Caught SIGTERM (Terminate Signal)\n")
        os._exit(0)


def create_daemon():
    print "Inside Daemonize"
    # Already Daemon Process

    if(os.getppid() == 1):
        return
    try:
        pid = os.fork()
    except OSError, e:
        raise Exception,"Exception occured %s [%d]"%(e.strerror,e.errno)
        os._exit(0)
    if pid == 0:
        # First child

        os.setsid()
        try:
            pid = os.fork()
        except OSError, e:
            raise Exception,"Exception occured %s [%d]"%(e.strerror,e.errno)
            os._exit(0)
        if pid == 0:
            # Second child

            # Change the running directory
            os.chdir(RUNNING_DIR)
            # Now file creation permission will be 0777 & ~027 = 0750
            os.umask(027)
        else:
            # Parent of Second Child (First child) exits
            os._exit(0)
    else:

        os.wait()
        os._exit(0) # Parent of First Child exits
    # Second child continues as Daemon
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if maxfd == resource.RLIM_INFINITY:
        maxfd = MAX_FD
    # Close all open files (assuming they are open) 
    for fd in range(0,maxfd):
        try:

           os.close(fd)
        except OSError:
            # Not an error file isn't open :)
            pass
     # STDIN to /dev/null
    fd = os.open(os.devnull,os.O_RDWR)
    os.dup(fd) # STDOUT

    os.dup(fd) # STDERR
    lfp = os.open(LOCK_FILE,os.O_RDWR|os.O_CREAT)
    os.write(lfp,str(os.getpid())+"\n")
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)
    signal.signal(signal.SIGTSTP,signal.SIG_IGN)
    signal.signal(signal.SIGTTOU,signal.SIG_IGN)
    signal.signal(signal.SIGTTIN,signal.SIG_IGN)
    signal.signal(signal.SIGHUP,signal_handler)
    signal.signal(signal.SIGTERM,signal_handler)
    return 0
# if __name__ == "__main__":
#     i = daemonize()
#     while True:
#         time.sleep(1)


def create_daemon_dependent():
    try:
        pid = os.fork()
        if pid > 0:
            # Exit parent process
            os._exit(0)
    except OSError, e:
        print "Create fork file"

    # Configure the child processes environment
    os.chdir("/")
    os.setsid()
    os.umask(0)

    return pid