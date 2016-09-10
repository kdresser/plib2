# Copyright 2011, 2015 by J Kelly Dresser.  All rights reserved.

#> !P2! or !P3!

#
## A class for screen writing.
##     ScreenWriter class.
##     For incremental and same-line writing.
##     All output goes to sys.__stdout_, evading any stdout capture.
##     Thread-safe (serialized), though this is unlikely to look good in reality.
#

import sys, time, threading, string
P3 = (sys.version_info[0] == 3)
P2 = not P3

class ScreenWriter():

    def __init__(self):
        self.LOCK = threading.Lock()
        self.VSCRNLL = 0                        # !V!  visible line length (ignores trailing spaces)
        self.SCRNLL = 0                         # !L!  line length including trailing spaces
                                                # !!! Check: all this may be unnecessary!

    def cr(self, s, rstrip=False, lock=True):
        """Write to current line, followed by a <cr>."""
        # Write to current line, followed by a carriage return.
        # Don't embed control chars.
        # S is optionally rstrip()'d.
        # Nulls ignored.
        # Pads to VSCRNLL.
        # Write blanks to clear the writing area.
        if lock:
            self.LOCK.acquire()
        try:
            if rstrip:
                s = s.rstrip()
            s = self._noctls(s)
            minw = self.VSCRNLL                                     # !V!
            s = s.ljust(minw)
            sys.__stdout__.write(s + '\r')
            sys.__stdout__.flush()
            self.VSCRNLL = len(s.rstrip())                          # !V!
            self.SCRNLL = self.VSCRNLL                              # !L! !V!
        finally:
            if lock:
                self.LOCK.release()

    def ln(self, s, lock=True):
        if lock:
            self.LOCK.acquire()
        try:
            """Write to current line, followed by a <nl>."""
            # Write to current line, followed by a newline.
            # s is rstrip()'d.
            # Don't use line control chars.
            # Nulls ignored.
            s = s.rstrip()
            s = s.ljust(self.VSCRNLL)                               # !V!  # ???  # In case cr did last screen writing.
            sys.__stdout__.write(s + '\n')
            sys.__stdout__.flush()
            self.SCRNLL = 0                                         # !L!
            self.VSCRNLL = 0                                        # !V!
        finally:
            if lock:
                self.LOCK.release()

    def iw(self, s, ctl=False, rstrip=False, lock=True):       # 130808: Changed default to no strip.
        """Simple incremental write to current line."""
        # A simple-minded incremental write to current line.
        # S is optionally rstrip()'d.
        # Warning:  !!! Usually ignores control chars!
        if lock:
            self.LOCK.acquire()
        try:
            if rstrip:
                s = s.rstrip()
            if not ctl:
                s = self._noctls(s)
            if not s:
                return
            if P3 and isinstance(s, bytes):
                s = s.decode(encoding='utf-8')
            sys.__stdout__.write(s)
            sys.__stdout__.flush()
            self.SCRNLL += len(s)                                   # !L!
            self.VSCRNLL = self.SCRNLL                              # !V! !L!
        finally:
            if lock:
                self.LOCK.release()

    def blank(self, lock=True):
        """Blanks any visible line."""
        # Blank any visible line. Zeros line lengths.
        if lock:
            self.LOCK.acquire()
        try:
            self.iw('\r', ctl=True, lock=False) 
            self.cr('', lock=False)
        finally:
            if lock:
                self.LOCK.release()

    def nlln(self, s, lock=True):
        """.nl + .ln"""
        # Combo offer.
        # Nulls ignored.
        if lock:
            self.LOCK.acquire()
        try:
            s = s.rstrip()
            s = self._noctls(s)
            self.nl(lock=False)
            self.ln(s, lock=False)
        finally:
            if lock:
                self.LOCK.release()

    def nl(self, vblank=False, lock=True):
        """Be at a newline."""
        if lock:
            self.LOCK.acquire()
        try:
            if self.VSCRNLL > 0:                                    # !V!
                if vblank:
                    self.cr('', lock=False)
                else:
                    self.VSCRNLL = 0                                # !V!
                    self.ln('', lock=False)
                return
            if self.SCRNLL > 0:                                     # !L!
                self.ln('', lock=False)
        finally:
            if lock:
                self.LOCK.release()

    def wait(self, s, pfx='-- ', pulse=1.0, lock=True, quiet=False):    # 151211: Added quiet=False.
        """Wait, with a countdown.  Returns False if <ctrl>-c interruped."""
        if lock:
            self.LOCK.acquire()
        try:
            try:    s = float(s)
            except: s = 0
            if pfx is None:
                pfx = ''
            if s > 0:
                self.nl(lock=False)
                try:
                    if pulse >= 1:  self.cr('%swait %3d sec' % (pfx, s), lock=False)
                    else:           self.cr('%swait %5.1f sec' % (pfx, s), lock=False)
                    while s > 0.0:
                        if s > pulse:
                            time.sleep(pulse)
                            s -= pulse
                        else:
                            time.sleep(s)
                            break
                        if pulse >= 1:  self.cr('%swait %3d sec' % (pfx, s), lock=False)
                        else:           self.cr('%swait %5.1f sec' % (pfx, s), lock=False)
                    self.cr(' ', lock=False)
                    return True
                except:
                    self.ln('%swait interrupted' % pfx, lock=False)
                    if quiet:
                        return False
                    else:
                        raise
        finally:
            if lock:
                self.LOCK.release()

    def sleep(self, s):
        """Silent sleep.  Just a call to time.sleep()."""
        # Lock?
        try:    s = float(s)
        except: s = 0
        if s > 0.0:
            time.sleep(s)

    def _noctls(self, s):
        if P3:
            if s.isprintable():
                return s
            t = ''
            for c in s:
                if c.isprintable():
                    t += c
                else:
                    t += '?'
            return t
        else:
            t = ''
            for c in s:
                if c in string.printable:
                    t += c
                else:
                    t += '?'
            return t
