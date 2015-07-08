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
        # try to find from where script is executed, use current directory as
        # fallback
        tmp="$(dirname $0)"
        tmp=${tmp:-"$cwd"}
        # convert to absolute path
        tmp=`readlink -f "$tmp"`
        # move up until standalone/setup.sh found, or root reached
        while test \( \! -d "$tmp"/standalone \) -a -n "$tmp" -a "$tmp"\!="/"; do
            tmp=`dirname "$tmp"`
        done
        if test -d "$tmp"/standalone; then
            cd "$tmp"/standalone
            . ./setup.sh
        else
            echo `basename $0`: Unable to locate standalone/setup.sh
            exit 1
        fi
        cd "$cwd"
        unset tmp
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
from ROOT import RooFit, RooArgSet, RooArgList

from optparse import OptionParser
from math     import pi
import os, sys

# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

# MISCELLANEOUS
bName = 'B_{s}'
isDsK = True

onlyLargeModes = not True

nBinsTime = 146 if isDsK else 146
defaultModes = (
        # modes for DsK
        #[ ]
        ( 
           # ['Bs2DsK', 'Bs2DsPi', 'Bs2DsstPi', 'Bs2DsRho', 'CombBkg']
            ['Bs2DsK', 'Bs2DsPi', ['Bs2DsstPi', 'Bs2DsRho'], ['Bd2DK',
                'Bd2DPi', 'Lb2LcK', 'Lb2LcPi', 'Lb2Dsp', 'Lb2Dsstp',
                'Bd2DsK'], 'CombBkg']
            if onlyLargeModes else
            ['Bs2DsK', 'Bs2DsPi', 'Bs2DsstPi', 'Bs2DsRho', 'Bd2DK', 'Bd2DPi', 'Lb2LcK', 'Lb2LcPi', 'Lb2Dsp', 'Lb2Dsstp', 'Bd2DsK', 'CombBkg']
            )
        if isDsK else
        # modes for DsPi
        #[ ]
        [ 'Bs2DsPi', 'Bd2DPi', 'Bs2DsstPi', 'Bd2DsPi', 'Bs2DsK', 'Lb2LcPi', 'CombBkg']
        )

groupedmodes = {
        'Bs2DsstPi': 'B_{s}^{0} #rightarrow     D_{s}^{(*)-}(#pi^{+},#rho^{+})',
        'Bd2DK': '(B_{d}^{0},#Lambda_{b}^{0}) #rightarrow X',
        } if onlyLargeModes else { }

# FIXME: do something nicer here, both nicer colors, and be consistent
# between DsK and DsPi for the BG contributions (use a dictionary!)
from ROOT import ( RooLinkedList, kRed, kBlue, kGreen, kOrange, kYellow,
        kMagenta, kCyan, kBlack, kSolid, kDashed )

styledict = {
        'Bs2DsK':       { 'color': kBlue + 3, 'style': 9 if onlyLargeModes else 1 },
        'Bs2DsPi':      { 'color': kMagenta - 2, 'style': 3 if onlyLargeModes else 1 },
        'Bs2DsstPi':    { 'color': kMagenta - 2, 'style': 4 },
        'Bs2DsRho':     { 'color': kMagenta - 2, 'style': 5 },
        'Bd2DK':        { 'color': kRed, 'style': 5 if onlyLargeModes else 1 },
        'Bd2DPi':       { 'color': kRed, 'style': 2 },
        'Lb2LcK':       { 'color': kGreen + 3, 'style': 1 },
        'Lb2LcPi':      { 'color': kGreen + 3, 'style': 2 },
        'Lb2Dsp':       { 'color': kYellow + 1, 'style': 1 },
        'Lb2Dsstp':     { 'color': kYellow + 1, 'style': 2 },
        'Bd2DsK':       { 'color': kBlue - 10, 'style': 1 },
        'CombBkg':      { 'color': kBlue - 6, 'style': 2 if onlyLargeModes else 1 },
        }

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
    from ROOT import RooFit, RooLinkedList
    plotopts = RooLinkedList()
    for o in options:
        plotopts.Add(o)
    ds = wksp.data(dsname)
    ds.plotOn(frame, plotopts)
    hist = frame.getHist('h_%s' % ds.GetName())
    for i in xrange(0, hist.GetN()):
        if 0. == abs(hist.GetY()[i]):
            hist.SetPointEYhigh(i, 0.)
            hist.SetPointEYlow(i, 0.)
    return ds
    #dataset.statOn(frame,
    #                RooFit.Layout(0.56, 0.90, 0.90),
    #                RooFit.What('N'))

#------------------------------------------------------------------------------
def plotFitModel(frame, wksp, modelname, options = [], sliceoptlist = [ [] ],
        modes = defaultModes,
        snames = ['nonres', 'phipi', 'kstk', 'kpipi', 'pipipi']):
    components = {} 
    modEx = {}
    for mode in modes:
        if type(mode) == list:
            lmodes = mode
            modenick = mode[0]
        else:
            modenick = mode
            lmodes = [mode]
        tmp = []
        for mmm in lmodes:
            for sname in snames:
                compname = '%s_%s_PDF' % (mmm, sname)
                if None == wksp.pdf(compname): continue
                if len(tmp): tmp.append(',')
                tmp.append(compname)
        if not len(tmp): 
            modEx[modenick] = False
            continue
        else:
            modEx[modenick] = True
        components[modenick] = ''.join(tmp)
        
    model = wksp.pdf(modelname)

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
        mainplot = model.plotOn(frame, plotopts)

        pull = frame.pullHist()
        # plot the different components
        
        i = 0
        for mode in defaultModes:
            if type(mode) == list:
                lmodes = mode
                modenick = mode[0]
            else:
                modenick = mode
                lmodes = [mode]
            if modEx[modenick] == False: 
                i=i+1
                continue 
            print 'DEBUG: MODE %s COMPONENTS %s for %d' % (mode, components[modenick], i)
            name = '%s_%s_slice%d' % (model.GetName(), mode, isl)
            lastname = '%s_%s_slice%d' % (model.GetName(), lmodes[len(lmodes)-1], isl - 1)
            opts = list(options) + slopts
            opts.append(RooFit.Name(name))
            if isl + 1 != len(sliceoptlist) and 1 < len(sliceoptlist):
                opts.append(RooFit.Invisible())
            if 0 != isl:
                opts.append(RooFit.AddTo(lastname, 1., 1.))
            opts = opts + [ RooFit.LineWidth(2),
                    RooFit.LineColor(styledict[modenick]['color']),
                    RooFit.LineStyle(styledict[modenick]['style']),
                    RooFit.Components(components[modenick]) ]
            i = i + 1
            plotopts = RooLinkedList()
            for o in opts:
                plotopts.Add(o)
            model.plotOn(frame, plotopts)
             
    # put model parameters on plot
    #model.paramOn(frame,
    #               RooFit.Layout(0.56, 0.90, 0.85),
    #               RooFit.Format('NEU', RooFit.AutoPrecision(2)))
    return mainplot, pull

#------------------------------------------------------------------------------
def legend():
    from ROOT import TLegend, TH1D, TGraphErrors, TLine
    from B2DXFitters import TLatexUtils
    # Legend of EPDF components
    leg = TLegend(0.475, 0.50, 0.89, 0.89)
    leg.SetTextSize(0.05)
    leg.SetTextFont(12)
    leg.SetFillColor(0)
    leg.SetShadowColor(0)
    leg.SetBorderSize(0)
    leg.SetTextFont(132)
    leg.SetNColumns(1 if onlyLargeModes else 2)
    
    gr = TGraphErrors(10)
    gr.SetName("gr")
    gr.SetLineColor(kBlack)
    gr.SetLineWidth(2)
    gr.SetMarkerStyle(20)
    gr.SetMarkerSize(1.3)
    gr.SetMarkerColor(ROOT.kBlack)
    gr.Draw("P")
    ROOT.SetOwnership(gr, False)
    leg.AddEntry("gr","data","lep")
    
    ths = []
    ths.append(TLine())
    ths[0].SetLineColor(kBlue)
    ths[0].SetLineWidth(4)
    ths[0].SetLineStyle(1)
    ROOT.SetOwnership(ths[0], False)
    leg.AddEntry(ths[0],"total",'L')

    for m in defaultModes:
        if type(m) == list:
            lmodes = m
            modenick = m[0]
        else:
            modenick = m
            lmodes = [m]
        if modenick in groupedmodes:
            tmpmode = groupedmodes[modenick]
        else:
            tmpmode = modenick
        prettym = str(TLatexUtils.DecDescrToTLatex(tmpmode))
        i = len(ths)
        ths.append(TLine())
        ths[i].SetLineColor(styledict[modenick]['color'])
        ths[i].SetLineWidth(4)
        ths[i].SetLineStyle(styledict[modenick]['style'])
        ROOT.SetOwnership(ths[i], False)
        leg.AddEntry(ths[i],prettym,'L') 
   
    return leg

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

    from ROOT import (TFile, TCanvas, gROOT, TLegend, RooAbsReal, gStyle, gPad,
            TLine, TColor, TLatex, TString, RooPlot)
    gROOT.SetBatch( True )

    gROOT.SetStyle('Plain')
    gStyle.SetOptTitle(0)
    gStyle.SetLabelFont(132, 'XYZ ')
    gStyle.SetLabelFont(132)
    gStyle.SetTitleFont(132, 'XYZ ')
    gStyle.SetTitleFont(132)
    gStyle.SetTextFont(132)
    gStyle.SetStatFont(132)
    gStyle.SetLabelSize(0.06, 'XYZ ')
    gStyle.SetLabelSize(0.06)
    gStyle.SetTitleSize(0.06, 'XYZ ')
    gStyle.SetTitleSize(0.06)
    gStyle.SetLabelOffset(0.004, 'XYZ ')
    gStyle.SetTitleOffset(0.85, 'XYZ ')

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
    time.setBins(nBinsTime)
    time.SetTitle('#tau(B_{s}#rightarrow D_{s}K)')
    time.setUnit('ps')
    mass = w.var('mass')
    mass.setBins(25)

    datasetname = ('agglomeration' if None != w.data('agglomeration')
            else 'hmaster')

    plots = [ [ 'all data',  [], [ [] ] ],
#            [ ('B_{s} #rightarrow D_{s}^{-}K^{+} + #bar{B_{s}} #rightarrow D_{s}^{+}K^{-}'
#                if isDsK else
#                'B_{s} #rightarrow D_{s}^{-}#pi^{+} + #bar{B_{s}} #rightarrow D_{s}^{+}#pi^{-}'),
#                [ RooFit.Cut("qf*qt > 0") ],
#               [ [ RooFit.Slice(w.cat('qt'), 'B_1'),
#               RooFit.Slice(w.cat('qf'), 'h+') ],
#               [ RooFit.Slice(w.cat('qt'), 'B_2'),
#               RooFit.Slice(w.cat('qf'), 'h+') ],
#               [ RooFit.Slice(w.cat('qt'), 'B_3'),
#               RooFit.Slice(w.cat('qf'), 'h+') ],
#               [ RooFit.Slice(w.cat('qt'), 'Bbar_1'),
#               RooFit.Slice(w.cat('qf'), 'h-') ],
#               [ RooFit.Slice(w.cat('qt'), 'Bbar_2'),
#               RooFit.Slice(w.cat('qf'), 'h-') ],
#               [ RooFit.Slice(w.cat('qt'), 'Bbar_3'),
#               RooFit.Slice(w.cat('qf'), 'h-') ] ]
#                ],
#            [ ('B_{s} #rightarrow D_{s}^{+}K^{-} + #bar{B_{s}} #rightarrow D_{s}^{-}K^{+}'
#                if isDsK else
#                'B_{s} #rightarrow D_{s}^{+}#pi^{-} + #bar{B_{s}} #rightarrow D_{s}^{-}#pi^{+}'),
#                [ RooFit.Cut("qf*qt < 0") ],
#               [ [ RooFit.Slice(w.cat('qt'), 'B_1'),
#               RooFit.Slice(w.cat('qf'), 'h-') ],
#               [ RooFit.Slice(w.cat('qt'), 'B_2'),
#               RooFit.Slice(w.cat('qf'), 'h-') ],
#               [ RooFit.Slice(w.cat('qt'), 'B_3'),
#               RooFit.Slice(w.cat('qf'), 'h-') ],
#               [ RooFit.Slice(w.cat('qt'), 'Bbar_1'),
#               RooFit.Slice(w.cat('qf'), 'h+') ],
#               [ RooFit.Slice(w.cat('qt'), 'Bbar_2'),
#               RooFit.Slice(w.cat('qf'), 'h+') ],
#               [ RooFit.Slice(w.cat('qt'), 'Bbar_3'),
#               RooFit.Slice(w.cat('qf'), 'h+') ] ]
#                ],
            ]

    iplot = 0
    for p in plots:
        canvas = TCanvas('TimeCanvas', 'Decay time canvas', 1200, 1000)
        canvas.SetTitle('Fit in decay time')
        canvas.cd()
        canvas.Divide(0, 2, 0.0001, 0.0001)
        canvas.cd(2)
        gPad.SetPad(.050, .005, 1.0, .3275) 
        gPad.SetBorderMode(0)
        gPad.SetBorderSize(-1)
        gPad.SetFillStyle(0)
        gPad.SetBottomMargin(0.325)
        canvas.cd(1)
        gPad.SetPad( .050, .22, 1.0, 1.0)
        gPad.SetBorderMode(0)
        gPad.SetBorderSize(-1)
        gPad.SetFillStyle(0)
        gPad.SetTopMargin(0.99)
        

        frame_t = time.frame()
        frame_t.SetTitle('Fit in reconstructed %s decay time (%s)' % (bName, p[0]))

        dataplotopts = p[1]
        sliceopts = p[2]
        ds = plotDataSet(frame_t, w, datasetname, dataplotopts)
        # ok, set up projection data
        if None != w.obj('timeerr'):
            w.obj('timeerr').setBins(20)
        projset = RooArgSet(*(w.obj(vname) for vname in ('sample', 'timeerr')))
        projds = ds.reduce(RooFit.SelectVars(projset))
        ROOT.SetOwnership(projds, True)
        projds = projds.binnedClone()
        ROOT.SetOwnership(projds, True)
        projds.Print('v')
        
        pdfplotopts = [
                RooFit.Precision(1e-6),
                RooFit.Normalization(1. / projds.sumEntries(), RooAbsReal.Relative),
                RooFit.ProjWData(projds, True),
                RooFit.NumCPU(6),
                ]

        frame_t.Draw()
        canvas.Update()
        gPad.SetLogy(True)
        canvas.Print(FILENAME + '.%u.time.dataonly.pdf' % iplot)
        canvas.Print(FILENAME + '.%u.time.dataonly.root' % iplot)
        
        mainplot, pull = plotFitModel(frame_t, w, 'TotEPDF', pdfplotopts, sliceopts)
        mainplot.GetYaxis().SetTitle(mainplot.GetYaxis().GetTitle().replace(' ps ', ' [ps] '))
        mainplot.GetYaxis().SetTitle((TString.Format("Candidates / ( " +
                                                str(time.getBinWidth(1))+" ps)") ).Data())
        #leg, curve = legends(modelPDF, frame_t)
        #frame_t.addObject(leg)
        if onlyLargeModes:
            frame_t.GetYaxis().SetRangeUser(0.4,250.)
        else:
            frame_t.GetYaxis().SetRangeUser(0.12,250.)
        
        frame_t.Draw()
        leg = legend()
        leg.Draw()
        canvas.Update()
        gPad.SetLogy(True)
        lhcbtext = TLatex()
        lhcbtext.SetTextFont(132)
        lhcbtext.SetTextColor(1)
        lhcbtext.SetTextSize(0.07)
        lhcbtext.SetTextAlign(12) 
        lhcbtext.DrawTextNDC(0.35,0.86,"LHCb")
        canvas.cd(2)
        from B2DXFitters import TLatexUtils
        gStyle.SetOptLogy(0)
        pull.GetXaxis().SetRangeUser(time.getMin(), time.getMax())
        pull.GetXaxis().SetLabelSize(0.15)
        pull.GetXaxis().SetTitleSize(0.15)
        pull.GetXaxis().SetTitleOffset(0.95)
        pull.GetXaxis().SetTitle(str(
            TLatexUtils.DecDescrToTLatex('#tau ((Bs2DsK) [ps]')))
        pull.GetYaxis().SetRangeUser(-3.5, 3.5)
        pull.GetYaxis().SetNdivisions(5)
        pull.GetYaxis().SetLabelSize(0.15)
        pull.GetYaxis().SetTitleSize(0.15)
        pull.GetYaxis().SetTitleOffset(0.15)
        pull.GetYaxis().SetTitle('')
        pull.Draw("ap")
   
        l1 = TLine(time.getMin(), -3., time.getMax(), -3.)
        l2 = TLine(time.getMin(), +3., time.getMax(), +3.)
        l3 = TLine(time.getMin(), 0., time.getMax(), 0.)
        for l in (l1, l2):
            l.SetLineColor(ROOT.kRed)
            l.Draw()
        l3.SetLineColor(ROOT.kBlack)
        l3.Draw()
        canvas.Print(FILENAME + '.%u.time.dataandpdf.pdf' % iplot)
        canvas.Print(FILENAME + '.%u.time.dataandpdf.root' % iplot)

        #plotDataSet(frame_m, w, datasetname, dataplotopts)
        #plotFitModel(frame_m, w, 'TotEPDF', pdfplotopts, sliceopts)

        #frame_m.Draw()

        #canvas.Update()
        #canvas.SetLogy(False)
        #canvas.Print(FILENAME + '.mass.eps')
        del canvas
        iplot = iplot + 1
        sys.exit(0)       
 
    f.Close()

#------------------------------------------------------------------------------
