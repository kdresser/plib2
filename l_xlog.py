# Copyright 2015 by J Kelly Dresser.  All rights reserved.

#
## l_xlog: Class for tx'ing to tcp/ip socket logger app "xlog".
#

import json, queue, threading

from l_xlogtxrx import XLogTxRx
import l_misc as _m


class XLog():
    def __init__(self, xloghost=None, xlogport=None, xlogid=None, xlogel='2', xlogsl='_', screenwriter=None, txrate=0.02):
        self.xlog     = None        # Default no logging.
        self.xloghost = xloghost
        self.xlogport = xlogport
        self.xlogid   = xlogid
        self.xlogel   = '2'         # Default error-level to info.
        self.xlogsl   = '_'         # Default sub-level   to base.
        self.sw = screenwriter      # Optional screen writer.
        self.q = None               # Queue
        self.t = None               # Thread.
        self.stop = False
        if self.xloghost and self.xlogport:
            try:
                self.xlog = XLogTxRx((self.xloghost, self.xlogport), txrate=txrate)
                self.q = queue.Queue(10000)     # 10k
                self.t = threading.Thread(target=self._xlogthread)      # ??? daemon?
                self.t.start()
            except Exception as E:
                if self.sw:
                    self.sw.error('cannot setup up xlog: %s' % E)
                self.xlog = None

    def _xlogthread(self):
        """Processes a FIFO queue of 3-tuples."""
        while not self.stop:
            try:    
                z = self.q.get(timeout=1)
                self._xlogsend(z)
            except: 
                pass
        1/1

    def _xlog(self, msg, el=None, sl=None):
        if not (self.xlog and msg):
            return
        self.q.put((msg, el, sl), block=False)      # !!! Will explode when queue is full!

    def _xlogsend(self, args):
        msg, el, sl = args
        me = '_xlogsend'
        if not (self.xlog and msg):
            return
        if el is None:
            el = self.xlogel
        if sl is None:
            sl = self.xlogsl
        # el: NOTSET, DEBUG, INFO, WARNING, ERROR CRITICAL
        #       0       1      2       3      4      5
        try:
            '''...
            z = {'_id': self.xlogid, '_el': str(el), '_sl': str(sl), '_msg': msg}
            y = json.dumps(z)
            x = json.loads(y)
            self.xlog.send(y)
            ...''' 
            if   isinstance(msg, dict):     # Assume it's a ready-to-xlog dict.
                msg = json.dumps(msg)
                self.xlog.send(msg)
                return
            elif isinstance(msg, bytes):
                msg = msg.decode()
            else:
                try:
                    msg = str(msg)
                except:
                    return                  # !!! Warning: silent exception!
            z = json.dumps({'_id': self.xlogid, '_el': str(el), '_sl': str(sl), '_msg': msg})
            self.xlog.send(z)
            ###self.xlog.send(json.dumps({'_id': self.xlogid, '_el': str(el), '_sl': str(sl), '_msg': msg}))
        except Exception as E:
            _m.beeps(3)
            ###errmsg = 'xlog: ' + str(E)
            errmsg = '{}: {} @ {}'.format(me, E, _m.tblineno())
            if self.sw:
                self.sw.error(errmsg)
                self.sw.error(msg)
            else:
                print('**', errmsg) 
                print('**', msg)
            1/1

    def close(self):
        #$#print('mxlog: close')#$#
        self.stop = True
        self.t.join()
        self.xlog.close()
        1/1

    def busy(self):
        # !!! Watch for not connected!
        return not self.q.empty()

    def stop(self):
        self.q.stop = True

    # Wrap xlog + ml.xxx.

    def null(self, msg=None):
        if msg:
            self._xlog(msg, el=0, sl='_')	
            if self.sw:
                self.sw.null(msg)

    def debug(self, msg=None):
        if msg:
            self._xlog(msg, el=1, sl='.')
            if self.sw:
                self.sw.debug(msg)

    def info(self, msg=None):
        if msg:
            self._xlog(msg)
            if self.sw:
                self.sw.info(msg)

    def warning(self, msg=None):
        if msg:
            self._xlog(msg, el=3, sl='>')
            if self.sw:
                self.sw.warning(msg)

    def error(self, msg=None):
        if msg:
            self._xlog(msg, el=4, sl='*')
            if self.sw:
                self.sw.error(msg)

    def critical(self, msg=None):
        if msg:
            self._xlog(msg, el=5, sl='!')
            if self.sw:
                self.sw.error(msg)

    def extra(self, msg=None):
        if msg:
            self._xlog(msg, el=0, sl='+')       
            if self.sw:
                self.sw.error(msg)
