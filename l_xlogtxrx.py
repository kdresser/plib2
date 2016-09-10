
1/1

import time
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
import l_misc as _m

# Python error levels div 10: NOTSET, DEBUG, INFO, WARNING, ERROR CRITICAL
#                                0      1      2      3       4       5

TXENCODING, TXERRORS = 'ascii', 'strict'  # For Tx of unicode.

class XLogTxRx():
    """A TCP/IP transmitter/receiver, with reconnection and backlogging, for use with an xlog server."""

    def __init__(self, hostport, txrate=0, cxrate=60, cxtimeout=3, txtimeout=0.5, cx=True, acking=True):
        self.hostport = hostport
        self.skt = None         # Will be none when not connected.
        self.cxts = 0           # Timestamp of last connection attempt.
        self.cxrate = cxrate    # Minimum time between connection attempts.
        self.cxwait = 0         # Countdown to next reconnection attempt.  0 when connected.
        self.cxtimeout = cxtimeout
        self.cxstatus = None    # -1: a connection attemp failed.  0: waiting for connection attempt. 1: connected.
        self.cxfails = 0        # Current number of failed connection attempts.  0 when connected.
        self.cxerrmsg = None    # Last connection attempt errmsg.
        self.txbacklog = []     # For stashing a messages when unconnected.
        self.txbackout = False  # True when draining a backlog.
        self.txts = 0           # Timestamp of last transmission.
        self.txrate = txrate    # Mininum time between transmissions.
        self.txtimeout = txtimeout
        self.txerrmsg = None    # Last tx errmsg.
        self.acking = acking    # Does the remote server ack (with 'OK')?
        if cx:
            z = self.connect()

    def connect(self):
        """Connect (if not rate-waiting) to hostport, and test. Return: -1: failed.  0: waiting.  1: successful."""
        try:
            #$#print('>> self.connect:', repr(self.skt))#$#
            # Already?
            if self.skt:
                self.cxstatus = 1
                return 
            # Throttle connection rate.
            self.cxwait = self.cxrate - (time.time() - self.cxts)
            if self.cxwait > 0:
                self.cxstatus = 0
                return 
            # Try a connect.
            #$#print('-- self.connect try')#$#
            self.cxerrmsg = None
            self.cxts = time.time()
            self.skt = socket(AF_INET, SOCK_STREAM)
            self.skt.settimeout(self.cxtimeout)         
            self.skt.connect(self.hostport)
            self.skt.settimeout(self.txtimeout)
            self.csstatus = 1
            self.cxfails = 0 
        except Exception as E:
            errmsg = 'connect: %s @ %s' % (E, _m.tblineno())
            #$#print('** self.connect:', errmsg)#$#
            self.cxerrmsg = errmsg
            #$#ml.error(errmsg)#$#      # No logging here!
            self.disconnect()
            self.cxstatus = -1
            self.cxfails += 1
        finally:
            return self.cxstatus 

    def send(self, msg):
        """Return True if msg+newline sent and 'OK' received.
           Will backlog unsent messages for when (re)connected.
           A None msg can be used to attempt (re)connection and 
           backlog output.
           An 'OK' is expected in response to all messages 
           successfully received by xlog.
           Use send for legitimate log messages, for which 
           an 'OK' can mean that the message looked OK.
           Unicode is encoded to ascii, strict.
           TODO: 'E: ...' responses.
        """
        sent = False        # See finally.
        try:
            #$#print('-- self.send:', repr(msg))#$#
            # None can be used to flush any backlog and to attempt a (re)connect.
            if msg is not None:
                # Force msg to ascii bytes.
                if   isinstance(msg, bytes):
                    pass
                elif isinstance(msg, str):
                    msg = msg.encode(encoding=TXENCODING, errors=TXERRORS)
                else:
                    msg = str(msg).encode(encoding=TXENCODING, errors=TXERRORS)  
            else:
                pass
            # If there's no socket, try connecting.
            if not self.skt:
                #$#print('>> no self.skt -> self.connect')#$#
                self.connect()
                # If there's still no socket, bail.
                if not self.skt:
                    return sent
            # There's a socket.  Any backlog to output?
            if self.txbacklog and not self.txbackout:       # Inhibit recursive txbackout calls to send.
                self.txbackout = True
                try:
                    while self.txbacklog:
                        if self.send(self.txbacklog[0]):
                            self.txbacklog.pop(0)
                        else:
                            # A txbackout hasn't finished. 
                            return sent
                finally:
                    self.txbackout = False
            # None msg?
            if msg is None:
                sent = True         # Pretend.
                return sent         # Connected and all txbacklog has been output.
            # Throttle (blocking).
            w = self.txrate - (time.time() - self.txts)
            if w > 0:
                time.sleep(w)
            try:
                self.txerrmsg = None
                self.txts = time.time()
                try:  rx = self.txrx(msg).rstrip()
                except:  rx = None
                if self.acking:
                    if rx and rx.startswith(b'OK'):     # Every transmission is acknowledged with an OK.
                        sent = True
                else:
                    sent = True                 # Assume success.
            except Exception as E:
                errmsg = 'sendall: %s @ %s' % (E, _m.tblineno())
                self.txerrmsg = errmsg
                #$#ml.error(self.txerrmsg)#$#   # Nope!
                self.disconnect()
            return sent
        except Exception as E:
            errmsg = 'send: {} @ {}'.format(E, _m.tblineno())
            self.txerrmsg = errmsg
            #$#ml.error(errmsg)#$#              # Nope!
            raise                   # Reraise.                 
        finally:
            if not sent:
               self.disconnect()
               if msg is not None and not self.txbackout:
                   self.txbacklog.append(msg)

    def close(self):
        """Disconnect and release socket."""
        try:
            #$#print('mxlogtxrx: close')#$#
            self.skt.shutdown(SHUT_RDWR)
            self.skt.close()
        except:
            pass
        finally:
            self.skt = None
            self.cxstatus = None
    disconnect = close

    def txrx(self, msg):
        """Tx msg, then rx (either None or up to 1024 bytes returned).
           Low level, for the contents of log messages or for '!TEST!', 
	       '!PING!' or '!STOP!'.
           Unicode is encoded to ascii, strict.
        """
        if not self.skt:
            return None
        try:
            if isinstance(msg, str):
                msg = msg.encode(encoding=TXENCODING, errors=TXERRORS)   
            self.skt.sendall(msg + b'\n')
            return self.skt.recv(1024)
        except Exception as E:
            errmsg = 'txrx: %s' % E
            self.txerrmsg = errmsg
            #$#ml.error(errmsg)#$#      # Nope!
            return None
