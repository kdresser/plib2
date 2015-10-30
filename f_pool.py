
# 
## FlaskPool: A *very* simple thread-safe pool of objects.
##            No exception handling.
##            No recovery from dead objectsk, though something 
##            could be done with smarter objects.
#

# None is a valid pool object.
# -1 is returned when a pool is exhausted.

import _thread, time


class FlaskPool(object):

  def __init__(self, ctor, dtor, maxn, name):
    """Create a pool, given a constructor, destructor and max size."""
    self.lock = _thread.allocate_lock()	
    self.ctor = ctor
    self.dtor = dtor
    self.maxn = maxn
    self.name = name
    self.nall = 0
    self.pool = []

  def status(self):
    return (len(self.pool), self.nall)

  def get(self):
    """Get an object from pool.  Up to maxn objects are lazily created."""
    # Returns -1 if pool is empty.
    # Pool objects may be None.
    with self.lock:
      if len(self.pool) == 0:
        if self.nall >= self.maxn:
          return -1			# !MAGIC!
        obj = self.ctor(self.nall + 1)
        self.pool.append(obj)
        self.nall += 1
      return self.pool.pop()
      #@return z

  def getw(self, w=0.1, max=None):	
    """Get an object from pool, waiting up to max seconds.  Up to maxn objects are lazily created."""
    tw = 0
    obj = self.get()
    while obj == -1:
      if max and (tw > max):
        return obj
      time.sleep(w)
      tw += w
      obj = self.get()
    return obj

  def ret(self, obj):
    """Return an object to pool."""
    # None is allowed, but not -1.
    if obj != -1:
      with self.lock:
        self.pool.append(obj)

  def zap(self, obj):
    """Apply destructor to an object."""
    # None allowed.
    with self.lock:
      self.dtor(obj)
      self.nall -= 1
      if self.nall < 0:
        raise ValueError('%s.zap: %d < 0' % (self.name, self.nall))

  def zapall(self):
    """Apply destructor to all objects in pool."""
    with self.lock:
      while len(self.pool) > 0:
        obj = self.pool.pop()
        self.dtor(obj)
        self.nall -= 1
        if self.nall < 0:
          raise ValueError('%s.zapall: %d < 0' % (self.name, self.nall))
