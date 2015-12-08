
# !!! This is a poorly named and conceived module!

import math, time

# Cloned into l_helpers...
DOW = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
def utcut():
    """-> UTC Unix Time."""
    return time.time()

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
# ...end of l_helpers cloning.

###
