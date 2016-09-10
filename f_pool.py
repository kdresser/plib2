
## 
## FlaskPool: A *very* simple thread-safe pool of objects.
##            Up to maxn objects are lazily created.
##            None is returned when maxn is exceeded.  
##              - None is !MAGIC!.  Means trouble.
##              - But 0 is a valid handle for a NOP object.
##            If an object dies (e.g., db disconnected), the user 
##            should simply recreate it.
##
## TODO: Use the reconnecting wrapper for the mysql.connector object.
##

import _thread          # ??? What for?
import time


class FlaskPool(object):

    def __init__(self, ctor, dtor, maxn, name):
        """Create a pool, given a constructor, destructor and max size."""
        self.lock = _thread.allocate_lock()	
        self.ctor = ctor
        self.dtor = dtor
        self.maxn = maxn
        self.name = name
        self.total = 0
        self.pool = []

    def status(self):
        """Returns (waiting in pool, total created)."""
        return (len(self.pool), self.total)

    def get(self):
        """Get an object from pool.  Up to maxn objects are lazily created."""
        with self.lock:
            if len(self.pool) == 0:
                if self.total >= self.maxn:
                    return None
                obj = self.ctor(self.total + 1)
                self.pool.append(obj)
                self.total += 1
            return self.pool.pop()

    def getw(self, w=0.1, max=None):	
        """Get an object from pool, waiting up to max seconds.  Up to maxn objects are lazily created."""
        # None is returned if there's no object in a maxn-sized to pool.
        tw = 0
        obj = self.get()
        while obj is None:
            if max and (tw > max):
                return obj
            time.sleep(w)
            tw += w
            obj = self.get()
        return obj

    def ret(self, obj):
        """Return an object to pool."""
        if obj is None:                     # 0 OK.
            return
        with self.lock:
            self.pool.append(obj)

    def zap(self, obj):
        """Apply destructor to an object."""
        # Note: object must not be in pool (not checked).
        if not obj:
            return 
        with self.lock:
            self.dtor(obj)
            self.total -= 1
            if self.total < 0:
                raise ValueError('%s.zap: %d < 0' % (self.name, self.total))

    def zapall(self):
        """Apply destructor to all objects in pool."""
        with self.lock:
            while len(self.pool) > 0:
                obj = self.pool.pop()
                self.dtor(obj)
                self.total -= 1
                if self.total < 0:
                    raise ValueError('%s.zapall: %d < 0' % (self.name, self.total))
