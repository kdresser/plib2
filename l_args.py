#! !P3!

###
### Process command line and ini file arguments.
###   1. For command line args, uses either:
###        Docopt: see get_sysargvs(_doc=..., _docopt=True)
###        Simple KVs: see get_sysargvs(_clkvs=True)
###      SYSARGVS dict contains command line results.
###   2. Uses configparser for init file args.
###        INI object contains configparser results.
###      ARGS is a dict containing any INI['args'][*] 
###        section plus updates from SYSARGVS.
###   ARGS is the final dict of arguments.
###

import os, sys, configparser
import docopt
import l_misc as _m

INI = None          # Contains [args], plus possibly other sections.
SYSARGVS = None     # Arguments from command line (via docopt).
ARGS = {}	        # Final arguments, from INI[args] with SYS.ARGV overrides via DOCOPT.
                    # Note: Additional sections (other than [args]) must be accessed via INI.

(_ME, _), _VERSION = os.path.splitext(os.path.split(sys.argv[0])[1]), 'unknown'

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
            # --qqsv=	-> ''
            # --qqsv	-> None
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
# 150914: lowercase.
def get_clkvs(lowercase=True):      
    clkvs = {}
    try:
        for kv in sys.argv[1:]:
            if '=' in kv:
                k, v = kv.split('=', 1)
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
        SYSARGVS = docopt.docopt(docstr, help=help, version=_VERSION)
        # (Will do a sys.exit() after printing help.)
    elif clkvs:
        SYSARGVS = get_clkvs()
    else:
        SYSARGVS = {}

def get_args(doc=None, version=None, me=None, help=True, docopt=True, clkvs=False, inipfn=None):
    global ARGS, INIPFN, _ME, _VERSION, CWD
    try:
        if me:
            _ME = me
        _VERSION = version
        if inipfn:
            INIPFN = inipfn
        else:
            INIPFN = _ME + '.ini'
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
            ARGS['--me'] = _ME
            ARGS['--version'] = _VERSION
            ARGS['cwd'] = CWD                   # Record environment directory.
            ARGS['inipfn'] = INIPFN             # Record what was used.
            return _ME
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
    x = str(x).strip().upper()
    if x in ('0', 'F', 'N') or x in ('FALSE', 'NO'):
        return False
    if x in ('1', 'T', 'Y') or x in ('TRUE', 'YES'):
        return True
    return default

def x2float(x, default=None):
    try:    return float(str(x).strip())
    except: return default

def x2int(x, default=None):
    try:    return int(str(x).strip())
    except: return default
