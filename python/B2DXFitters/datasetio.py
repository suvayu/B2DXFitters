"""
@file datasetio.py

@author Manuel Schiller <Manuel.Schiller@cern.ch>
@date 2015-05-24

@brief read and write data sets and templates
"""

import ROOT
from B2DXFitters.WS import WS as WS

# read a 1D template from a file (either PDF,data set, or plain 1D TH1)
def readTemplate1D(
    fromfile,           # file to read from
    fromws,             # workspace to read from
    fromvarname,        # variable name in fromws
    objname,            # object to ask for
    ws,                 # workspace to import into
    variable,           # variable
    pfx,                # prefix of imported objects
    binIfPDF = False    # bin if the template comes as Pdf
    ):
    """
    read a 1D template from a file (either PDF,data set, or plain 1D TH1)

    fromfile --     name of file to read from
    fromws --       name of workspace to read from (or None for plain TH1)
    fromvarname --  name of dependent variable in workspace
    objname --      name of pdf, data set, or histogram
    ws --           workspace into which to import template
    variable --     dependent variable of template after import into ws
    pfx --          name prefix for imported objects
    binIfPDF --     if True and the object is a pdf, bin upon import

    This routine is a generic 1D template importer. It will read PDFs and
    RooDataSets from RooWorkspaces, or read a plain TH1*. It will then import
    this object into the workspace given by ws, and "connect" it to the
    variable given in variable (this can be used to "rename" variables when
    the original template in the file does not have the right name).
    """
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
    binning = RooBinning(bins.size() - 1, bins.data() if ROOT.gROOT.GetVersionCode() > 0x53600 else bins.begin().base())
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

# read dataset from workspace
def readDataSet(
    config,             # configuration dictionary
    ws,                 # workspace to which to add data set
    observables,        # observables
    rangeName = None    # name of range to clip dataset to
    ):
    """
    read data set from given Ntuple (or a RooDataSet inside a workspace) into
    a RooDataSet

    arguments:
    config      -- configuration dictionary (see below for relevant keys)
    ws          -- workspace into which to import data from tuple
    observables -- RooArgSet containing the observables to be read
    rangeName   -- optional, can be the name of a range of one observable, if
                   the data read from the tuple needs to be explicitly clipped
                   to that range for some reason

    the routine returns the data set that has been read in and stored inside
    ws.

    relevant configuration dictionary keys:
    'DataFileName' -- file name of data file from which to read ntuple or data
                      set
    'DataSetNames' -- name (TTree or RooDataSet) of the data set to be read;
                      more than one can be given in a dictionary, providing a
                      mapping between the sample name and the data set to be
                      read (see below for an explanation)
    'DataWorkSpaceName'
                   -- name of workspace to read data from (if any - leave None
                      for reading tuples)
    'DataSetCuts' --  cuts to apply to data sets on import - anything that
                      RooDataSet.reduce will understand is permissible here
                      (set to None to not apply any cuts on import)
    'DataSetVarNameMapping'
                   -- mapping from variable names in set of observables to
                      what these variable names are called in the
                      tuple/workspace to be imported

    "special" observable names:
    The routine treats some variable names special on import based on their
    likely meaning:
    'weight' -- this variable name must be used to read in (s)weighted events
    'qf'     -- final state charge (e.g. +1 for K+ vs -1 for K-); only the
                sign is important here, and the import code enforces that
    'qt'     -- tagging decision; this can be any integer number (positive or
                negative); if the tuple should contain a float/double with
                that information, it is rounded appropriately
    'mistag' -- predicted mistag; the import code makes sure that events with
                qt == 0 have mistag = 0.5
    'sample' -- if more than one final state is studied (e.g. Ds final states
                phipi, kstk, nonres, kpipi, pipipi), the events for these
                subsamples often reside in different samples; therefore the
                config dictionary entry 'DataSetNames' can contain a
                dictionary which maps the category labels (phipi etc) to the
                names of the data samples in the ROOT file/workspace

    The config dict key 'DataSetVarNameMapping' contains a useful feature:
    Instead of providing a one-to-one-mapping of observables to tuple/data set
    names, an observable can be calculated from more than one tuple column.
    This is useful e.g. to convert a tuple that's stored the tagging decision
    as untagged/mixed/unmixed, or to sum up sweights for the different
    samples. Most simple formulae should be supported, but constants in
    scientific notation (1.0E+00) are not for now (until someone write a
    better parser for this).

    Example:
    @code
    seed = 42 # it's easy to modify the filename depending on the seed number
    configdict = {
        # file to read from
        'DataFileName': '/some/path/to/file/with/toy_%04d.root' % seed,
        # data set is in a workspace already
        'DataWorkSpaceName':    'FitMeToolWS',
        # name of data set inside workspace
        'DataSetNames':         'combData',
        # mapping between observables and variable name in data set
        'DataSetVarNameMapping': {
            'sample':  'sample',
            'mass':    'lab0_MassFitConsD_M',
            'pidk':    'lab1_PIDK',
            'dsmass':  'lab2_MM',
            'time':    'lab0_LifetimeFit_ctau',
            'timeerr': 'lab0_LifetimeFit_ctauErr',
            'mistag':  'tagOmegaComb',
            'qf':      'lab1_ID',
            'qt': '    tagDecComb',
            # sweights need to be combined from different branches in this
            # case, only one of the branches is ever set to a non-zero value,
            # depending on which subsample the event is in
            'weight': ('nSig_both_nonres_Evts_sw+nSig_both_phipi_Evts_sw+'
                       'nSig_both_kstk_Evts_sw+nSig_both_kpipi_Evts_sw+'
                       'nSig_both_pipipi_Evts_sw')
            }
        }
    # define all observables somewhere, and put the into a RooArgSet called obs
    # import observables in to a workspace saved in ws

    # now read the data set
    data = readDataSet(configdict, ws, observables)
    @endcode
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
        # # additional complication: toys save decay time in ps, data is in nm
        # # figure out which time conversion factor to use
        # timeConvFactor = 1e9 / 2.99792458e8
        # meantime = sdata.mean(smap['time'])
        # if ((dmap['time'].getMin() <= meantime and
        #         meantime <= dmap['time'].getMax() and config['IsToy']) or
        #         not config['IsToy']):
        #     timeConvFactor = 1.
        # print 'DEBUG: Importing data sample meantime = %f, timeConvFactor = %f' % (
        #         meantime, timeConvFactor)
        timeConvFactor = 1.
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
    """
    writes a given data set into a given tree in a given file

    dataset  -- RooDataSet to write to ntuple
    filename -- ROOT file to write tuple to
    treename -- name of TTree instance inside ROOT file
    bnamemap -- branch name renaming map (default: empty, no renaming done)

    example:
    @code
    data = # get RooDataSet from somewhere
    writeDataSet(data,
        '/path/to/some/file.root',
        'datasetnameinrootfile',
        {
            # variable mass in data is renamed to bsmass in file, pidk is
            # uppercased
            'mass': 'bsmass',
            'pidk': 'PIDK'
        })
    @endcode
    """
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


