#!/bin/sh
# -*- mode: python; coding: utf-8 -*-
# vim: ft=python:sw=4:tw=78:expandtab
# ---------------------------------------------------------------------------
# @file runMDFitter_Bd.py
#
# @brief MDFit for Bd->DPi
#
# @author Vincenzo Battista
# @date 2016-05-20
#
# ---------------------------------------------------------------------------
# This file is used as both a shell script and as a Python script.
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

# set ulimit to protect against bugs which crash the machine: 3G vmem max,
# no more then 8M stack
ulimit -v $((3072 * 1024))
ulimit -s $((   8 * 1024))

# trampoline into python
exec $schedtool /usr/bin/time -v env python -O "$0" - "$@"
"""
__doc__ = """ real docstring """
# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
#"
import B2DXFitters
import ROOT
from ROOT import RooFit

from ROOT import *
from B2DXFitters import *
from B2DXFitters import WS
from B2DXFitters.WS import WS

from optparse import OptionParser
from math     import pi, log
from  os.path import exists
import os, sys, gc

import array
from array import array

gROOT.SetBatch()

#------------------------------------------------------------
def makeFitCanvasForSWeights(dataset,
			     model,
			     sgn,
			     bkg,
			     hypo,
			     var,
			     result,
			     configfile,
			     logScale,
			     title,
			     save):

	#Get some options
	min = configfile["sWeights"]["Range"][var.GetName()][0]
	max = configfile["sWeights"]["Range"][var.GetName()][1]
	bins = configfile["sWeights"]["Bins"]
	Xaxis = configfile["AxisTitle"][var.GetName()][hypo]
	var.SetTitle(Xaxis)

	#Create canvas
	canv = TCanvas("canv_"+dataset.GetName(),"Canvas of "+dataset.GetTitle(), 1200, 1000)
	canv.Divide(1,2)

	#Setup upper pad
	canv.cd(1)
	pad1 = canv.GetPad(1)
	pad1.cd()
	pad1.SetPad(.0, .22, 1.0, 1.0)
	pad1.SetBorderMode(0)
	pad1.SetBorderSize(-1)
	pad1.SetFillStyle(0)
	pad1.SetTickx(0)
	if logScale:
		pad1.SetLogy()

	frame_top = makeTopFrame(var,title,min,max,bins)
	dataset.plotOn(frame_top)


	#Plot total PDF
	model.plotOn(frame_top,
		     #RooFit.Normalization(1.0, RooAbsReal.RelativeExpected),
		     RooFit.LineStyle(configfile["sWeightsFitPlot"]["Total"]["Style"]),
		     RooFit.LineColor(configfile["sWeightsFitPlot"]["Total"]["Color"]))

	#Build pull histogram and get chi2/ndof
	pullHist = frame_top.pullHist()
	if None != result:
		#Fitted parameters: compute ndof properly
		chi2ndof = frame_top.chiSquare(result.floatParsFinal().getSize())
	else:
		#No fit: ndof only given by binning
		chi2ndof = frame_top.chiSquare(0)
		chi2ndof = round(chi2ndof,2)
	chi2ndof = round(chi2ndof,2)

	#Plot signal and background PDFs
	model.plotOn(frame_top,
		     #RooFit.Normalization(1.0, RooAbsReal.RelativeExpected),
		     RooFit.Components(sgn),
		     RooFit.LineStyle(configfile["sWeightsFitPlot"]["Signal"]["Style"]),
		     RooFit.LineColor(configfile["sWeightsFitPlot"]["Signal"]["Color"]))
	model.plotOn(frame_top,
		     #RooFit.Normalization(1.0, RooAbsReal.RelativeExpected),
		     RooFit.Components(bkg),
		     RooFit.LineStyle(configfile["sWeightsFitPlot"]["Background"]["Style"]),
		     RooFit.LineColor(configfile["sWeightsFitPlot"]["Background"]["Color"]))

	frame_top.Draw()

	#Plot legend
	legend = TLegend(configfile["Legend"]["Xmin"],
			 configfile["Legend"]["Ymin"],
			 configfile["Legend"]["Xmax"],
			 configfile["Legend"]["Ymax"])
	legend.SetFillColor(4000)
	legend.SetShadowColor(0)
	legend.SetBorderSize(0)
	legend.SetTextFont(132)

	print ""
	print "Adding data points to legend"
	gr = TGraphErrors(10)
	gr.SetName("gr")
	gr.SetLineColor(kBlack)
	gr.SetLineWidth(2)
	gr.SetMarkerStyle(8)
	gr.SetMarkerSize(1.3)
	gr.SetMarkerColor(kBlack)
	legend.AddEntry("gr","Data","LEP")

	print "Adding PDFs to legend"
	lineT = TLine()
	lineT.SetLineColor(configfile["sWeightsFitPlot"]["Total"]["Color"])
	lineT.SetLineWidth(4)
	lineT.SetLineStyle(configfile["sWeightsFitPlot"]["Total"]["Style"])
	legend.AddEntry(lineT, configfile["sWeightsFitPlot"]["Total"]["Title"], "L")

	lineS = TLine()
	lineS.SetLineColor(configfile["sWeightsFitPlot"]["Signal"]["Color"])
	lineS.SetLineWidth(4)
	lineS.SetLineStyle(configfile["sWeightsFitPlot"]["Signal"]["Style"])
	legend.AddEntry(lineS, configfile["sWeightsFitPlot"]["Signal"]["Title"], "L")

	lineB = TLine()
	lineB.SetLineColor(configfile["sWeightsFitPlot"]["Background"]["Color"])
	lineB.SetLineWidth(4)
	lineB.SetLineStyle(configfile["sWeightsFitPlot"]["Background"]["Style"])
	legend.AddEntry(lineB, configfile["sWeightsFitPlot"]["Background"]["Title"], "L")

	legend.Draw("SAME")

	#Add some text
	lhcbtext = makeText(0.07)
	lhcbtext.DrawTextNDC(configfile["LHCbText"]["X"],
			     configfile["LHCbText"]["Y"],
			     configfile["LHCbText"]["Text"])

	chi2text = makeText(0.05)
	chi2text.DrawLatexNDC(configfile["Chi2"]["X"],configfile["Chi2"]["Y"],"#chi^{2}/ndof="+str(chi2ndof))

	pad1.Update()
	pad1.Draw()

	#Setup lower pad
	canv.cd(2)
	pad2 = canv.GetPad(2)
	pad2.cd()
	pad2.SetPad(.0, .005, 1.0, .3275)
	pad2.cd()
	pad2.SetBorderMode(0)
	pad2.SetBorderSize(-1)
	pad2.SetFillStyle(0)
	pad2.SetBottomMargin(0.35)
	pad2.SetTickx(0)
	pad2.SetGridx()
	pad2.SetGridy()
	pad2.SetLogy(0)

	gStyle.SetOptLogy(0)

	frame_bot = makeBottomFrame(var,min,max,bins,Xaxis)
	frame_bot.addPlotable(pullHist,"P")
	frame_bot.Draw()

	pad2.Update()
	pad2.Draw()
	canv.Update()

	canv.SaveAs(save+".pdf")

#------------------------------------------------------------
def makeFitCanvas(dataset,
		  model,
		  dictionary,
		  var,
		  category,
		  label,
		  hypo,
		  result,
		  configfile,
		  logScale,
		  title,
		  save):

	#Get some options
	min = configfile["Range"][var.GetName()]["Range"][0]
	max = configfile["Range"][var.GetName()]["Range"][1]
	bins = configfile["Range"][var.GetName()]["Bins"]
	Xaxis = configfile["AxisTitle"][var.GetName()][hypo]

	var.SetTitle(Xaxis)

        #Create canvas
	canv = TCanvas("canv_"+dataset.GetName(),"Canvas of "+dataset.GetTitle(), 1200, 1000)
	canv.Divide(1,2)

        #Setup upper pad
	canv.cd(1)
	pad1 = canv.GetPad(1)
	pad1.cd()
	pad1.SetPad(.0, .22, 1.0, 1.0)
	pad1.SetBorderMode(0)
	pad1.SetBorderSize(-1)
	pad1.SetFillStyle(0)
	pad1.SetTickx(0)
	if logScale:
		pad1.SetLogy()

	frame_top = makeTopFrame(var,title,min,max,bins)
	dataset.plotOn(frame_top,
		       RooFit.Cut("sample==sample::"+label))

	#Plot total PDF
	model.plotOn(frame_top,
		     RooFit.Slice(category,label),
		     #RooFit.Normalization(1.0, RooAbsReal.RelativeExpected),
		     RooFit.ProjWData(RooArgSet(category),dataset),
		     RooFit.LineStyle(dictionary["Total"]["Style"]),
		     RooFit.LineColor(dictionary["Total"]["Color"]))

	#Build pull histogram and get chi2/ndof
	pullHist = frame_top.pullHist()
	if None != result:
		#Fitted parameters: compute ndof properly
		chi2ndof = frame_top.chiSquare(result.floatParsFinal().getSize())
	else:
	        #No fit: ndof only given by binning
		chi2ndof = frame_top.chiSquare(0)
	chi2ndof = round(chi2ndof,2)

	#Plot other pdf components
	for comp in dictionary[hypo].iterkeys():
		if comp != "Total" and comp in dictionary[hypo].keys() and "Name" in dictionary[hypo][comp].keys() and "Style" in dictionary[hypo][comp].keys() and "Color" in dictionary[hypo][comp].keys():
			print ""
			print "Plotting "+comp+" component"
			print "with line style "+str(dictionary[hypo][comp]["Style"])
			print "and line color "+str(dictionary[hypo][comp]["Color"])
			print ""
			model.plotOn(frame_top,
				     RooFit.Slice(category,label),
				     #RooFit.Normalization(1.0, RooAbsReal.RelativeExpected),
				     RooFit.Components(dictionary[hypo][comp]["Name"]),
				     RooFit.ProjWData(RooArgSet(category),dataset),
				     RooFit.LineStyle(dictionary[hypo][comp]["Style"]),
				     RooFit.LineColor(dictionary[hypo][comp]["Color"]))

	frame_top.Draw()

	if logScale:
		minY = configfile["LogScale"][var.GetName()][hypo][0]
		maxY = configfile["LogScale"][var.GetName()][hypo][1]
		frame_top.GetYaxis().SetRangeUser(minY, maxY)

	#Plot legend
	legend = TLegend(configfile["Legend"]["Xmin"],
			 configfile["Legend"]["Ymin"],
			 configfile["Legend"]["Xmax"],
			 configfile["Legend"]["Ymax"])
	legend.SetFillColor(4000)
	legend.SetShadowColor(0)
	legend.SetBorderSize(0)
	legend.SetTextFont(132)

	print ""
	print "Adding data points to legend"
	gr = TGraphErrors(10)
	gr.SetName("gr")
	gr.SetLineColor(kBlack)
	gr.SetLineWidth(2)
	gr.SetMarkerStyle(8)
	gr.SetMarkerSize(1.3)
	gr.SetMarkerColor(kBlack)
	legend.AddEntry("gr","Data","LEP")

	print "Adding Total PDF to legend"
	line = TLine()
	line.SetLineColor(dictionary["Total"]["Color"])
	line.SetLineWidth(4)
	line.SetLineStyle(dictionary["Total"]["Style"])
	legend.AddEntry(line, dictionary["Total"]["Title"], "L")

	lines = []
	l=0
	for comp in dictionary[hypo].iterkeys():
		print "Adding "+comp+" PDF to legend..."
		if comp != "Total" and comp in dictionary[hypo].keys() and "Name" in dictionary[hypo][comp].keys() and "Style" in dictionary[hypo][comp].keys() and "Color" in dictionary[hypo][comp].keys():
			lines.append( TLine() )
			lines[l].SetLineColor(dictionary[hypo][comp]["Color"])
			lines[l].SetLineWidth(4)
			lines[l].SetLineStyle(dictionary[hypo][comp]["Style"])
			legend.AddEntry(lines[l], dictionary[hypo][comp]["Title"], "L")
			l = l+1

	legend.Draw("SAME")

	#Add some text
	lhcbtext = makeText(0.07)
	lhcbtext.DrawTextNDC(configfile["LHCbText"]["X"],
			     configfile["LHCbText"]["Y"],
			     configfile["LHCbText"]["Text"])

	chi2text = makeText(0.05)
	chi2text.DrawLatexNDC(configfile["Chi2"]["X"],configfile["Chi2"]["Y"],"#chi^{2}/ndof="+str(chi2ndof))

	pad1.Update()
	pad1.Draw()

        #Setup lower pad
	canv.cd(2)
	pad2 = canv.GetPad(2)
	pad2.cd()
	pad2.SetPad(.0, .005, 1.0, .3275)
	pad2.cd()
	pad2.SetBorderMode(0)
	pad2.SetBorderSize(-1)
	pad2.SetFillStyle(0)
	pad2.SetBottomMargin(0.35)
	pad2.SetTickx(0)
	pad2.SetGridx()
	pad2.SetGridy()
	pad2.SetLogy(0)

	gStyle.SetOptLogy(0)

	frame_bot = makeBottomFrame(var,min,max,bins,Xaxis)
	frame_bot.addPlotable(pullHist,"P")
	frame_bot.Draw()

	pad2.Update()
	pad2.Draw()
	canv.Update()

	canv.SaveAs(save+".pdf")

#------------------------------------------------------------
def makeTopFrame(var,title,min,max,bins):
	if None != bins and None != min and None != max:
		frame_top = var.frame(min,max,bins)
	else:
		frame_top = var.frame()
	frame_top.SetTitle(title)
	frame_top.GetXaxis().SetLabelSize( 0.05 )
	frame_top.GetYaxis().SetLabelSize( 0.038 )#0.05 )
	frame_top.GetXaxis().SetLabelFont( 132 )
	frame_top.GetYaxis().SetLabelFont( 132 )
	frame_top.GetXaxis().SetLabelOffset( 0.006 )
	frame_top.GetYaxis().SetLabelOffset( 0.006 )
	frame_top.GetXaxis().SetLabelColor( kWhite)
	frame_top.GetXaxis().SetTitleSize( 0.05 )
	frame_top.GetYaxis().SetTitleSize( 0.045 )#0.06 )
	frame_top.GetYaxis().SetNdivisions(512)
	frame_top.GetXaxis().SetTitleOffset( 1.00 )
	frame_top.GetYaxis().SetTitleOffset( 1.15 )

	return frame_top

#------------------------------------------------------------
def makeBottomFrame(var,min,max,bins,Xaxis):
	if None != bins and None != min and None != max:
		frame_bot = var.frame(min,max,bins)
	else:
		frame_bot = var.frame()
	frame_bot.SetTitle("")
	frame_bot.GetYaxis().SetTitle("")
	frame_bot.GetXaxis().SetTitle(Xaxis)
	frame_bot.GetYaxis().SetTitleSize(0.06)#0.09)
	frame_bot.GetYaxis().SetTitleOffset(0.26)
	frame_bot.GetYaxis().SetTitleFont(132)
	frame_bot.GetYaxis().SetNdivisions(106)
	frame_bot.GetYaxis().SetLabelSize(0.1)#0.12)
	frame_bot.GetYaxis().SetLabelOffset(0.016)
	frame_bot.GetXaxis().SetTitleSize(0.13)#0.15)
	frame_bot.GetXaxis().SetTitleFont(132)
	frame_bot.GetXaxis().SetTitleOffset(1.00)
	frame_bot.GetXaxis().SetNdivisions(5)
	frame_bot.GetYaxis().SetNdivisions(5)
	frame_bot.GetYaxis().SetRangeUser(-5,5)
	frame_bot.GetXaxis().SetLabelSize(0.10)#0.12)
	frame_bot.GetXaxis().SetLabelFont( 132 )
	frame_bot.GetYaxis().SetLabelFont( 132 )

	return frame_bot

#------------------------------------------------------------
def makeText(size):
	text = TLatex()
	text.SetTextFont(132)
	text.SetTextColor(1)
	text.SetTextSize(size)
	text.SetTextAlign(132)

	return text

#------------------------------------------------------------
def BuildParForPDF(workOut, typemode, varName, parName, samplemode, pdfDict):

	par = False
	if type(pdfDict[parName]) == dict:
		print "Creating parameter "+typemode+"_"+varName+"_"+parName+"_"+samplemode
		par = WS(workOut, RooRealVar(typemode+"_"+varName+"_"+parName+"_"+samplemode,
					     pdfDict[parName]["title"],
					     *pdfDict[parName]["par"]))
	elif type(pdfDict[parName]) == str:
		print "Taking parameter "+pdfDict[parName]+" from workspace"
		par = workOut.obj( pdfDict[parName] )
	else:
		print "ERROR when building "+parName+". Please check config file."
		exit(-1)

	if not par:
		print "ERROR when building "+parName+". Please check config file."
		exit(-1)

	return par

#------------------------------------------------------------
def BuildExponentialPDF(workOut, obs, nickname, samplemode, pdfDict, debug):

        #Build parameters
	varName = obs.GetName()
	typemode = nickname+"_E"

	cB = BuildParForPDF(workOut, typemode, varName, "cB", samplemode, pdfDict)

        #Build PDF
	pdf = Bs2Dsh2011TDAnaModels.buildExponentialPDF(obs,
                                                        workOut,
                                                        samplemode,
                                                        typemode,
                                                        debug)

	return WS(workOut, pdf)

#------------------------------------------------------------
def BuildDoubleExponentialPDF(workOut, obs, nickname, samplemode, pdfDict, debug):

	#Build parameters
	varName = obs.GetName()
	typemode = nickname+"_2E"

	parList = []
	for par in ["cB1", "cB2", "frac"]:
		parList.append(BuildParForPDF(workOut, typemode, varName, par, samplemode, pdfDict))

        #Build PDF
	pdf = Bs2Dsh2011TDAnaModels.buildDoubleExponentialPDF(obs,
							      workOut,
							      samplemode,
							      typemode,
							      debug)

	return WS(workOut, pdf)

#------------------------------------------------------------
def BuildExponentialPlusConstantPDF(workOut, obs, nickname, samplemode, pdfDict, debug):

	#Build parameters
	varName = obs.GetName()
	typemode = nickname+"_EplusC"

	parList = []
	for par in ["cB", "fracExpo"]:
		parList.append(BuildParForPDF(workOut, typemode, varName, par, samplemode, pdfDict))

	#Build PDF
	pdf = Bd2DhModels.buildExponentialPlusConstantPDF(obs,
							  workOut,
							  samplemode,
							  typemode,
							  debug)

	return WS(workOut, pdf)

#------------------------------------------------------------
def BuildGaussPDF(workOut, obs, nickname, samplemode, pdfDict, debug):

        #Build parameters
	varName = obs.GetName()
	typemode = nickname+"_G"
	shiftMean = pdfDict["shiftMean"]

	parList = []
	for par in ["mean", "sigma"]:
		parList.append(BuildParForPDF(workOut, typemode, varName, par, samplemode, pdfDict))
	if shiftMean:
		parList.append(BuildParForPDF(workOut, typemode, varName, "shift", samplemode, pdfDict))

        #Build PDF
	pdf = Bs2Dsh2011TDAnaModels.buildGaussPDF(obs,
                                                  workOut,
                                                  samplemode,
                                                  typemode,
						  shiftMean,
                                                  debug)

	return WS(workOut, pdf)

#------------------------------------------------------------
def BuildDoubleGaussPDF(workOut, obs, nickname, samplemode, pdfDict, debug):

	#Build parameters
	varName = obs.GetName()
	typemode = nickname+"_DG"
	sameMean = pdfDict["sameMean"]
	shiftMean = pdfDict["shiftMean"]

	parList = []
	for par in ["mean", "sigma1", "sigma2", "frac"]:
		parList.append(BuildParForPDF(workOut, typemode, varName, par, samplemode, pdfDict))
	if shiftMean:
		parList.append(BuildParForPDF(workOut, typemode, varName, "shift", samplemode, pdfDict))

	#Build PDF
	pdf = Bs2Dsh2011TDAnaModels.buildDoubleGaussPDF(obs,
							workOut,
							samplemode,
							typemode,
							False,
							sameMean,
							shiftMean,
							debug)

	return WS(workOut, pdf)

#------------------------------------------------------------
def BuildCrystalBallPDF(workOut, obs, nickname, samplemode, pdfDict, debug):

        #Build parameters
	varName = obs.GetName()
	typemode = nickname+"_CB"

	parList = []
	for par in ["mean", "alpha", "n", "sigma"]:
		parList.append(BuildParForPDF(workOut, typemode, varName, par, samplemode, pdfDict))

        #Build PDF
	pdf = Bs2Dsh2011TDAnaModels.buildCrystalBallPDF(obs,
                                                        workOut,
                                                        samplemode,
                                                        typemode,
                                                        debug)

	return WS(workOut, pdf)


#------------------------------------------------------------
def BuildCrystalBallPlusGaussianPDF(workOut, obs, nickname, samplemode, pdfDict, debug):

	#Build parameters
	varName = obs.GetName()
	typemode = nickname+"_CBplusG"
	shiftMean = pdfDict["shiftMean"]
	scaleWidths = pdfDict["scaleWidths"]

	parList = []
	for par in ["mean", "alpha", "n", "sigmaCB", "sigmaG", "fracG"]:
		parList.append(BuildParForPDF(workOut, typemode, varName, par, samplemode, pdfDict))
	if shiftMean:
		parList.append(BuildParForPDF(workOut, typemode, varName, "shift", samplemode, pdfDict))
	if scaleWidths:
		parList.append(BuildParForPDF(workOut, typemode, varName, "scaleSigma", samplemode, pdfDict))

	#Build PDF
	pdf = Bd2DhModels.buildCrystalBallPlusGaussianPDF(obs,
							  workOut,
							  samplemode,
							  typemode,
							  shiftMean,
							  scaleWidths,
							  debug)

	return WS(workOut, pdf)

#------------------------------------------------------------
def BuildCrystalBallPlusExponentialPDF(workOut, obs, nickname, samplemode, pdfDict, debug):

	#Build parameters
	varName = obs.GetName()
	typemode = nickname+"_CBplusE"
	shiftMean = pdfDict["shiftMean"]

	parList = []
	for par in ["mean", "alpha", "n", "sigmaCB", "cB", "fracExpo"]:
		parList.append(BuildParForPDF(workOut, typemode, varName, par, samplemode, pdfDict))
	if shiftMean:
		parList.append(BuildParForPDF(workOut, typemode, varName, "shift", samplemode, pdfDict))

	#Build PDF
	pdf = Bd2DhModels.buildCrystalBallPlusExponentialPDF(obs,
							     workOut,
							     samplemode,
							     typemode,
							     shiftMean,
							     debug)

	return WS(workOut, pdf)

#------------------------------------------------------------
def BuildDoubleCrystalBallPDF(workOut, obs, nickname, samplemode, pdfDict, debug):

        #Build parameters
	varName = obs.GetName()
	typemode = nickname+"_DCB"
	sameMean = pdfDict["sameMean"]

	parList = []
	for par in ["mean", "alpha1", "alpha2", "n1", "n2", "sigma1", "sigma2", "frac"]:
		parList.append(BuildParForPDF(workOut, typemode, varName, par, samplemode, pdfDict))

        #Build PDF
	pdf = Bs2Dsh2011TDAnaModels.buildDoubleCrystalBallPDF(obs,
                                                              workOut,
                                                              samplemode,
                                                              typemode,
                                                              False,
                                                              sameMean,
                                                              debug)

	return WS(workOut, pdf)

#------------------------------------------------------------
def BuildJohnsonSUPDF(workOut, obs, nickname, samplemode, pdfDict, debug):

        #Build parameters
	varName = obs.GetName()
	typemode = nickname+"_johnson"
	shiftMean = pdfDict["shiftMean"]

	parList = []
	for par in ["mean", "sigma", "nu", "tau"]:
		parList.append(BuildParForPDF(workOut, typemode, varName, par, samplemode, pdfDict))
	if shiftMean:
		parList.append(BuildParForPDF(workOut, typemode, varName, "shift", samplemode, pdfDict))

        #Build PDF
	pdf = Bd2DhModels.buildJohnsonSUPDF(obs,
                                            workOut,
                                            samplemode,
                                            typemode,
					    shiftMean,
                                            debug)

	return WS(workOut, pdf)

#------------------------------------------------------------
def BuildJohnsonSUPlusGaussianPDF(workOut, obs, nickname, samplemode, pdfDict, debug):

        #Build parameters
	varName = obs.GetName()
	typemode = nickname+"_JplusG"
	sameMean = pdfDict["sameMean"]
	shiftMean = pdfDict["shiftMean"]

	parList = []
	for par in ["meanJ", "sigmaJ", "nuJ", "tauJ", "sigmaG", "frac"]:
		parList.append(BuildParForPDF(workOut, typemode, varName, par, samplemode, pdfDict))
	if shiftMean:
		parList.append(BuildParForPDF(workOut, typemode, varName, "shift", samplemode, pdfDict))
	if not sameMean:
		parList.append(BuildParForPDF(workOut, typemode, varName, "meanGshift", samplemode, pdfDict))

        #Build PDF
	pdf = Bd2DhModels.buildJohnsonSUPlusGaussianPDF(obs,
							workOut,
							samplemode,
							typemode,
							sameMean,
                                                        shiftMean,
							debug)

	return WS(workOut, pdf)

#------------------------------------------------------------
def BuildJohnsonSUPlusGaussianPlusExponentialPDF(workOut, obs, nickname, samplemode, pdfDict, debug):

	#Build parameters
	varName = obs.GetName()
	typemode = nickname+"_JplusGplusExpo"
	sameMean = pdfDict["sameMean"]

	parList = []
	for par in ["mean", "sigmaJ", "nuJ", "tauJ", "meanG", "sigmaG", "cB", "relFracSignal", "fracExponential"]:
		parList.append(BuildParForPDF(workOut, typemode, varName, par, samplemode, pdfDict))

	#Build PDF
	pdf = Bd2DhModels.buildJohnsonSUPlusGaussianPlusExponentialPDF(obs,
								       workOut,
								       samplemode,
								       typemode,
								       sameMean,
								       debug)

	return WS(workOut, pdf)

#------------------------------------------------------------
def BuildJohnsonSUPlus2GaussianPDF(workOut, obs, nickname, samplemode, pdfDict, debug):

	#Build parameters
	varName = obs.GetName()
	typemode = nickname+"_Jplus2G"
	sameMean = pdfDict["sameMean"]

	parList = []
	for par in ["mean", "sigmaJ", "nuJ", "tauJ", "meanG1shift", "meanG2shift", "sigma1G", "sigma2G", "frac1G", "frac2G"]:
		parList.append(BuildParForPDF(workOut, typemode, varName, par, samplemode, pdfDict))

        #Build PDF
	pdf = Bd2DhModels.buildJohnsonSUPlus2GaussianPDF(obs,
							 workOut,
							 samplemode,
							 typemode,
							 sameMean,
							 debug)

	return WS(workOut, pdf)

#------------------------------------------------------------
def BuildIpatiaPDF(workOut, obs, nickname, samplemode, pdfDict, debug):

	#Build parameters
	varName = obs.GetName()
	typemode = nickname+"_Ipatia"
	shiftMean = pdfDict["shiftMean"]
	scaleTails = pdfDict["scaleTails"]

	parList = []
	for par in ["l", "zeta", "fb", "mean", "sigma", "a1", "n1", "a2", "n2"]:
		parList.append(BuildParForPDF(workOut, typemode, varName, par, samplemode, pdfDict))
	if shiftMean:
		parList.append(BuildParForPDF(workOut, typemode, varName, "shift", samplemode, pdfDict))

	#Build PDF
	pdf = Bs2Dsh2011TDAnaModels.buildIpatiaPDF(obs,
						   workOut,
						   samplemode,
						   typemode,
						   shiftMean,
						   scaleTails,
						   debug)

	return WS(workOut, pdf)

#------------------------------------------------------------
def BuildIpatiaPlusExponentialPDF(workOut, obs, nickname, samplemode, pdfDict, debug):

	#Build parameters
	varName = obs.GetName()
	typemode = nickname+"_IpatiaPlusExponential"

	parList = []
	for par in ["l", "zeta", "fb", "mean", "sigma", "a1", "n1", "a2", "n2", "cB", "frac"]:
		parList.append(BuildParForPDF(workOut, typemode, varName, par, samplemode, pdfDict))

	#Build PDF
	pdf = Bd2DhModels.buildIpatiaPlusExponentialPDF(obs,
							workOut,
							samplemode,
							typemode,
							debug)

	return WS(workOut, pdf)

#------------------------------------------------------------
def BuildIpatiaGaussConvPDF(workOut, obs, nickname, samplemode, pdfDict, debug):

	#Build parameters
	varName = obs.GetName()
	typemode = nickname+"_IpatiaGaussConv"
	shiftMean = pdfDict["shiftMean"]

	parList = []
	for par in ["l", "zeta", "fb", "mean", "sigmaI", "sigmaG", "a1", "n1", "a2", "n2"]:
		parList.append(BuildParForPDF(workOut, typemode, varName, par, samplemode, pdfDict))
	if shiftMean:
		parList.append(BuildParForPDF(workOut, typemode, varName, "shift", samplemode, pdfDict))

	#Build PDF
	pdf = Bd2DhModels.buildIpatiaGaussConvPDF(obs,
						  workOut,
						  samplemode,
						  typemode,
						  shiftMean,
						  debug)

	return WS(workOut, pdf)

#------------------------------------------------------------
def BuildRooKeysPdf(workOut, obs, nickname, samplemode, pdfDict, data, debug):

	#Build parameters
	rho = pdfDict["Rho"]
	mirror = pdfDict["Mirror"]

	if mirror == "MirrorBoth":
		pdf = RooKeysPdf(nickname+"_"+str(obs.GetName())+"_RooKeysPdf_all",
				 nickname+"_"+str(obs.GetName())+"_RooKeysPdf_all",
				 obs,
				 data,
				 RooKeysPdf.MirrorBoth,
				 rho)
	elif mirror == "NoMirror":
		pdf = RooKeysPdf(nickname+"_"+str(obs.GetName())+"_RooKeysPdf_all",
				 nickname+"_"+str(obs.GetName())+"_RooKeysPdf_all",
				 obs,
				 data,
				 RooKeysPdf.NoMirror,
				 rho)
	else:
		print "ERROR: mirror mode "+str(mirror)+" not currently handled"
		exit(-1)

	return WS(workOut, pdf)

#------------------------------------------------------------
def TakeInputPdf(workOut, workTemplates, pdfDict):
	name = pdfDict["InputPdf"]
	pdf = workTemplates.pdf(name)
	return WS(workOut, pdf)

#------------------------------------------------------------
def BuildCompPdf(workOut, workTemplates, configfile, component, hypothesys, samplemodeyearhyp, obsList, debug):

	#Loop over observables and build PDF
	pdfList = []
	for obs in obsList:
		print "...observable "+str(obs.GetName())
		pdfDict = configfile["pdfList"][component][hypothesys][obs.GetName()]
		pdfType = configfile["pdfList"][component][hypothesys][obs.GetName()]["PDF"]
		title = configfile["pdfList"][component]["Title"]
		color = configfile["pdfList"][component]["Color"]
		style = configfile["pdfList"][component]["Style"]
		nickname = component
		if "JohnsonSUPlus2Gaussian" in pdfType:
			pdfList.append(BuildJohnsonSUPlus2GaussianPDF(workOut, obs, nickname, samplemodeyearhyp, pdfDict, debug))
		elif "JohnsonSUPlusGaussianPlusExponential" in pdfType:
			pdfList.append(BuildJohnsonSUPlusGaussianPlusExponentialPDF(workOut, obs, nickname, samplemodeyearhyp, pdfDict, debug))
		elif "JohnsonSUPlusGaussian" in pdfType:
			pdfList.append(BuildJohnsonSUPlusGaussianPDF(workOut, obs, nickname, samplemodeyearhyp, pdfDict, debug))
		elif "JohnsonSU" in pdfType:
			pdfList.append(BuildJohnsonSUPDF(workOut, obs, nickname, samplemodeyearhyp, pdfDict, debug))
		elif "IpatiaGaussConv" in pdfType:
			pdfList.append(BuildIpatiaGaussConvPDF(workOut, obs, nickname, samplemodeyearhyp, pdfDict, debug))
		elif "IpatiaPlusExponential" in pdfType:
			pdfList.append(BuildIpatiaPlusExponentialPDF(workOut, obs, nickname, samplemodeyearhyp, pdfDict, debug))
		elif "Ipatia" in pdfType:
			pdfList.append(BuildIpatiaPDF(workOut, obs, nickname, samplemodeyearhyp, pdfDict, debug))
		elif "CrystalBallPlusGaussian" in pdfType:
			pdfList.append(BuildCrystalBallPlusGaussianPDF(workOut, obs, nickname, samplemodeyearhyp, pdfDict, debug))
		elif "CrystalBallPlusExponential" in pdfType:
			pdfList.append(BuildCrystalBallPlusExponentialPDF(workOut, obs, nickname, samplemodeyearhyp, pdfDict, debug))
		elif "DoubleGaussian" in pdfType:
			pdfList.append(BuildDoubleGaussPDF(workOut, obs, nickname, samplemodeyearhyp, pdfDict, debug))
		elif "Gaussian" in pdfType:
			pdfList.append(BuildGaussPDF(workOut, obs, nickname, samplemodeyearhyp, pdfDict, debug))
		elif "DoubleCrystalBall" in pdfType:
			pdfList.append(BuildDoubleCrystalBallPDF(workOut, obs, nickname, samplemodeyearhyp, pdfDict, debug))
		elif "CrystalBall" in pdfType:
			pdfList.append(BuildCrystalBallPDF(workOut, obs, nickname, samplemodeyearhyp, pdfDict, debug))
		elif "ExponentialPlusConstant" in pdfType:
			pdfList.append(BuildExponentialPlusConstantPDF(workOut, obs, nickname, samplemodeyearhyp, pdfDict, debug))
		elif "DoubleExponential" in pdfType:
			pdfList.append(BuildDoubleExponentialPDF(workOut, obs, nickname, samplemodeyearhyp, pdfDict, debug))
		elif "Exponential" in pdfType:
			pdfList.append(BuildExponentialPDF(workOut, obs, nickname, samplemodeyearhyp, pdfDict, debug))
		elif "TakeInputPdf" in pdfType:
			pdfList.append(TakeInputPdf(workOut, workTemplates, pdfDict))
		elif "None" in pdfType:
			return None
		else:
			print "ERROR: "+pdfType+" pdf not currently handled"
			exit(-1)

	#Build yield variable
	if type(configfile["Yields"][component][hypothesys]) == dict:
		if "Sig" in component: #Guarantee compatibility with runSFit*.py scripts
			nEvts = RooRealVar("nSig_"+samplemodeyearhyp+"_Evts",
					   configfile["Yields"][component][hypothesys]["title"],
					   *configfile["Yields"][component][hypothesys]["par"])
		else:
			nEvts = RooRealVar("n"+component+"_"+samplemodeyearhyp+"_Evts",
					   configfile["Yields"][component][hypothesys]["title"],
					   *configfile["Yields"][component][hypothesys]["par"])
	elif type(configfile["Yields"][component][hypothesys]) == str:
		nEvts = workOut.obj(configfile["Yields"][component][hypothesys])
	else:
		print "ERROR: please check yields in config file."
		exit(-1)

	#Build final PDF
	if obsList.__len__() == 1:
		pdf = pdfList[0]
		pdf.SetName(component+"_"+hypothesys+"Hypo_PDF")
		pdf.SetTitle(component+"_"+hypothesys+"Hypo_PDF")
	else:
		#Multiply each pdf assuming uncorrelated observables
		pdfArgList = RooArgList()
		for o in range(0,obsList.__len__()):
			pdfArgList.add(pdfList[o])
		pdf = RooProdPdf(component+"_"+hypothesys+"Hypo_PDF",
				 component+"_"+hypothesys+"Hypo_PDF",
				 pdfArgList)

	if not pdf:
		print "ERROR. Pdf not created."
		exit(-1)
	if not nEvts:
		print "ERROR. Yield variable not created."
		exit(-1)

	return {"PDF"  : WS(workOut, pdf),
		"Yield": WS(workOut, nEvts),
		"Title": title,
		"Color": color,
		"Style": style,
		"Name" : pdf.GetName()}

#------------------------------------------------------------
def BuildGlobalVariables(workOut, configfile, debug):

	#Build all RooRealVar first, and then RooFormulaVar
	newvar = []
	for var in configfile["GlobalVariables"].iterkeys():
		if configfile["GlobalVariables"][var]["Type"] == "RooRealVar":
			if debug:
				print "Building "+var+" of RooRealVar type"
			newvar.append(WS(workOut, RooRealVar(var,
							     configfile["GlobalVariables"][var]["Title"],
							     *configfile["GlobalVariables"][var]["Range"])))
	for var in configfile["GlobalVariables"].iterkeys():
		if configfile["GlobalVariables"][var]["Type"] == "RooFormulaVar":
			if debug:
				print "Building "+var+" of RooFormulaVar type"
			depList = RooArgList()
			for dep in configfile["GlobalVariables"][var]["Dependents"]:
				depList.add( workOut.var(dep) )
			newvar.append(WS(workOut, RooFormulaVar(var,
								configfile["GlobalVariables"][var]["Title"],
								configfile["GlobalVariables"][var]["Formula"],
								depList)))

	if debug:
		print "Workspace content:"
		workOut.Print("v")

#------------------------------------------------------------
def BuildExternalConstraints(workOut, configfile, toys, seed, debug):

	if "GaussianConstraints" in configfile.keys():
		constrPDFs = RooArgSet()
		pdf = []
		idx = 0
		for constr in configfile["GaussianConstraints"].iterkeys():
			if configfile["GaussianConstraints"][constr]["Parameters"].__len__() == 1:
				par = workOut.obj(configfile["GaussianConstraints"][constr]["Parameters"][0])
				if debug:
					print "Building Gaussian constraint for "+par.GetName()
				if toys:
					#Sample mean of gaussian constraint
					gaussGen = TRandom3(seed)
					mean = WS(workOut, RooConstVar("mean_"+par.GetName(),
								       "mean_"+par.GetName(),
								       gaussGen.Gaus(configfile["GaussianConstraints"][constr]["Mean"][0],
										     configfile["GaussianConstraints"][constr]["Covariance"][0])))
					if debug:
						print "Toys: draw random mean for gaussian constraint"
						print "Seed: "+str(seed)
						print "Constraint mean: "+str(configfile["GaussianConstraints"][constr]["Mean"][0])
						print "New, random mean: "+str(mean.getVal())
				else:
					#Build normal gaussian constraint
					mean = WS(workOut, RooConstVar("mean_"+par.GetName(),
								       "mean_"+par.GetName(),
								       configfile["GaussianConstraints"][constr]["Mean"][0]))

				sigma = WS(workOut, RooConstVar("sigma_"+par.GetName(),
								"sigma_"+par.GetName(),
								configfile["GaussianConstraints"][constr]["Covariance"][0]))
				pdf.append(WS(workOut, RooGaussian("ExtConstraint_"+par.GetName(),
								   "ExtConstraint_"+par.GetName(),
								   par,
								   mean,
								   sigma)))
				constrPDFs.add(pdf[idx])
				idx += 1
			else:
				print "ERROR: multivariate constraints not currently handled"
				exit(-1)
			return constrPDFs

	else:
		print "No Gaussian constraints to apply"
		return None


#------------------------------------------------------------
#------------------------------------------------------------
#------------------------------------------------------------
def runMDFitter_Bd( debug,
		    configName,
		    inputFile,
		    templatesFile,
		    outputFile,
		    workData,
		    workTemplates,
		    workOut,
		    initial,
		    decay,
		    mode,
		    sample,
		    year,
		    merge,
		    hypo,
		    dim,
		    superimpose,
		    binned,
		    title,
		    noFitPlot,
		    sWeights,
		    sWeightsName,
		    preselection,
		    plotsWeights,
		    toys,
		    seed,
		    pullFile,
		    pullFilesWeights,
		    outputplotdir):

	if binned and int(dim)>2:
		print "ERROR: multidimensional binning not yet supported."
		exit(-1)

	# Tune integrator configuration
	RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-7)
	RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-7)
	RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('extrapolation','Wynn-Epsilon')
	RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('maxSteps','1000')
	RooAbsReal.defaultIntegratorConfig().getConfigSection('RooIntegrator1D').setCatLabel('minSteps','0')
	RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setCatLabel('method','21Points')
	RooAbsReal.defaultIntegratorConfig().getConfigSection('RooAdaptiveGaussKronrodIntegrator1D').setRealValue('maxSeg', 1000)
	# Since we have finite ranges, the RooIntegrator1D is best suited to the job
	RooAbsReal.defaultIntegratorConfig().method1D().setLabel('RooIntegrator1D')

	RooAbsData.setDefaultStorageType(RooAbsData.Tree)

	from B2DXFitters.MDFitSettingTranslator import Translator

	from B2DXFitters.mdfitutils import getExpectedValue as getExpectedValue
	from B2DXFitters.mdfitutils import getExpectedYield as getExpectedYield
	from B2DXFitters.mdfitutils import setConstantIfSoConfigured as setConstantIfSoConfigured
	from B2DXFitters.mdfitutils import getObservables  as getObservables
	from B2DXFitters.mdfitutils import readVariables as readVariables
	from B2DXFitters.mdfitutils import getSigOrCombPDF as getSigOrCombPDF
	from B2DXFitters.mdfitutils import getType as getType
	from B2DXFitters.mdfitutils import getPDFNameFromConfig as getPDFNameFromConfig
	from B2DXFitters.mdfitutils import getPIDKComponents as getPIDKComponents
	from B2DXFitters.mdfitutils import setBs2DsXParameters as setBs2DsXParameters

	#Handle some input options
	hypoList = hypo.split("_")

	t = TString('_')
	decayTS = TString(decay)
	modeTS = TString(mode)
	sampleTS = TString(sample)
	yearTS = TString(year)
	hypoTS = TString(hypo)
	datasetTS = TString("dataSet")+decayTS+t

	if merge == "pol" or merge == "both":
		sampleTS = TString("both")
	if merge == "year" or merge == "both":
		yearTS = TString("run1")

	# Get the configuration file
	samplemodeyear = sampleTS+t+modeTS+t+yearTS
	myconfigfilegrabber = __import__(configName,fromlist=['getconfig']).getconfig
	myconfigfile = myconfigfilegrabber( samplemodeyear.Data() )

	print "=========================================================="
	print "RUNMDFITTER_Bd IS RUNNING WITH THE FOLLOWING CONFIGURATION OPTIONS"
	for option in myconfigfile :
		if option == "constParams" :
			for param in myconfigfile[option] :
				print param, "is constant in the fit"
		else :
			print option, " = ", myconfigfile[option]
	print "=========================================================="

	mdt = Translator(myconfigfile,"MDSettings",False)

	MDSettings = mdt.getConfig()
	MDSettings.Print("v")

	fitResult = None
	sWeightsFitResult = None

	print ""
	print "========================================="
	print "Get input workspace with data "+str(workData)+" from:"
	print str(inputFile)
	print "========================================="
	print ""
	workspace = GeneralUtils.LoadWorkspace(TString(inputFile), TString(workData), debug)

	workspaceTemplates = None
	if templatesFile != "":
		print ""
		print "========================================="
		print "Get input workspace with templates "+str(workTemplates)+" from:"
		print str(templatesFile)
		print "========================================="
		print ""
		workspaceTemplates = GeneralUtils.LoadWorkspace(TString(templatesFile), TString(workTemplates), debug)

	print ""
	print "========================================="
	print "Create output workspace "+str(workOut)
	print "========================================="
	print ""
	if initial != "":
		workspaceOut = GeneralUtils.LoadWorkspace(TString(initial),TString(workOut),debug)
	else:
		workspaceOut = RooWorkspace(workOut,workOut)

	print ""
	print "========================================="
	print "Get input observables from:"
	print str(workData)
	print "========================================="
	print ""
	observables = getObservables(MDSettings, workspace, False, debug)
	dim = int(dim)
	obsList = []
	rangeList = []

	bMass = observables.find(MDSettings.GetMassBVarOutName().Data())
	bMass.setUnit("MeV/c^{2}")
	#bMass.setRange(MDSettings.GetMassBVarOutName().Data()+"_range",
	#	       *myconfigfile["Range"][MDSettings.GetMassBVarOutName().Data()]["Range"])
	bMass =  WS(workspaceOut, bMass)
	obsList.append(bMass)
	#rangeList.append(MDSettings.GetMassBVarOutName().Data()+"_range")
	if dim == 2:
		dMass = observables.find(MDSettings.GetMassDVarOutName().Data())
		#dMass.setRange(MDSettings.GetMassDVarOutName().Data()+"_range",
		#	       *myconfigfile["Range"][MDSettings.GetMassDVarOutName().Data()]["Range"])
		dMass = WS(workspaceOut, dMass)
		dMass.setUnit("MeV/c^{2}")
		obsList.append(dMass)
		#rangeList.append(MDSettings.GetMassDVarOutName().Data()+"_range")
	elif dim>2:
		print "ERROR: more than two dimensions not currently handled for Bd->DPi MDFit"
		exit(-1)
	else:
		pass

	print ""
	print "========================================="
	print "Get dataset from:"
	print str(workData)
	print "========================================="
	print ""

	sam = WS(workspaceOut, RooCategory("sample","sample"))
	dataSet_temp = GeneralUtils.GetDataSet(workspace, observables, sam, datasetTS, sampleTS, modeTS, yearTS, hypoTS, merge, debug )
	if preselection != "":
		print "Applying following preselection to reduce dataset:"
		print preselection
		dataSet = RooDataSet(dataSet_temp.GetName(), dataSet_temp.GetTitle(), dataSet_temp, dataSet_temp.get(), preselection, "")
		print "Entries:"
		print "...before cut: "+str( dataSet_temp.sumEntries() )
		print "...after cut: "+str( dataSet.sumEntries() )
	else:
		print "No additional preselection"
		dataSet = dataSet_temp

	pidBins = {}
	for h in range(0,hypoList.__len__()):
		sam.setIndex(h)
		pidBins[hypoList[h]] = sam.getLabel()

	if binned:
		print "Binning dataset"
		histList = []
		importList = []
		min = myconfigfile["Range"][bMass.GetName()]["Range"][0]
		max = myconfigfile["Range"][bMass.GetName()]["Range"][1]
		nbins = myconfigfile["Range"][bMass.GetName()]["Bins"]
		for h in range(0,hypoList.__len__()):
			sam.setIndex(h)
			histList.append( TH1F("hist_"+hypoList[h], "hist_"+hypoList[h], nbins, min, max))
			dataSet.fillHistogram(histList[h], RooArgList(bMass), "sample==sample::"+sam.getLabel())
			importList.append( RooFit.Import(sam.getLabel(), histList[h]) )
			histList[h].Print("v")
			importList[h].Print("v")
		dataSetBinned = WS(workspaceOut, RooDataHist(dataSet.GetName()+"_binned",
							     dataSet.GetTitle()+" binned", RooArgList(bMass), RooFit.Index(sam), *importList))
		if sWeights:
			print "WARNING: binning and sWeights requested at the same time. Performing fit on a binned copy, and evaluating sWeights on unbinned dataset."
			dataSet = WS(workspaceOut, dataSet)
	else:
		dataSet = WS(workspaceOut, dataSet)

	if debug:
		print "Dataset:"
		if binned:
			dataSetBinned.Print("v")
			print dataSetBinned.sumEntries()
		else:
			dataSet.Print("v")
			print dataSet.sumEntries()
		print "Sample categories"
		sam.Print("v")
		print "Category dictionary:"
		print pidBins

	if None == workspaceOut.data(dataSet.GetName()):
		dataSet = WS(workspaceOut, dataSet)

	print ""
	print "========================================="
	print "Build global variables"
	print "========================================="
	print ""

	BuildGlobalVariables(workspaceOut, myconfigfile, debug)

	print ""
	print "========================================="
	print "Build PDF to fit dataset:"
	print str(dataSet.GetName())
	print "========================================="
	print ""

	compList = myconfigfile["pdfList"].keys()
	print "List of PDF components:"
	print compList
	print "List of hypotheses (PID bins):"
	print hypoList
	print "List of observables:"
	print obsList

	s = GeneralUtils.GetSampleModeYearHypo( sampleTS, modeTS, yearTS, hypoTS, merge, debug )

	print "Start to build PDF for each component..."
	pdfList = {}
	corrYieldDictsWeights = {}
	idx = 0
	for hyp in hypoList:
		pdfList[hyp] = {}
		for comp in compList:
			if comp != "Total":
				print "...hypothesys "+hyp+", component "+comp
				pdfList[hyp][comp] = {}
				pdfDetails = BuildCompPdf(workspaceOut,
							  workspaceTemplates,
							  myconfigfile,
							  comp,
							  hyp,
							  s[idx].Data(),
							  obsList,
							  debug)

				if toys and pdfDetails != None and hyp == myconfigfile["sWeights"]["Hypo"] and sWeights and compList.__len__() > 2:
					corrYieldDictsWeights[pdfDetails["Yield"].GetName()] = {}
					if debug:
						print "Compute generated yield in the signal region (to get pulls)"
					argset = RooArgSet()
					for obs in obsList:
						argset.add(obs)
					#Define signal range and get integral
					for obs in obsList:
						obs.setRange("Signal",*myconfigfile["sWeights"]["Range"][obs.GetName()])
					sgnInt = pdfDetails["PDF"].createIntegral(argset, RooFit.NormSet(argset), RooFit.Range("Signal"))
					#Define total range and get integral
					for obs in obsList:
						obs.setRange("Total",*myconfigfile["BasicVariables"][obs.GetName()]["Range"])
					totInt = pdfDetails["PDF"].createIntegral(argset, RooFit.NormSet(argset), RooFit.Range("Total"))
					#Get generated yield rescaled into signal range
					corrYieldDictsWeights[pdfDetails["Yield"].GetName()] = pdfDetails["Yield"].getVal() * (sgnInt.getVal()/totInt.getVal())
					if debug:
						print "Integral and yield in the total region:"
						print totInt.getVal()
						print pdfDetails["Yield"].getVal()
						print "Integral and yield in the signal region:"
						print sgnInt.getVal()
						print corrYieldDictsWeights[pdfDetails["Yield"].GetName()]
				if pdfDetails != None:
					pdfList[hyp][comp]["PDF"] = pdfDetails["PDF"]
					pdfList[hyp][comp]["Yield"] = pdfDetails["Yield"]
					pdfList[hyp][comp]["Title"] = pdfDetails["Title"]
					pdfList[hyp][comp]["Color"] = pdfDetails["Color"]
					pdfList[hyp][comp]["Style"] = pdfDetails["Style"]
					pdfList[hyp][comp]["Name"]  = pdfDetails["Name"]

		idx = idx+1

	if debug:
		print "PDF dictionary:"
		for hyp in hypoList:
			for comp in compList:
				if comp != "Total":
					print ""
					print "Hypo: "+hyp+", component: "+comp
					print pdfList[hyp][comp]
					print ""
		if toys:
			print "Corrected yields dictionary:"
			print corrYieldDictsWeights

	print "Create total PDF..."
	pdf = RooSimultaneous("totEPDF", "totEPDF", sam)
	for hyp in hypoList:
		if compList.__len__() == 2: #i.e., a single component (signal) + total
			if debug:
				print "Building single PDF (signal only)"
			for comp in compList:
				if comp != "Total" and "PDF" in pdfList[hyp][comp].keys() and "Yield" in pdfList[hyp][comp].keys():
					sumpdf = WS(workspaceOut, RooExtendPdf(hyp+"Hypo_EPDF",
									       hyp+"Hypo_EPDF",
									       pdfList[hyp][comp]["PDF"],
									       pdfList[hyp][comp]["Yield"]))
		else:
			pdfArgList = RooArgList()
			yieldArgList = RooArgList()
			for comp in compList:
				if comp != "Total" and "PDF" in pdfList[hyp][comp].keys() and "Yield" in pdfList[hyp][comp].keys():
					pdfArgList.add( pdfList[hyp][comp]["PDF"] )
					yieldArgList.add( pdfList[hyp][comp]["Yield"] )
			sumpdf = WS(workspaceOut, RooAddPdf(hyp+"Hypo_EPDF",
							    hyp+"Hypo_EPDF",
							    pdfArgList,
							    yieldArgList))

		pdf.addPdf(sumpdf,pidBins[hyp])


	if debug:
		print "Total PDF:"
		pdf.Print("v")


	pdfList["Total"] = {}
	pdfList["Total"]["Title"] = myconfigfile["pdfList"]["Total"]["Title"]
	pdfList["Total"]["Color"] = myconfigfile["pdfList"]["Total"]["Color"]
	pdfList["Total"]["Style"] = myconfigfile["pdfList"]["Total"]["Style"]

	if not superimpose:

		print ""
		print "========================================="
		print "Build external constraints on parameters (if any):"
		print "========================================="
		print ""

		constrPDFs = BuildExternalConstraints(workspaceOut, myconfigfile, toys, int(seed), debug)

		print ""
		print "========================================="
		print "Fit PDF:"
		print str(pdf.GetName())
		print "to dataset:"
		print str(dataSet.GetName())
		print "========================================="
		print ""

		rangeName=""
		for r in range(0,rangeList.__len__()):
			rangeName+=rangeList[r]
			if r!=rangeList.__len__()-1:
				rangeName+=","

		fitOpts = [#RooFit.Range(rangeName),
			RooFit.Save(1),
			RooFit.Optimize(2),
			RooFit.Offset(True),
			RooFit.Strategy(2),
			#RooFit.Verbose(False),
			RooFit.Timer(True),
			RooFit.NumCPU(1),
			RooFit.Minimizer("Minuit2", "migrad")]#,
			#RooFit.Minos(True)]
		if None != constrPDFs:
			fitOpts.append(RooFit.ExternalConstraints(constrPDFs))

		if debug:
			print "Fit options:"
			print fitOpts

		if binned:
			fitResult = pdf.fitTo(dataSetBinned, *fitOpts)
		else:
			fitResult = pdf.fitTo(dataSet, *fitOpts)

		fitResult.SetName("FitTo_"+dataSet.GetName())
		fitResult.SetTitle("Fit to "+dataSet.GetTitle())

		print ""
		print "========================================="
		print "Fit done. Summarizing results:"
		print "========================================="
		print ""

		fitResult.Print("v")

		covMat = fitResult.covarianceMatrix()
		corrMat = fitResult.correlationMatrix()

		covMat.Print("v")
		corrMat.Print("v")

		#Plot correlation and covariance matrices
		from B2DXFitters.FitResultGrabberUtils import PlotResultMatrix
		PlotResultMatrix(fitResult, "covariance", outputplotdir+"MDFit_CovarianceMatrix.pdf")
		PlotResultMatrix(fitResult, "correlation", outputplotdir+"MDFit_CorrelationMatrix.pdf")

		#Update what is contained in workspace
		fitResult = WS(workspaceOut, fitResult)
		pdf = WS(workspaceOut, pdf)

		if toys:
			if fitResult.status() != 0 or fitResult.covQual() != 3:
				print "ERROR: fit quality is bad. Not saving pull tree."

			else:
				print ""
				print "========================================="
				print "Create pull tree in"
				print pullFile
				print "for pull analysis"
				print "========================================="
				print ""

				from B2DXFitters import FitResultGrabberUtils
				FitResultGrabberUtils.CreatePullTree(pullFile, fitResult)

	else:
		fitResult = None


	if not noFitPlot:
		print ""
		print "========================================="
		print "Saving fit plot"
		print "========================================="
		print ""

		logScale = [False, True]
		for obs in obsList:
			for pidbin in pidBins.iterkeys():
				for log in logScale:
					namefile = outputplotdir+"MDFit_"+str(obs.GetName())+"_"+pidbin
					if superimpose:
						namefile += "_noFit"
					if log:
						namefile += "_logScale"
					print ""
					print "Plotting PDF in "+str(obs.GetName())
					print "for "+pidbin+" hypothesys"
					print ""
					makeFitCanvas(dataSet if not binned else dataSetBinned,
						      pdf,
						      pdfList,
						      obs,
						      sam,
						      pidBins[pidbin],
						      pidbin,
						      fitResult,
						      myconfigfile,
						      log,
						      title,
						      namefile)


	if sWeights and not superimpose:

		if fitResult.status() != 0 or fitResult.covQual() != 3:
			print "ERROR: fit quality is bad. Not computing sWeights."
			exit(-1)

		if compList.__len__() == 2:
			print "WARNING: only one component included. Not computing sWeights."
		else:
			print ""
			print "========================================="
			print "Merging background PDFs into a single PDF"
			print "in order to compute sWeights."
			print "Will have Sgn+TotBkg only at the end"
			print "========================================="
			print ""

			#Build new pdf, and select only one category (the one chosen in myconfigfile["sWeights"]["Hypo"])
			hyp = myconfigfile["sWeights"]["Hypo"]

			#Build ranges
			signalWindow = ""
			for obs in obsList:
				obs.setRange("Total",*myconfigfile["BasicVariables"][obs.GetName()]["Range"])
				obs.setRange("Signal",*myconfigfile["sWeights"]["Range"][obs.GetName()])
				signalWindow += " && "+obs.GetName()+">="+str(myconfigfile["sWeights"]["Range"][obs.GetName()][0])
				signalWindow += " && "+obs.GetName()+"<="+str(myconfigfile["sWeights"]["Range"][obs.GetName()][1])

			#Select dataset corresponding to chosen hypo, and take only the selected signal peak window
			dataSetForSWeights = dataSet.reduce(dataSet.get(), "sample==sample::"+pidBins[hyp]+signalWindow)

			#Create ranges properly
			for obs in obsList:
				dataSetForSWeights.get().find(obs.GetName()).setRange("Signal",*myconfigfile["sWeights"]["Range"][obs.GetName()])
				observables.find(obs.GetName()).setRange("Signal",*myconfigfile["sWeights"]["Range"][obs.GetName()])

			if debug:
				print "Selecting signal region with following cut:"
				print "sample==sample::"+pidBins[hyp]+signalWindow
				print "Obtained dataset:"
				dataSetForSWeights.Print("v")

			#Build new pdf, and select only one category (the one chosen in myconfigfile["sWeights"]["Hypo"])
			bkgPdfList = RooArgList()
			bkgFracList = RooArgList()
			countFrac = 0
			totBkgYield = 0.0
			totGenBkg = 0.0
			last = ""
			integralratio = {}
			for comp in compList:
				if comp not in ["Total","Signal"] and "PDF" in pdfList[hyp][comp].keys() and "Yield" in pdfList[hyp][comp].keys():

					print ""
					print "Component: "+comp

					#Including bkg pdf with updated parameters from previous fit
					bkgPdfList.add( workspaceOut.obj( pdfList[hyp][comp]["PDF"].GetName() ) )
					#Computing fraction of bkg that falls into the signal region for each component
					argset = RooArgSet()
					for obs in obsList:
						argset.add(obs)
					thisintegralSgn = workspaceOut.obj( pdfList[hyp][comp]["PDF"].GetName() ).createIntegral(argset,
																 RooFit.NormSet(argset),
																 RooFit.Range("Signal"))
					thisintegralTot = workspaceOut.obj( pdfList[hyp][comp]["PDF"].GetName() ).createIntegral(argset,
																 RooFit.NormSet(argset),
																 RooFit.Range("Total"))
					integralratio[comp] = thisintegralSgn.getVal() / thisintegralTot.getVal()

					print "PDF integral in the signal region: "+str(thisintegralSgn.getVal())
					print "PDF integral in the total region: "+str(thisintegralTot.getVal())
					print "PDF integral ratio: "+str(integralratio[comp])

					#Accumulate total background yield
					thisyield = workspaceOut.obj( pdfList[hyp][comp]["Yield"].GetName() ).getVal()
					totBkgYield = totBkgYield + thisyield * integralratio[comp]

					print "Fitted yield: "+str(thisyield)
					print "Fitted yield in the signal region: "+str(thisyield * integralratio[comp])

					#Accumulate total generated background yield
					if toys:
						totGenBkg = totGenBkg + corrYieldDictsWeights[pdfList[hyp][comp]["Yield"].GetName()]

						print "Generated background yield in the signal region: "+str(corrYieldDictsWeights[pdfList[hyp][comp]["Yield"].GetName()])

					countFrac = countFrac + 1
					last = comp
			if debug:
				print ""
				print "Number of background components: "+str(countFrac)
				print "Total fitted background yield in signal region: "+str(totBkgYield)
				if toys:
					print "Total generated background in the signal region: "+str(totGenBkg)
				print "Dictionary of background integral ratios in the signal region:"
				print integralratio
				print ""

			for comp in compList:
				if comp not in ["Total","Signal"] and "PDF" in pdfList[hyp][comp].keys() and "Yield" in pdfList[hyp][comp].keys():
					if comp != last:
						#Computing fraction of given background over the total background in signal region
						bkgFracList.add( WS(workspaceOut,
								    RooRealVar("frac_"+comp+"_"+hyp+"Hypo",
									       "frac_"+comp+"_"+hyp+"Hypo",
									       (workspaceOut.obj( pdfList[hyp][comp]["Yield"].GetName() ).getVal() * integralratio[comp])/totBkgYield)))
			if debug:
				print "Background pdf list:"
				bkgPdfList.Print("v")
				print "Background fractions list:"
				bkgFracList.Print("v")

			#Build total bkg pdf + yield
			totbkg = WS(workspaceOut, RooAddPdf(hyp+"Hypo_TotBkgPDF",
							    hyp+"Hypo_TotBkgPDF",
							    bkgPdfList,
							    bkgFracList))
			sam.setLabel(pidBins[hyp])
			totbkgYield = WS(workspaceOut, RooRealVar("nBkg_"+s[ sam.getIndex() ].Data()+"_Evts",
								  "nBkg_"+s[ sam.getIndex() ].Data()+"_Evts",
								  totBkgYield,
								  0.0,
								  totBkgYield*2.0))

			corrYieldDictsWeights[totbkgYield.GetName()] = totGenBkg

			totbkgE = WS(workspaceOut, RooExtendPdf(hyp+"Hypo_TotBkgEPDF",
								hyp+"Hypo_TotBkgEPDF",
								totbkg,
								totbkgYield))

			#Convert signal yield to RooRealVar if needed
			if pdfList[hyp]["Signal"]["Yield"].InheritsFrom("RooFormulaVar"):
				sgnYield = WS(workspaceOut, RooRealVar(pdfList[hyp]["Signal"]["Yield"].GetName()+"_converted",
								       pdfList[hyp]["Signal"]["Yield"].GetName()+"_converted",
								       pdfList[hyp]["Signal"]["Yield"].getVal(),
								       0.0,
								       workspaceOut.obj( pdfList[hyp]["Signal"]["Yield"].GetName() ).getVal()*2.0))
			else:
				sgnYield = workspaceOut.obj( pdfList[hyp]["Signal"]["Yield"].GetName() )

			sgnE = WS(workspaceOut, RooExtendPdf(hyp+"Hypo_SgnEPDF",
							     hyp+"Hypo_SgnEPDF",
							     pdfList[hyp]["Signal"]["PDF"],
							     sgnYield))
			mergedPdf = WS(workspaceOut, RooAddPdf(hyp+"Hypo_EPDF_merged", hyp+"Hypo_EPDF_merged", RooArgList(sgnE, totbkgE) ) )

			#Now set ranges properly
			for obs in obsList:
				obs.setRange(*myconfigfile["sWeights"]["Range"][obs.GetName()])
				dataSetForSWeights.get().find(obs.GetName()).setRange(*myconfigfile["sWeights"]["Range"][obs.GetName()])
				observables.find(obs.GetName()).setRange(*myconfigfile["sWeights"]["Range"][obs.GetName()])

			print ""
			print "========================================="
			print "Computing sWeights"
			print "========================================="
			print ""

			sWeightsCalculator = FitMeTool( debug )
			sWeightsCalculator.setObservables( observables )
			sWeightsCalculator.setModelPDF( mergedPdf )
			sWeightsCalculator.setData( dataSetForSWeights )
			RooMsgService.instance().Print('v')
			RooMsgService.instance().deleteStream(RooFit.Eval)
			sWeightsCalculator.savesWeights(bMass.GetName(),
							dataSetForSWeights,
							TString(sWeightsName),
							False,
							RooFit.Range("Signal"),
							RooFit.Save(1),
							RooFit.Optimize(2),
							RooFit.Strategy(2),
							RooFit.Verbose(False),
							RooFit.Timer(True),
							RooFit.Offset(True))
			RooMsgService.instance().reset()
			sWeightsFitResult = sWeightsCalculator.getFitResult()

			if not noFitPlot:

				for obs in obsList:
					print ""
					print "Plotting fit result for sWeights: "+obs.GetName()
					print ""

					namefile = outputplotdir+"MDFitForSWeights_"+str(obs.GetName())+"_"+myconfigfile["sWeights"]["Hypo"]
					makeFitCanvasForSWeights(dataSetForSWeights,
								 mergedPdf,
								 sgnE.GetName(),
								 totbkgE.GetName(),
								 myconfigfile["sWeights"]["Hypo"],
								 obs,
								 sWeightsFitResult,
								 myconfigfile,
								 False,
								 title,
								 namefile)

			if toys:

				if sWeightsFitResult.status() != 0 or sWeightsFitResult.covQual() != 3:
					print "ERROR: fit quality is bad. Not creating pull tree."

				else:

					print ""
					print "========================================="
					print "Create pull tree in"
					print pullFilesWeights
					print "for pull analysis"
					print "========================================="
					print ""

					from B2DXFitters import FitResultGrabberUtils
					FitResultGrabberUtils.CreatePullTree(pullFilesWeights, sWeightsFitResult, corrYieldDictsWeights)

			if plotsWeights:
				print ""
				print "========================================="
				print "Plotting sWeighted data for:"
				for o in myconfigfile["plotsWeights"].iterkeys():
					print o
				print "========================================="
				print ""

				fWeights = TFile.Open(sWeightsName, "READ")
				tWeights = fWeights.Get("merged")
				sam.setLabel(pidBins[hyp])
				sWeights = TString("nSig_")+s[ sam.getIndex() ].Data()+TString("_Evts_sw")
				if debug:
					tWeights.GetListOfLeaves().Print()
					print "sWeight leaf name: "+sWeights.Data()

				for o in myconfigfile["plotsWeights"].iterkeys():
					canv = TCanvas("canv_"+o)
					canv.cd()

					tWeights.Draw(o+">>hist_"+o,"","goff")
					hist = gDirectory.Get("hist_"+o)
					hist.SetLineColor(kRed)
					hist.SetLineWidth(2)
					hist.GetXaxis().SetTitle(myconfigfile["plotsWeights"][o])
					hist.SetTitle("")

					tWeights.Draw(o+">>hist_sw_"+o,sWeights.Data(),"goff")
					hist_sw = gDirectory.Get("hist_sw_"+o)
					hist_sw.SetLineColor(kBlue)
					hist_sw.SetLineWidth(2)
					hist_sw.GetXaxis().SetTitle(myconfigfile["plotsWeights"][o])
					hist_sw.SetTitle("")

					legend = TLegend(0.65,0.3,0.89,0.6)
					legend.SetFillColor(4000)
					legend.SetShadowColor(0)
					legend.SetBorderSize(0)
					legend.SetTextFont(132)
					legend.AddEntry(hist,"Non-weighted","L")
					legend.AddEntry(hist_sw,"sWeighted","L")

					hist.Draw()
					hist_sw.Draw("E1SAME")
					legend.Draw("SAME")

					lhcbtext = makeText(0.07)
					lhcbtext.DrawTextNDC(0.89,
							     0.8,
							     myconfigfile["LHCbText"]["Text"])

					canv.Update()

					canv.SaveAs(outputplotdir+"sWeightedDistribution_"+o+".pdf")
					del canv
					del hist
					del hist_sw

				fWeights.Close()
				del tWeights
				del fWeights


			if dim == 1:
				sWeightsCalculator.printYieldsInRange( '*Evts',
								       MDSettings.GetMassBVarOutName().Data() ,
								       myconfigfile["sWeights"]["Range"][MDSettings.GetMassBVarOutName().Data()][0],
								       myconfigfile["sWeights"]["Range"][MDSettings.GetMassBVarOutName().Data()][1])
			elif dim == 2:
				sWeightsCalculator.printYieldsInRange( '*Evts',
								       MDSettings.GetMassBVarOutName().Data() ,
								       myconfigfile["sWeights"]["Range"][MDSettings.GetMassBVarOutName().Data()][0],
								       myconfigfile["sWeights"]["Range"][MDSettings.GetMassBVarOutName().Data()][1],
								       "SignalRange",
								       dMass.GetName(),
								       dMass.getMin(),
								       dMass.getMax() )

			del sWeightsCalculator


	print ""
	print "========================================="
	print "Pretty-printing fit results"
	print "========================================="
	print ""
	# from B2DXFitters import FitResultGrabberUtils
	# if None != fitResult:
	# 	FitResultGrabberUtils.PrintLatexTable(fitResult)
	# if None != sWeightsFitResult:
	# 	FitResultGrabberUtils.PrintLatexTable(sWeightsFitResult)

	print ""
	print "========================================="
	print "Saving output workspace"
	print "========================================="
	print ""

	if debug:
		workspaceOut.Print("v")

	if outputFile != "":
		workspaceOut.SaveAs(outputFile)


#------------------------------------------------------------
_usage = '%prog [options]'

parser = OptionParser( _usage )

parser.add_option( '-d', '--debug',
		   action = 'store_true',
		   dest = 'debug',
		   default = False,
		   help = 'print debug information while processing'
		   )
parser.add_option( '--toys',
		   action = 'store_true',
		   dest = 'toys',
		   default = False,
		   help = 'create tree with generated and fitted values for pull analysis'
		   )
parser.add_option( '--seed',
		   dest = 'seed',
		   default = 193627,
		   help = 'seed for generation of gaussian constrained parameter (for toys only)'
		   )
parser.add_option( '--configName',
		   dest = 'configName',
		   default = 'MyConfigFile',
		   help = 'configuration file name'
		   )
parser.add_option( '--inputFile',
		   dest = 'inputFile',
		   default = 'MyInputFile.root',
		   help = 'input file containing workspace with MC/data samples to fit'
		   )
parser.add_option( '--templatesFile',
		   dest = 'templatesFile',
		   default = '',
		   help = 'input file containing workspace with templates (leave empty if not required)'
		   )
parser.add_option( '--workData',
		   dest = 'workData',
		   default = 'workspace',
		   help = 'workspace containing MC/data samples to fit'
		   )
parser.add_option( '--workTemplates',
		   dest = 'workTemplates',
		   default = 'workOut',
		   help = 'workspace containing input templates (if required)'
		   )
parser.add_option( '--workOut',
		   dest = 'workOut',
		   default = 'workResults',
		   help = 'workspace to store fit results, pdfs, observables'
		   )
parser.add_option( '--decay',
		   dest = 'decay',
		   metavar = 'DECAY',
		   default = 'Bd2DPi',
		   help = 'decay mode'
		   )
parser.add_option( '-m', '--mode',
		   dest = 'mode',
		   metavar = 'MODE',
		   default = 'KPiPi',
		   help = 'mode: choose all, KKPi, KPiPi, PiPiPi, nonres, kstk, phipi, 3modeskkpi'
		   )
parser.add_option( '-p', '--pol','--polarity',
		   dest = 'pol',
		   metavar = 'POL',
		   default = 'down',
		   help = 'Sample: choose up or down '
		   )
parser.add_option( '--year',
		   dest = 'year',
		   default = '2011',
		   help = 'year of data taking can be: 2011, 2012, run1')
parser.add_option( '--merge',
		   dest = 'merge',
		   default = '',
		   help = 'for merging magnet polarities use: --merge pol, for merging years of data taking use: --merge year, for merging both use: --merge both'
		   )
parser.add_option( '--hypo',
		   dest = 'hypo',
		   default = 'Bd2DPi',
		   help = 'bachelor mass hypothesys')
parser.add_option( '--dim',
		   dest = 'dim',
		   default = 1,
		   help = 'number of dimensions for MD fit')
parser.add_option( '--superimpose',
		   action = 'store_true',
		   dest = 'superimpose',
		   default = False,
		   help = 'plot PDF on data without fitting (use initial parameters)'
		   )
parser.add_option( '--binned',
		   action = 'store_true',
		   dest = 'binned',
		   default = False,
		   help = 'perform binned maximum likelihood fit'
		   )
parser.add_option( '--title',
		   dest = 'title',
		   default = "",
		   help = 'title of the fit plot'
		   )
parser.add_option( '--noFitPlot',
		   action = 'store_true',
		   dest = 'noFitPlot',
		   default = False,
		   help = 'veto production of fit plot'
		   )
parser.add_option( '--sWeights',
		   action = 'store_true',
		   dest = 'sWeights',
		   default = False,
		   help = 'compute sWeights after fit'
		   )
parser.add_option( '--sWeightsName',
		   dest = 'sWeightsName',
		   default = 'sWeights.root',
		   help = 'file to store sWeights'
		   )
parser.add_option( '--preselection',
		   dest = 'preselection',
		   default = "",
		   help = 'additional preselection to apply on dataset'
		   )
parser.add_option( '--plotsWeights',
		   action = 'store_true',
		   dest = 'plotsWeights',
		   default = False,
		   help = 'perform binned maximum likelihood fit'
		   )
parser.add_option( '--outputFile',
		   dest = 'outputFile',
		   default = '',
		   help = 'output file to store fit results')
parser.add_option( '--outputplotdir',
		   dest = 'outputplotdir',
		   default = '',
		   help = 'output directory to store plots'
		   )
parser.add_option( '--pullFile',
		   dest = 'pullFile',
		   default = 'MyPullFile.root',
		   help = 'output file to store pull tree for toys')
parser.add_option( '--pullFilesWeights',
		   dest = 'pullFilesWeights',
		   default = 'MyPullFilesWeights.root',
		   help = 'output file to store pull tree for toys')
parser.add_option( '--initial',
		   dest = 'initial',
		   default = '',
		   help = 'file to take the output workspace from (if it exists)'
		   )
#------------------------------------------------------------
if __name__ == '__main__' :
	( options, args ) = parser.parse_args()

	#if len( args ) > 0 :
	#	parser.print_help()
	#	exit( -1 )

	config = options.configName
	last = config.rfind("/")
	directory = config[:last+1]
	configName = config[last+1:]
	p = configName.rfind(".")
	configName = configName[:p]

	import sys
	sys.path.append(directory)

	print "Config file name: "+configName
	print "Directory: "+directory

	runMDFitter_Bd( options.debug,
			configName,
			options.inputFile,
			options.templatesFile,
			options.outputFile,
			options.workData,
			options.workTemplates,
			options.workOut,
			options.initial,
			options.decay,
			options.mode,
			options.pol,
			options.year,
			options.merge,
			options.hypo,
			options.dim,
			options.superimpose,
			options.binned,
			options.title,
			options.noFitPlot,
			options.sWeights,
			options.sWeightsName,
			options.preselection,
			options.plotsWeights,
			options.toys,
			options.seed,
			options.pullFile,
			options.pullFilesWeights,
			options.outputplotdir)

