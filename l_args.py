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

import os, sys, configparser
import docopt as _docopt
import l_dt as _dt
import l_misc as _m

INI = None          # Contains [args], plus possibly other sections.
SYSARGVS = None     # Arguments from command line (via docopt).
ARGS = {}           # Final arguments, from INI[args] with SYS.ARGV overrides via DOCOPT.
                    # Note: Additional sections (other than [args]) must be accessed via INI.

(ME, _), VERSION = os.path.splitext(os.path.split(sys.argv[0])[1]), 'unknown'

# Read INI file.  DNE is OK.
def get_ini():
    global INIPFN, INI
    INIPFN = SYSARGVS.get('--ini') if SYSARGVS.get('--ini') else INIPFN
    try:
        if not os.path.isfile(INIPFN):
            INI = None
            #$#print('>> no ini:', INIPFN)#$#
        else:
            #$#print('-- ini:', INIPFN)#$#
            INI = configparser.ConfigParser(allow_no_value=True)
            INI.read(INIPFN)
            # --qqsv=   -> ''
            # --qqsv    -> None
            if False:
                for s, _ in INI.items():
                    #$#print('SECTION:', s)#$#
                    for k, v in INI[s].items():
                        #$#print('  ', k, '=', v)#$#
                        pass
    except Exception as E:
        errmsg = str(E)
        #$#print('**', errmsg)#$#
        INI = None
        raise
        ''''...
        #$#print('**', errmsg)#$#
        #$#print('>> no ini file')#$#
        INI = None
        ...'''
    finally:
        1/1

# A simple KV parse (text-only) of sys.argv.
# V's are strings, but no '=' -> True.
# 150914: lowercase keys.
def get_clkvs(lowercase=True):
    clkvs = {}
    try:
        for kv in sys.argv[1:]:
            if '=' in kv:
                k, v = kv.split('=', 1)
                v = v.strip()               # ??? Redundant?
            else:
                k, v = kv, True
            if lowercase:
                k = k.lower()
            clkvs[k] = v
    finally:
        return clkvs

def get_sysargvs(docstr=None, help=None, docopt=True, clkvs=False):
    global SYSARGVS
    if   docopt:
        # Use docopt to parse sys.argv.
        SYSARGVS = _docopt.docopt(docstr, help=help, version=VERSION)
        # (Will do a sys.exit() after printing help.)
    elif clkvs:
        SYSARGVS = get_clkvs()
    else:
        SYSARGVS = {}

def get_args(doc=None, version=None, me=None, help=True, docopt=True, clkvs=False, inipfn=None):
    global ARGS, INIPFN, ME, VERSION, CWD
    try:
        if me:
            ME = me
        VERSION = version
        if inipfn:
            INIPFN = inipfn
        else:
            INIPFN = ME + '.ini'
        CWD = os.getcwd()
        get_sysargvs(docstr=doc, help=help, docopt=docopt, clkvs=clkvs)
        get_ini()
        # Build ARGS from INI[args] and SYSARGVS (overrides).
        try:
            if INI:
                ARGS = dict([(k, True if v is None else v) for k, v in INI['args'].items()])
            else:
                ARGS = {}
            ###ARGS.update(dict([(k, v) for k, v in SYSARGVS.items()])) # !!! None's clobber!
            for k, v in SYSARGVS.items():
                if v is not None:
                    ARGS[k] = v
            ARGS['--me'] = ME
            ARGS['--version'] = VERSION
            ARGS['cwd'] = CWD                   # Record environment directory.
            ARGS['inipfn'] = INIPFN             # Record what was used.
            return ME
        except Exception as E:
            raise
    except Exception as E:
        errmsg = 'get_args: %s @ %s' % (E, _m.tblineno())
        1/1
        raise
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
            raise Exception(errmsg)
        else:
            dflt()
            return default
    x = ARGS[key]
    if False and x == '':
        dflt()
        return default
    if not xisbool(x):
        errmsg = '{} / {} is not boolean: "{}"'.format(key, name, x)
        raise Exception(errmsg)
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
            raise Exception(errmsg)
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
        raise Exception(errmsg)
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
            raise Exception(errmsg)
        else:
            dflt()
            return default
    x = ARGS[key]
    if False and x == '':
        dflt()
        return default
    if not xisint(x):
        errmsg = '{} / {} is not integer: "{}"'.format(key, name, x)
        raise Exception(errmsg)
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
            raise Exception(errmsg)
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
