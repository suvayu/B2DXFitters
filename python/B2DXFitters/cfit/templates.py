"""Utilities to read templates (mass, mistag, etc)

@author Manuel Schiller
@email manuel dot schiller at nikhef.nl
@author Suvayu Ali
@email Suvayu dot Ali at cern.ch
@date 2014-04-25 Fri

"""


import ROOT
from ROOT import RooFit

from .utils import WS


# read dataset from workspace
def readDataSet(config, ws, observables, rangeName = None):
    """Read dataset (RooDataSet) from file.

    config      -- configuration dictionary
    ws          -- workspace to which to add data set
    observables -- observables
    rangeName   -- name of range to clip dataset to (default None)

    """

    from ROOT import ( TFile, RooWorkspace, RooRealVar, RooCategory,
        RooBinningCategory, RooUniformBinning, RooMappedCategory,
        RooDataSet, RooArgSet, RooArgList )
    import sys, math
    # local little helper routine
    def round_to_even(x):
        xfl = int(math.floor(x))
        rem = x - xfl
        if rem < 0.5: return xfl
        elif rem > 0.5: return xfl + 1
        else:
            if xfl % 2: return xfl + 1
            else: return xfl
    # another small helper routine
    def tokenize(s, delims = '+-*/()?:'):
        # FIXME: this goes wrong for numerical constants like 1.4e-3
        # proposed solution: regexp for general floating point constants,
        # replace occurences of matches with empty string
        delims = [ c for c in delims ]
        delims.insert(0, None)
        for delim in delims:
            tmp = s.split(delim)
            tmp = list(set(( s + ' ' for s in tmp)))
            s = ''.join(tmp)
        tmp = list(set(s.split(None)))
        return tmp
    # figure out which names from the mapping we need - look at the observables
    names = ()
    for n in config['DataSetVarNameMapping'].keys():
        if None != observables.find(n):
            names += (n,)
    # build RooArgSets and maps with source and destination variables
    dmap = { }
    for k in names: dmap[k] = observables.find(k)
    if None in dmap.values():
        raise NameError('Some variables not found in destination: %s' % str(dmap))
    dset = RooArgSet()
    for v in dmap.values(): dset.add(v)
    if None != dset.find('weight'):
        # RooFit insists on weight variable being first in set
        tmpset = RooArgSet()
        tmpset.add(dset.find('weight'))
        it = dset.fwdIterator()
        while True:
            obj = it.next()
            if None == obj: break
            if 'weight' == obj.GetName(): continue
            tmpset.add(obj)
        dset = tmpset
        del tmpset
        ddata = RooDataSet('agglomeration', 'of positronic circuits', dset, 'weight')
    else:
        ddata = RooDataSet('agglomeration', 'of positronic circuits', dset)
    # open file with data sets
    f = TFile(config['DataFileName'], 'READ')
    # get workspace
    fws = f.Get(config['DataWorkSpaceName'])
    ROOT.SetOwnership(fws, True)
    if None == fws or not fws.InheritsFrom('RooWorkspace'):
        # ok, no workspace, so try to read a tree of the same name and
        # synthesize a workspace
        from ROOT import RooWorkspace, RooDataSet, RooArgList
        fws = RooWorkspace(config['DataWorkSpaceName'])
        iset = RooArgSet()
        addiset = RooArgList()
        it = observables.fwdIterator()
        while True:
            obj = it.next()
            if None == obj: break
            name = config['DataSetVarNameMapping'][obj.GetName()]
            vnames = tokenize(name)
            if len(vnames) > 1 and not obj.InheritsFrom('RooAbsReal'):
                print 'Error: Formulae not supported for categories'
                return None
            if obj.InheritsFrom('RooAbsReal'):
                if 1 == len(vnames):
                    # simple case, just add variable
                    var = WS(fws, RooRealVar(name, name, -sys.float_info.max,
                        sys.float_info.max))
                    iset.addClone(var)
                else:
                    # complicated case - add a bunch of observables, and
                    # compute something in a RooFormulaVar
                    from ROOT import RooFormulaVar
                    args = RooArgList()
                    for n in vnames:
                        try:
                            # skip simple numerical factors
                            float(n)
                        except:
                            var = iset.find(n)
                            if None == var:
                                var = WS(fws, RooRealVar(n, n, -sys.float_info.max,
                                    sys.float_info.max))
                                iset.addClone(var)
                                args.add(iset.find(n))
                    var = WS(fws, RooFormulaVar(name, name, name, args))
                    addiset.addClone(var)
            else:
                for dsname in ((config['DataSetNames'], )
                        if type(config['DataSetNames']) == str else
                        config['DataSetNames']):
                    break
                leaf = f.Get(dsname).GetLeaf(name)
                if None == leaf:
                    leaf = f.Get(dsname).GetLeaf(name + '_idx')
                if leaf.GetTypeName() in (
                        'char', 'unsigned char', 'Char_t', 'UChar_t',
                        'short', 'unsigned short', 'Short_t', 'UShort_t',
                        'int', 'unsigned', 'unsigned int', 'Int_t', 'UInt_t',
                        'long', 'unsigned long', 'Long_t', 'ULong_t',
                        'Long64_t', 'ULong64_t', 'long long',
                        'unsigned long long'):
                    var = WS(fws, RooCategory(name, name))
                    tit = obj.typeIterator()
                    ROOT.SetOwnership(tit, True)
                    while True:
                        tobj = tit.Next()
                        if None == tobj: break
                        var.defineType(tobj.GetName(), tobj.getVal())
                else:
                    var = WS(fws, RooRealVar(name, name, -sys.float_info.max,
                        sys.float_info.max))
                iset.addClone(var)
        for dsname in ((config['DataSetNames'], )
               if type(config['DataSetNames']) == str else
               config['DataSetNames']):
            tmpds = WS(fws, RooDataSet(dsname, dsname,f.Get(dsname), iset), [])
            if 0 != addiset.getSize():
                # need to add columns with RooFormulaVars
                tmpds.addColumns(addiset)
            del tmpds
    # local data conversion routine
    def doIt(config, rangeName, dsname, sname, names, dmap, dset, ddata, fws):
        sdata = fws.obj(dsname)
        if None == sdata: return 0
        if None != config['DataSetCuts']:
            # apply any user-supplied cuts
            newsdata = sdata.reduce(config['DataSetCuts'])
            ROOT.SetOwnership(newsdata, True)
            del sdata
            sdata = newsdata
            del newsdata
        sset = sdata.get()
        smap = { }
        for k in names:
            smap[k] = sset.find(config['DataSetVarNameMapping'][k])
        if 'sample' in smap.keys() and None == smap['sample'] and None != sname:
            smap.pop('sample')
            dmap['sample'].setLabel(sname)
        if None in smap.values():
            raise NameError('Some variables not found in source: %s' % str(smap))
        # additional complication: toys save decay time in ps, data is in nm
        # figure out which time conversion factor to use
        timeConvFactor = 1e9 / 2.99792458e8
        meantime = sdata.mean(smap['time'])
        if ((dmap['time'].getMin() <= meantime and
                meantime <= dmap['time'].getMax() and config['IsToy']) or
                not config['IsToy']):
            timeConvFactor = 1.
        print 'DEBUG: Importing data sample meantime = %f, timeConvFactor = %f' % (
                meantime, timeConvFactor)
        # loop over all entries of data set
        ninwindow = 0
        if None != sname:
            sys.stdout.write('Dataset conversion and fixup: %s: progress: ' % sname)
        else:
            sys.stdout.write('Dataset conversion and fixup: progress: ')
        for i in xrange(0, sdata.numEntries()):
            sdata.get(i)
            if 0 == i % 128:
                sys.stdout.write('*')
            vals = { }
            for vname in smap.keys():
                obj = smap[vname]
                if obj.InheritsFrom('RooAbsReal'):
                    val = obj.getVal()
                    vals[vname] = val
                else:
                    val = obj.getIndex()
                    vals[vname] = val
            # first fixup: apply time/timeerr conversion factor
            if 'time' in dmap.keys():
                vals['time'] *= timeConvFactor
            if 'timeerr' in dmap.keys():
                vals['timeerr'] *= timeConvFactor
            # second fixup: only sign of qf is important
            if 'qf' in dmap.keys():
                vals['qf'] = 1 if vals['qf'] > 0.5 else (-1 if vals['qf'] <
                        -0.5 else 0.)
            # third fixup: untagged events are forced to 0.5 mistag
            if ('qt' in dmap.keys() and 'mistag' in dmap.keys() and 0 ==
                    vals['qt']):
                vals['mistag'] = 0.5
            # apply cuts
            inrange = True
            for vname in dmap.keys():
                if not dmap[vname].InheritsFrom('RooAbsReal'): continue
                # no need to cut on untagged events
                if 'mistag' == vname and 0 == vals['qt']: continue
                if None != rangeName and dmap[vname].hasRange(rangeName):
                    if (dmap[vname].getMin(rangeName) > vals[vname] or
                            vals[vname] >= dmap[vname].getMax(rangeName)):
                        inrange = False
                        break
                else:
                    if (dmap[vname].getMin() > vals[vname] or
                            vals[vname] >= dmap[vname].getMax()):
                        inrange = False
                        break
            # skip cuts which are not within the allowed range
            if not inrange: continue
            # copy values over, doing real-category conversions as needed
            for vname in smap.keys():
                dvar, svar = dmap[vname], vals[vname]
                if dvar.InheritsFrom('RooAbsRealLValue'):
                    if float == type(svar): dvar.setVal(svar)
                    elif int == type(svar): dvar.setVal(svar)
                elif dvar.InheritsFrom('RooAbsCategoryLValue'):
                    if int == type(svar): dvar.setIndex(svar)
                    elif float == type(svar):
                        dvar.setIndex(round_to_even(svar))
            if 'weight' in dmap:
                ddata.add(dset, vals['weight'])
            else:
                ddata.add(dset)
            ninwindow = ninwindow + 1
        del sdata
        sys.stdout.write(', done - %d events\n' % ninwindow)
        return ninwindow
    ninwindow = 0
    if type(config['DataSetNames']) == str:
        ninwindow += doIt(config, rangeName, config['DataSetNames'],
                None, names, dmap, dset, ddata, fws)
    else:
        for sname in config['DataSetNames'].keys():
            ninwindow += doIt(config, rangeName, config['DataSetNames'][sname],
                    sname, names, dmap, dset, ddata, fws)
    # free workspace and close file
    del fws
    f.Close()
    del f
    # put the new dataset into our proper workspace
    ddata = WS(ws, ddata, [])
    # for debugging
    if config['Debug']:
        ddata.Print('v')
        if 'qt' in dmap.keys():
            data.table(dmap['qt']).Print('v')
        if 'qf' in dmap.keys():
            data.table(dmap['qf']).Print('v')
        if 'qf' in dmap.keys() and 'qt' in dmap.keys():
            data.table(RooArgSet(dmap['qt'], dmap['qf'])).Print('v')
        if 'sample' in dmap.keys():
            data.table(dmap['sample']).Print('v')
    # all done, return Data to the bridge
    return ddata


def writeDataSet(dataset, filename, treename, bnamemap = {}):
    from ROOT import TFile, TTree
    import array
    f = TFile(filename, 'RECREATE')
    t = TTree(treename, treename)
    obs = dataset.get()
    # create branches
    branches = { }
    it = obs.fwdIterator()
    while True:
        obj = it.next()
        if None == obj: break
        bname = (bnamemap[obj.GetName()] if obj.GetName() in bnamemap else
                obj.GetName())
        branches[obj.GetName()] = (array.array('d', [0.]) if
                obj.InheritsFrom('RooAbsReal') else array.array('i', [0]))
        t.Branch(bname, branches[obj.GetName()], bname+('/D' if
            obj.InheritsFrom('RooAbsReal') else '/I'))
    # fill tuple
    for i in xrange(0, dataset.numEntries()):
        dataset.get(i)
        it = obs.fwdIterator()
        while True:
            obj = it.next()
            if None == obj: break
            branches[obj.GetName()][0] = (obj.getVal() if
                    obj.InheritsFrom('RooAbsReal') else obj.getIndex())
        t.Fill()
    t.Write()
    del t
    f.Close()
    del f


def readAcceptanceCorrection(
    config,	# config dictionary
    ws,	# workspace into which to import correction
    time	# time
    ):
    from ROOT import ( TFile, TH1, RooDataHist, RooHistPdf, RooArgList,
        RooArgSet )
    if None == config['AcceptanceCorrectionFile'] or \
            None == config['AcceptanceCorrectionHistName'] or \
            '' == config['AcceptanceCorrectionFile'] or \
            '' == config['AcceptanceCorrectionHistName']:
                return None
    f = TFile(config['AcceptanceCorrectionFile'], 'READ')
    h = f.Get(config['AcceptanceCorrectionHistName'])
    ROOT.SetOwnership(h, True)
    h.Scale(1. / h.Integral())
    if not config['AcceptanceCorrectionInterpolation']:
        dhist = RooDataHist('acc_corr_dhist', 'acc_corr_dhist',
                RooArgList(time), h)
        retVal = WS(ws, RooHistPdf('acc_corr', 'acc_corr',
            RooArgSet(time), dhist))
        del dhist
    else:
        from ROOT import RooBinned1DQuinticBase, RooAbsPdf
        RooBinned1DQuinticPdf = RooBinned1DQuinticBase(RooAbsPdf)
        retVal = WS(ws, RooBinned1DQuinticPdf(
            'acc_corr', 'acc_corr', h, time))
    del h
    del f
    return retVal


def readTemplate1D(
    fromfile,           # file to read from
    fromws,             # workspace to read from
    fromvarname,        # variable name in fromws
    objname,            # object to ask for
    ws, 	        # workspace to import into
    variable,	        # variable
    pfx,                # prefix of imported objects
    binIfPDF = False    # bin if the template comes as Pdf
    ):
    # read a 1D template from a file - can either be in a workspace (either
    # PDF or data set), or a plain 1D histogram
    from ROOT import ( TFile, RooWorkspace, RooKeysPdf, RooHistPdf,
        RooArgList, RooDataHist, RooArgSet )
    ff = TFile(fromfile, 'READ')
    if (None == ff or ff.IsZombie()):
        print 'ERROR: Unable to open %s to get template for %s' % (fromfile,
                variable.GetName())
    workspace = ff.Get(fromws)
    if None != workspace and workspace.InheritsFrom('RooWorkspace'):
        # ok, we're reading from a ROOT file which contains a RooWorkspace, so
        # we try to get a PDF of a RooAbsData from it
        ROOT.SetOwnership(workspace, True)
        var = workspace.var(fromvarname)
        if (None == var):
            print ('ERROR: Unable to read %s variable %s from '
                    'workspace %s (%s)') % (variable.GetName(), fromvarname,
                            fromws, fromfile)
            return None
        pdf = workspace.pdf(objname)
        if (None == pdf):
            # try to get a data sample of that name
            data = workspace.data(objname)
            if None == data:
                print ('ERROR: Unable to read %s pdf/data %s from '
                        'workspace %s (%s)') % (variable.GetName(),
                                fromvarname, fromws, fromfile)
                return None
            if data.InheritsFrom('RooDataSet'):
                # if unbinned data set, first create a binned version
                argset = RooArgSet(var)
                data = data.reduce(RooFit.SelectVars(argset))
                ROOT.SetOwnership(data, True)
                data = data.binnedClone()
                ROOT.SetOwnership(data, True)
            # get underlying histogram
            hist = data.createHistogram(var.GetName())
            del data
        else:
            # we need to jump through a few hoops to rename the dataset and variables
            # get underlying histogram
            if (pdf.InheritsFrom('RooHistPdf')):
                hist = pdf.dataHist().createHistogram(var.GetName())
            else:
                if binIfPDF:
                    hist = pdf.createHistogram(var.GetName(), var)
                else:
                    # ok, replace var with variable
                    from ROOT import RooCustomizer
                    c = RooCustomizer(pdf, '%sPdf' % pfx);
                    c.replaceArg(var, variable)
                    pdf = c.build()
                    ROOT.SetOwnership(pdf, True)
                    pdf.SetName('%sPdf' % pfx)
                    pdf = WS(ws, pdf)
                    del var
                    del workspace
                    ff.Close()
                    del ff
                    return pdf
    else:
        # no workspace found, try to find a TH1 instead
        hist = None
        for tmp in (fromws, objname):
            hist = ff.Get(tmp)
            if (None != tmp and hist.InheritsFrom('TH1') and
                    1 == hist.GetDimension()):
                break
        if (None == hist or not hist.InheritsFrom('TH1') or
                1 != hist.GetDimension()):
            print ('ERROR: Utterly unable to find any kind of %s '
                    'variable/data in %s') % (variable.GetName(), fromfile)
            return None
    ROOT.SetOwnership(hist, True)
    hist.SetNameTitle('%sPdf_hist' % pfx, '%sPdf_hist' % pfx)
    hist.SetDirectory(None)
    if hist.Integral() < 1e-15:
        raise ValueError('Histogram empty!')
    variable.setRange(
	    max(variable.getMin(),
		hist.GetXaxis().GetBinLowEdge(1)),
	    min(variable.getMax(),
		hist.GetXaxis().GetBinUpEdge(hist.GetNbinsX())))
    from ROOT import RooBinning, std
    bins = std.vector('double')()
    bins.push_back(hist.GetXaxis().GetBinLowEdge(1))
    for ibin in xrange(1, 1 + hist.GetNbinsX()):
        bins.push_back(hist.GetXaxis().GetBinUpEdge(ibin))
    binning = RooBinning(bins.size() - 1, bins.begin().base())
    del bins
    del ibin
    variable.setBinning(binning)
    # recreate datahist
    dh = RooDataHist('%sPdf_dhist' % pfx, '%sPdf_dhist' % pfx,
            RooArgList(variable), hist)
    del hist
    del pdf
    del var
    del workspace
    ff.Close()
    del ff
    # and finally use dh to create our pdf
    pdf = WS(ws, RooHistPdf('%sPdf' % pfx, '%sPdf' % pfx, RooArgSet(variable), dh))
    del dh
    return pdf


# read mistag distribution from file
def getMistagTemplate(
    config,	# configuration dictionary
    ws, 	# workspace to import into
    mistag,	# mistag variable
    mode,       # mode to look up
    taggernr = 0 # number of tagger
    ):
    # find the entry we're interested in
    if mode not in config['MistagTemplates']:
        modenicks = {
                'Bd2DK': 'Bd2DPi',
                'Bd2DsK': 'Bd2DPi',
                'Lb2LcK': 'Bd2DPi',
                'Lb2Dsp': 'Bd2DPi',
                'Lb2Dsstp': 'Bd2DPi',
                'Lb2LcPi': 'Bd2DPi',
                }
        if mode in modenicks:
            mode = modenicks[mode]
        else:
            mode = config['Modes'][0]
    tmp = config['MistagTemplates'][mode][taggernr]
    return readTemplate1D(tmp['File'], tmp['Workspace'], tmp['VarName'],
            tmp['TemplateName'], ws, mistag, '%s_Mistag_%u_PDF' % (
                mode, taggernr))


# read decay time error distribution from file
def getDecayTimeErrorTemplate(
    config,	# configuration dictionary
    ws, 	# workspace to import into
    timeerr,	# timeerr variable
    mode        # mode to look up
    ):
    # find the entry we're interested in
    if mode not in config['DecayTimeErrorTemplates']:
        modenicks = {
                }
        if mode in modenicks:
            mode = modenicks[mode]
        else:
            mode = config['Modes'][0]
    tmp = config['DecayTimeErrorTemplates'][mode]
    return readTemplate1D(tmp['File'], tmp['Workspace'], tmp['VarName'],
            tmp['TemplateName'], ws, timeerr, '%s_TimeErr_PDF' % (mode))


# load k-factor templates for all modes
def getKFactorTemplates(
    config,	# configuration dictionary
    ws, 	# workspace to import into
    k	# k factor variable
    ):
    templates = {}
    for mode in config['Modes']:
        tmp = (config['KFactorTemplates'][mode] if mode in
                config['KFactorTemplates'] else None)
        if None == tmp:
            templates[mode] = (None, None)
            continue
        kcopy = WS(ws, k.clone('%s_%s' % (mode, k.GetName())))
        print 'DEBUG: %s' % str(kcopy)
        templates[mode] = (readTemplate1D(tmp['File'], tmp['Workspace'],
            tmp['VarName'], tmp['TemplateName'], ws, kcopy,
            '%s_kFactor_PDF' % (mode)), kcopy)
    return templates


# obtain mass template from mass fitter (2011 CONF note version)
#
# we use the very useful workspace dump produced by the mass fitter to obtain
# the pdf and yields
#
# returns a dictionary with a pair { 'pdf': pdf, 'yield': yield }
def getMassTemplateOneMode2011Conf(
    config,	        # configuration dictionary
    ws,                 # workspace into which to import templates
    mass,	        # mass variable
    mode,	        # decay mode to load
    sname,              # sample name
    dsmass = None,      # ds mass variable
    pidk = None	        # pidk variable
    ):
    fromfile = config['MassTemplateFile']
    fromwsname = config['MassTemplateWorkspace']
    from ROOT import ( TFile, RooWorkspace, RooAbsPdf, RooAbsCategory,
        RooRealVar, RooArgSet, RooDataHist, RooHistPdf, RooArgList )
    import re

    # validate input (and break caller if invalid)
    if sname not in config['SampleCategories']: return None

    # open file and read in workspace
    fromfile = TFile(fromfile, 'READ')
    if fromfile.IsZombie():
        return None
    fromws = fromfile.Get(fromwsname)
    if None == fromws:
        return None
    ROOT.SetOwnership(fromws, True)

    # ok, depending on mode, we try to load a suitable pdf
    pdf = None
    if mode == 'Bs2DsK':
        pdf = fromws.pdf('DblCBPDF%s' % sname)
    elif mode == 'CombBkg':
        pdf = fromws.pdf('CombBkgPDF_m_%s' % sname)
    else:
        # any other mode may or may not have separate samples for
        # magnet polarity, Ds decay mode, ...
        #
        # we therefore constuct a list of successively less specialised name
        # suffices so we can get the most specific pdf from the workspace
        trysfx = [
            '%sPdf_m_%s' % (mode, sname),
            '%sPdf_m_%s' % (mode.replace('2', ''), sname),
            '%s_m_%s' % (mode, sname),
            '%s_m_%s' % (mode.replace('2', ''), sname),
            '%sPdf_m_both' % mode,
            '%sPdf_m_both' % mode.replace('2', ''),
            '%s_m_both' % mode,
            '%s_m_both' % mode.replace('2', ''),
            '%sPdf_m' % mode,
            '%sPdf_m' % mode.replace('2', ''),
            '%s_m' % mode,
            '%s_m' % mode.replace('2', '')
            ]
        for sfx in trysfx:
            pdf = fromws.pdf('PhysBkg%s' % sfx)
            if None != pdf:
                break
    # figure out name of mass variable - should start with 'lab0' and end in
    # '_M'; while we're at it, figure out how we need to scale yields due to
    # potentially different mass ranges
    massname = None
    yieldrangescaling = 1.
    if None != pdf:
        pdfvars = []
        varset = pdf.getVariables()
        ROOT.SetOwnership(varset, True)
        it = varset.createIterator()
        ROOT.SetOwnership(it, True)
        while True:
            obj = it.Next()
            if None == obj: break
            pdfvars.append(obj)
            pdfvarnames = [ v.GetName() for v in pdfvars ]
            regex = re.compile('^lab0.*_M$')
            for n in pdfvarnames:
                if regex.match(n):
                    oldmass = varset.find(n)
                    massname = n
            else:
                # set anything else constant
                varset.find(n).setConstant(True)
        # mass integration factorises, so we can afford to be a little sloppier
        # when doing numerical integrations
        pdf.specialIntegratorConfig(True).setEpsAbs(1e-9)
        pdf.specialIntegratorConfig().setEpsRel(1e-9)
        pdf.specialIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('sumRule', 'Trapezoid')
        pdf.specialIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('extrapolation', 'Wynn-Epsilon')
        pdf.specialIntegratorConfig().getConfigSection('RooIntegrator1D').setRealValue('minSteps', 3)
        pdf.specialIntegratorConfig().getConfigSection('RooIntegrator1D').setRealValue('maxSteps', 16)
        pdf.specialIntegratorConfig().method1D().setLabel('RooIntegrator1D')
        # figure out yield scaling due to mass ranges
        oldmass.setRange('signalRegion', mass.getMin(), mass.getMax())
        iset = nset = RooArgSet(oldmass)
        integral = pdf.createIntegral(iset, nset, 'signalRegion')
        ROOT.SetOwnership(integral, True)
        yieldrangescaling = integral.getVal()
        # ok, figure out yield
        nYield = None
        if mode == 'Bs2DsK':
            nYield = RooRealVar('nSig_%s_Evts' % sname,
                    'nSig_%s_Evts' % sname,
                    fromws.var('nSig_%s_Evts' % sname).getVal() *
                    yieldrangescaling)
        elif mode == 'CombBkg':
            nYield = RooRealVar('nCombBkg_%s_Evts' % sname,
                    'nCombBkg_%s_Evts' % sname,
                    fromws.var('nCombBkg_%s_Evts' % sname).getVal() *
                    yieldrangescaling)
        else:
            # yield for other modes are either simple and we deal with them here,
            # or we deal with them below
           nYield = fromws.var('n%s_%s_Evts' % (mode, sname))
           if None != nYield:
               nYield = RooRealVar(nYield.GetName(), nYield.GetTitle(),
                       nYield.getVal() * yieldrangescaling)
        if None != pdf and None == nYield:
            # fix for modes without fitted yields: insert with zero yield unless we
            # know better
            y = None
            # fixed yield modes we know about
            fixedmodes = {
                    'Bd2DK': { 
                        'up_kkpi': 14., 'up_kpipi': 2., 
                        'down_kkpi': 23., 'down_kpipi': 3.
                        },
                    'Lb2LcK': {
                        'up_kkpi': 4.1088*100./15.,
                        'down_kkpi': 6.7224*100./15.
                        },
                    'Lb2Dsp': {
                        'up_kkpi': 0.5 * 46., 'up_kpipi': 0.5 * 5., 'up_pipipi': 0.5 * 10., 
                        'down_kkpi': 0.5 * 78., 'down_kpipi': 0.5 * 8., 'down_pipipi': 0.5 * 16.
                        },
                    'Lb2Dsstp': {
                        'up_kkpi': 0.5 * 46., 'up_kpipi': 0.5 * 5., 'up_pipipi': 0.5 * 10.,
                        'down_kkpi': 0.5 * 78., 'down_kpipi': 0.5 * 8., 'down_pipipi': 0.5 * 16.
                        }
                    }
            if (mode in fixedmodes and sname in fixedmodes[mode]):
                # it's a fixed yield mode, so set yield
                y = fixedmodes[mode][sname]
            else:
                # might be a "grouped mode"
                group1 = ['Bd2DsK', 'Bs2DsstK', 'Bs2DsKst', 'Bs2DsstKst']
                group2 = ['Bs2DsPi', 'Bs2DsstPi', 'Bs2DsRho', 'Bs2DsstRho']
                fracGroup1 = [
                    fromws.var('g1_f%d_frac' % i).getVal() for i in xrange(1, 4) ]
                fracGroup2 = [
                    fromws.var('g2_f%d_frac' % i).getVal() for i in xrange(1, 4) ]
                if mode in group1:
                    # get the group yield
                    y = fromws.var(
                        'nBs2DsDssKKst_%s_Evts' % sname).getVal()
                    # multiply with correct (recursive) fraction
                    for i in xrange(0, 3):
                        if group1[i] == mode:
                            y *= fracGroup1[i]
                            break
                        else:
                            y *= 1. - fracGroup1[i]
                elif mode in group2:
                    # get the group yield
                    y = fromws.var(
                        'nBs2DsDsstPiRho_%s_Evts' % sname).getVal()
                    # multiply with correct (recursive) fraction
                    for i in xrange(0, 3):
                        if group2[i] == mode:
                            y *= fracGroup2[i]
                            break
                        else:
                            y *= 1. - fracGroup2[i]
                else: # mode not recognized
                    pass
            if None == y:
                print '@@@@ - ERROR: NO YIELD FOR MODE %s SAMPLE NAME %s' % (
                        mode, sname)
                nYield = None
            else:
                nYield = RooRealVar('n%s_%s_Evts' % (mode, sname),
                        'n%s_%s_Evts' % (mode, sname),
                        y * yieldrangescaling)
    # ok, we should have all we need for now
    if None == pdf or None == nYield:
        print '@@@@ - ERROR: NO PDF FOR MODE %s SAMPLE CATEGORY %s' % (
                mode, sname)
        return None
    # import mass pdf and corresponding yield into our workspace
    # in the way, we rename whatever mass variable was used to the one supplied
    # by our caller
    nYield = WS(ws, nYield, [
        RooFit.RenameConflictNodes('_%s_%s' % (mode, sname)),
        RooFit.Silence()])

    if None != ws.pdf(pdf.GetName()):
        # reuse pdf if it is already in the workspace - that's fine as long
        # as all parameters are fixed and the yields are not reused
        pdf = ws.pdf(pdf.GetName())
        # see if there is a binned version, if so prefer it
        if None != ws.pdf('%s_dhist_pdf' % pdf.GetName()):
            pdf = ws.pdf('%s_dhist_pdf' % pdf.GetName())
    else:
        # ok, pdf not in workspace, so swallow it
        if None != massname:
            pdf = WS(ws, pdf, [
                RooFit.RenameVariable(massname, mass.GetName()),
                RooFit.RenameConflictNodes('_%s_%s' % (mode, sname)),
                RooFit.Silence()])
        else:
            pdf = WS(ws, pdf, [
                RooFit.RenameConflictNodes('_%s_%s' % (mode, sname)),
                RooFit.Silence()])
        if config['NBinsMass'] > 0 and not config['MassInterpolation']:
            obins = mass.getBins()
            mass.setBins(config['NBinsMass'])
            hist = pdf.createHistogram('%s_hist' % pdf.GetName(), mass)
            ROOT.SetOwnership(hist, True)
            dhist = WS(ws, RooDataHist(
                '%s_dhist' % pdf.GetName(), '%s_dhist' % pdf.GetName(),
                RooArgList(mass), hist), [])
            pdf = WS(ws, RooHistPdf('%s_pdf' % dhist.GetName(),
                '%s_pdf' % dhist.GetName(), RooArgSet(mass), dhist))
            del hist
            del dhist
            mass.setBins(obins)
            del obins
    # ok, all done, return
    if config['MassInterpolation']:
        from ROOT import RooBinned1DQuinticBase
        RooBinned1DQuinticPdf = RooBinned1DQuinticBase(RooAbsPdf)
        obins = mass.getBins()
        nbins = config['NBinsMass']
        if 0 == nbins:
            print 'ERROR: requested binned interpolation of mass %s %d %s' % (
                    'histograms with ', nbins, ' bins - increasing to 100 bins')
            nbins = 100
        mass.setBins(nbins)
        hist = pdf.createHistogram('%s_hist' % pdf.GetName(), mass)
        ROOT.SetOwnership(hist, True)
        pdf = WS(ws, RooBinned1DQuinticPdf(
            '%s_interpol' % pdf.GetName(),
            '%s_interpol' % pdf.GetName(), hist, mass, True))
        del hist
        mass.setBins(obins)
        del obins
        del nbins
    if None != nYield:
        nYield.setConstant(True)
    return { 'pdf': WS(ws, pdf), 'yield': WS(ws, nYield) }


# obtain mass template from mass fitter (2011 PAPER version)
#
# we use the very useful workspace dump produced by the mass fitter to obtain
# the pdf and yields
#
# returns a dictionary with a pair { 'pdf': pdf, 'yield': yield }
def getMassTemplateOneMode2011Paper(
    config,	        # configuration dictionary
    ws,                 # workspace into which to import templates
    mass,	        # mass variable
    mode,	        # decay mode to load
    sname,              # sample name
    dsmass = None,      # ds mass variable
    pidk = None	        # pidk variable
    ):
    fromfile = config['MassTemplateFile']
    fromwsname = config['MassTemplateWorkspace']
    from ROOT import ( TFile, RooWorkspace, RooAbsPdf, RooAbsCategory,
        RooRealVar, RooArgSet, RooDataHist, RooHistPdf, RooArgList )
    import re

    # validate input (and break caller if invalid)
    if sname not in config['SampleCategories']: return None

    # open file and read in workspace
    fromfile = TFile(fromfile, 'READ')
    if fromfile.IsZombie():
        return None
    fromws = fromfile.Get(fromwsname)
    if None == fromws:
        return None
    ROOT.SetOwnership(fromws, True)

    # ok, depending on mode, we try to load a suitable pdf
    pdf, nYield = None, None
    for polsearch in config['MassTemplatePolaritySearch']:
        if mode == config['Modes'][0]:
            pdf = fromws.pdf('SigProdPDF_%s_%s' % (polsearch, sname))
            nYield = fromws.var('nSig_%s_%s_Evts' % (polsearch, sname))
            if None != nYield: nYield = nYield.getVal()
        elif mode == 'CombBkg':
            pdf = fromws.pdf('CombBkgPDF_m_%s_%s_Tot' % (polsearch, sname))
            if None == pdf:
                pdf = fromws.pdf('PhysBkgCombBkgPdf_m_%s_%s_Tot' % (polsearch, sname))
            nYield = fromws.var('nCombBkg_%s_%s_Evts' % (polsearch, sname))
            if None != nYield: nYield = nYield.getVal()
        else:
            # any other mode may or may not have separate samples for
            # magnet polarity, Ds decay mode, ...
            #
            # we therefore constuct a list of successively less specialised name
            # suffices so we can get the most specific pdf from the workspace
            modemap = {
                    'Bs2DsKst': 'Bs2DsDsstKKst',
                    'Bd2DsK': 'Bs2DsDsstKKst',
                    'Bs2DsstPi': ('BsLb2DsDsstPPiRho' if
                        'Bs2DsK' == config['Modes'][0] else 'Bs2DsDsstPi'),
                    'Bs2DsRho': ('Bs2DsDsstPiRho' if
                        'Bs2DsPi' == config['Modes'][0] else 'BsLb2DsDsstPPiRho'),
                    'Bs2DsstRho': 'Bs2DsDsstPiRho',
                    'Lb2Dsp': ('Lb2DsDsstP' if
                        'Bs2DsPi' == config['Modes'][0] else 'BsLb2DsDsstPPiRho'),
                    'Lb2Dsstp': ('Lb2DsDsstP' if
                        'Bs2DsPi' == config['Modes'][0] else 'BsLb2DsDsstPPiRho'),
                    'Bs2DsPi': 'Bs2DsPi',
                    'Lb2LcK': 'Lb2DsK',
                    'Lb2LcPi': 'Lb2DsPi',
                    'Bd2DK': 'Bd2DK',
                    'Bd2DPi': 'Bd2DPi',
                    'Bd2DsPi': ('Bs2DsDsstPi' if
                        'Bs2DsPi' == config['Modes'][0] else 'BsLb2DsDsstPPiRho'),
                    'Bs2DsPi': ('Bs2DsPi' if
                        'Bs2DsPi' == config['Modes'][0] else 'BsLb2DsDsstPPiRho'),
                    'Bs2DsK': 'Bs2DsK'
                    }
            trysfx = [
                '%sPdf_m_%s_%s_Tot' % (mode, polsearch, sname),
                '%sPdf_m_%s_Tot' % (mode, polsearch),
                '%sPdf_m_%s_%s_Tot' % (modemap[mode], polsearch, sname),
                '%sPdf_m_%s_Tot' % (modemap[mode], polsearch),
                # "modeless" names for single-mode DsPi toys (only in DsK, I
                # think, but we need the fallback solution at least once)
                '%sPdf_m_%s_%s_Tot' % (mode, polsearch, ''),
                '%sPdf_m_%s_%s_Tot' % (modemap[mode], polsearch, ''),
                ]
            for sfx in trysfx:
                pdf = fromws.pdf('PhysBkg%s' % sfx)
                if None != pdf:
                    break
            tryyieldsfx = [
                'n%s_%s_%s_Evts' % (mode, polsearch, sname),
                'n%s_%s_%s_Evts' % (mode.replace('Dsst', 'Dss'), polsearch, sname),
                'n%s_%s_%s_Evts' % (mode.replace('DsstP', 'Dsstp'), polsearch, sname),
                'n%s_%s_%s_Evts' % (mode.replace('DsstPi', 'DsstPiRho'), polsearch, sname),
                'n%s_%s_%s_Evts' % (modemap[mode], polsearch, sname),
                'n%s_%s_%s_Evts' % (modemap[mode].replace('Dsst', 'Dss'), polsearch, sname),
                'n%s_%s_%s_Evts' % (modemap[mode].replace('DsstP', 'Dsstp'), polsearch, sname),
                'n%s_%s_%s_Evts' % (modemap[mode].replace('DsstPi', 'DsstPiRho'), polsearch, sname),
                ]
            for sfx in tryyieldsfx:
                nYield = fromws.var(sfx)
                if None != nYield:
                    nYield = nYield.getVal()
                    break
	    if None == nYield and None == pdf: continue
            if None == nYield and mode in ('Bd2DK', 'Bd2DPi', 'Lb2LcK',
                    'Lb2LcPi'):
                # Agnieszka's yield-removal for modes that were not found
                nYield = 0.
            if tryyieldsfx[0] != sfx and tryyieldsfx[1] != sfx and 0. != nYield:
                # ok, we're in one of the modes which have a shared yield and a
                # fraction, so get the fraction, and fix up the yield 
                if 'Bs2DsDsstKKst' in sfx or 'Bs2DsDssKKst' in sfx:
                    f = fromws.var('g1_f1_frac')
                    if 'Bd2DsK' == mode:
                        f = f.getVal() if None != f else 1.
                    elif 'Bs2DsKst' == mode: 
                        f = (1. - f.getVal()) if None != f else 0.
                    else:
                        f = None
                elif ('BsLb2DsDsstPPiRho' in sfx and 'Bs2DsK' == config['Modes'][0]
                        and 'Bs2Ds' in mode):
                    f = fromws.var('g2_f2_frac')
                    if 'Bs2DsstPi' == mode:
                        f = f.getVal()
                    elif 'Bs2DsRho' == mode:
                        f = 1. - f.getVal()
                    elif 'Bs2DsPi' == mode:
                        f = fromws.var('g2_f1_frac').getVal()
                    else:
                        f = None
                    if None != f and 'Bs2DsPi' != mode:
                        f *= (1. - fromws.var('g2_f1_frac').getVal())
                    if None != f:
                        f *= fromws.var('g5_f1_frac').getVal()
                elif ('Lb2DsDsstP' in sfx or 'Lb2DsDsstp' in sfx or
                        ('Lb2Ds' in mode and 'BsLb2DsDsstPPiRho' in sfx)):
                    f = fromws.var('g3_f1_frac')
                    if 'Lb2Dsp' == mode:
                        f = f.getVal()
                    elif 'Lb2Dsstp' == mode:
                        f = 1. - f.getVal()
                    else:
                        f = None
                    if None != f and 'Bs2DsK' == config['Modes'][0]:
                        f *= (1. - fromws.var('g5_f1_frac').getVal())
                elif 'Bs2DsDsstPiRho' in sfx and 'Bs2DsPi' == config['Modes'][0]:
                    f = fromws.var('g1_f1_frac')
                    if 'Bs2DsstPi' == mode:
                        f = f.getVal()
                    elif 'Bd2DsPi' == mode:
                        f = 1. - f.getVal()
                    else:
                        f = None
                else:
                    print 'ERROR: Don\'t know how to fix mode %s/%s' % (sfx, mode)
                    return None
                # ok, fix the yield with the right fraction
                nYield = (nYield * f) if (0. != f) else 0.
        if None != pdf and None != nYield: break
    # ok, we should have all we need for now
    if None == pdf or None == nYield:
        if None == pdf and 0. != nYield:
            print '@@@@ - ERROR: NO PDF FOR MODE %s SAMPLE CATEGORY %s' % (
                    mode, sname)
            return None
        if None == nYield and 0. != nYield:
            print '@@@@ - ERROR: NO YIELD FOR MODE %s SAMPLE CATEGORY %s' % (
                    mode, sname)
            return None
    # figure out name of mass variable - should start with 'lab0' and end in
    # '_M'; while we're at it, figure out how we need to scale yields due to
    # potentially different mass ranges
    massname, dsmassname, pidkname = None, None, None
    yieldrangescaling = 1.
    if None != pdf:
        pdfvars = []
        varset = pdf.getVariables()
        ROOT.SetOwnership(varset, True)
        it = varset.createIterator()
        ROOT.SetOwnership(it, True)
        while True:
            obj = it.Next()
            if None == obj: break
            pdfvars.append(obj)
            pdfvarnames = [ v.GetName() for v in pdfvars ]
            regex = re.compile('^lab0.*_M$')
            regex1 = re.compile('^lab2.*_M*$')
            regex2 = re.compile('^lab1.*_PIDK$')
            for n in pdfvarnames:
                if regex.match(n):
                    oldmass = varset.find(n)
                    massname = n
                if regex1.match(n):
                    olddsmass = varset.find(n)
                    dsmassname = n
                if regex2.match(n):
                    oldpidk = varset.find(n)
                    pidkname = n
            else:
                # set anything else constant
                varset.find(n).setConstant(True)
        # figure out yield scaling due to mass ranges
        oldmass.setRange('signalRegion', mass.getMin(), mass.getMax())
        iset = nset = RooArgSet(oldmass, olddsmass, oldpidk)
        integral = pdf.createIntegral(iset, nset, 'signalRegion')
        ROOT.SetOwnership(integral, True)
        yieldrangescaling = integral.getVal()
        # ok, figure out yield
        nYield = RooRealVar('n%s_%s_Evts' % (mode, sname),
                'n%s_%s_Evts' % (mode, sname), nYield * yieldrangescaling)
    else:
        if 0. == nYield:
            nYield = RooRealVar('n%s_%s_Evts' % (mode, sname),
                    'n%s_%s_Evts' % (mode, sname), 0.)
    # import mass pdf and corresponding yield into our workspace
    # in the way, we rename whatever mass variable was used to the one supplied
    # by our caller
    nYield = WS(ws, nYield, [
        RooFit.RenameConflictNodes('_%s_%s' % (mode, sname)),
        RooFit.Silence()])
    if 0. != nYield.getVal():
        if None != ws.pdf(pdf.GetName()):
            # reuse pdf if it is already in the workspace - that's fine as long
            # as all parameters are fixed and the yields are not reused
            pdf = ws.pdf(pdf.GetName())
            # see if there is a binned version, if so prefer it
            if None != ws.pdf('%s_dhist_pdf' % pdf.GetName()):
                pdf = ws.pdf('%s_dhist_pdf' % pdf.GetName())
        else:
            # ok, pdf not in workspace, so swallow it
            if None != massname:
                fromnames = '%s,%s,%s' % (massname, dsmassname, pidkname)
                tonames = '%s,%s,%s' % (mass.GetName(), dsmass.GetName(),
                        pidk.GetName())
                if ROOT.gROOT.GetVersionInt() > 53405:
                    pdf = WS(ws, pdf, [ RooFit.Silence(),
                        RooFit.RenameVariable(fromnames, tonames),
                        RooFit.RenameConflictNodes('_%s_%s' % (mode, sname)),
                        RooFit.Silence()])
                else:
                    # work around RooFit's limitations in ROOT 5.34.05 and
                    # earlier...
                    tmpws = RooWorkspace()
                    pdf = WS(tmpws, pdf, [ RooFit.Silence(),
                        RooFit.RenameVariable(fromnames, tonames)])
                    pdf = WS(ws, pdf, [
                        RooFit.RenameConflictNodes('_%s_%s' % (mode, sname)),
                        RooFit.Silence()])
                    del tmpws
            else:
                pdf = WS(ws, pdf, [
                    RooFit.RenameConflictNodes('_%s_%s' % (mode, sname)),
                    RooFit.Silence()])
            if config['NBinsMass'] > 0 and not config['MassInterpolation']:
                print 'WARNING: binned mass requested for %s/%s ' \
                    'mass/dsmass/pidk shape - not implemented yet' % (mode, sname)
    else:
        # yield is zero, so put a dummy pdf there
        from ROOT import RooUniform
        pdf = RooUniform('DummyPdf_m_both_Tot', 'DummyPdf_m_both_Tot',
                RooArgSet(mass, dsmass, pidk))
    # ok, all done, return
    if config['MassInterpolation']:
        print 'WARNING: interpolation requested for %s/%s mass/dsmass/pidk ' \
                'shape - not implemented yet' % (mode, sname)
    if None != nYield:
        nYield.setConstant(True)
    pdf = WS(ws, pdf)
    nYield = WS(ws, nYield)
    return { 'pdf': pdf, 'yield': nYield }


# read mass templates for specified modes
#
# returns dictionary d['mode']['polarity']['kkpi/kpipi/pipipi'] which contains
# a dictionary of pairs { 'pdf': pdf, 'yield': yield }
def getMassTemplates(
    config,		# configuration dictionary
    ws,			# wksp into which to import templates
    mass,		# mass variable
    dsmass = None,      # ds mass variable
    pidk = None,        # pidk variable
    snames = None       # sample names to read
    ):
    personalisedGetMassTemplateOneMode = {
            '2011Conf': getMassTemplateOneMode2011Conf,
            '2011ConfDATA': getMassTemplateOneMode2011Conf,
            '2011PaperDsK': getMassTemplateOneMode2011Paper,
            '2011PaperDsPi': getMassTemplateOneMode2011Paper,
            '2011PaperDsKDATA': getMassTemplateOneMode2011Paper,
            '2011PaperDsPiDATA': getMassTemplateOneMode2011Paper,
            '2011PaperDsK-Agn70': getMassTemplateOneMode2011Paper,
            '2011PaperDsK-Agn116': getMassTemplateOneMode2011Paper,
            '2011PaperDsK-Agn140': getMassTemplateOneMode2011Paper,
            '2011PaperDsPi-Agn70': getMassTemplateOneMode2011Paper,
            '2011PaperDsKDATA-sFit': getMassTemplateOneMode2011Paper,
            '2011PaperDsPiDATA-sFit': getMassTemplateOneMode2011Paper,
            '2011PaperDsK-Agn70-sFit': getMassTemplateOneMode2011Paper,
            '2011PaperDsK-Agn140-sFit': getMassTemplateOneMode2011Paper,
            '2011PaperDsPi-Agn70-sFit': getMassTemplateOneMode2011Paper,
            '2011PaperDsK-MC': getMassTemplateOneMode2011Paper,
            }
    import sys
    if None == snames:
        snames = config['SampleCategories']
    retVal = {}
    for mode in config['Modes']:
        for sname in snames:
            tmp = personalisedGetMassTemplateOneMode[ config['Personality'] ](
                    config, ws, mass, mode, sname, dsmass, pidk)
            if None == tmp:
                # break caller in case of error
                return None
            if mode not in retVal: retVal[mode] = {}
            retVal[mode][sname] = tmp
    sample = ws.obj('sample')
    totyield = 0.
    totyields = [ 0. for i in snames ]
    for sname in snames:
        for mode in config['Modes']:
            i = sample.lookupType('%s' % sname).getVal()
            totyield += retVal[mode][sname]['yield'].getVal()
            totyields[i] += retVal[mode][sname]['yield'].getVal()
    # scale the yields to the desired number of events
    for sname in snames:
        for mode in config['Modes']:
            i = sample.lookupType('%s' % sname).getVal()
            y = retVal[mode][sname]['yield']
            if len(config['SampleCategories']) == len(config['NEvents']):
                y.setVal(y.getVal() * (config['NEvents'][i] / totyields[i]))
            elif 1 == len(config['NEvents']):
                y.setVal(y.getVal() * (config['NEvents'][0] / totyield))
            else:
                print 'ERROR: invalid length of config[\'NEvents\']!'
                sys.exit(1)
            # make sure things stay constant
            y.setConstant(True)
    if None != config['S/B']:
        # allow users to hand-tune S/B (if desired)
        sigmode = config['Modes'][0]
        nsig, nbg = 0., 0.
        for sname in snames:
            for mode in config['Modes']:
                y = retVal[mode][sname]['yield']
                if sigmode == mode:
                    nsig += y.getVal()
                else:
                    nbg += y.getVal()
        sb = config['S/B']
        for sname in snames:
            for mode in config['Modes']:
                y = retVal[mode][pol][DsMode]['yield']
                if sigmode == mode:
                    y.setVal(sb / (1. + sb) * (nsig + nbg) * (
                        y.getVal() / nsig))
                else:
                    y.setVal(1. / (1. + sb) * (nsig + nbg) * (
                        y.getVal() / nbg))

    return retVal
