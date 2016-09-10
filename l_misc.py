# Copyright 2011, 2015 by J Kelly Dresser.  All rights reserved.
#> !P2! !P3!

###
### l_misc:
###

1/1

import sys
import time
import binascii

P3 = (sys.version_info[0] == 3)
P2 = not P3
try:
    import winsound
    GOTWINSOUND = True
except:
    GOTWINSOUND = False

# Beep.
def beep(n=1):
    for x in range(n):
        if GOTWINSOUND:
            winsound.Beep(3333, 100)
        time.sleep(0.1)

# Click.
def click(n=1):
    for x in range(n):
        if GOTWINSOUND:
            winsound.Beep(2000, 2)
        time.sleep(0.1)

# Traceback line number.
def tblineno():
    try:
        if P2:  return str(sys.exc_traceback.tb_lineno)
        else:   return str(sys.exc_info()[2].tb_lineno)
    except:
        return '???'

# CRC32: Non-incremental CRC of given bytes.
def crc32(b):
    return binascii.crc32(b) & 0xffffffff
    # '0x%08x' % result

# NEW: A simple is-it-new" check & store of KV's.
NEW = {}
def isNew(k, v):
    global NEW
    new = (k not in NEW or v != NEW[k])
    NEW[k] = v
    return new

# The following 3 are duplicated in f_helpers.

def unicodetoascii(s, encoding='ascii', rplc=None):
    """A crude str encoder.  Replaces '?' from s.encode with rplc (if not None).  Bytes returned unchanged."""
    # Another choice: encoding='latin-1'.
    # ??? Is this sane: just to have a different replacement char than '?'?
    if not isinstance(s, str):
        return s
    t = s.encode(encoding, 'replace')	# ASCII encoding failures -> '?'.
    if isinstance(rplc, str):
        # Replace encoding failures with rplc.
        u = ''
        for (cs, ct) in zip(s, t):
            if ct == 63 and cs != '?':	# 63 = ord(b'?'). 
                u += rplc
            else:
                u += chr(ct)
        return u
    else:
        return t.decode(encoding)		# ASCII bytes to str.

def toascii(s, rplc='~'):
    """Calls _unicodetoascii(s) with rplc defaulting to '~'.  Bytes returned unchanged."""
    if isinstance(s, str):
        return unicodetoascii(s, rplc=rplc)
    else:
        return s

def tolatin1(s):
    """Calls _unicodetoascii(s, encoding='latin-1') with rplc defaulting to '~'.  Bytes returned unchanged."""
    if isinstance(s, str):
        return unicodetoascii(s, encoding='latin-1', rplc='~')
    else:
        return s

def xor(a, b):
    if bool(a) == bool(b):
        return False
    else:
        return a or b

TFN2V = {'True': True, 'False': False, 'None': None}
def s2v(s):
    """Convert str to int, float, True, False, None, unquoted str."""
    if not isinstance(s, str):
        raise ValueException('parameter is not str')
    try:    return int(s)
    except: pass
    try:    return float(s)
    except: pass
    if s in TFN2V:
        return TFN2V[s]
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        s = s[1:-1]
    return s

def iso2ms(iso):
    """Modify ISO 8601 (from arrow) to millisecond suffix + (Z or '')."""
    #
    # iso '2016-05-20 00:15:20.200875+00:00'
    #     '2016-05-19 17:15:20.200875-07:00'
    #
    #  -> '2016-05-20 00:15:20.201Z'              
    #     '2016-05-19 17:15:20.201'
    #
    ymdhms = iso[:-13]
    subsec = float(iso[-13:-6])
    ms = ',' + ('%.3f' % round(subsec, 3))[2:]
    ofs = iso[-6:]
    sfx = 'Z' if ofs == '+00:00' else ''
    return ymdhms + ms + sfx

def utc2ms(utc):
    """UTC to modified ISO 8601."""
    return iso2ms(utc.isoformat(sep=' '))

def simple2string(x):
    """
    Simple objects (bytes, bool, float, int, None, str) are converted
    to string and returned. Other types are returned as None.
    """
    if  isinstance(x, bytes) or \
        isinstance(x, bool ) or \
        isinstance(x, float) or \
        isinstance(x, int  ) or \
        x is None            or \
        isinstance(x, str  ):
        return str(x)
    else:
        return None

def string2simple(s):
    """
    If s is not a string, it is returned asis.
    Otherwise, it's eval'd in an attempt to create a simple 
    object (bytes, bool, float, int, None, str).
    The eval will raise an EXCEPTION if the source does not 
    represent a simple object or is an unquoted object reference.
    *** Warning: since the source string is eval'd, it must be 
    trustworthy. ***
    """
    if isinstance(s, str):
        return eval(s)
    else:
        return s
