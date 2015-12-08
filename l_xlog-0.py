# Copyright 2015 by J Kelly Dresser.  All rights reserved.

#
## l_xlog: Class for tx'ing to tcp/ip socket logger app "xlog".
##         A queue of messages is saved to a queue and sent frp, 
##         within a thread.  As much processing as possible is 
##         deferred to the thread.
##         Functions:
##           1. null(msg), debug(msg), info(msg), warning(msg), 
#3              error(msg), critical(msg), extra(msg) that 
##              add the appropriate el & sl.
##           2. msg2xlog(msg, el=None, sl=None) for a simple message.
##           3. d2xlog(d) for a ready-to-use dict.
##           4. j2xlog(j) for a ready-to-use json'd dict.
##         Uses XLogTxRx class which has backlogging and 
##         reconnection abilities.
#

import json, queue, threading

from l_xlogtxrx import XLogTxRx
import l_misc as _m

class XLog():
    def __init__(self, xloghost=None, xlogport=None, xlogid=None, xsubid=None, xlogel=2, xlogsl='_', screenwriter=None, txrate=0.02):
        me = 'XLog.__init__'
        self.xlog     = None        # Default no logging until host & port connected.
        self.xloghost = xloghost    # xlog server host IP.
        self.xlogport = xlogport    # xlog server port.
        # The following logid, subid, el & sl are defaults used by 
        # various message builder.
        # null .. critical, extra helper functions.
        self.xlogid   = xlogid      # Source ID.  Caller can override this.
        self.xsubid   = xsubid      # Sub    ID.  Caller can override this.
        self.xlogel   = xlogel      # Default error-level (info).
        self.xlogsl   = xlogsl      # Default sub-level   (base).
        self.sw = screenwriter      # Optional screen writer object for 
                                    # error messages (otherwise print).
        self.q = None               # Queue of messages to send.
        self.t = None               # Thread to send messages.
        self.stop = False           # External signal to stop XLog instance.
        self.stopped = False        # When stopped by self.stop.
        self.nmsgs = 0              # Number of messages sent.
        if self.xloghost and self.xlogport:
            try:
                # !TODO! TEST EXCEPTION
                self.xlog = XLogTxRx((self.xloghost, self.xlogport), txrate=txrate)
                self.q = queue.Queue(10000)     # 10^4
                self.t = threading.Thread(target=self._xlogthread)      # ??? daemon?
                self.t.start()
                if FAIL_CONNECT:
                    1/0
            except Exception as E:
                _m.beeps(10)
                errmsg = '{}: {}: {} @ {}'.format(me, 'setup failed', E, _m.tblineno())
                self._p('** ' + errmsg)
                raise Exception(errmsg)

    # Internal: _p, _xlogthread.

    def _p(self, s):
        """Print using either self.sw or system print function."""
        s = s.rstrip()
        if self.sw:
            self.sw.nlln(s)
        else:
            print(s)

    def _xlogthread(self):
        """A thread to send a FIFO queue of objects to an xlog server."""
        me = '_xlogthread'
        while not self.stop:
            try:    
                o = self.q.get(timeout=1)           # !MAGIC!  1 sec timeout.
                try:
                    if FAIL_O:
                        1/0
                    # Ready-to-use dict?
                    if   isinstance(o, dict):    
                        z = json.dumps(o)
                        if DEBPRT:
                            self._p('>> ' + z)
                        self.xlog.send(z)
                        self.nmsgs += 1
                        continue
                    # Ready-to-use json?
                    elif isinstance(o, str):    
                        z = o
                        if DEBPRT:
                            self._p('>> ' + z)
                        self.xlog.send(z)
                        self.nmsgs += 1
                        continue
                    # (id, si, msg, el, sl) tuple?
                    elif (isinstance(o, tuple) or isinstance(o, list)) and len(o) == 5:
                        id, si, msg, el, sl = o
                        if not msg:
                            continue
                        if el is None:
                            el = self.xlogel
                        if sl is None:
                            sl = self.xlogsl
                        z = json.dumps({'_id': str(id), '_si': str(si), '_el': str(el), '_sl': str(sl), '_msg': str(msg)})
                        if False and DEBPRT:
                            self._p('>> ' + z)
                        self.xlog.send(z)
                        self.nmsgs += 1
                        continue
                    else:
                        _m.beeps(3)
                        # Switch to errmsg.
                        errmsg = '{}: {}: {}'.format(me, 'unexpected object type', type(o)) 
                        self._p('** ' + errmsg)
                        z = json.dumps({'_id': self.xlogid, '_si': self.xsubid, '_el': 5, '_sl': '!', '_msg': '[' + errmsg + ']'})
                        self.xlog.send(z)
                        self.nmsgs += 1
                        continue
                    pass
                except Exception as E:
                    _m.beeps(3)
                    errmsg = '{}: {} @ {}'.format(me, E, _m.tblineno())
                    self._p('** ' + errmsg)
                    self._p('** ' + repr(o))
                    # Switch to errmsg.
                    z = json.dumps({'_id': self.xlogid, '_si': self.xsubid, '_el': 5, '_sl': '!', '_msg': '[' + errmsg + ']'})
                    self.xlog.send(z)
                    self.nmsgs += 1
                    continue
                ###---self._xlogsend(z)
            except: 
                # Queue get timeout.
                pass
        ##### not self.stop: ^^^
        self.stopped = True
    ### _xlogthread(self): ^^^

    # >>> msg2xlog, d2xlog & j2xlog.

    def msg2xlog(self, msg, el=None, sl=None):
        """Tx msg (with optional el, sl) via xlog."""
        if not msg:
            return
        # Include the logid and subid from the time of call.
        self.q.put((self.xlogid, self.xsubid, msg, el, sl), block=False)   

    def d2xlog(self, d):
        """Tx ready-to-use dict via xlog."""
        if not d:
            return
        self.q.put(d, block=False)   

    def j2xlog(self, j):
        """Tx ready-to-use json'd dict via xlog."""
        if not j:
            return
        self.q.put(j, block=False)   

    # >>> close, busy & stop.

    def close(self):
        self.stop = True
        self.t.join(timeout=1)
        if self.t.is_alive():
            _m.beeps(3)
            errmsg = 'XLog._xlogthread did not self-stop'
            self._p('** ' + errmsg)
        self.xlog.close()
        1/1

    def busy(self):
        # !TODO! !!! Check for not connected!
        return not self.q.empty()

    def stop(self):
        self.q.stop = True

    # >>> Functions named by logging level.

    def null(self, msg=None):
        if msg:
            self.msg2xlog(msg, el=0, sl='_')	
            if self.sw:
                self.sw.null(msg)

    def debug(self, msg=None):
        if msg:
            self.msg2xlog(msg, el=1, sl='.')
            if self.sw:
                self.sw.debug(msg)

    def info(self, msg=None):
        if msg:
            self.msg2xlog(msg, el=2, sl='-')
            if self.sw:
                self.sw.info(msg)

    def warning(self, msg=None):
        if msg:
            self.msg2xlog(msg, el=3, sl='>')
            if self.sw:
                self.sw.warning(msg)

    def error(self, msg=None):
        if msg:
            self.msg2xlog(msg, el=4, sl='*')
            if self.sw:
                self.sw.error(msg)

    def critical(self, msg=None):
        if msg:
            self.msg2xlog(msg, el=5, sl='!')
            if self.sw:
                self.sw.error(msg)

    def extra(self, msg=None):
        if msg:
            self.msg2xlog(msg, el=6, sl='+')       
            if self.sw:
                self.sw.error(msg)

# >>> Tests.

DEBPRT = False
FAIL_CONNECT = False
FAIL_O = False

def tests():
    import time
    global DEBPRT, FAIL_CONNECT, FAIL_O
    me, action = 'tests', None

    def _p(s):
        nonlocal xlog
        if xlog and xlog.sw:
            xlog.sw.nlln(s.rstrip())
        else:
            print(s.rstrip())

    xlog = None
    _p('')
    _p('-- tests begins')

    DEBPRT = True

    if False:
        action = 'fail connect test'
        _p('')
        _p(action)
        FAIL_CONNECT = True
        try:
            xlog = XLog(xloghost='192.168.100.1', xlogport=12321, xlogid='TEST', xsubid='test', xlogel=0, xlogsl='_', screenwriter=None, txrate=0.02)
        except Exception as E:
            _m.beeps(10)
            errmsg = '{}: {}: {}'.format(me, action, E)
            _p('** ' + errmsg)
            1/1
        FAIL_CONNECT = False

    if False:
        action = 'simple log-type functions'
        _p('')
        _p('-- ' + action)
        nm = 0
        try:
            xlog = XLog(xloghost='192.168.100.1', xlogport=12321, xlogid='TEST', xsubid='test', xlogel=0, xlogsl='_', screenwriter=None, txrate=0.01)
            for x in range(100):
                xlog.null    ('f: null'    )
                nm += 1
                xlog.debug   ('f: debug'   )
                nm += 1
                xlog.info    ('f: info'    )
                nm += 1
                xlog.warning ('f: warning' )
                nm += 1
                xlog.error   ('f: error'   )
                nm += 1
                xlog.critical('f: critical')
                nm += 1
                xlog.extra   ('f: extra'   )
                nm += 1
            for x in range(100):
                if not xlog.busy():
                    break
                time.sleep(0.1)
            time.sleep(0.1)             # Needs a little more.
            nmsgs = xlog.nmsgs
            assert nmsgs == nm, 'expecting %d but got %d nmsgs' % (nm, nmsgs)
            xlog.close()
            assert xlog.stopped, 'did not see xlog.stopped'
        except Exception as E:
            _m.beeps(10)
            errmsg = '{}: {}: {}'.format(me, action, E)
            _p('** ' + errmsg)
            1/1

    if False:
        action = 'prepared dict and json functions'
        _p('')
        _p('-- ' + action)
        nm = 0
        try:
            xlog = XLog(xloghost='192.168.100.1', xlogport=12321, xlogid='TEST', xsubid='test', xlogel=0, xlogsl='_', screenwriter=None, txrate=0.01)
            d = {'_id': 'TEST', '_si': 'test', '_el': 6, '_sl': '|', '_msg': 'Hello World!', 'foo': 123, 'rat': 'fink'}
            xlog.d2xlog(d)
            nm += 1
            j = json.dumps(d)
            xlog.j2xlog(j)
            nm += 1
            for x in range(100):
                if not xlog.busy():
                    break
                time.sleep(0.1)
            time.sleep(0.1)             # Needs a little more.
            nmsgs = xlog.nmsgs
            assert nmsgs == nm, 'expecting %d but got %d nmsgs' % (nm, nmsgs)
            xlog.close()
            assert xlog.stopped, 'did not see xlog.stopped'
        except Exception as E:
            _m.beeps(10)
            errmsg = '{}: {}: {}'.format(me, action, E)
            _p('** ' + errmsg)
            1/1

    if False:
        action = 'unexpected object type'
        _p('')
        _p('-- ' + action)
        nm = 0
        try:
            xlog = XLog(xloghost='192.168.100.1', xlogport=12321, xlogid='TEST', xsubid='test', xlogel=0, xlogsl='_', screenwriter=None, txrate=0.01)
            xlog.q.put(123456789, block=False)
            nm += 1
            for x in range(100):
                if not xlog.busy():
                    break
                time.sleep(0.1)
            time.sleep(1.0)         # Needs enough time for beeps(3).
            nmsgs = xlog.nmsgs
            assert nmsgs == nm, 'expecting %d but got %d nmsgs' % (nm, nmsgs)
            xlog.close()
            assert xlog.stopped, 'did not see xlog.stopped'
        except Exception as E:
            _m.beeps(10)
            errmsg = '{}: {}: {}'.format(me, action, E)
            _p('** ' + errmsg)
            1/1

    if False:
        action = 'fail processing object'
        _p('')
        _p('-- ' + action)
        nm = 0
        try:
            xlog = XLog(xloghost='192.168.100.1', xlogport=12321, xlogid='TEST', xsubid='test', xlogel=0, xlogsl='_', screenwriter=None, txrate=0.01)
            FAIL_O = True
            xlog.msg2xlog('1/0')
            nm += 1
            for x in range(100):
                if not xlog.busy():
                    break
                time.sleep(0.1)
            time.sleep(1.0)         # Needs enough time for beeps(3).
            FAIL_O = False
            nmsgs = xlog.nmsgs
            assert nmsgs == nm, 'expecting %d but got %d nmsgs' % (nm, nmsgs)
            xlog.close()
            assert xlog.stopped, 'did not see xlog.stopped'
        except Exception as E:
            _m.beeps(10)
            errmsg = '{}: {}: {}'.format(me, action, E)
            _p('** ' + errmsg)
            1/1

    _p('')
    _p('-- tests ends')
    _p('')
    1/1

if __name__ == '__main__':
    tests()

###