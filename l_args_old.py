# Copyright 2011, 2012, 2015 by J Kelly Dresser.  All rights reserved.

###
### l_args_old: An early args processor, from when I was young and foolish.
###             Brought up to date with newer l_* modules.
###             Still sketchy.
###
### Extracts K=V's from sys.argv.  They are added to ARGSDICT.
### Some K's cause immediate action:
###     'ps=...' reads a parameters file (recursively) contents into ARGSDICT.
###     'cwd=...' changes the current working directory.
### There are both fancy and simple functions to access the V's.
###

import os
import sys
#!#import l_simple_logger as sl
###from mtwe import *
#!#from mpfn import *
#!#from mpspe2 import *
#!#from mfio import *
###from mdt import *
import l_dt as dt
import l_misc as mi

SL = None           # Will become a simple_logger.

# Module globals.  Users can, but shouldn't, use directly.
ARGSDICT = None     # Generated at first call to argsDict().

###
### argsMe: Return executing filename (no path, no extension).
###
def argsMe():
    return os.path.splitext(os.path.basename(sys.argv[0]))[0]
### argsMe

###
### argsDict
### Returns ARGSDICT if it exists.  If not, it is created first.
### Looks for k=v patterns in args.  If found, k.lower()=v added to ARGSDICT.
### All v's are strings.  User must convert as required.
### 121216: The ps=1 stuff is falling out of use.
###
def argsDict(simple_logger=None, includePSfile=False):
    global ARGSDICT, SL
    if ARGSDICT:
        return ARGSDICT

    def IncludeFile(_pfn):
        global ARGSDICT
        # Include pfn, expecting one k=v per line.
        # Comment lines begin with '#'.
        # Can be nested.
        # No looping check.
        # pfn=:foo.bar+d:\rat.fink
        if not _pfn:
            return
        _pfn = _pfn.strip()
        if not _pfn:
            return
        pfns = _pfn.split('+')
        for pfn in pfns:
            if pfn and pfn[0] == ':':
                pfn = os.path.join(argCWD(), pfn[1:])#!#mnormpath(margCWD(), pfn[1:])
            if os.path.isfile(pfn):#!#misfile(pfn): # Catches all kinds of bad PFNs.
                f = open(pfn, 'rt')#!#mopenr(pfn)
                for r in f:#!#mfgenlines(f):
                    r = r.strip()
                    if (not r) or (r[0] == '#'):
                        continue
                    if not '=' in r:
                        continue
                    k, v = r.split('=', 1)
                    k = k.strip().lower()
                    v = v.strip()
                    # cwd=...?
                    if k == 'cwd':
                        argCWD(v)#!#margCWD(v)
                        continue
                    # ps=...?
                    if k == 'ps':
                        IncludeFile(v)
                    else:
                        ARGSDICT[k] = v
                    pass
                mclose(f)
            pass
        pass
    ### IncludeFile

    SL = simple_logger
    me, errmsg = 'argsDict', ''
    try:
        ARGSDICT = {}
        for x in range(1, len(sys.argv)):       # Skips whoami arg0.
            arg = sys.argv[x]
            ARGSDICT['arg%d' % (x-1)] = arg     # A simple-minded collection of simple arguments.
            if not '=' in arg:
                continue
            k, v = arg.split('=', 1)
            k = k.strip().lower()
            v = v.strip()
            # Immediately obey any cwd=... arguments (current working directory).
            if k == 'cwd':
                argCWD(v)#!#margCWD(v)
                continue
            # Immediately include any ps=... arguments (parameter set file).
            # (This is falling out of favour, but it may come back).
            # v can be a catenation ('+') of filenames.
            # Filenames beginning with ':' have it replaced with the current working directory.
            #   ??? May not be necessary?
            if includePSfile and (k == 'ps'):
                IncludeFile(v)
            else:
                ARGSDICT[k] = v
            pass
        return ARGSDICT
    except Exception as E:
        errmsg = '{}: {} @ {}'.format(me, E, mi.tblineno())
        SL.error(errmsg)
        raise
        '''...
        errmsg, ln = str(E), mtwe.mtblineno()
        raise PgmError2(me, action, errmsg, ln)
        ...'''
### margsDict
#!#margDict = margsDict

###
### Str2Bool - Used mostly by parameter interpretation (below).
###             Has a default for cases where S isn't understandable.
###
def Str2Bool(s, default=None):
    me, errmsg = 'Str2Bool', ''
    #
    if type(default) is not bool:
        if not ((type(s) is str) or (type(s) is unicode)):
            return None
        s = str(s).strip().upper()
        if (s == '1') or (s == 'T') or (s == 'TRUE'):
            return True
        if (s == '0') or (s == 'F') or (s == 'FALSE'):
            return False
        return None
    # Default is a boolean.
    if default:
        # Default to True, with False coming from good input.
        if not s:  s = 'T'
        s = str(s).strip().upper()
        return not ((s == '0') or (s == 'F') or (s == 'FALSE'))
    else:
        # Default to False, with True coming from good input.
        if not s:  s = 'F'
        s = str(s).strip().upper()
        return (s == '1') or (s == 'T') or (s == 'TRUE')
### Str2Bool

def argsBoolean(key, name, default=None, stop=False):
    me, errmsg = 'argsBoolean', ''
    try:
        r = ARGSDICT[key]
    except:
        if stop:
            errmsg = 'no "{}" boolean arg'.format(name)
            raise Exception
            #!#raise PgmStop2(me, action, errmsg)
        else:
            SL.warning('args: {}: {} (default)'.format(name, default))
            return default
    try:
        if r is None:       # But not if ''.
            r = default
        if r == '':
            r = default     # 140524: !!! Added!
        if r:
            r = Str2Bool(r, default)
        SL.info('args: {}: {}'.format(name, r))
        return r
    except Exception as E:
        errmsg = '{}: {} @ {}'.format(me, errmsg if errmsg else E, mi.tblineno())
        SL.error(errmsg)
        raise
    '''...
    except Exception as E:
        errmsg = 'boolean conversion error ({}) for: {}'.format(str(E), r)
        raise PgmStop2(me, action, errmsg)
    ...'''
### argsBoolean
#!#margBoolean = margsBoolean

def argsString(key, name, default=None, stop=False):
    me, errmsg = 'argsString', ''
    try:
        r = ARGSDICT[key].replace('~me~', argsMe())         # !LC!
    except:
        if stop:
            errmsg = 'no "{}" string arg'.format(name)
            raise Exception
            #!#raise PgmStop2(me, action, errmsg)
        else:
            SL.warning('args: {}: {} (default)'.format(name, default))
            return default
    try:
        if r is None:       # But not if ''.
            r = default
        r = str(r)
        SL.info('args: {}: {}'.format(name, r))
        return r
    except Exception as E:
        errmsg = '{}: {} @ {}'.format(me, errmsg if errmsg else E, mi.tblineno())
        SL.error(errmsg)
        raise
    '''...
    except Exception as E:
        errmsg = 'str conversion error ({}) for: {}'.format(str(E), r)
        raise PgmStop2(me, action, errmsg)
    ...'''
### argsString
#!#margsString = margsString

def argsInteger(key, name, default=None, stop=False):
    me, errmsg = 'argsInteger', ''
    try:
        r = ARGSDICT[key]
    except:
        if stop:
            errmsg = 'no "{}" int arg'.format(name)
            raise Exception
            #!#raise PgmStop2(me, action, errmsg)
        else:
            SL.warning('args: {}: {} (default)'.format(name, default))
            return default
    try:
        if (r is None) or (r == ''):    # Include ''.
            r = default
        if r:
            r = int(r)
        SL.info('args: {}: {}'.format(name, r))
        return r
    except Exception as E:
        errmsg = '{}: {} @ {}'.format(me, errmsg if errmsg else E, mi.tblineno())
        SL.error(errmsg)
        raise
    '''...
    except Exception as E:
        errmsg = 'int conversion error ({}) for: {}'.format(str(E), r)
        raise PgmStop2(me, action, errmsg)
    ...'''
### argsInteger
#!#margInteger = margsInteger

def argsFloat(key, name, default=None, stop=False):
    me, errmsg = 'argsFloat', ''
    try:
        r = ARGSDICT[key]
    except:
        if stop:
            errmsg = 'no "{}" float arg'.format(name)
            raise Exception
            #!#raise PgmStop2(me, action, errmsg)
        else:
            SL.info('args: {}: {} (default)'.format(name, default))
            return default
    try:
        if (r is None) or (r == ''):    # Include ''.
            r = default
        if r:
            r = float(r)
        SL.info('args: {}: {}'.format(name, r))
        return r
    except Exception as E:
        errmsg = '{}: {} @ {}'.format(me, errmsg if errmsg else E, mi.tblineno())
        SL.error(errmsg)
        raise
    '''...
    except Exception as E:
        errmsg = 'float conversion error ({}) for: {}'.format(str(E), r)
        raise PgmStop2(me, action, errmsg)
    ...'''
### argsFloat
#!#margFloat = margsFloat

def argsCWDpfx(s):
    if s and s.startswith(':'):
        return os.path.join(argsCWD(), s[1:])###mnormpath(margsCWD(), s[1:])
    else:
        return s
### argsCWDpfx
#!#margCWDpfx = margsCWDpfx

def __fnkvs(s, fnkvs):
    if not fnkvs:
        return s
    for k, v in fnkvs:
        s = s.replace(k, v)
    return s
### __fnkvs

def argsInput(k, binary=False, fnkvs=None):
    me, errmsg = 'argsInput', ''
    ipfn = None
    ifile = None
    try:
        ipfn = ARGSDICT[k].strip().replace('~me~', argsMe())        # !LC!
        ipfn = argCWDpfx(ipfn)#!#margCWDpfx(ipfn)
        ipfn = __fnkvs(ipfn, fnkvs)
    except:
        errmsg = me + ': ' + str(E)
        errmsg = errmsg
        return (ipfn, ifile)
    ifile = open(ipfn, 'r' + ('b' if binary else 't'))#!#mopenr(ipfn, binary=binary)
    return (ipfn, ifile)
### margsInput
#!#margInput = margsInput

def argsOutput(k, append=False, binary=False, fnkvs=None):
    me, errmsg = 'argsOutput', ''
    opfn = None
    ofile = None
    try:
        opfn = ARGSDICT[k].strip().replace('~me~', argsMe())        # !LC!
        opfn = argsCWDpfx(opfn)#!#margCWDpfx(opfn)
        opfn = __fnkvs(opfn, fnkvs)
    except Exception as E:
        errmsg = me + ': ' + str(E)
        errmsg = errmsg
        return (opfn, ofile)
    ofile = open(opfn, ('a' if append else 'w') + ('b' if binary else 't'))#!#mopenw(opfn, append=append, binary=binary)
    return (opfn, ofile)
### argsOutput
#!#margOutput = margsOutput

def startup():
    # A shortcut for the the pre-maininits() section of an app startup.
    me = argsMe()#!#margsMe()
    msg = ''
    #!#msg += '## <%s> %s' % (mNowISOlongCS(True), 50*'-')     # !!! <<<
    msg += '## <%s> %s' % (dt.ut2isofs(dt.locut()), 50*'-')     # !!! <<<
    msg += '\n'
    #!#msg += '%s begins @ %s' % (me, mNowISOlongCS(True))     # !!! <<<
    msg += '%s begins @ %s' % (me, dt.ut2isofs(dt.locut()))     # !!! <<<
    return me, msg
### startup

def shutdown():
    # A shortcut for the the post-main section of an app shutdown.
    me = argsMe()#!#margsMe()
    msg = ''
    #!#msg += '%s   ends @ %s' % (me, mNowISOlongCS(True))     # !!! <<<
    msg += '%s   ends @ %s' % (me, dt.ut2isofs(dt.locut()))     # !!! <<<
    msg += '\n'
    #!#msg += '## <%s> %s' % (mNowISOlongCS(True), 50*'=')     # !!! <<<
    msg += '## <%s> %s' % (dt.ut2isofs(dt.locut()), 50*'=')     # !!! <<<
    return msg
### shutdown

def str2bool(s):
    return istrue(s)#!#misTrue(s)
### str2bool

def istrue(s):
    # Looks specifically for True's (and returns True if found).
    if s:
        s = s.upper().strip()
        if s:
            return (s == 'TRUE') or (s == 'T') or (s == '1') or (s == 'YES') or (s == 'Y')
        pass
    pass
### istrue

def isfalse(s):
    # Looks specifically for False's (and returns True (!) if found).
    if s:
        s = s.upper().strip()
        if s:
            return (s == 'FALSE') or (s == 'F') or (s == '0') or (s == 'NO') or (s == 'N')
        pass
    pass
### isfalse

###
### Simple boolean, integer, float and string getters.
### Any trouble and return is None (or False).
###
def aB(k):
    v = ARGSDICT.get(k.lower())
    return mistrue(v)
### aB

def aF(k):
    v = ARGSDICT.get(k.lower())
    try:    return float(v)
    except: pass
### aF

def aI(k):
    v = ARGSDICT.get(k.lower())
    try:    return int(v)
    except: pass
### aI

def aS(k):
    v = ARGSDICT.get(k.lower())
    return v
### aS

def argsRP(RP, trc=True):
    me, action, errmsg = 'argsRP', 'getting repetition period from: ' + repr(RP), ''
    try:
        if trc:  SL.info(action)
        if not RP:                      # RP begins life as a string.
            RP = 0
        else:
            s = RP[-1].upper()
            if   s.isdigit():
                s = 'S'
                RP += s
            if   s == 'S':  m = 1.0
            elif s == 'M':  m = 60.0
            elif s == 'H':  m = 3600.0
            else:
                errmsg = 'unrecognisable repetition period multiplier: ' + s
                raise Exception
                #!#raise PgmStop2(me, action, errmsg)
            s = RP[:-1]
            try:
                rp = float(s) * m
                RP = rp                 # RP is now a float; seconds.
                msg = 'repetition period is %.1f secs' % (RP)
                if trc:  SL.info(msg)
                return RP
            except:
                errmsg = 'error converting: ' + s
                raise Exception
                #!#raise PgmStop2(me, action, errmsg)
            pass
    except Exception as E:
        errmsg = '{}: {}: {} @ {}'.format(me, action, errmsg if errmsg else E, mi.tblineno())
        SL.error(errmsg)
        raise
    '''...
    except PgmStop2:    raise
    except PgmError2:   raise
    except Exception as E:
        errmsg, ln = str(E), mtwe.mtblineno()
        raise PgmError2(me, action, errmsg, ln)
    ...'''
### argsRP
#!#margRP = margsRP

### END
