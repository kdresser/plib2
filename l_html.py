#! !P3!

# Copyright 2011, 2012 by J Kelly Dresser.  All rights reserved.

###
### HTML parsing.
### Plus some scraping utilitiies.
### 150820: Updated for mh.function usage.
###         P3.
###

import urllib

import l_misc as _m

import sys
P3 = (sys.version_info[0] == 3)
P2 = not P3
assert P3, 'expecting P3'

###
### Fake browser: Returns an Opera user agent string.
###
def fakebrowser(bc='O'):
    # E.g., User-Agent: Opera/9.80 (Windows NT 5.1; U; en) Presto/2.10.229 Version/11.61
    try:    bc = bc.strip().upper()[0]
    except: bc = 'O'
    if   bc == 'C':
        return 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.79 Safari/537.4'
    elif bc == 'F':
        return 'Mozilla/5.0 (Windows NT 5.1; rv:15.0) Gecko/20100101 Firefox/15.0.1'
    elif bc == 'I':
        return 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 1.1.4322; Open Codecs 0.85.17777; .NET4.0C; .NET4.0E)'
    elif bc == 'K':
        return 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.24pre) Gecko/20100228 K-Meleon/1.5.4'
    elif bc == 'O':
        return 'Opera/9.80 (Windows NT 5.1; U; en) Presto/2.10.229 Version/11.61'
    elif bc == 'Q':
        return 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/534.34 (KHTML, like Gecko) QupZilla/1.2.0 Safari/534.34'
    else:
        return

###
### A simple HTML tokeniser.
### Input: Raw HTML string.  Both \r and \n are newlines.
### Output: A list of tag strings:
###     Each line is either an tag ('< ... >') or 
###       the text chunks between elements.
###     All whitespace is reduced to single blanks (default).
###     There is no awareness of &nbsp;'s or any special encodings.
### Returns (True/False, Response Message, Token List)
###
def html2tokens(rawhtm, ws2sb=True):
    me = 'html2tokens'
    rc, rm, tks = False, '???', []
    try:

        if not rawhtm:
            rc, rm = True, ''
            return rc, rm, tks

        # Split into lines.
        if type(rawhtm) is tuple or type(rawhtm) is list:
            ls = rawhtm
        else:
            ls = rawhtm.replace('\r', '\n').split('\n')

        # Split the lines into tags & text fragments.
        ttfs = []
        for l in ls:
            l = l.strip()
            if l:
                # Split by '>', then by '<' into tags and text fragments.
                ss = l.replace('>', '>\x00').split('\x00')
                for s in ss:
                    s = s.strip()
                    if s:
                        # Split off any text before '<'.
                        x = s.find('<')
                        if x > 0:
                            ttfs.append(s[:x].strip())
                            ttfs.append(s[x:])
                        else:
                            ttfs.append(s)

        # Join text fragments.
        tks = []
        jt = None
        for s in ttfs:
            if s.startswith('<'):
                if jt:
                    if ws2sb:
                        tks.append(' '.join(jt.split()))
                    else:
                        tks.append(jt)
                    jt = None
                if ws2sb:
                    tks.append(' '.join(s.split()))
                else:
                    tks.append(s)
            else:
                if jt:
                    jt += ' ' + s
                else:
                    jt = s

        # Done.
        rc, rm = True, ''
        return rc, rm, tks

    except Exception as E:
        errmsg = '{}: E: {} @ {}'.format(me, E, _m.tblineno())
        raise RuntimeError(errmsg)
        
"""...
###
### parseelement:  Returns a dict, including an 'e-n'='element name' (lowercased).
###                Keys are lowercased.
###
# t = '<script language="JavaScript1.2" src="dui.js" type="text/javascript">'
# t = '<link href="App_Themes/Zorilla.net/mathml.css" type="text/css" rel="stylesheet">'
def parseelement(e):
    me = 'parseelement'
    rc, rm, rd = False, '???', {}
    try:
        rd = {}
        if not e or e[0] != '<' or e[-1] != '>':
            rc, rm = True, ''
            return rc, rm, rd
        w = e[1:-1].strip()
        try:    z, w = w.split(' ', 1)
        except: z, w = w, None
        if not z:   rd['e-n'] = None         # '' and None become None.
        else:       rd['e-n'] = z.lower()
        while w and w.strip():
            try:
                k, w = w.strip().split('=', 1)
            except:
                k, w = w, None
            if not w:
                rd[k.lower()] = None
                break
            c = w[0]
            if c in '"\'':
                try:
                    ###v, w = w[1:].split((c + ' '), 1)     # ??? Right?
                    v, w = w[1:].split((c + ' '), 1)
                except:
                    v, w = w[1:-1], None
            else:
                try:
                    ###v, w = w.split(' ', 1)               # ??? Right?
                    v, w = w.split(' ', 1)
                except:
                    v, w = w, None
            rd[k.lower()] = v
        rc, rm = True, ''
        return rc, rm, rd
    except Exception as E:
        errmsg = '{}: E: {} @ {}'.format(me, E, _m.tblineno())
        raise RuntimeError(errmsg)
..."""

# Parse a tag into name, KV's and a delta-level value.
def tagParse(tag):
    me = 'tagParse'
    tn, kvs, dl = None, None, None
    try:

        # Nothing? 
        if not tag:
            return tn, kvs, dl
        tag = tag.strip()
        if not tag or tag[0] != '<' or tag[-1] != '>':
            1/1
            # Empty, or not a tag at all.
            return tn, kvs, dl

        tag = tag

        # <!-- ... -->
        if   tag.startswith('<!--') and tag[-1] == '-->':
            tn, kvs, dl = 'comment', tag[4:-3].strip(), 0
            return tn, kvs, dl

        # <!-- ... >
        elif tag.startswith('<!--') and tag[-1] == '>':
            tn, kvs, dl = 'extension', tag[4:-3].strip(), +1
            return tn, kvs, dl

        # <! ... -->
        elif tag.startswith('<!') and tag[-1] == '-->':
            tn, kvs, dl = 'extension', tag[4:-3].strip(), -1
            return tn, kvs, dl

        # <! ... >
        elif tag.startswith('<!') and tag[-1] == '>':
            z = tag[2:-1].strip()
            try:    tn, kvs = z.split(' ', 1)
            except: tn, kvs = z, None
            try:    tn = tn.strip()
            except: tn = None
            try:    kvs = kvs.strip()
            except: kvs = None
            dl = 0
            return tn, kvs, dl

        # </ ... >
        elif tag.startswith('</') and tag[-1] == '>':
            tn, kvs, dl = tag[2:-1].strip(), None, -1
            return tn, kvs, dl

        # < ... />
        elif tag[0] == '<' and tag.endswith('/>'):
            z = tag[1:-2].strip()
            tn, kvs = z.split(' ', 1)
            pass
        
        # < ... >
        elif tag[0] == '<' and tag[-1] == '>':
            z = tag[1:-1].strip()
            try:    tn, kvs = z.split(' ', 1)
            except: tn, kvs = z, None
            try:    tn = tn.strip()
            except: tn = None
            try:    kvs = kvs.strip()
            except: kvs = None
            dl = +1
            pass

        # < ??? >
        else:
            tn, kvs, dl = '???', tag[1:-1].strip(), None, 0
            return tn, kvs, dl

        # Convert kvs to a dict.

        if not kvs:
            return tn, kvs, dl
        kvs = kvs.strip()
        if not kvs:
            return tn, kvs, dl
        w = kvs
        rd = {}

        z = None
        while w != z:
            z = w
            w = w.replace(' =', '=').replace('= ', '=')

        while True:
            w = w.strip()
            if not w:
                break
            try:

                xe, xs = w.find('='), w.find(' ')

                # foo
                if   xe == -1 and xs == -1:
                    k, v = w, None
                    w = ''
                    continue

                # foo bar
                elif xe == -1:
                    k, w = w.split(' ', 1)
                    v = None
                    continue

                # foo=bar.
                elif xs == -1:
                    k, v = w.split('=')
                    if v and v[0] in ('"', "'") and (v[0] == v[-1]):
                        v = v[1:-1]
                    w = ''
                    continue

                # Detect solo value (becomes k with a None v).

                if xs < xe:
                    k = w[:xs]
                    w = w[xs+1:]
                    v = None
                    continue

                # Detect one k = v (quoted or unquoted v).

                w = w
                # Remove k
                xe = w.index('=')       # Must.
                k = w[:xe]
                w = w[xe+1:]
                # v is now at the front of w.
                if w:
                    if w[0] in ('"', "'"):
                        xq = w.index(w[0], 1)
                        v = w[1:xq]
                        w = w[xq+1:].strip()
                    else:
                        xs = w.find(' ')
                        if xs == -1:
                            v = w
                            w = ''
                        else:
                            v = w[:xs]
                            w = w[xs:].strip()
                else:
                    v = ''

            finally:
                k = k.strip()
                try:    v = v.strip()
                except: v = None
                k, v = k, v
                rd[k] = v

        kvs = rd

        return tn, kvs, dl

    except Exception as E:
        errmsg = '{}: E: {} @ {}'.format(me, E, _m.tblineno())
        raise ValueError(errmsg)

"""...
###
### parseElement:  Returns a dict, including an 'e-n'='element name' (lowercased).
###                Keys are lowercased.
###
# t = '<script language="JavaScript1.2" src="dui.js" type="text/javascript">'
# t = '<link href="App_Themes/Zorilla.net/mathml.css" type="text/css" rel="stylesheet">'
# -> en, kvs
# <head>       -> 'head/', {}
# <foo a="b"/> -> '/foo/', {'a': 'b'}
# </head>      -> '/head', {}
def parseElement(e):
    me = 'parseElement'
    en, kvs = None, {}
    try:
        if not e:
            return en, kvs
        e = e.strip()
        if not e or e[0] != '<' or e[-1] != '>':
            return en, kvs
        ###
        if   irec.startswith('<!--') and irec[-1] == '>':
            pfx, sfx, z = '!', '', e[4:-1].strip()
        elif irec.startswith('<!') and irec[-1] == '-->':
            pfx, sfx, z = '!', '', e[2:-3].strip()
        elif irec.startswith('<!--') and irec[-1] == '-->':
            pfx, sfx, z = '!', '!', e[4:-3].strip()
        elif irec.startswith('<!') and irec[-1] == '>':
            pfx, sfx, z = '!', '!', e[2:-1].strip()
        elif irec.startswith('</') and irec[-1] == '>':
            pfx, sfx, z = '', '/', e[2:-1].strip()
        elif irec[0] == '<' and irec.endswith('/>'):
            pfx, sfx, z = '/', '', e[1:-2].strip()
        elif irec[0] == '<' and irec[-1] == '>':
            pfx, sfx, z = '', '/', e[1:-1].strip()
        else:
            pfx, sfx, z = '?', '?', e.strip()
        pfx, sfx, z = pfx, sfx, z
        en, y = z.split(' ', 1)
        en = pfx + en + sfx
        for k, v in y.strip().split(' '):
            if len(v) >= 2 and v[0] in ('"', "'") and v[0] == v[-1]:
                kvs[k.lower()] = v[1:-1].strip()
        return en, kvs
    except Exception as E:
        errmsg = '{}: E: {} @ {}.format(me, E, _m.tblineno())
        raise RuntimeError(errmsg)
..."""

###
### Find (if exists) all <base ...> elements in the <head></head>.
### First href's and target's rule.
### Returns None if no base element(s) encountered.
###
def findbase(tks):
    me = 'findbase'
    rc, rm, rd = False, '???', {}
    try:
        inhead, z = False, {}
        for tk in tks:
            try:
                en = mparseelement(tk).get('e-n').lower()
                if not en:
                    continue
                if   en == 'head':
                    inhead = True
                elif en == '/head':
                    inhead = False
                    return rc, rm, None if not rd else rd
                elif inhead and en == 'base':
                    href, target = z.get('href'), z.get('target')
                    if   href and rd.get('href') is None:
                        rd['href'] = href
                    elif target and rd.get('target') is None:
                        rd['target'] = target
                    pass
                pass
            except:
                continue
            pass
        rc, rm = True, ''
        return rc, rm, None if not rd else rd
    except Exception as E:
        errmsg = '{}: E: {} @ {}'.format(me, E, _m.tblineno())
        raise RuntimeError(errmsg)

def pctdecode(s):
    if s:
        return urllib.unquote(s)
    else:
        return s

"""...
t = '<script language="JavaScript1.2" src="dui.js" type="text/javascript">'
z = mparseelement(t)
z = z
t = '<link href="App_Themes/Zorilla.net/mathml.css" type="text/css" rel="stylesheet">'
z = mparseelement(t)
z = z
..."""

"""...
t = '<>'
z = mparseelement(t)
z = z
t = '<head>'
z = mparseelement(t)
z = z
t = '</head>'
z = mparseelement(t)
z = z
..."""

"""...
htm= '''
<!-- Comment #1 -->
<!--
Comment #2a
Comment #2b
-->
<block id=BLOCK>
<!-- Comment #3 -->
</block>
'''

tks = mhtml2tokens(htm)
tks = tks
..."""

"""---

!BASE!

<head>
<base href="http://www.w3schools.com/images/" target="_blank">
</head>

href, target, or both.

HTML DOM Base Object has properties href, target.

Does Se support this?

---"""

### END
