# Copyright 2011, 2015 by J Kelly Dresser.  All rights reserved.

#> !P2! !P3!

###
### l_simple_logger:  A simple logger class.
###     Uses Python logging level numbers and nomenclature.
###     Output can go to: 1) a screen_writer and/or 2) an open log_file.
###     Thread-safe unless caller overrides lock=True parameters.
###     Uses a ScreenWriter object for screen logging (optional).
###

import os, sys, threading

P3 = (sys.version_info[0] == 3)
P2 = not P3

if P3:
    from io import IOBase
    FILE = IOBase
else:
    FILE = file

DEBUG = False

class SimpleLogger():

    def __init__(self, screen_writer=None, log_file=None):
        """A simple logger to either screen_writer and/or open log_file."""
        # Locks for everything that moves; used during debugging/testing.
        self.MLLOCK = threading.Lock()  # _any() 
        self.LGLOCK = threading.Lock()  # _log() 
        self.SWLOCK = threading.Lock()  # screen_writer 
        self.LFLOCK = threading.Lock()  # log_file
        # Objects to log to.
        self.SW = screen_writer
        self.LF = log_file
        # Instrumentation for lock debugging
        self.MLLK = None                
        self.LGLK = None                
        self.SWLK = None                
        self.LFLK = None                

    def _MLLOCK(self, ar):
        if ar[0] == '-':
            if self.MLLK != ar[1:]:
                z = self.MLLK
                1/1
            self.MLLOCK.release()
            self.MLLK = None
            return
        assert ar[0] == '+'
        if self.MLLOCK.acquire(timeout=1):
            self.MLLK = ar[1:]
            return
        z = self.MLLK
        1/1

    def _LGLOCK(self, ar):
        if ar[0] == '-':
            if self.LGLK != ar[1:]:
                z = self.LGLK
                1/1
            self.LGLOCK.release()
            self.LGLK = None
            return
        assert ar[0] == '+'
        if self.LGLOCK.acquire(timeout=1):
            self.LGLK = ar[1:]
            return
        z = self.LGLK
        1/1

    def _MSLOCK(self, ar):
        if ar[0] == '-':
            if self.SWLK != ar[1:]:
                z = self.SWLK
                1/1
            self.SWLOCK.release()
            self.SWLK = None
            return
        assert ar[0] == '+'
        if self.SWLOCK.acquire(timeout=1):
            self.SWLK = ar[1:]
            return
        z = self.SWLK
        1/1

    def _LFLOCK(self, ar):
        if ar[0] == '-':
            if self.LFLK != ar[1:]:
                z = self.LFLK
                1/1
            self.LFLOCK.release()
            self.LFLK = None
            return
        assert ar[0] == '+'
        if self.LFLOCK.acquire(timeout=1):
            self.LFLK = ar[1:]
            return
        z = self.LFLK
        1/1

    def _prefixed(self, s):
        """   # -> True if s is already prefixed.  Mostly used internally."""
        return s[:3] in ('-- ', '>> ', '** ', '## ', '~~ ', '.. ', '== ', '^^ ', '__ ', '!! ')

    def _log(self, s):
        """Log s asis. Mostly used internally."""
        # Null s ignored.
        if DEBUG:
            self._LGLOCK('+0')
        else:
            self.LGLOCK.acquire()
        try:
            if not s:   return
            s = str(s).rstrip()
            if s:
                if self.SW:
                    if DEBUG:
                        self._MSLOCK('+0')
                    else:
                        self.SWLOCK.acquire()
                    try:
                        self.SW.nlln(s)
                    finally:
                        if DEBUG:
                            self._MSLOCK('-0')
                        else:
                            self.SWLOCK.release()
                if self.LF:
                    if DEBUG:
                        self._LFLOCK('+0')
                    else:
                        self.LFLOCK.acquire()
                    try:
                        self.LF.write(s + '\n')
                        self.LF.flush()
                        os.fsync(self.LF.fileno())
                    except:
                        try:    self.LF.close()
                        except: pass
                        self.LF = None
                    finally:
                        if DEBUG:
                            self._LFLOCK('-0')
                        else:
                            self.LFLOCK.release()
        finally:
            if DEBUG:
                self._LGLOCK('-0')
            else:
                self.LGLOCK.release()

    def _any(self, pfx, s, lock=True):
        """Log with given pfx and s.  Mostly used internally."""
        # Null s are processed (a pfx is prepended).
        if lock:
            if DEBUG:
                self._MLLOCK('+1')
            else:
                self.MLLOCK.acquire()
        try:
            s = str(s).rstrip()
            if '\n' in s:
                for l in s.split('\n'):
                    self._any(pfx, l, lock=False)   # !!!
            else:
                if self._prefixed(s):  self._log(s)
                else:                  self._log(pfx + s)
        finally:
            if lock:
                if DEBUG:
                    self._MLLOCK('-1')
                else:
                    self.MLLOCK.release()

    def null(self, s='', lock=True):        # [0]
        """Level 0: null '__ ' prefix."""
        pfx = '__ '
        self._any(pfx, s, lock=lock)

    def debug(self, s='', lock=True):       # [1]
        """Level 1: debug '.. ' prefix."""
        pfx = '.. '
        self._any(pfx, s, lock=lock)

    def info(self, s='', lock=True):        # [2]
        """Level 2: info '-- ' prefix."""
        pfx = '-- '
        self._any(pfx, s, lock=lock)

    def warning(self, s='', lock=True):     # [3]
        """Level 3: warning '>> ' prefix."""
        pfx = '>> '
        self._any(pfx, s, lock=lock)

    def error(self, s='', lock=True):       # [4]
        """Level 0: error '** ' prefix."""
        pfx = '** '
        self._any(pfx, s, lock=lock)

    def critical(self, s='', lock=True):    # [5]
        """Level 5: critical '!! ' prefix."""
        pfx = '!! '
        self._any(pfx, s, lock=lock)

    def extra(self, s='', lock=True):       # Extra
        """ '~~ ' prefix."""
        pfx = '~~ '
        self._any(pfx, s, lock=lock)