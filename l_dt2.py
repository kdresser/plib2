#> !P3!
# Copyright 2011, 2013 by J Kelly Dresser.  All rights reserved.

#
# l_dt2: A straight copy of N:/P/LIB/mdt.py.
#        Needs cleanup.
#        ??? Move some of this to l_dt?
#        ??? Or use a better OS lib?
#

#
# Date amd Time helpers.
#

import os
from math import floor, modf
from time import localtime as loctime, strftime, time as utctime, gmtime, mktime
import calendar as _c
import datetime as _dt
import time as _t
from pytz import timezone
import pytz

# Becomes a dictionary of holidays.
TRADINGHOLIDAYS = None          # Calling InitTradingHolidays() is up to the user.

###UNIX_EPOCH = _dt.datetime(1970, 1, 1, 0, 0, tzinfo = pytz.utc)
NaiveUE = _dt.datetime(1970, 1, 1)

UD2JD = 25569
JD2UD = -UD2JD

# DateTime to Unix Time (naive).
def DT2UT(dt):
    z = dt.replace(tzinfo=None) - NaiveUE
    return (z.microseconds + (z.seconds + z.days * 86400) * 1e6) / 1e6
    ### Alternate (from http://www.seehuhn.de/pages/pdate).
    ###z = mktime(dt.timetuple()) + 1e-6 * dt.microsecond
    ###return z

# DateTime to Unix Time (raw).
# From http://www.seehuhn.de/pages/pdate.
def DT2UT_(dt):
    z = mktime(dt.timetuple()) + 1e-6 * dt.microsecond
    return z

# 140617: Added.
# Unix Time to DateTime (naive).
# No subseconds.
def UT2DT(ut, tz=None):
    st = gmtime(ut)     # struct_time
    dt = _dt.datetime(st.tm_year, st.tm_mon, st.tm_mday, st.tm_hour, st.tm_min, st.tm_sec, 0, tz)
    return dt
    '''...
    z = dt.replace(tzinfo=None) - NaiveUE
    return (z.microseconds + (z.seconds + z.days * 86400) * 1e6) / 1e6
    ...'''

# UTC Unix Time now (naive).
def UTCUT():
    return DT2UT(UTCDT())
    # But, on Windows, outside of DST, this looks OK:
    # But, on Windows,  inside of DST, this looks OK:
    return time.time()

# Local Unix Time now (naive).
def LocalUT():
    return DT2UT(LocalDT())

# UTC Unix Date now (naive).
def UTCUD():
    return UT2UD(UTCUT())

# Local Unix Date now (naive).
def LocalUD():
    return UT2UD(LocalUT())

# UTC DateTime now (naive).
def UTCDT():
    return _dt.datetime.utcnow()

# Local DateTime now (naive).
def LocalDT():
    return _dt.datetime.now()

# 140728: Added.
def ISOlong2DT(ISO, seps=False):
    """ISO long form to DateTime."""
    z = ISO[:8] + '_' + ISO[9:]
    if seps:
        dt = _dt.datetime.strptime(z, "%Y-%m-%d_%H:%M:%S")
    else:
        dt = _dt.datetime.strptime(z, "%Y%m%d_%H%M%S")
    return dt

# 140728: Added.
def ISOlong2UT(ISO, seps=False):
    """ISO long form to Unix time."""
    dt = ISOlong2DT(ISO, seps)
    ut = DT2UT(dt)
    return ut
    ###ut_ = DT2UT_(dt)
    ###return ut, ut_

def UT2ISOymdhms(UT, seps):
    # UT (Unix Time) == GM Time.
    if seps:
        return strftime("%Y-%m-%dT%H:%M:%S", gmtime(UT))
    else:
        return strftime("%Y%m%dT%H%M%S", gmtime(UT))

def str2ISOymdhms(str, seps, T):
    if seps:
        z = strftime("%Y-%m-%dT%H:%M:%S", str)
        if not T:
            z = z.replace('T', ' ')             # Blank.
        return z
    else:
        z = strftime("%Y%m%dT%H%M%S", str)
        if not T:
            z = z.replace('T', '')              # Remove.
        return z

def UT2ISOlong(UT, seps=False, T=False):
    """Unix time to ISO long form."""
    str = gmtime(floor(UT+0.5))
    return str2ISOymdhms(str, seps, T)

def UT2ISOlongDS(UT, seps=False, sep=False, T=False):
    """Unix time to ISO long form, with deciseconds."""
    fUT, iUT = modf(UT)
    str = gmtime(iUT)
    return '%s%s%s' % (str2ISOymdhms(str, seps, T), (',' if sep else ''), ('%.1f' % fUT)[-1:])

def UT2ISOlongCS(UT, seps=False, sep=False, T=False):
    """Unix time to ISO long form, with centiseconds."""
    fUT, iUT = modf(UT)
    str = gmtime(iUT)
    return '%s%s%s' % (str2ISOymdhms(str, seps, T), (',' if sep else ''), ('%.2f' % fUT)[-2:])

def UT2ISOlongMS(UT, seps=False, sep=False, T=False):
    """Unix time to ISO long form, with milliseconds."""
    fUT, iUT = modf(UT)
    str = gmtime(iUT)
    return '%s%s%s' % (str2ISOymdhms(str, seps, T), (',' if sep else ''), ('%.3f' % fUT)[-3:])

def UTCUT2localISOlong(UT, seps=False, T=False):
    """UTC Unix time to local time to ISO long form."""
    ###str = loctime(floor(UT+0.5))
    str = loctime(floor(UT))
    return str2ISOymdhms(str, seps, T)
    '''...
    if seps:
        return strftime("%Y-%m-%dT%H:%M:%S", loctime(floor(UT+0.5)))
    else:
        return strftime("%Y%m%dT%H%M%S", loctime(floor(UT+0.5)))
    ...'''
UT2localISOlong = UTCUT2localISOlong

def UTCUT2localYYYYMMDD(UT):
    loc = loctime(floor(UT))
    return '%04d%02d%02d' % (loc.tm_year, loc.tm_mon, loc.tm_mday)

def UTCUT2localISOlongDS(UT, seps=False, sep=False, T=False):
    """UTC Unix time to local time to ISO long form, with deciseconds."""
    fUT, iUT = modf(UT)
    str = loctime(iUT)
    return '%s%s%s' % (str2ISOymdhms(str, seps, T), (',' if sep else ''), ('%.1f' % fUT)[-1:])
    '''...
    if seps:
        return strftime("%Y-%m-%dT%H:%M:%S", loctime(iUT)) + ('%.1f' % (fUT))[-2:]
    else:
        return strftime("%Y%m%dT%H%M%S", loctime(iUT)) + ('%.1f' % (fUT))[-2:]
    ...'''
UT2localISOlongDS = UTCUT2localISOlongDS

def UTCUT2localISOlongCS(UT, seps=False, sep=False, T=False):
    """UTC Unix time to local time to ISO long form, with centiseconds."""
    fUT, iUT = modf(UT)
    str = loctime(iUT)
    return '%s%s%s' % (str2ISOymdhms(str, seps, T), (',' if sep else ''), ('%.02f' % fUT)[-2:])
    '''...
    if seps:
        return strftime("%Y-%m-%dT%H:%M:%S", loctime(iUT)) + ('%.2f' % (fUT))[-3:]
    else:
        return strftime("%Y%m%dT%H%M%S", loctime(iUT)) + ('%.2f' % (fUT))[-3:]
    ...'''
UT2localISOlongCS = UTCUT2localISOlongCS

def UTCUT2localISOlongMS(UT, seps=False, sep=False, T=False):
    """UTC Unix time to local time to ISO long form, with milliseconds."""
    fUT, iUT = modf(UT)
    str = loctime(iUT)
    return '%s%s%s' % (str2ISOymdhms(str, seps, T), (',' if sep else ''), ('%.03f' % fUT)[-3:])
    '''...
    if seps:
        return strftime("%Y-%m-%dT%H:%M:%S", loctime(iUT)) + (',%.3f' % (fUT))[-3:] # ,
    else:
        return strftime("%Y%m%dT%H%M%S", loctime(iUT)) + (',%.3f' % (fUT))[-3:]     # ,
    ...'''
UT2localISOlongMS = UTCUT2localISOlongMS

def NowISOlong(seps=False, T=False):
    return UTCUT2localISOlong(utctime(), seps, T)

def NowISOlongDS(seps=False, sep=False, T=False):
    return UTCUT2localISOlongDS(utctime(), seps, sep, T)

def NowISOlongCS(seps=False, sep=False, T=False):
    return UTCUT2localISOlongCS(utctime(), seps, sep, T)

def NowISOlongMS(seps=False, sep=False, T=False):
    return UTCUT2localISOlongMS(utctime(), seps, sep, T)

#
# Unix julian dates, named 'UD'.
# Based on Unix epoch.
# Unix seconds timestamps are named 'UT'.
# All naive!
#
# Delphi: Days and fraction since 1899/12/31.
# Name 'JD' here, even though JD is ambiguous.
#

# Unix Time to Unix Date.
def UT2UD(UT):
    return int(UT / 86400)      # Outer int handles leap-seconds.

# Unix Date to Unix Time.
def UD2UT(UD):
    return int(UD) * 86400      # Returning int should be OK.

# Unix Time to SSM.  Rounded to nearest second.
def UT2SSM(UT):
    return int((UT + 0.5) % 86400)

def UD2YYYYMMDD(UD, sep=''):
    return UT2YYYYMMDD(UD2UT(UD), sep)

def UD2YYMMDD(UD, sep=''):
    return UT2YYMMDD(UD2UT(UD), sep)

def UT2YYYYMMDD(UT, sep=''):
    try:    dt = gmtime(UT)
    except: return '????????'
    try:        return '{:04d}{:s}{:02d}{:s}{:02d}'.format(dt[0], sep, dt[1], sep, dt[2])
    except:     return '????????'

def UT2YYMMDD(UT, sep=''):
    return UT2YYYYMMDD(UT, sep)[2:]

def UT2DOW(UT):    # 0..6 for Monday..Sunday
    try:    return gmtime(UT).tm_wday
    except: return -1

def UD2DOW(UD):    # 0..6 for Monday..Sunday
    return UT2DOW(UD2UT(UD))

def UT2MonFri(UT):
    dow = UT2DOW(UT)
    return 0 <= dow <= 4

def UD2MonFri(UD):
    return UT2MonFri(UD2UT(UD))

def YYYYMMDD2UD(ymd):
    try:
        s = ymd[4]
        if not s.isdigit():
            ymd = ymd.replace(s, '')
        t = _c.timegm((int(ymd[0:4]), int(ymd[4:6]), int(ymd[6:8]), 0, 0, 0))
        d = int(t / 86400)              # P2, P3 division.
        return d
    except:
        return None

def YYMMDD2UD(ymd):
    return YYYYMMDD2UD('20' + ymd)

def YYYYMMDD2UT(ymd):
    return UD2UT(mYYYYMMDD(ymd))

def YYMMDD2UT(ymd):
    return UD2UT(YYMMDD(ymd))

def JD2UD(JD):
    try:    return JD - 25569
    except: return None

def UD2JD(UD):
    try:    return UD + 25569
    except: return None

def JD2DOW(JD):    # 0..6 for Monday..Sunday
    return UD2DOW(JD2UD(JD))

def NowJD():
    return UD2JD(LocalUD())

def NowYYMMDD():
    return JD2YYMMDD(NowJD())

def NowYYYYMMDD():
    return JD2YYYYMMDD(NowJD())

def NowSE():  # Rounded to nearest second.
    return UT2SSM(LocalUT())

def YY(jd=None):
        if jd is None:  jd = NowJD()
        return JD2YYMMDD(jd)[0:2]

def MM(jd=None):
        if jd is None:  jd = NowJD()
        return JD2YYMMDD(jd)[2:4]

def DD(jd=None):
        if jd is None:  jd = NowJD()
        return JD2YYMMDD(jd)[4:6]

def StartOfYearJD(jd=None):
        if jd is None:  jd = NowJD()
        return YYMMDD2JD(YY(jd) + '0101')

def EndOfYearJD(jd=None):
        if jd is None:  jd = NowJD()
        return YYMMDD2JD(YY(jd) + '1231')

def StartOfMonthJD(jd=None):
        if jd is None:  jd = NowJD()
        return YYMMDD2JD(YY(jd) + MM(jd) + '01')

def EndOfMonthJD(jd=None):
        jd = StartOfMonthJD(jd)
        jd += 31
        ymd = JD2YYMMDD(jd)
        jd = YYMMDD2JD(ymd[0:4] + '01')
        jd -= 1
        return jd

def JD2YYMMDD(JD, sep=''):
    return UD2YYMMDD(JD2UD(JD), sep)

def JD2YYYYMMDD(JD, sep=''):
    return UD2YYYYMMDD(JD2UD(JD), sep)

def YYYYMMDD2JD(ymd):
    return UD2JD(YYYYMMDD2UD(ymd))

def YYMMDD2JD(ymd):
    return UD2JD(YYMMDD2UD(ymd))

def HHMMSS2SE(hms, sep=''):
    if sep:
        hms = hms.replace(sep, '')
    assert len(hms) == 6, 'mHHMMSS2S: ' + hms
    assert hms.isdigit(), 'mHHMMSS2S: ' + hms
    return 3600 * int(hms[0:2]) + 60 * int(hms[2:4]) + int(hms[4:6])

def MI2HHMM(mi, sep=''):
        z = int(round(mi))
        h = z // 60
        m = z % 60
        return '{:02d}{:s}{:02d}'.format(h, sep, m)

def SE2HHMMSS(se, sep=''):
    z = int(round(se))
    h = z // 3600
    z = z % 3600
    m = z // 60
    s = z % 60
    return '{:02d}{:s}{:02d}{:s}{:02d}'.format(h, sep, m, sep, s)

def DOW2Full(dow):
    if 0 <= dow <= 6:
        return ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][dow]

def DOW2Abr(dow):
    if 0 <= dow <= 6:
        return ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][dow][0:3]

#
# Trading Holidays (UD accessing).
#
def InitTradingHolidays(pfn='n:\etc\HOLIDAYS.ini', noisy=True):
    global TRADINGHOLIDAYS
    me = 'InitTradingHolidays'
    try:
        if not os.path.isfile(pfn):
            if noisy:
                errmsg = '{}: pfn dne: {}'.format(me, pfn)
                raise RuntimeError(errmsg)
            else:
                return
        # Already?
        if TRADINGHOLIDAYS is not None:
            return True
        TRADINGHOLIDAYS = {}
        rc = '??'                   # Region code: CA, US or BF.
        eh = '?'                    # E)arly close, H)oliday.
        1/1
        with open(pfn, 'r') as f:
            for r in f:
                # Clean.
                r = r.strip()
                if not r or r[0] in ';#':
                    1/1
                    continue
                # [EOF]
                if r.upper() == '[EOF]':
                    1/1
                    break
                # [2012-US]
                if len(r) == 9 and r.startswith('['):
                    rc = r[6:8]
                    continue
                # 120102=H
                yymmdd = r[0:6]
                if len(r) == 8 and r[6] == '=' and yymmdd.isdigit():
                    eh = r[7].upper()
                    if eh in 'EH':
                        TRADINGHOLIDAYS[rc+yymmdd] = eh
                    else:
                        if noisy:
                            errmsg = '{}: funny record: {}'.format(me, r)
                            raise RuntimeError(errmsg)
                        else:
                            return
                        pass
                    continue
                # ???
                if noisy:
                    errmsg = '{}: funny record: {}'.format(me, r)
                    raise RuntimeError(errmsg)
                else:
                    return
                pass
        return True
    finally:
        TRADINGHOLIDAYS = TRADINGHOLIDAYS
        1/1

def checkTRADINGHOLIDAYS():
    if not TRADINGHOLIDAYS:
        if not (InitTradingHolidays() and TRADINGHOLIDAYS):
            raise RuntimeError('checkTRADINGHOLIDAYS failed')

def IsTradingDay(UD, region='US'):
    return IsFullTradingDay(UD, region) or IsShortTradingDay(UD, region)

def IsFullTradingDay(UD, region='US'):
    checkTRADINGHOLIDAYS()
    if not UD2MonFri(UD):
        return False
    eh = TRADINGHOLIDAYS.get(region.upper() + UD2YYMMDD(UD))
    return eh is None

def IsShortTradingDay(UD, region='US'):
    checkTRADINGHOLIDAYS()
    if not UD2MonFri(UD):
        return False
    eh = TRADINGHOLIDAYS.get(region.upper() + UD2YYMMDD(UD))
    return eh == 'E'

def IsTradingDayJD(JD, region='US'):
    return IsFullTradingDay(JD2UD(JD), region) or IsShortTradingDay(JD2UD(JD), region)

def IsFullTradingDayJD(jd, region='US'):
    return IsFullTradingDay(JD2UD(jd), region)

def IsShortTradingDayJD(jd, region='US'):
    return IsShortTradingDay(JD2UD(jd), region)

def NextTradingDay(ud, region='US'):
    ud += 1
    while not IsTradingDay(ud, region):
        ud += 1
    return ud

def PrevTradingDay(ud, region='US'):
    ud -= 1
    while not IsTradingDay(ud, region):
        ud -= 1
    return ud

def NextTradingDayJD(jd, region='US'):
    ud = JD2UD(jd) + 1
    while not IsTradingDay(ud, region):
        ud += 1
    return UD2JD(ud)

def PrevTradingDayJD(jd, region='US'):
    ud = JD2UD(jd) - 1
    while not IsTradingDay(ud, region):
        ud -= 1
    return UD2JD(ud)

def CurrNextTradingDay(ud, region='US'):
    return NextTradingDay(ud - 1, region)

def CurrPrevTradingDay(ud, region='US'):
    return PrevTradingDay(ud + 1, region)

def CurrNextTradingDayJD(jd, region='US'):
    return NextTradingDayJD(jd - 1, region)

def CurrPrevTradingDayJD(jd, region='US'):
    return PrevTradingDayJD(jd + 1, region)

def IsFirstTradingOfMonthJD(JD, region='US'):
    z = PrevTradingDayJD(JD, region=region)
    return (JD2YYMMDD(z)[:4] != JD2YYMMDD(JD)[:4])

def SymbolicDate(d):
    me = 'SymbolicDate(%r)' % d
    try:
        if not d:
            return d
        if d.upper() == 'TODAY':
            return NowYYMMDD()
        if d.upper() == 'YYMMDD':
            return os.getenv('YYMMDD')      # !!! Doesn't work in PTVS!
        return d
    except Exception as E:
        errmsg = '{}: {}'.format(me, E)
        raise RuntimeError(errmsg)

#
# SimpleLoHiYMD:    Adjust given Lo/HiYMD to actual trading days.
#                   Force each of LOYMD & HIYMD to be a trading day.
#                   Adjustment directions are parameters.
#
def SimpleLoHiYMD(loymd, hiymd, loadj, hiadj):
    me = 'SimpleLoHiYMD(%r, %r, %r, %r)' % (loymd, hiymd, loadj, hiadj)
    try:
        orig_loymd, orig_hiymd = loymd, hiymd
        assert loymd.isdigit(), 'non-numeric LOYMD: ' + repr(loymd)
        assert hiymd.isdigit(), 'non-numeric HIYMD: ' + repr(hiymd)
        assert loymd and hiymd, 'need both LOYMD and HIYMD'
        assert loymd <= hiymd, 'backwards LOYMD and HIYMD'

        z = loymd
        if   loadj == -1:
            loymd = JD2YYMMDD(CurrPrevTradingDayJD(YYMMDD2JD(loymd)))
        elif loadj == 0:
            loymd = loymd
        elif loadj == +1:
            loymd = JD2YYMMDD(CurrNextTradingDayJD(YYMMDD2JD(loymd)))
        else:
            assert False, 'bad LOADJ: ' + repr(loadj)

        z = hiymd
        if   hiadj == -1:
            hiymd = JD2YYMMDD(CurrPrevTradingDayJD(YYMMDD2JD(hiymd)))
        elif hiadj == 0:
            hiymd = hiymd
        elif hiadj == +1:
            hiymd = JD2YYMMDD(CurrNextTradingDayJD(YYMMDD2JD(hiymd)))
        else:
            assert False, 'bad HIADJ: ' + repr(hiadj)

        return (loymd, hiymd)
    except Exception as E:
        errmsg = '{}: {}'.format(me, E)
        raise RuntimeError(errmsg)
    '''...
    except:
        return (None, None)
    ...'''

if False:
    1/1
    jd = StartOfMonthJD()
    ymd = JD2YYMMDD(jd, '-')
    jd = EndOfMonthJD()
    ymd = JD2YYMMDD(jd, '-')
    1/1
    jd = StartOfMonthJD(YYMMDD2JD('130102'))
    ymd = JD2YYMMDD(jd, '-')
    jd = EndOfMonthJD(YYMMDD2JD('130130'))
    ymd = JD2YYMMDD(jd, '-')
    1/1
    jd = StartOfMonthJD(YYMMDD2JD('130202'))
    ymd = JD2YYMMDD(jd, '-')
    jd = EndOfMonthJD(YYMMDD2JD('130227'))
    ymd = JD2YYMMDD(jd, '-')
    1/1
    jd = StartOfMonthJD(YYMMDD2JD('130302'))
    ymd = JD2YYMMDD(jd, '-')
    jd = EndOfMonthJD(YYMMDD2JD('130330'))
    ymd = JD2YYMMDD(jd, '-')
    1/1
    jd = StartOfMonthJD(YYMMDD2JD('130402'))
    ymd = JD2YYMMDD(jd, '-')
    jd = EndOfMonthJD(YYMMDD2JD('130429'))
    ymd = JD2YYMMDD(jd, '-')
    1/1
    jd = StartOfMonthJD(YYMMDD2JD('131202'))
    ymd = JD2YYMMDD(jd, '-')
    jd = EndOfMonthJD(YYMMDD2JD('131230'))
    ymd = JD2YYMMDD(jd, '-')

if False:
    1/1
    s = NowISOlong(True)
    s = s
    z = utctime()
    z = z
    s = str2ISOymdhms(gmtime(z), seps=False, T=True)
    s = s
    s = str2ISOymdhms(gmtime(z), seps=False, T=False)
    s = s
    s = str2ISOymdhms(gmtime(z), seps=True, T=True)
    s = s
    s = str2ISOymdhms(gmtime(z), seps=True, T=False)
    s = s
    s = UT2ISOlong(z, True, False)
    s = s
    s = UT2ISOlongDS(z, True, True, False)
    s = s
    s = UT2ISOlongCS(z, True, True, False)
    s = s
    s = UT2ISOlongMS(z, True, True, False)
    s = s
    s = UTCUT2localISOlong(z, True, False)
    s = s
    s = UTCUT2localISOlongDS(z, True, True, False)
    s = s
    s = UTCUT2localISOlongCS(z, True, True, False)
    s = s
    s = UTCUT2localISOlongMS(z, True, True, False)
    s = s

if False:
    1/1
    b = InitTradingHolidays()
    1/1
    jd = YYMMDD2JD('160311')
    b = IsTradingDayJD(jd)
    1/1
    jd = YYMMDD2JD('160312')
    b = IsTradingDayJD(jd)
    1/1
