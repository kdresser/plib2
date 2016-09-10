#! !P3!

# Misc date, time functions.

import calendar, datetime, math, time

DOW = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
SECSPERDAY = 24 * 60 * 60
dtEPOCH = datetime.datetime.utcfromtimestamp(0)

# UTC unix time now.  Has fractional seconds.
def utcut():
    """-> UTC Unix Time now.  Uses library time.time()."""   
    return time.time()

# UTC unix time now.  Fractional seconds kludged. 
def utcut_WONKY():
    """-> UTC Unix Time now."""
    return datetime.datetime.utcnow().timestamp()     # P3.4
    '''...
    a = datetime.datetime.utcnow()
    b = calendar.timegm(a.utctimetuple())
    c = b + float(a.microsecond) / 1000000
    return c
    ###return calendar.timegm(datetime.datetime.utcnow().utctimetuple())
    #                                           ^        ^ drops/truncates fractional secs
    #                                           ^ has fractional secs
    # ??? datetetime.datetime.utcnow()[6] is microsecnds?
    ...'''

# UTC Unix Time -> LOCal Unix Time.
def utc2loc(uu):
    """UTC UT to LOCal UT."""
    ff, ii = math.modf(uu)
    return calendar.timegm(time.localtime(ii)) + ff

# Local time unix time now.
def locut(uu=None):
    """-> LOCal Unix Time now."""
    if not uu:
        uu = utcut()
    return utc2loc(uu)

# A seconds-resolution (rounded) ISO date & time.  Assumes UTC input.  Defaults to a space date-time separator.
def ut2iso(ut, sep=' '):
    """UTC UT (rounded seconds) -> 'YYYY-MM-DD HH:MM:SS'. No TZ or offset."""
    tm = time.gmtime(round(ut))
    return '%04d-%02d-%02d%s%02d:%02d:%02d' % \
        (tm.tm_year, tm.tm_mon, tm.tm_mday, sep, tm.tm_hour, tm.tm_min, tm.tm_sec)

# An ISO date & time with fraction seconds.  Assumes naive UTC input.  
# Defaults to a space for the date-time separator.
# Defaults to 4 decimal digits.  E.g., Setting ndd=1 will produce deciseconds.
def ut2isofs(ut, sep=' ', ndd=4):
    """UTC UT -> 'YYYY-MM-DD HH:MM:SS.1234'. No TZ or offset."""
    b, a = math.modf(ut)   # Fractional part, whole part.
    tm = time.gmtime(a)
    fs = (('%%.%df' % ndd) % b)[1:]
    return '%04d-%02d-%02d%s%02d:%02d:%02d%s' % \
        (tm.tm_year, tm.tm_mon, tm.tm_mday, sep, tm.tm_hour, tm.tm_min, tm.tm_sec, fs)

# ISO date.  Unix Date input (seconds since Unix epoch).
def ud2iso(ud):
    """UD -> 'YYYY-MM-DD'."""
    z = time.gmtime(ud * SECSPERDAY)      # -> UT
    return '%04d-%02d-%02d' % (z.tm_year, z.tm_mon, z.tm_mday)

def iso2ut(iso, sep=' '):
    fmt = '%%Y-%%m-%%d%s%%H:%%M:%%S' % sep
    dt = datetime.datetime.strptime(iso, fmt)
    tt = dt.timetuple()
    ut = calendar.timegm(tt)
    return ut

# Day-of-week (integer) from UTC input.
def utcut2dow(ut):
    """UTC UT -> day-of-week: 0..6 (Mon..Sun)."""
    return time.gmtime(ut).tm_wday

# Day-of-week (integer) from UD input.
def ud2dow(ud):
    return utcut2dow(ud * SECSPERDAY)   # -> UT

# Day-of-week (str).  Assumes UTC input.
def utcut2DOW(ut):
    """UTC UT -> day-of-week: Mon..Sun."""
    return DOW[utcut2dow(ut)]

# Day-of-week (str) from UD input.
def ud2DOW(ud):
    return utcut2DOW(ud * SECSPERDAY)   # -> UT

def iso2yyyymmdd(iso):
    # '2015-07-15 23:15:18' -> yyyymmdd
    return iso[:4]+iso[5:7]+iso[8:10]

def iso2yymmdd(iso):
    # '2015-07-15 23:15:18' -> yymmdd
    return iso[2:4]+iso[5:7]+iso[8:10]

def iso2hhmmss(iso):
    # '2015-07-15 23:15:18' -> hhmmss
    return iso[11:13]+iso[14:16]+iso[17:19]

def yyyymmdd2ud(ymd):
    dt = datetime.datetime.strptime(ymd, '%Y%m%d')
    tt = dt.timetuple()
    ut = calendar.timegm(tt)
    ud = ut / SECSPERDAY
    return int(ud)

def ut2doy(ut):
    dt = datetime.datetime.utcfromtimestamp(ut)
    tt = dt.timetuple()
    return tt.tm_yday

def ud2doy(ud):
    dt = datetime.datetime.utcfromtimestamp(ud2ut(ud))
    tt = dt.timetuple()
    return tt.tm_yday

def utcut2doy(uu):
    dt = datetime.datetime.utcfromtimestamp(uu)
    tt = dt.timetuple()
    return tt.tm_yday

def ut2ud_BAD(ut):
    a = datetime.datetime.utcfromtimestamp(ut)
    b = datetime.datetime(a.year, a.month, a.day)
    c = b.timetuple()
    d = calendar.timegm(c)
    return d

def ut2ud(ut):
    a = datetime.datetime.utcfromtimestamp(ut)
    b = a - dtEPOCH
    ud = b.days
    return ud

def ud2ut(ud):
    a = datetime.timedelta(ud)
    b = dtEPOCH + a
    c = b.timetuple()
    ut = calendar.timegm(c)
    return ut

'''!!!

# A subset of l_dt (above) for Flask f_helpers.

import math, time

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

!!!'''
