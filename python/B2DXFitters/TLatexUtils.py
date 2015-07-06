class TLatexBeautifier:
    class _Element:
        def __init__(self, elemType, elemValue, elemArg = None):
            if elemType not in {'silentgroup', 'group', 'literal','command','supersub'}:
                raise TypeError('Unknown element type')
            self._elemType = elemType
            self._elemValue = elemValue
            self._elemArg = elemArg
            print 'DEBUG: new element: %s(val="%s",arg=%s)' % (elemType, elemValue, elemArg)

        def elemType(self):
            return self._elemType

        def elemValue(self):
            return self._elemValue

        def elemArg(self):
            return self._elemArg

        def setElemType(self, elemType):
            self._elemType = elemType

        def setElemValue(self, elemValue):
            self._elemValue = elemValue

        def setElemArg(self, elemArg):
            self._elemArg = elemArg

        def visitInOrder(self, visitor):
            visitor(self)
            if list == type(self._elemArg):
                for __el in self._elemArg:
                    __el.visitInOrder(visitor)
            elif type(self) == type(self._elemArg):
                self._elemArg.visitInOrder(visitor)

        def visitDepthFirst(self, visitor):
            if list == type(self._elemArg):
                for __el in self._elemArg:
                    __el.visitDepthFirst(visitor)
            elif type(self) == type(self._elemArg):
                self._elemArg.visitDepthFirst(visitor)
            visitor(self)

        def __str__(self):
            if 'silentgroup' == self._elemType:
                return ''.join((str(el) for el in self._elemArg))
            elif 'group' == self._elemType:
                return '{%s}' % (''.join((str(el) for el in self._elemArg)))
            elif 'literal' == self._elemType:
                return self._elemValue
            elif 'command' == self._elemType:
                return (('#%s' % self._elemValue) if None == self._elemArg else
                        ('#%s[%s]' % (self._elemValue, self._elemArg)))
            elif self._elemType == 'supersub':
                return '%s%s' % ((self._elemValue), str(self._elemArg))
            else:
                raise TypeError('Unknown element type')

    def _doParseGroup(self, s, start = 0, end = -1):
        if -1 == end: end = len(s)
        delimmap = {'{' : '}', '[': ']'}
        delim = s[start]
        if delim not in delimmap:
            raise SyntaxError('invalid syntax in TLatex string: unknown '
                    'delimiter "%s" in _doParseGroup' % delim)
        enddelim = delimmap[delim]
        ndelim = 1
        myend = 1 + start
        while myend < end:
            if delim == s[myend]: ndelim = ndelim + 1
            elif enddelim == s[myend]: ndelim = ndelim - 1
            myend = myend + 1
            if 0 == ndelim: break
        if 0 != ndelim:
            raise SyntaxError(
                    'invalid syntax in TLatex string: unmatched "%s" at %d' %
                    (delim, start))
        return myend

    def _parse(self, s, start = 0, end = -1):
        if 0 == start and -1 == end:
            yield self._Element('silentgroup', None, list(self._parse(s, 0, len(s))))
        else:
            tmp, parser = None, lambda: self._doParse(s, start, end)
            while None != parser:
                tmp, parser = parser()
                if None != tmp: yield tmp

    def _doParse(self, s, start = 0, end = -1):
        if start >= end: return None, None
        if '#' == s[start] and start + 1 < end:
            # command: '#cmdname' or '#cmdname[argument]
            # - cmdname: string of characters
            # - argument: delimited by matching ]
            myend = start + 1
            while (s[myend].isalpha() and myend < end): myend = myend + 1
            if myend < end:
                # okay, have command name
                cmdname = s[(1+start):myend]
                # get argument, if any
                if myend + 1 < end and '[' == s[myend]:
                    myend2 = self._doParseGroup(s, myend, end)
                    cmdarg = s[(1 + myend):(myend2 - 1)]
                    myend = myend2
                else: cmdarg = None
                # command was parsed, return it, together with deferred parser
                # for remainder of string
                return self._Element('command', cmdname, cmdarg), \
                        lambda : self._doParse(s, myend, end)
        elif '{' == s[start] and start + 1 < end:
            # group: '{' + group contents + '}' + more text
            el = self._Element('group', None, [ 'fixup dummy' ])
            # find end of group
            myend = self._doParseGroup(s, start, end)
            # parse group content
            el.setElemArg(list(self._parse(s, 1 + start, myend - 1)))
            # return group, deferred parser
            return el, lambda : self._doParse(s, myend, end)
        elif s[start] in ('^', '_'):
            # sub- or superscript: '^'/'_' group more text
            el = self._Element('supersub', s[start], [ 'fixup dummy' ])
            # parse text after sub/superscript
            content, deferredParser = self._doParse(s, start + 1, end)
            # put group following sub/superscript into sub/superscript element
            el.setElemArg(content)
            if 'group' != content.elemType():
                raise SyntaxError('invalid syntax in TLatex string: sub/'
                        'superscript must be followed by {...}, not %s' %
                        str(content))
            return el, deferredParser
        # neither command nor group nor sub/superscript - must be literal
        # scan forward to the next control character which could start either of
        # those
        controlchars = ('{', '#', '^', '_')
        myend = min(((idx if idx > -1 else end) for idx in (s.find(c, start + 1, end) for c in controlchars)))
        return self._Element('literal', s[start:myend]), lambda : self._doParse(s, myend, end)

    def _superscriptLowerer(self):
        def doSuperscriptLowerer(el):
            # lower superscripts by a bit
            # if it contains '(*)', the star needs some massaging to make things
            # prettier
            if 'supersub' != el.elemType(): return
            if '^' != el.elemValue(): return
            el = el.elemArg()
            if 'group' != el.elemType(): return
            contents = el.elemArg()
            newcontents = []
            for c in contents:
                if c.elemType() not in ('literal', 'command') and (
                        'command' == c.elemType() and None != c.elemArg()):
                    newcontents.append(c)
                    continue
                # rewrite literals or simple commands (#mp,#pm,#eta etc)
                # two cases: literal == '*' - complicated because of tweaks
                #            literal != '*' - easy
                if '*' == c.elemValue():
                    # '*' is a pain in the behind...
                    newcontents += [
                            self._Element('command', 'scale', '1.4'),
                            self._Element('group', None, [
                                self._Element('command', 'lower', '0.35'),
                                self._Element('group', None, [
                                        self._Element('literal', '*') ] )
                                ] )
                            ]
                elif '(' == c.elemValue() or ')' == c.elemValue():
                    # brackets in superscripts are easy - they usually have a
                    # star inside, so lower them a bit less
                    newcontents += [
                            self._Element('command', 'lower', '0.05'),
                            self._Element('group', None, [
                                self._Element('command', 'scale', '0.9'),
                                self._Element('group', None, [ self._Element(c.elemType(), c.elemValue()) ] )
                                ])
                            ]
                else:
                    newcontents += [
                            self._Element('command', 'lower', '0.1'),
                            self._Element('group', None, [ self._Element(c.elemType(), c.elemValue()) ] )
                            ]
            if 1 == len(newcontents) and 'group' == newcontents[0].elemType():
                el.setElemArg(newcontents[0].elemArg())
            else:
                el.setElemArg(newcontents)
            # insert a thin space after a superscript
            newcontents += [ self._Element('command', 'kern', '-.5'),
                    self._Element('group', None, [ self._Element('literal', ' ') ] )
                    ]
        return lambda el: doSuperscriptLowerer(el)

    def _splitLiteralsAt(self, splitat):
        def doSplitLiteralsAt(splitat, el):
            if 'literal' != el.elemType(): return
            s = el.elemValue()
            if len(s) <= len(splitat): return
            ssplit = s.split(splitat)
            if 1 > len(ssplit): return
            ssplit = [ self._Element('literal', s if '' != s else splitat) for s in ssplit ]
            el.setElemType('silentgroup')
            el.setElemValue(None)
            el.setElemArg(ssplit)
        return lambda el: doSplitLiteralsAt(splitat, el)

    def _normaliseSilentGroupsInGroup(self):
        def doNormaliseSilentGroupsInGroup(el):
            if 'group' != el.elemType(): return
            print 'DEBUG: doNormaliseSilentGroupsInGroup("%s")' % str(el)
            newcontents = []
            for c in el.elemArg():
                print 'DEBUG:\t\tgroup "%s"' % str(el)
                if 'silentgroup' != c.elemType():
                    newcontents.append(c)
                else:
                    newcontents += c.elemArg()
            el.setElemArg(newcontents)
        return lambda el: doNormaliseSilentGroupsInGroup(el)
    
    def _plusMinusRewriter(self):
        def doPlusMinusRewrite(el):
            rewritemap = { '+': 'plus', '-': 'minus' }
            if 'literal' != el.elemType() or el.elemValue() not in rewritemap:
                return
            el.setElemType('command')
            el.setElemValue(rewritemap[el.elemValue()])
        return lambda el: doPlusMinusRewrite(el)

    def __init__(self, s):
        tmp = [el for el in self._parse(s)]
        for el in tmp:
            # replace '+' and '-' by '#plus' and '#minus'
            el.visitDepthFirst(self._splitLiteralsAt('+'))
            el.visitDepthFirst(self._normaliseSilentGroupsInGroup())
            el.visitDepthFirst(self._splitLiteralsAt('-'))
            el.visitDepthFirst(self._normaliseSilentGroupsInGroup())
            el.visitDepthFirst(self._plusMinusRewriter())
            # hack off '(', '*', ')', so we can massage the in superscripts
            el.visitDepthFirst(self._splitLiteralsAt('('))
            el.visitDepthFirst(self._normaliseSilentGroupsInGroup())
            el.visitDepthFirst(self._splitLiteralsAt(')'))
            el.visitDepthFirst(self._normaliseSilentGroupsInGroup())
            el.visitDepthFirst(self._splitLiteralsAt('*'))
            el.visitDepthFirst(self._normaliseSilentGroupsInGroup())
            # massage superscipts
            el.visitDepthFirst(self._superscriptLowerer())
        tmp = list((str(el) for el in tmp))
        self._str = ''.join(tmp)

    def __str__(self):
        return self._str

class DecDescrToTLatex:
    _rewritemap = {
            'Bs2DsK': 'B_{s}^{0} #rightarrow D_{s}^{#mp}K^{#pm}',
            'Bs2DsPi': 'B_{s}^{0} #rightarrow D_{s}^{-}#pi^{+}',
            'Bs2DsstPi': 'B_{s}^{0} #rightarrow D_{s}^{*-}#pi^{+}',
            'Bs2DsstRho': 'B_{s}^{0} #rightarrow D_{s}^{*-}#rho^{+}',
            'Bs2DsRho': 'B_{s}^{0} #rightarrow D_{s}^{-}#rho^{+}',
            'Bs2DsDsstPiRho': 'B_{(d,s)}^{0} #rightarrow D_{s}^{(*)-}#pi^{+}',
            'Bs2DsDsstKKst':'B_{s}^{0} #rightarrow D_{s}^{(*)#mp}K^{(*)#pm}',
            'Bd2DK': 'B_{d}^{0} #rightarrow D^{#mp}K^{#pm}',
            'Bd2DPi': 'B_{d}^{0} #rightarrow D^{#mp}#pi^{#pm}',
            'Bd2DKPi': 'B_{d}^{0} #rightarrow D^{#mp}(K^{#pm},#pi^{#pm})',
            'Lb2LcK': '#Lambda_{b}^{0} #rightarrow #Lambda_{c}^{+}K^{-}',
            'Lb2LcPi': '#Lambda_{b}^{0} #rightarrow #Lambda_{c}^{+}#pi^{-}',
            'Lb2LcKPi': '#Lambda_{b}^{0} #rightarrow #Lambda_{c}^{+}(K^{-},#pi^{-})',
            'Lb2Dsp': '#Lambda_{b}^{0} #rightarrow D_{s}^{-}p',
            'Lb2Dsstp': '#Lambda_{b}^{0} #rightarrow D_{s}^{*-}p',
            'Lb2DsDsstP': '#Lambda_{b}^{0} #rightarrow D_{s}^{(*)-}p',
            'Bd2DsK': 'B_{d}^{0} #rightarrow D_{s}^{#mp}K^{#pm}',
            'CombBkg': 'Combinatorial'
            }

    def __init__(self, s, rewritemap = _rewritemap):
        for k in rewritemap:
            s = s.replace(k, rewritemap[k])
        self._str = str(TLatexBeautifier(s))

    def __str__(self):
        return self._str

# vim: ft=python:sw=4
