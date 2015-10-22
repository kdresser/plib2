
# Flask App Helpers.  !P3!.

import sys, binascii, time, math, hashlib

DOW = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')

def unicodetoascii(s, rplc=None):
  """A crude str encoder.  Replaces '?' from s.encode with rplc (if not None).  Bytes returned unchanged."""
  if not isinstance(s, str):
    return s
  t = s.encode('ascii', 'replace')	# ASCII encoding failures -> '?'.
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
    return t.decode('ascii')		# ASCII bytes to str.

def toascii(s):
  """Calls _unicodetoascii(s) with rplc defaulting to '~'.  Bytes returned unchanged."""
  if isinstance(s, str):
    return unicodetoascii(s, rplc='~')
  else:
    return s

def ZZZnulstr(s):                       # 151003: Discontinued, use none2null instead.
  """None -> empty string, otherwise unchanged."""
  if s is None:
    s = ''
  return s

def none2null(s):
  """None -> null (empty string)."""
  if s is None:
    return ''
  return s

def null2none(s):
  """Null string (including all blank) -> None."""
  if not s.strip():
    return None
  return s

def none2zero(v):
  """None -> zero."""
  if v is None:
    return 0
  return v

def zero2none(v):
  """Zero -> None."""
  if v == 0:
      return None
  return v

def tbln():		
  """Return str(traceback line number)."""
  try:
    z = str(sys.exc_info()[2].tb_lineno)  # !P3!.
  except:
    z = None
  if z is None or z == '':
    z = '???'
  return z

def crc32(s):
  """Converts s (if a str) to utf-8 bytestring and applies crc32."""
  if isinstance(s, str):
    s = s.encode('utf-8')
  return binascii.crc32(s) & 0xffffffff

def md532(s):
  if isinstance(s, str):
    s = s.encode('utf-8')
  h = hashlib.md5()
  h.update(s)
  return int.from_bytes(h.digest()[:4], sys.byteorder, signed=True)

def fnsplit(fn):
  """/path/fnr.x -> (/path/fnr, x) when possible.  Non-str treated as None."""
  if not (isinstance(fn, str) and fn):
    return (None, None)
  fn = fn.strip()
  if not fn:	
    return (None, None)
  x = fn.rfind('.')
  if x == -1:
    return fn, None
  return (fn[:x], fn[x:])

def ZZZrow2dict(row, squawk=True):		# 151003: Discontinued, no longer using pyodb.
  """Convert a pyodbc row result to a dict."""
  if not row:
    return {}
  else:
    return { k[0]: v for (k, v) in zip(row.cursor_description, row) }

def ZZZcurrow2dict(cur, row, squawk=True):      # 151003: Discontinued, use dictionary=True in cursor() call.
  """Convert a pyodbc cursor and row result to a dict."""
  if not row:
    return {}
  else:
    return { k[0]: v for (k, v) in zip(cur.description, row) }

def utcut():
  """-> UTC Unix Time."""
  z = time.time()
  return z

def utcut2local(utcut):
  """-> 'Dow yyyy-mm-dd hh:mm:ss' (seconds resolution)."""
  loc = time.localtime(round(utcut))
  return '%s %04d-%02d-%02d %02d:%02d:%02d' % \
    (DOW[loc.tm_wday], loc.tm_year, loc.tm_mon, loc.tm_mday, loc.tm_hour, loc.tm_min, loc.tm_sec)

def utcut2localds(utcut):
  """-> 'Dow yyyy-mm-dd hh:mm:ss,d' (deciseconds resolution)."""
  (f, i) = math.modf(utcut)
  loc = time.localtime(i)
  return '%s %04d-%02d-%02d %02d:%02d:%02d,%s' % \
    (DOW[loc.tm_wday], loc.tm_year, loc.tm_mon, loc.tm_mday, loc.tm_hour, loc.tm_min, loc.tm_sec, ('%.1f' % f)[-1:])

def utcut2dow(utcut):
  """-> day of week (e.g., 'Mon') from utcut."""
  loc = time.localtime(math.floor(utcut))
  return DOW[loc.tm_wday]

def utcut2ymd(utcut):
  """-> '2015-12-31' from utcut."""
  loc = time.localtime(math.floor(utcut))
  return '%04d-%02d-%02d' % \
    (loc.tm_year, loc.tm_mon, loc.tm_mday)

def ut2isocs(ut):
  """Unix time -> ISO centiseconds string.  Blank between date and time."""
  f, i = math.modf(ut)
  return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(i)) + ',' + ('%.2f' % f)[-2:]

def ts(ts=None):
  """-> ut2isocs from ts (or now if None or zero)."""
  if not ts:
    ts = utcut()
  return ut2isocs(ts)  

'''...
def etseconds(pc0):
  """Elapsed time, seconds, given starting pc."""
  return time.perf_counter() - pc0
...'''

def etfooter(pc0, pc1=None):
  """Elapsed time string for use as page footer, given an initial perfcntr."""
  return '[%s]' % prettydt(pc0, pc1)
  
def prettydt(pc0, pc1=None):
  """Make and pretty-format a delta time, given a starting perfcntr."""
  if pc1 is None:
      pc1 = time.perf_counter()
  return prettyet(pc1 - pc0)
  
def ZZZprettyet(et):
  """Pretty format an elapsed-time."""
  if   et < 0.001:
    ###return '[%.1f us]' % (et * 1000000, )
    return '%.1f us' % (et * 1000000, )
  elif et < 1:
    ###return '[%.1f ms]' % (et * 1000, )
    return '%.1f ms' % (et * 1000, )
  else:
    ###return '[%.1f s]'  % (et, )
    return '%.1f s'  % (et, )

def prettyet(et):
  """Pretty format an elapsed-time."""
  zt = et * 1000000         # -> us
  if round(zt) < 10000:
    #@return '%.1f us' % zt
    return '{:,.1f} us'.format(zt)
  zt /= 1000                # -> ms
  if round(zt) < 10000:
    #@return '%.1f ms' % zt
    return '{:,.1f} ms'.format(zt)
  zt /= 1000                # -> se
  if zt < 600:
    #@return '%.1f se' % zt
    return '{:,.1f} se'.format(zt)
  zt /= 60                  # -> mi
  if zt < 600:
    #@return '%.1f mi' % zt
    return '{:,.1f} mi'.format(zt)
  zt /= 60                  # -> hr
  if zt < 24:
    #@return '%.1f hr' % zt
    return '{:,.1f} hr'.format(zt)
  zt /= 24                  # -> da
  if True:
    #@return '%.1f da' % zt
    return '{:,.1f} da'.format(zt)
"""

KB=1,024  MB=1,048,576  GB=1,073,741,824

.rar    application/x-rar-compressed, application/octet-stream
.zip    application/zip, application/octet-stream

.zip	application/x-compressed
.zip	application/x-zip-compressed
.zip	application/zip
.zip	multipart/x-zip

.gif	

"""

if __name__ == '__main__':

    # Test prettyet.
    print('us:', prettyet(123.456 * 0.000001))
    print('ms:', prettyet(123.456 * 0.001))
    print('se:', prettyet(123.456 * 1))
    print('mi:', prettyet(123.456 * 60))
    print('hr:', prettyet(123.456 * 60 * 60))
    print('da:', prettyet(123.456 * 60 * 60 * 24))
