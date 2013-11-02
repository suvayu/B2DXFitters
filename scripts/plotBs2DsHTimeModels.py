#!/bin/sh
# -*- mode: python; coding: utf-8 -*-
# vim: ft=python:sw=4:tw=78
""":"
# This part is run by the shell. It does some setup which is convenient to save
# work in common use cases.

# make sure the environment is set up properly
if test -n "$CMTCONFIG" \
         -a -f $B2DXFITTERSROOT/$CMTCONFIG/libB2DXFittersDict.so \
     -a -f $B2DXFITTERSROOT/$CMTCONFIG/libB2DXFittersLib.so; then
    # all ok, software environment set up correctly, so don't need to do 
    # anything
    true
else
    if test -n "$CMTCONFIG"; then
    # clean up incomplete LHCb software environment so we can run
    # standalone
        echo Cleaning up incomplete LHCb software environment.
        PYTHONPATH=`echo $PYTHONPATH | tr ':' '\n' | \
            egrep -v "^($User_release_area|$MYSITEROOT/lhcb)" | \
            tr '\n' ':' | sed -e 's/:$//'`
        export PYTHONPATH
        LD_LIBRARY_PATH=`echo $LD_LIBRARY_PATH | tr ':' '\n' | \
            egrep -v "^($User_release_area|$MYSITEROOT/lhcb)" | \
            tr '\n' ':' | sed -e 's/:$//'`
        export LD_LIBRARY_PATH
        exec env -u CMTCONFIG -u B2DXFITTERSROOT "$0" "$@"
    fi
    # automatic set up in standalone build mode
    if test -z "$B2DXFITTERSROOT"; then
        cwd="$(pwd)"
        if test -z "$(dirname $0)"; then
        # have to guess location of setup.sh
        cd ../standalone
        . ./setup.sh
        cd "$cwd"
        else
        # know where to look for setup.sh
        cd "$(dirname $0)"/../standalone
        . ./setup.sh
        cd "$cwd"
        fi
    unset cwd
    fi
fi

# figure out which custom allocators are available
# prefer jemalloc over tcmalloc
for i in libjemalloc libtcmalloc; do
    for j in `echo "$LD_LIBRARY_PATH" | tr ':' ' '` \
        /usr/local/lib /usr/lib /lib; do
        for k in `find "$j" -name "$i"'*.so.?' | sort -r`; do
            if test \! -e "$k"; then
            continue
        fi
        echo adding $k to LD_PRELOAD
        if test -z "$LD_PRELOAD"; then
            export LD_PRELOAD="$k"
            break 3
        else
            export LD_PRELOAD="$LD_PRELOAD":"$k"
            break 3
        fi
    done
    done
done

# set batch scheduling (if schedtool is available)
schedtool="`which schedtool 2>/dev/zero`"
if test -n "$schedtool" -a -x "$schedtool"; then
    echo "enabling batch scheduling for this job (schedtool -B)"
    schedtool="$schedtool -B -e"
else
    schedtool=""
fi

# set ulimit to protect against bugs which crash the machine: 2G vmem max,
# no more then 8M stack
ulimit -v $((2048 * 1024))
ulimit -s $((   8 * 1024))

# trampoline into python
exec $schedtool /usr/bin/time -v env python -O -- "$0" "$@"
"""
__doc__ = """ real docstring """
# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
import B2DXFitters
import ROOT
from ROOT import RooFit

from optparse import OptionParser
from math     import pi
import os, sys

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

# MISCELLANEOUS
bName = 'B_{s}'
isDsK = True

nBinsTime = 30 if isDsK else 66
defaultModes = (
        # modes for DsK
        ['Bs2DsK', 'Bs2DsKst', 'Bs2DsPi', 'Bs2DsstPi', 'Bs2DsRho', 'Bd2DK',
            'Bd2DsK', 'Lb2LcK', 'Lb2Dsp', 'Lb2Dsstp', 'CombBkg']
        if isDsK else
        # modes for DsPi
        [ 'Bs2DsPi', 'Bd2DPi', 'Bs2DsstPi', 'Bd2DsPi', 'Bs2DsK', 'Lb2LcPi',
            'CombBkg'])



#------------------------------------------------------------------------------
def WS(ws, obj, opts = [RooFit.RecycleConflictNodes(), RooFit.Silence()]):
    name = obj.GetName()
    wsobj = ws.obj(name)
    if obj.InheritsFrom('RooAbsArg') or obj.InheritsFrom('RooAbsData'):
        if None == wsobj:
            if len(opts) > 0:
                ws.__getattribute__('import')(obj, *opts)
            else:
                ws.__getattribute__('import')(obj)
            wsobj = ws.obj(name)
        else:
            if wsobj.Class() != obj.Class():
                raise TypeError()
    elif obj.InheritsFrom('RooArgSet'):
        if None == wsobj:
            ws.defineSet(name, obj, True)
            wsobj = ws.set(name)
        else:
            if wsobj.Class() != obj.Class():
                raise TypeError()
    else:
        if None == wsobj:
            ws.__getattribute__('import')(obj, name)
            wsobj = ws.obj(name)
        else:
            if wsobj.Class() != obj.Class():
                raise TypeError()

#------------------------------------------------------------------------------
def plotDataSet(frame, wksp, dsname, options = []) :
    from ROOT import RooLinkedList
    plotopts = RooLinkedList()
    for o in options:
        plotopts.Add(o)
    ds = wksp.data(dsname)
    ds.plotOn(frame, plotopts)
    #dataset.statOn(frame,
    #                RooFit.Layout(0.56, 0.90, 0.90),
    #                RooFit.What('N'))

#------------------------------------------------------------------------------
def plotFitModel(frame, wksp, modelname, options = [], sliceoptlist = [ [] ],
        modes = defaultModes,
        snames = ['nonres', 'phipi', 'kstk', 'kpipi', 'pipipi']):
    from ROOT import ( RooLinkedList, kRed, kBlue, kGreen, kOrange, kYellow,
            kMagenta, kCyan, kBlack )
    components = {}
    for mode in modes:
        tmp = []
        for sname in snames:
            compname = '%s_%s_PDF' % (mode, sname)
            if None == wksp.pdf(compname): continue
            if len(tmp): tmp.append(',')
            tmp.append(compname)
        if not len(tmp): continue
        components[mode] = ''.join(tmp)

    model = wksp.pdf(modelname)

    # FIXME: do something nicer here, both nicer colors, and be consistent
    # between DsK and DsPi for the BG contributions (use a dictionary!)
    colors = [ ROOT.kRed, ROOT.kGreen + 2, ROOT.kOrange, ROOT.kMagenta,
            ROOT.kBlue + 2, ROOT.kCyan + 1, ROOT.kYellow, ROOT.kBlack,
            ROOT.kRed + 2, ROOT.kMagenta + 2, ROOT.kGreen, ROOT.kYellow + 2 ]
    # plot the total PDF
    for slopts in sliceoptlist:
        isl = sliceoptlist.index(slopts)
        name = '%s_slice%d' % (model.GetName(), isl)
        lastname = '%s_slice%d' % (model.GetName(), isl - 1)
        opts = list(options) + slopts
        opts.append(RooFit.Name(name))
        if isl + 1 != len(sliceoptlist) and 1 < len(sliceoptlist):
            opts.append(RooFit.Invisible())
        if 0 != isl:
            opts.append(RooFit.AddTo(lastname, 1., 1.))
        plotopts = RooLinkedList()
        for o in opts:
            plotopts.Add(o)
        model.plotOn(frame, plotopts)

        # plot the different components
        i = 0
        for mode in components:
            print 'DEBUG: MODE %s COMPONENTS %s' % (mode, components[mode])
            name = '%s_%s_slice%d' % (model.GetName(), mode, isl)
            lastname = '%s_%s_slice%d' % (model.GetName(), mode, isl - 1)
            opts = list(options) + slopts
            opts.append(RooFit.Name(name))
            if isl + 1 != len(sliceoptlist) and 1 < len(sliceoptlist):
                opts.append(RooFit.Invisible())
            if 0 != isl:
                opts.append(RooFit.AddTo(lastname, 1., 1.))
            opts = opts + [ RooFit.LineWidth(1), RooFit.LineColor(colors[i]),
                    RooFit.Components(components[mode]) ]
            i = i + 1
            plotopts = RooLinkedList()
            for o in opts:
                plotopts.Add(o)
            model.plotOn(frame, plotopts)

    # put model parameters on plot
    #model.paramOn(frame,
    #               RooFit.Layout(0.56, 0.90, 0.85),
    #               RooFit.Format('NEU', RooFit.AutoPrecision(2)))

#------------------------------------------------------------------------------
def legends(model, frame):
    # FIXME: very much out of date!
    stat = frame.findObject('data_statBox')
    prefix = 'Sig' if signalModelOnly else 'Tot'
    if not stat: stat = frame.findObject('%sEPDF_tData_statBox' % prefix)
    if stat :
        stat.SetTextSize(0.025)
    pt = frame.findObject('%sEPDF_t_paramBox' % prefix)
    if pt :
        pt.SetTextSize(0.02)
    # Legend of EPDF components
    leg = TLegend(0.56, 0.42, 0.87, 0.62)
    leg.SetFillColor(0)
    leg.SetTextSize(0.02)
    comps = model.getComponents()
    if signalModelOnly :
        pdfName = 'sigEPDF_t'
        pdf = comps.find(pdfName)
        curve = frame.findObject(pdfName + '_Norm[time]')
        if curve : leg.AddEntry(curve, pdf.GetTitle(), 'l')
        return leg, curve
    else :
        pdf1 = comps.find('sigEPDF_t')
        pdfName = 'TotEPDF_t_Norm[time]_Comp[%s]' % 'sigEPDF_t'
        curve1 = frame.findObject(pdfName)
        if curve1 : leg.AddEntry(curve1, pdf1.GetTitle(), 'l')
        pdf = comps.find('Bd2DKEPDF_t')
        pdfName = 'TotEPDF_t_Norm[time]_Comp[%s]' % 'Bd2DKEPDF_t'
        curve2 = frame.findObject(pdfName)
        if curve2 : leg.AddEntry(curve2, pdf.GetTitle(), 'l')
        pdf = comps.find('CombBkgEPDF_t')
        pdfName = 'TotEPDF_t_Norm[time]_Comp[%s]' % 'CombBkgEPDF_t'
        curve3 = frame.findObject(pdfName)
        if curve3 : leg.AddEntry(curve3, pdf.GetTitle(), 'l')
        pdfName = 'TotEPDF_t_Norm[time]_Comp[%s]' % 'CombBkgEPDF_t,Bd2DKEPDF_t'
        curve4 = frame.findObject(pdfName)
        if curve4 :
            leg.AddEntry(curve4, 'All but %s' % pdf1.GetTitle(), 'f')
            curve4.SetLineColor(0)
        pdfName = 'TotEPDF_t_Norm[time]'
        pdf = comps.find('TotEPDF_t')
        curve5 = frame.findObject(pdfName)
        #if curve5 : leg.AddEntry(curve5, pdf.GetTitle(), 'l')
        if curve5 : leg.AddEntry(curve5, 'Model (signal & background) EPDF', 'l')
        return leg, curve4

#------------------------------------------------------------------------------
_usage = '%prog [options] <filename>'

parser = OptionParser(_usage)

parser.add_option('-w', '--workspace',
                   dest = 'wsname',
                   metavar = 'WSNAME',
                   default = 'WS_FIT',
                   help = 'RooWorkspace name as stored in ROOT file'
)

#------------------------------------------------------------------------------

if __name__ == '__main__' :
    (options, args) = parser.parse_args()

    if len(args) != 1 :
        parser.print_help()
        exit(-1)

    FILENAME = (args[ 0 ])
    if not os.path.exists(FILENAME) :
        parser.error('ROOT file "%s" not found! Nothing plotted.' % FILENAME)
        parser.print_help()

    from ROOT import TFile, TCanvas, gROOT, TLegend, RooAbsReal
    gROOT.SetBatch( True )

    gROOT.SetStyle('Plain')

    RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-9)
    RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-9)
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','15Points')
    RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 1000)
    RooAbsReal.defaultIntegratorConfig().method1D().setLabel('RooAdaptiveGaussKronrodIntegrator1D')
    RooAbsReal.defaultIntegratorConfig().method1DOpen().setLabel('RooAdaptiveGaussKronrodIntegrator1D')

    f = TFile(FILENAME)

    w = f.Get(options.wsname)
    #w.Print('v')
    if not w :
        parser.error('Workspace "%s" not found in file "%s"! Nothing plotted.' %\
                      (options.wsname, FILENAME))

    time = w.var('time')
    time.setRange(time.getMin(), 8.0)
    time.setBins(nBinsTime)
    mass = w.var('mass')
    mass.setBins(25)

    datasetname = ('agglomeration' if None != w.data('agglomeration')
            else 'hmaster')

    plots = [ [ 'all data',  [], [ [] ] ],
            [ ('B_{s} #rightarrow D_{s}^{-}K^{+} + #bar{B_{s}} #rightarrow D_{s}^{+}K^{-}'
                if isDsK else
                'B_{s} #rightarrow D_{s}^{-}#pi^{+} + #bar{B_{s}} #rightarrow D_{s}^{+}#pi^{-}'),
                [ RooFit.Cut("+1 == qf*qt") ],
                [ [ RooFit.Slice(w.cat('qt'), 'B'),
                    RooFit.Slice(w.cat('qf'), 'h+') ],
                    [ RooFit.Slice(w.cat('qt'), 'Bbar'),
                        RooFit.Slice(w.cat('qf'), 'h-') ] ]
                ],
            [ ('B_{s} #rightarrow D_{s}^{+}K^{-} + #bar{B_{s}} #rightarrow D_{s}^{-}#K^{+}'
                if isDsK else
                'B_{s} #rightarrow D_{s}^{+}#pi^{-} + #bar{B_{s}} #rightarrow D_{s}^{-}#pi^{+}'),
                [ RooFit.Cut("-1 == qf*qt") ],
                 [ [ RooFit.Slice(w.cat('qt'), 'B'),
                     RooFit.Slice(w.cat('qf'), 'h-') ],
                     [ RooFit.Slice(w.cat('qt'), 'Bbar'),
                         RooFit.Slice(w.cat('qf'), 'h+') ] ]
                ]
            ]

    iplot = 0
    for p in plots:
        canvas = TCanvas('TimeCanvas', 'Decay time canvas')
        canvas.SetTitle('Fit in decay time')
        canvas.cd()

        frame_t = time.frame()
        #frame_m = mass.frame()

        frame_t.SetTitle('Fit in reconstructed %s decay time (%s)' % (bName, p[0]))

        frame_t.GetXaxis().SetLabelSize(0.03)
        frame_t.GetYaxis().SetLabelSize(0.03)

        dataplotopts = p[1]
        pdfplotopts = [
                RooFit.Precision(1e-6),
                # I suppose we need to tweak the normalisation because sample has
                # five states (nonres, phipi, kstk, kpipi, pipipi)
                RooFit.Normalization(.2, RooAbsReal.Relative) ]
        sliceopts = p[2]
        plotDataSet(frame_t, w, datasetname, dataplotopts)

        frame_t.Draw()
        canvas.Update()
        #canvas.SetLogy(True)
        canvas.Print(FILENAME + '.%u.time.dataonly.pdf' % iplot)
        
        plotFitModel(frame_t, w, 'TotEPDF', pdfplotopts, sliceopts)

        #leg, curve = legends(modelPDF, frame_t)
        #frame_t.addObject(leg)

        frame_t.Draw()
        canvas.Update()
        #canvas.SetLogy(True)
        canvas.Print(FILENAME + '.%u.time.dataandpdf.pdf' % iplot)

        #plotDataSet(frame_m, w, datasetname, dataplotopts)
        #plotFitModel(frame_m, w, 'TotEPDF', pdfplotopts, sliceopts)

        #frame_m.Draw()

        #canvas.Update()
        #canvas.SetLogy(False)
        #canvas.Print(FILENAME + '.mass.eps')
        del canvas
        iplot = iplot + 1
    f.Close()

#------------------------------------------------------------------------------
