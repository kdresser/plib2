# -*- coding: latin-1 -*-

import os, socket, time, random
import pymysql

from f_pool import *
from f_log import *

LOG_HP = LOG_PFN = ST_DB_CFG = None

# Constructors, destructors for logfile, logsocket and database connections.

def lf_ctor(n):
  ###pfn = app.config['LOG_PFN'].replace('~lfn~', ('%02d' % n))
  pfn = LOG_PFN.replace('~lfn~', ('%02d' % n))
  return open(pfn, mode='at', buffering=1, encoding='utf-8')		# Append.  Line buffering.

def lf_dtor(lf):
  lf.close()

def ls_ctor(n):
  ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  ls.settimeout(0.25)		# Be quick.
  ###ls.connect(app.config['LOG_HP'])
  ls.connect(LOG_HP)
  ls.settimeout(0)		# Non-blocking.
  return ls

def ls_dtor(ls):
  ls.shutdown(socket.SHUT_WR)
  ls.close()

def db_ctor(n):
  ###return pyodbc.connect(app.config['ST_DB_CS'])
  ###return pyodbc.connect(ST_DB_CS)
  return pymysql.connect(**ST_DB_CFG)

def db_dtor(db):
  db.close()

# Startup, shutdown of connection pools.

lfPool = lsPool = dbPool = None

def startup_pools():
  global lfPool, lsPool, dbPool
  lfPool = FlaskPool(lf_ctor, lf_dtor, 12)
  lsPool = FlaskPool(ls_ctor, ls_dtor, 12)
  dbPool = FlaskPool(db_ctor, db_dtor, 12)
  
def shutdown_pools():
  lfPool.zapall()
  lsPool.zapall()
  dbPool.zapall()

def main():
  global LOG_HP, LOG_PFN, ST_DB_CFG

  # Local globals standing in for app.config['*'].
  if   os.getenv('LOCATION') == 'HOMEDEV':
    LOG_HP = ('192.168.100.1', 222)
    LOG_PFN = 'C:/ZZ/logs/pix-~lfn~.log'
    ST_DB_CFG = {'user': 'root', 'password': 'woofuswoofus', 'host': '192.168.100.3', 'database': 'ST0'}
  elif os.getenv('LOCATION') == 'HOMEPRD':
    # The following 2 are not quite production...
    LOG_HP = ('192.168.100.1', 222)		
    LOG_PFN = '/home/kelly/pjs/PIX/logs/pix-~lfn~.log'
    ST_DB_CFG = {'user': 'root', 'password': 'woofuswoofus', 'host': '192.168.100.3', 'database': 'ST0'}
  else:
    print('bad LOCATION: %s' % repr(os.getenv('LOCATION')))

  print()
  print('main...')

  print()
  print('startup_pools...')
  startup_pools()

  print()
  print('exercise pools...')
  for x in range(42):
    lfs, lss, dbs = [], [], []
    for y in range(10):
      lfs.append(lfPool.get())
      lss.append(lsPool.get())
      dbs.append(dbPool.get())
    random.shuffle(lfs)
    random.shuffle(lss)
    random.shuffle(dbs)
    for y in range(10):
      lfPool.ret(lfs.pop())
      lsPool.ret(lss.pop())
      dbPool.ret(dbs.pop())
    print('%02d' % (x+1))

  print()
  print('test socket log...')
  try:
    for x in range(42):
      #
      lf = lfPool.get()
      ls = lsPool.get()
      db = dbPool.get()
      log = mLog(lf, ls)
      #
      z = 'msg.%02d' % (x+1)
      print(z)
      log.log(z)
      #
      lfPool.ret(lf)
      lsPool.ret(ls)
      dbPool.ret(db)
      del log    
      #
      ###time.sleep(0.001)
  except Exception as E:
    print('**', str(E))
  else:
    print('...test socket log')

  print()
  print('shutdown_pools...')
  shutdown_pools()

  print()
  print('done')

if __name__ == '__main__':
  main()


