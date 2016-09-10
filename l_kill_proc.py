#
# Kill process (by name, for now).
# For Windows now and for Linux later.
#

# Kills a process by process name
#
# Uses the Performance Data Helper to locate the PID, then kills it.
# Will only kill the process if there is only one process of that name
# (eg, attempting to kill "Python.exe" will only work if there is only
# one Python.exe running.  (Note that the current process does not
# count - ie, if Python.exe is hosting this script, you can still kill
# another Python.exe (as long as there is only one other Python.exe)

# Really just a demo for the win32pdh(util) module, which allows you
# to get all sorts of information about a running process and many
# other aspects of your system.

import sys

# Win/Linux/Unknown?
if sys.platform.startswith('win'):
    import win32api, win32pdhutil, win32con, sys
    SP = 'W'
elif sys.platform.startswith('linux'):
    import psutil
    SP = 'L'
else: 
    SP = sys.platform

def killProcByName(procname):
    # Note: Windows procname is not case sensitive.

    # Win?
    if SP == 'W':

        try:
            win32pdhutil.GetPerformanceAttributes('Process', 'ID Process', procname)
        except:
            pass

        try:
            pids = win32pdhutil.FindPerformanceAttributesByName(procname)
        except Exception as E:
            return [(False, 'win32pdhutil.FindPerformanceAttributesByName E: {}'.format(E))]

        # Don't kill self.
        try:
            pids.remove(win32api.GetCurrentProcessId())
        except ValueError:
            pass

        if len(pids) == 0:
            return [(False, 'cannot find procname: {}'.format(procname))]

        elif len(pids) > 1:
            return False, 'found {} occurrences of procname: {}'.format(len(pids), procname)

        else:
            handle = win32api.OpenProcess(win32con.PROCESS_TERMINATE, 0, pids[0])
            win32api.TerminateProcess(handle, 0)
            win32api.CloseHandle(handle)
            return True, 'killed procname: {}'.format(procname)

    # Linux?
    elif SP == 'L':
        return False, 'not yet implemented for Linux'

    # Other
    else:
        return False, 'unknown platform: {}'.format(SP)

import win32api, win32pdhutil, win32con, sys

def ORIGINAL_killProcName(procname):
	# Change suggested by Dan Knierim, who found that this performed a
	# "refresh", allowing us to kill processes created since this was run
	# for the first time.
	try:
		win32pdhutil.GetPerformanceAttributes('Process', 'ID Process', procname)
	except:
		pass

	pids = win32pdhutil.FindPerformanceAttributesByName(procname)

	# If _my_ pid in there, remove it!
	try:
		pids.remove(win32api.GetCurrentProcessId())
	except ValueError:
		pass

	if len(pids)==0:
		result = 'Can\'t find %s' % procname
	elif len(pids)>1:
		result = 'Found too many %s pids: %r' % (procname, pids)
	else:
		handle = win32api.OpenProcess(win32con.PROCESS_TERMINATE, 0,pids[0])
		win32api.TerminateProcess(handle,0)
		win32api.CloseHandle(handle)
		result = ''

	return result


'''... psutil no longer works on Win XP
import psutil
def killProcName(procname):
    1/1
    print()
    print('kill:', procname)
    print()
    procs = psutil.pids()
    names = []
    for pid in procs:
        name = p.name()
        names.append((pid, name))
        print('{:10d}  {}'.format(pid, name))
    1/1
    print()
    for pid, name in sorted(pidsnames, cmp=lambda pid, name: name + '|' + str(pid)):
        print('{:10d}  {}'.format(pid, name))
    1/1
    return False
...'''

if __name__ == '__main__':
    if len(sys.argv) > 1:
        for procname in sys.argv[1:]:
            rb, rm = killProcByName(procname)
            if rb:
                print('>>', rm)
            else:
                print('**', rm)
                '''...
                print('Dumping all processes...')
                win32pdhutil.ShowAllProcesses()
                ...'''
    else:
        print('Usage: killProcName.py procname ...')
    1/1

### DC1PD DC1T1 CRU02D1
### GOM
### gom DC1PD DC1T1 CRU02D1
