#> !P3!

###
### Process command line and ini file arguments.
###   1. For command line args, uses either:
###        Docopt: see get_sysargvs(_doc=..., _docopt=True)
###        Simple KVs: see get_sysargvs(_clkvs=True)
###      SYSARGVS dict contains command line results.
###   2. Uses configparser for ini file args.
###        INI object contains configparser results.
###      ARGS is a dict containing any INI['args'][*]
###        section plus updates from SYSARGVS.
###   ARGS is the final dict of arguments.
###
### 160121: Deprecating docopt (in favor of clkvs).
###

import os, sys, configparser
import l_dt as _dt
import l_misc as _m

'''...
CWD = None          # Being phased out, along with docopt.
VERSION = None      # ...

ME = None           # Determined in get_args().
INIPFN = None       # If used, provides defaults for clkvs.
INI = None          # Contains [args], plus possibly other sections.
SYSARGVS = None     # Arguments from command line (via clkvs).
ARGS = None         # Final arguments, from INI[args] with SYS.ARGV 
                    # overrides via clkvs. INI can be used to 
                    # access sections other than [args].
...'''

def GLOBAL_INITS():
    global CWD, VERSION
    global ME, INIPFN, INI, SYSARGVS, ARGS
    CWD = VERSION = None
    ME = INIPFN = INI = None
    ###---# ??? Might {} be a better default for INI?
    SYSARGVS, ARGS = {}, {}

# Read INI file if INIPFN.
def get_ini():
    global INIPFN, INI
    1/1
    if INI or not INIPFN or not os.path.isfile(INIPFN):
        return
    me = 'get_ini({})'.format(INIPFN)
    try:
        INI = configparser.ConfigParser(allow_no_value=True)
        # something =   -> ''
        # something     -> None
        INI.read(INIPFN)
        if False:
            for s, _ in INI.items():
                #$#print('SECTION:', s)#$#
                for k, v in INI[s].items():
                    #$#print('  ', k, '=', v)#$#
                    pass
    except Exception as E:
        errmsg = '{}: {}'.format(me, E)
        raise RuntimeError(errmsg)
    finally:
        1/1

# A simple KV parse (text-only) of sys.argv.
# V's are strings, but no '=' -> True.
# 150914: lowercase keys.
def get_clkvs(lowercase=True):
    1/1
    clkvs = {}
    for kv in sys.argv[1:]:
        if '=' in kv:
            k, v = kv.split('=', 1)
            v = v.strip()               # ??? Redundant?
        else:
            # This matches ini file behaviour (as used).
            k, v = kv, True     
            # TODO: ??? -/+ prefixes?
        if lowercase:
            k = k.lower()
        clkvs[k] = v
    1/1
    return clkvs

### get_sysargvs(docstr=None, help=None, docopt=True, clkvs=False): # Phasing out.
def get_sysargvs(docstr=None, help=None, docopt=False, clkvs=True):
    global SYSARGVS
    1/1
    if   docopt:
        import docopt as _docopt
        # Use docopt to parse sys.argv.
        SYSARGVS = _docopt.docopt(docstr, help=help, version=VERSION)
        # (Will do a sys.exit() after printing help.)
    elif clkvs:
        SYSARGVS = get_clkvs()
    else:
        SYSARGVS = {}
    1/1

# Deprecated docopt -> a suffixed version using it.
def get_args_docopt(doc=None, version=None, me=None, help=True, docopt=True, clkvs=False, inipfn=None, useini=True):
    global ARGS, ME, INIPFN, USEINI, INI, VERSION, CWD
    1/1
    try:
        GLOBAL_INITS()
        if me:
            ME = me
        VERSION = version
        USEINI = useini
        if inipfn:
            INIPFN = inipfn
        else:
            INIPFN = ME + '.ini'
        CWD = os.getcwd()
        get_sysargvs(docstr=doc, help=help, docopt=docopt, clkvs=clkvs)
        get_ini()
        # Build ARGS from INI[args] and 
        # SYSARGVS (overrides via docopt).
        try:
            if USEINI and INI:
                ARGS = dict([(k, True if v is None else v) for k, v in INI['args'].items()])
            else:
                ARGS = {}
            # None's from docopt clobber ini values.
            ###ARGS.update(dict([(k, v) for k, v in SYSARGVS.items()]))
            for k, v in SYSARGVS.items():
                if v is not None:
                    ARGS[k] = v
            return ME
        except Exception as E:
            raise
    except Exception as E:
        errmsg = 'get_args: %s @ %s' % (E, _m.tblineno())
        1/1
        raise
    finally:
        1/1

# New implementation uses command line kv's and optionally, an ini file.
def get_args(me=None, inipfn=None, useini=True):
    global SYSARGVS, ARGS, INIPFN, INI, ME, VERSION
    1/1
    try:
        GLOBAL_INITS()

        # Hide/disable old version stuff.
        doc = version = None
        help = docopt = False
        clkvs = True

        # Determine ME.
        if me:
            ME = me
        else:
            (ME, _) = os.path.splitext(os.path.split(sys.argv[0])[1])

        # Get command line arguments, holding them aside.
        1/1
        get_sysargvs(docstr=doc, help=help, docopt=docopt, clkvs=clkvs)
        SYSARGVS = SYSARGVS
        1/1

        # Determine INI, if used.
        if useini:
            INIPFN = ME + '.ini'
            INIPFN = SYSARGVS.get('ini', INIPFN)
            INIPFN = inipfn or INIPFN
            get_ini()
        INI = INI
        1/1

        # ARGS <- combine INI [args] and SYSARGVS (clkvs).
        1/1
        try:    ARGS = dict([(k, True if v is None else v) for k, v in INI['args'].items()])
        #                        ^^^          ^^^
        #                                     ^^^ When ini kv has no = and no v.
        except: ARGS = {}
        ARGS = ARGS
        1/1
        ARGS.update(dict([(k, v) for k, v in SYSARGVS.items()]))
        ARGS = ARGS
        1/1

        return ME

    except Exception as E:
        1/1
        errmsg = '{}: {} @ {}' % (me, E, _m.tblineno())
        raise RuntimeError(errmsg)
    finally:
        1/1

# String to bool, float, int.

def x2bool(x, default=False):
    try:
        x = str(x).strip().upper()
        if x in ('0', 'F', 'N', 'FALSE', 'NO'):
            return False
        if x in ('1', 'T', 'Y', 'TRUE', 'YES'):
            return True
    except:
        return default
    return default

def xisbool(x):
    try:
        x = str(x).strip().upper()
        return x in ('0', 'F', 'N', 'FALSE', 'NO',
                     '1', 'T', 'Y', 'TRUE', 'YES')
    except:
        return False

def x2float(x, default=None):
    try:    return float(str(x).strip())
    except: return default

def xisfloat(x):
    try:
        _ = float(str(x).strip())
        return True
    except:
        return False

def x2int(x, default=None):
    try:    return int(str(x).strip())
    except: return default

def xisint(x):
    try:
        _ = int(str(x).strip())
        return True
    except:
        return False

_sl = None      
def argSL(sl):  
    """Set SimpleLogger for module usage."""
    global _sl
    _sl = sl

def argBoolean(key, name, default=None, must=False):
    def dflt():
        msg = '{} / {} defaulting to {}'.format(key, name, default)
        if _sl:
            _sl.warning(msg)

    me = 'argBoolean'
    if not key in ARGS:
        if must:
            errmsg = 'no {} / {}'.format(key, name)
            raise RuntimeError(errmsg)
        else:
            dflt()
            return default
    x = ARGS[key]
    if False and x == '':
        dflt()
        return default
    if not xisbool(x):
        errmsg = '{} / {} is not boolean: "{}"'.format(key, name, x)
        raise ValueError(errmsg)
    y = x2bool(x)
    msg = '{} / {} "{}" -> {}'.format(key, name, x, y)
    if _sl:
        _sl.info(msg)
    return y

def argFloat(key, name, default=None, must=False):
    def dflt():
        msg = '{} / {} defaulting to {}'.format(key, name, default)
        if _sl:
            _sl.warning(msg)

    me = 'argFloat'
    if not key in ARGS:
        if must:
            errmsg = 'no {} / {}'.format(key, name)
            raise RuntimeError(errmsg)
        else:
            msg = '{} / {} defaulting to {}'.format(key, name, default)
            if _sl:
                _sl.warning(msg)
            return default
    x = ARGS[key]
    if False and x == '':
        dflt()
        return default
    if not xisfloat(x):
        errmsg = '{} / {} is not float: "{}"'.format(key, name, x)
        raise ValueError(errmsg)
    y = x2float(x)
    msg = '{} / {} "{}" -> {}'.format(key, name, x, y)
    if _sl:
        _sl.info(msg)
    return y

def argInteger(key, name, default=None, must=False):
    def dflt():
        msg = '{} / {} defaulting to {}'.format(key, name, default)
        if _sl:
            _sl.warning(msg)

    me = 'argInteger'
    if not key in ARGS:
        if must:
            errmsg = 'no {} / {}'.format(key, name)
            raise RuntimeError(errmsg)
        else:
            dflt()
            return default
    x = ARGS[key]
    if False and x == '':
        dflt()
        return default
    if not xisint(x):
        errmsg = '{} / {} is not integer: "{}"'.format(key, name, x)
        raise ValueError(errmsg)
    y = x2int(x)
    msg = '{} / {} "{}" -> {}'.format(key, name, x, y)
    if _sl:
        _sl.info(msg)
    return y

def argString(key, name, default=None, must=False):
    def dflt():
        msg = '{} / {} defaulting to "{}"'.format(key, name, default)
        if _sl:
            _sl.warning(msg)

    me = 'argString'
    if not key in ARGS:
        if must:
            errmsg = 'no {} / {}'.format(key, name)
            raise RuntimeError(errmsg)
        else:
            dflt()
            return default
    x = ARGS[key]
    y = x.replace('~me~', ME)
    if True or y == x:
        msg = '{} / {} -> "{}"'.format(key, name, y)
    else:
        msg = '{} / {} "{}" -> "{}"'.format(key, name, x, y)
    if _sl:
        _sl.info(msg)
    return y

def sep_(sl, local, name, width, prefix, fillchar):
    """Make separator line for sepBegin, sepEnd."""
    # sl Falsey -> separator line is returned but not logged.
    if local:   ts, sep = _dt.locut(_dt.utcut()), 'L'
    else:       ts, sep = _dt.utcut(), 'U'
    sep = '{}{} '.format(prefix, _dt.ut2iso(ts, sep=sep))
    if name:
        sep += '{} '.format(name)
    n = width - len(sep)
    if n > 0:
        sep += n * fillchar
    if sl:
        sl._log(sep)
    return sep

def sepBegin(sl, local=True, name=None, width=79):
    #                                         ^^
    """Make a beginning separator line."""
    # sl Falsey -> separator line is returned but not logged.
    return sep_(sl, local=local, name=name, width=width, prefix='## B ', fillchar='-')

def sepEnd  (sl, local=True, name=None, width=79):
    #                                         ^^
    """Make an ending separator line."""
    # sl Falsey -> separator line is returned but not logged.
    return sep_(sl, local=local, name=name, width=width, prefix='## E ', fillchar='=')
