# Copyright 2011, 2015 by J Kelly Dresser.  All rights reserved.
#> !P2! !P3!

###
### l_misc:
###

import sys, time, binascii

P3 = (sys.version_info[0] == 3)
P2 = not P3
try:
	import winsound
	GOTWINSOUND = True
except:
	GOTWINSOUND = False

# Beeps.
def beep(n=1):
	for x in range(n):
		if GOTWINSOUND:
			winsound.Beep(3333, 100)
		time.sleep(0.1)
beeps = beep

# Clicks.
def click():
	if GOTWINSOUND:
		winsound.Beep(2000, 2)
	time.sleep(0.1)
clicks = click

# Traceback line number.
def tblineno():
	try:
		if P2:	return str(sys.exc_traceback.tb_lineno)
		else:	return str(sys.exc_info()[2].tb_lineno)
	except:
		return '???'

# CRC32: Non-incremental CRC of given bytes.
def crc32(b):
    return binascii.crc32(b) & 0xffffffff
    # '0x%08x' % result

# NEW: A simple is-it-new" check & store of KV's.
NEW = {}
def isNew(k, v):
    global NEW
    new = (k not in NEW or v != NEW[k])
    NEW[k] = v
    return new


