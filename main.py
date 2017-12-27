#!/usr/bin/env python3

import sys
from argparse import ArgumentParser
import os
import termios
import re


RootDir = "."
Sources = []
Blacklist = []
DownloadOnly = False
Args = None
reloadHandlers = []


def print_stdin_help():
    print("Console control:")
    print("  <r>:  reload lists (sources, blacklist)")
    print("  <q>:  quit")


def prepare_stdin():
    fd = sys.stdin.fileno()

    if not os.isatty(fd):
        print("Not a tty. No stdin control.")
        return

    old = termios.tcgetattr(fd)
    new = termios.tcgetattr(fd)
    new[3] = new[3] & ~termios.ICANON & ~termios.ECHO
    # http://www.unixguide.net/unix/programming/3.6.2.shtml
    new[6][termios.VMIN] = 0
    new[6][termios.VTIME] = 1  # timeout

    termios.tcsetattr(fd, termios.TCSANOW, new)
    termios.tcsendbreak(fd, 0)

    import atexit
    atexit.register(lambda: termios.tcsetattr(fd, termios.TCSANOW, old))

    print_stdin_help()


def stdin_get_char():
    fd = sys.stdin.fileno()
    ch = os.read(fd, 7)
    return ch


def stdin_handler_loop():
    while True:
        ch = stdin_get_char()
        if not ch:
            continue
        elif ch == b"q":
            print("Exit.")
            import Threading
            from Action import IssueSystemExit
            Threading.do_in_main_thread(IssueSystemExit(), wait=False)
            return
        elif ch == b"r":
            print("Reload lists.")
            setup_lists()
            for handler in reloadHandlers:
                handler()
        else:
            print("Unknown key command: %r" % ch)
            print_stdin_help()


def start_stdin_handler_loop():
    prepare_stdin()

    from threading import Thread
    t = Thread(target=stdin_handler_loop, name="stdin control")
    t.daemon = True
    t.start()


def setup_lists():
    main.Sources = open(RootDir + "/sources.txt").read().splitlines()
    if os.path.exists(RootDir + "/blacklist.txt"):
        blacklist = open(RootDir + "/blacklist.txt").read().splitlines()
        main.Blacklist = [re.compile(bad_pattern) for bad_pattern in blacklist]
    else:
        main.Blacklist = []


def allowed_by_blacklist(entry):
    for bad_pattern_re in main.Blacklist:
        if bad_pattern_re.match(entry):
            return False
    return True


def setup(*raw_arg_list):
    print("RandomFtpGrabber startup.")

    import better_exchook
    better_exchook.install()
    import Logging
    better_exchook.output = Logging.log

    argParser = ArgumentParser()
    argParser.add_argument("--dir", default=os.getcwd())
    argParser.add_argument("--numWorkers", type=int)
    argParser.add_argument("--shell", action="store_true")
    argParser.add_argument("--downloadRemaining", action="store_true")
    global Args
    Args = argParser.parse_args(raw_arg_list)

    if sys.version_info.major != 3:
        Logging.log("Warning: This code was only tested with Python3.")

    start_stdin_handler_loop()

    import main
    main.RootDir = Args.dir
    Logging.log("root dir: %s" % RootDir)

    main.DownloadOnly = Args.downloadRemaining
    if not main.DownloadOnly:
        setup_lists()

    import TaskSystem # important to be initially imported in the main thread
    if Args.numWorkers:
        TaskSystem.kNumWorkers = Args.numWorkers
    if Args.shell:
        TaskSystem.kNumWorkers = 0
    TaskSystem.setup()


def main_entry():
    import TaskSystem
    import Logging
    try:
        TaskSystem.main_loop()
    except KeyboardInterrupt:
        Logging.log("KeyboardInterrupt")


# Has the effect that this module is know as 'main' and not just '__main__'.
import main


if __name__ == "main":
    setup(*sys.argv[1:])

elif __name__ == "__main__":
    if main.Args.shell:
        import better_exchook
        better_exchook.debug_shell(globals(), globals())
        sys.exit()
    main.main_entry()

