
#
## >>> Simple Flask logging to file and socket connections for the duration of a request.
##     Connections, drawn from pools, are supplied (or None) at creation.
##     No console output here, except for debugging.
##     151030: Replace socket logging with xlog access.
#

# Note: '\n' is the line ending used throughout.

class FlaskLog(object):
  """A logging object using supplied thread-shared file and socket connections."""	

  ###def __init__(self, lf, ls, usexlog):
  def __init__(self, lf, ls):
    self.lf = lf
    self.ls = ls
    ###self.usexlog = usexlog	# !TEMP! A flag.

  def write(self, raw, flush=True):
    """Low level raw write to both file and socket logs, as possible."""

    if self.lf is not None:
      self.lf.write(raw)
      if flush:
        self.lf.flush()

    if self.ls is not None:
        # xlog wants str's.
        if isinstance(raw, bytes):	
            raw = raw.decode('utf-8')
        self.ls.null(raw)	# No logging level, yet.
        '''... Goes.
        if self.usexlog:
            if isinstance(raw, bytes):	# xlog wants strs.
                raw = raw.decode('utf-8')
            #$#print('~~ mLog.null:', repr(raw))#$#
            self.ls.null(raw)	# No logging level, yet.
        else:
            if isinstance(raw, str):
                raw = raw.encode('utf-8')	# Sockets want bytes.
            #$#print('~~ mLog.sendall:', repr(raw))#$#
            self.ls.sendall(raw)
        ...'''

  def flush(self):
    """Flush a log file.  Superfluous bcs writing defaults to flushing."""
    if self.lf is not None:
      self.lf.flush()

  def log(self, msg, pfx='-- '):
    """High level write to both file and socket logs, as possible. Expects 3-char prefixes, defaulting to '-- '.  '\n' is appended to rec."""
    if msg is None:
      return
    if not (len(msg) >= 3 and msg[0] == msg[1] and msg[2] == ' '): 
      msg = pfx + msg
    self.write(msg + '\n')

  def rawlog(self, raw):
    """High level raw write to both file and socket logs, as possible.  Newline not appended."""
    if raw is None:
      return
    self.write(raw)

  def xlog(self, o):
    self.xlog(o)


class mNullLog(object):
  """A null log object for not doing logging."""

  def __init__(self, lf, ls):	
    pass

  def write(self, raw, flush=True):
    pass

  def flush(self):
    pass

  def log(self, msg, pfx='-- '):
    pass

  def rawlog(self, raw):
    pass

  def xlog(self, o):
    pass
