# Copyright 2015 by J Kelly Dresser.  All rights reserved.

#
## l_xlog: Class for tx'ing to tcp/ip socket logger app "xlog".
##         Messages (actually dicts) are saved to a queue and sent
##         from within a thread.  As much processing as possible is 
##         deferred to the thread.
##         Functions that create (or accept) these dicts:
##           1. null, debug, info, warning, error, critical and extra
##              take a msg plus optional srcid and subid overrides.
##              el and sl are determined by each function.
##              Uses msg2xlog.
##           2. msg2xlog(msg, srcid=None, subid=None, el=None, sl=None).
##           3. logd2xlog(logd) for a ready-to-use dict.
##           4. logdj2xlog(logdj) for a ready-to-use json'd dict.
##         Uses XLogTxRx class which has backlogging and 
##         reconnection abilities.
##         Can be a nop logger with nop=True.
#

1/1

import json
import queue
import threading

from l_xlogtxrx import XLogTxRx
import l_misc as _m

ENSURE_ASCII = True
SORT_KEYS = True

class XLog():

    def __init__(self, xloghost=None, xlogport=None, xsrcid=None, xsubid=None, xlogel='2', xlogsl='_', 
                 sl=None, sw=None, txrate=0.02, nop=False):
        me = 'XLog.__init__'
        self.nop      = nop         # Make a do-nothing logger.
        self.xlog     = None        # Default no logging until host & port connected.
        self.xloghost = xloghost    # xlog server host IP.
        self.xlogport = xlogport    # xlog server port.
        # srcid, subid, el & sl are defaults used by message builders if no
        # overrides are supplied in the log dict.
        self.xsrcid   = xsrcid      # Initial source ID.  
        self.xsubid   = xsubid      # Initial sub    ID. 
        self.xlogel   = xlogel      # Default error-level (info).
        self.xlogsl   = xlogsl      # Default sub-level   (base).
        # Optional simple logger and screenwriter objects.
        self.sl = sl                # Optional simple logger to mimic what's being 
                                    # sent to xlog.
        self.sw = sw                # Optional screen writer object for 
                                    # error messages (otherwise print).
        # Message queue.
        self.q = None               # Queue of messages to send.
        # Processing thread.
        self.t = None               # Thread to send messages.
        # Stop signal.
        self.stop = False           # External signal to stop XLog instance.
        self.stopped = False        # When stopped by self.stop.
        # Count messages.
        self.nmsgs = 0              # Number of messages sent.
        # 
        if self.xloghost and self.xlogport:
            try:
                if not self.nop:
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
                    otn = o[0]                      # object type number
                    if   otn == 0:                  
                        # srcid, subid, el, sl, msg -> {_id, _si, _el, _sl, _msg}
                        d = {'_id': str(o[1]), '_si': str(o[2]), '_el': str(o[3]), '_sl': str(o[4]), '_msg': str(o[5])}
                        j = json.dumps(d, ensure_ascii=ENSURE_ASCII, sort_keys=SORT_KEYS)
                        if DEBPRT:
                            self._p('~~ 0: [%d] -> [%d]' % (len(d), len(j)))
                        self.xlog.send(j)
                        self.nmsgs += 1
                        continue
                    elif otn == 1:
                        # dict
                        d = o[1]
                        j = json.dumps(d, ensure_ascii=ENSURE_ASCII, sort_keys=SORT_KEYS)
                        if DEBPRT:
                            self._p('~~ 1: [%d] -> [%d]' % (len(d), len(j)))
                        self.xlog.send(j)
                        self.nmsgs += 1
                        continue
                    elif otn == 2:
                        # json
                        j = o[1]
                        if DEBPRT:
                            self._p('~~ 2: [%d]' % (len(j)))
                        self.xlog.send(j)
                        self.nmsgs += 1
                        continue
                    else:
                        _m.beeps(3)
                        # Switch to errmsg.
                        errmsg = '{}: {}: {}'.format(me, 'unexpected object type number', repr(otn)) 
                        self._p('** ' + errmsg)
                        z = json.dumps({'_id': self.xsrcid, '_si': self.xsubid, '_el': 5, '_sl': '!', '_msg': '[' + errmsg + ']'},
                                       ensure_ascii=ENSURE_ASCII, sort_keys=SORT_KEYS)
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
                    z = json.dumps({'_id': self.xsrcid, '_si': self.xsubid, '_el': 5, '_sl': '!', '_msg': '[' + errmsg + ']'},
                                   ensure_ascii=ENSURE_ASCII, sort_keys=SORT_KEYS)
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

    def msg2xlog(self, msg, srcid=None, subid=None, el=None, sl=None):
        """Tx msg (with optional srcid, subid, el, sl overridess) via xlog."""
        if self.nop or not msg or not isinstance(msg, str):
            return
        # Sample self.* defaults when adding to queue.
        self.q.put((0,  # 0 -> srcid, subid, el, sl, msg
                    self.xsrcid if srcid is None else srcid, 
                    self.xsubid if subid is None else subid, 
                    self.xlogel if el is None else el,
                    self.xlogsl if sl is None else sl, 
                    msg), block=False)

    def logd2xlog(self, logd):
        """Tx ready-to-use dict via xlog."""
        # srcid, subid, el and sl must already be in dict.
        if self.nop or not logd or not isinstance(logd, dict):
            return
        self.q.put((1, # 1 -> dict
                    logd), block=False)   

    def logdj2xlog(self, logdj):
        """Tx ready-to-use json'd dict via xlog."""
        # Srcid and subid must already be in json.
        if self.nop or not logdj or not isinstance(logdj, str):
            return
        self.q.put((2, # 2 -> json
                    logdj), block=False)   

    # >>> close, busy & stop.

    def close(self):
        """Shut down xlog wrap."""
        if self.nop:
            self.stopped = True
            return
        self.stop = True
        self.t.join(timeout=1)
        if self.t.is_alive():
            _m.beeps(3)
            errmsg = 'XLog._xlogthread did not self-stop'
            self._p('** ' + errmsg)
        self.xlog.close()
        1/1

    def busy(self):
        """Check queue not empty."""
        if self.nop:
            return False
        # !TODO! !!! Check for not connected!
        return not self.q.empty()

    def stop(self):
        """Signal stop to tx thread."""
        if self.nop:
            return
        self.q.stop = True

    #
    # >>> Functions named by logging level.
    #     msg must be a string.
    #     srcid and subid can be supplied to override defaults.
    #     el and sl are set by each logging level function.
    #

    def null(self, msg=None, srcid=None, subid=None):
        """Null level msg."""
        self.msg2xlog(msg, srcid=srcid, subid=subid, el=0, sl='_')	
        if self.sl:
            self.sl.null(msg)

    def debug(self, msg=None, srcid=None, subid=None):
        """Debug level msg."""
        self.msg2xlog(msg, srcid=srcid, subid=subid, el=1, sl='.')
        if self.sl:
            self.sl.debug(msg)

    def info(self, msg=None, srcid=None, subid=None):
        """Info level msg."""
        self.msg2xlog(msg, srcid=srcid, subid=subid, el=2, sl='-')
        if self.sl:
            self.sl.info(msg)

    def warning(self, msg=None, srcid=None, subid=None):
        """Warning level msg."""
        self.msg2xlog(msg, srcid=srcid, subid=subid, el=3, sl='>')
        if self.sl:
            self.sl.warning(msg)

    def error(self, msg=None, srcid=None, subid=None):
        """Error level msg."""
        self.msg2xlog(msg, srcid=srcid, subid=subid, el=4, sl='*')
        if self.sl:
            self.sl.error(msg)

    def critical(self, msg=None, srcid=None, subid=None):
        """Critical level msg."""
        self.msg2xlog(msg, srcid=srcid, subid=subid, el=5, sl='!')
        if self.sl:
            self.sl.critical(msg)

    def extra(self, msg=None, srcid=None, subid=None):
        """Extra level msg."""
        self.msg2xlog(msg, srcid=srcid, subid=subid, el=6, sl='+')       
        if self.sl:
            self.sl.extra(msg)

# >>> Tests.

DEBPRT = False
FAIL_CONNECT = False
FAIL_O = False

def tests(tn=None):
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

    if True and tn == 1:
        action = 'fail connect test'
        _p('')
        _p(action)
        FAIL_CONNECT = True
        try:
            xlog = XLog(xloghost='192.168.100.1', xlogport=12321, xsrcid='TEST', xsubid='test', xlogel=0, xlogsl='_', sw=None, txrate=0.02)
        except Exception as E:
            _m.beeps(10)
            errmsg = '{}: {}: {}'.format(me, action, E)
            _p('** ' + errmsg)
            1/1
        FAIL_CONNECT = False

    if True and tn == 2:
        action = 'simple log-type functions'
        _p('')
        _p('-- ' + action)
        nm = 0
        try:
            xlog = XLog(xloghost='192.168.100.1', xlogport=12321, xsrcid='TEST', xsubid='test', xlogel=0, xlogsl='_', sw=None, txrate=0.01)
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

    if True and tn == 3:
        action = 'prepared dict and json functions'
        _p('')
        _p('-- ' + action)
        nm = 0
        try:
            xlog = XLog(xloghost='192.168.100.1', xlogport=12321, xsrcid='TEST', xsubid='test', xlogel=0, xlogsl='_', sw=None, txrate=0.01)
            d = {'_id': 'TEST', '_si': 'test', '_el': 6, '_sl': '|', '_msg': 'Hello World!', 'foo': 123, 'rat': 'fink'}
            xlog.d2xlog(d)
            nm += 1
            j = json.dumps(d, ensure_ascii=ENSURE_ASCII, sort_keys=SORT_KEYS)
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

    if True and tn == 4:
        action = 'unexpected object type'
        _p('')
        _p('-- ' + action)
        nm = 0
        try:
            xlog = XLog(xloghost='192.168.100.1', xlogport=12321, xsrcid='TEST', xsubid='test', xlogel=0, xlogsl='_', sw=None, txrate=0.01)
            xlog.q.put((9, 123456789), block=False)
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

    if True and tn == 5:
        action = 'fail processing object'
        _p('')
        _p('-- ' + action)
        nm = 0
        try:
            xlog = XLog(xloghost='192.168.100.1', xlogport=12321, xsrcid='_src', xsubid='_sub', xlogel=0, xlogsl='_', sw=None, txrate=0.01)
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