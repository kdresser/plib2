###
### l_xlog_levels_prefixes: 
###	Globals for logging levels and prefixes as used 
###       generally and by xlog in particular.
###     Levels are the Python's log levels divided by 50
###       and augmented with the EXTRA level (6).
###     Prefixes are arbitrary, with a carryover of 
###       info (trace), warning and error from earlier
###       Delphi programming days.
###

LOG_LEVEL_NOT_SET   = 0         # '__ '
LOG_LEVEL_DEBUG     = 1         # '.. '
LOG_LEVEL_INFO      = 2         # '-- '
LOG_LEVEL_WARNING   = 3         # '>> '
LOG_LEVEL_ERROR     = 4         # '** '
LOG_LEVEL_CRITICAL  = 5         # '!! '
LOG_LEVEL_EXTRA     = 6         # '~~ '

LOG_PREFIX_NOT_SET  = '__ '     # 0
LOG_PREFIX_DEBUG    = '.. '     # 1
LOG_PREFIX_INFO     = '-- '     # 2
LOG_PREFIX_WARNING  = '>> '     # 3
LOG_PREFIX_ERROR    = '** '     # 4
LOG_PREFIX_CRITICAL = '!! '     # 5
LOG_PREFIX_EXTRA    = '~~ '     # 6

LOG_LEVEL_TO_PREFIX = {
    LOG_LEVEL_NOT_SET  : LOG_PREFIX_NOT_SET, 
    LOG_LEVEL_DEBUG    : LOG_PREFIX_DEBUG,
    LOG_LEVEL_INFO     : LOG_PREFIX_INFO, 
    LOG_LEVEL_WARNING  : LOG_PREFIX_WARNING, 
    LOG_LEVEL_ERROR    : LOG_PREFIX_ERROR, 
    LOG_LEVEL_CRITICAL : LOG_PREFIX_CRITICAL, 
    LOG_LEVEL_EXTRA    : LOG_PREFIX_EXTRA, 
    }

LOG_PREFIX_TO_LEVEL = {
    LOG_PREFIX_NOT_SET  : LOG_LEVEL_NOT_SET, 
    LOG_PREFIX_DEBUG    : LOG_LEVEL_DEBUG,
    LOG_PREFIX_INFO     : LOG_LEVEL_INFO, 
    LOG_PREFIX_WARNING  : LOG_LEVEL_WARNING, 
    LOG_PREFIX_ERROR    : LOG_LEVEL_ERROR, 
    LOG_PREFIX_CRITICAL : LOG_LEVEL_CRITICAL, 
    LOG_PREFIX_EXTRA    : LOG_LEVEL_EXTRA, 
    }
