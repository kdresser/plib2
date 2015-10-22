# -*- coding: latin-1 -*-

import f_helpers as _h

def main():

  # unicodetoascii, toascii
  print()
  print('unicodetoascii, toascii...')
  a = 'abcdé'			# é: 233, \xe9
  b = 'Marc-André'
  print('type(a):', type(a))
  print('a:', a)
  print('type(b):', type(b))
  print('b:', b)
  print('u2a(a):', _h.unicodetoascii(a))
  print("u2a(b, '~'):", _h.unicodetoascii(b, '~'))
  print('ta(a):', _h.toascii(a))
  c = a.encode('latin-1')
  print('type(c):', type(c))
  print('c:', c)
  print('ta(c):', _h.toascii(c))
  print("ta(c.decode('latin-1')):", _h.toascii(c.decode('latin-1')))
  pass

  # nulstr
  print()
  print('nulstr...')
  print("repr(nulstr('')):", repr(_h.nulstr('')))
  print("nulstr('abc'):", _h.nulstr('abc'))
  print("nulstr(b'abc'):", _h.nulstr(b'abc'))
  print('repr(_nulstr(None)):', repr(_h.nulstr(None)))

  # crc32
  print()
  print('crc32...')
  a = 'abc'
  b = b'abc'
  print('a:', a)
  print('b:', b)
  print('crc32(a):', _h.crc32(a))
  print('crc32(b):', _h.crc32(b))

  # fnsplit
  print()
  print('fnsplit...')
  a = None
  (b, c) = _h.fnsplit(a)
  print(a, '->', b, c)
  a = ''
  (b, c) = _h.fnsplit(a)
  print(repr(a), '->', b, c)
  a = 'abc'
  (b, c) = _h.fnsplit(a)
  a = 'abc.def'
  (b, c) = _h.fnsplit(a)
  print(a, '->', b, c)
  a = b'abc'
  (b, c) = _h.fnsplit(a)
  print(a, '->', b, c)
  a = b'abc.def'
  (b, c) = _h.fnsplit(a)
  print(a, '->', b, c)
  a = 'abc.'
  (b, c) = _h.fnsplit(a)
  print(a, '->', repr(b), repr(c))
  a = '.'
  (b, c) = _h.fnsplit(a)
  print(a, '->', repr(b), repr(c))

  # utc, utc2local, utc2localds, utc2dow, utc2ymd, utc2isocs, ts
  print()
  print('utc, utc2local, utc2localds, utc2dow, utc2ymd, utc2isocs, ts...')
  z = _h.utcut()
  print('utcut:', z)
  print('  utcut2local:', _h.utcut2local(z))
  print('utcut2localds:', _h.utcut2localds(z))
  print('utcut2dow:', _h.utcut2dow(z))
  print('utcut2ymd:', _h.utcut2ymd(z))
  print('ut2isocs:', _h.ut2isocs(z))
  print('      ts:', _h.ts())

if __name__ == '__main__':
  main()


