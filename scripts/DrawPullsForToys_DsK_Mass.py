from optparse import OptionParser
from os.path  import join

import GaudiPython

GaudiPython.loaddict( 'B2DXFittersDict' )

from ROOT import *

gStyle.SetOptStat(0)
gStyle.SetOptFit(1011)

import sys
sys.path.append("../data/")

debug = True
largeToys = False
drawGeneratedYields = False

ntoys               = 1000
toysdir             = '/afs/cern.ch/work/a/adudziak/public/Bs2DsKToys/Gamma140/'
toystupleprefix     = 'DsK_Toys_sWeights_ForTimeFit_'
if largeToys : toystupleprefix     = 'DsK_Toys_FullLarge_Tree_'
toystuplesuffix     = '.root'
toysresultprefix    = 'DsK_Toys_MassFitResult_'
if largeToys : toysresultprefix    = 'DsK_Toys_FullLarge_MassFitResult_'
toysresultsuffix    = '.log'    

#outputdir = '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/DsKToysAgnieszka_010813/'
outputdir = '/afs/cern.ch/work/a/adudziak/public/Bs2DsKToys/Gamma140/'

eventtypes = {"Signal" : 1.0, 
              "DK"     : 2.0,
              "Bd2DsK" : 3.0,
              "DsPi"   : 4.0,
              "LcK"    : 5.0,
              "Dsp"    : 6.0,
              "LMK"    : 7.0,
              "LMPi"   : 8.0,
              "Combo"  : 10.0 }

# Get the configuration file
myconfigfilegrabber = __import__("Bs2DsKConfigForGenerator",fromlist=['getconfig']).getconfig
myconfigfile = myconfigfilegrabber()

numgenevt = {"Signal" : ntoys*[1863]}
numfitted = {"Signal" : ntoys*[(0,0)]}
numgenevt["Combo"] = ntoys*[4057]
numfitted["Combo"] = ntoys*[(0,0)]
numgenevt["LMK"] = ntoys*[143.4]
numfitted["LMK"] = ntoys*[(0,0)]
numgenevt["LMPi"] = ntoys*[432.8]
numfitted["LMPi"] = ntoys*[(0,0)]
numgenevt["Dsp"] = ntoys*[152.1]
numfitted["Dsp"] = ntoys*[(0,0)]

numevents       = {}
numeventshistos = {}

for eventtype in eventtypes :
    numevents[eventtype]    = ntoys*[0]
    maxevents = 5000
    if eventtype in ["DK","LcK","Dsp","LMPi","LMK","Bd2DsK"] :
        maxevents = 500
    if eventtype in ["Signal","DsPi"] :
        maxevents = 2500
    if largeToys :
        maxevents *= 10
    numeventshistos[eventtype] = TH1F("genhist"+eventtype,"genhist"+eventtype,400,0,maxevents)
    numeventshistos[eventtype].GetXaxis().SetTitle("Number of generated "+eventtype+" events")

if drawGeneratedYields :
    for thistoy in range(0,ntoys) :
        print "Processing toy",thistoy
        thistoyfile = TFile(toysdir+toystupleprefix+str(thistoy)+toystuplesuffix)
        thistoytree = thistoyfile.Get('merged') 
        for thisentry in range(0,thistoytree.GetEntries()) :
            thistoytree.GetEntry(thisentry)
            for eventtype in eventtypes :
                if abs(thistoytree.lab0_TRUEID-eventtypes[eventtype]) < 0.5 :
                    numevents[eventtype][thistoy] += 1
        for eventtype in eventtypes :
            if eventtype == "LMK" :
                numeventshistos[eventtype].Fill(numevents["LMK"][thistoy]+numevents["Bd2DsK"][thistoy])
            else :
                numeventshistos[eventtype].Fill(numevents[eventtype][thistoy])
        numevents["LMK"][thistoy] += numevents["Bd2DsK"][thistoy]
    
    if debug : print numevents
    
    geneventcanvas = TCanvas("geneventcanvas","geneventcanvas",1600,1600)
    geneventcanvas.Divide(3,3)
    for i,eventtype in enumerate(eventtypes) :
        print "Fitting number of generated",eventtype,"events now!"
        geneventcanvas.cd(i+1) 
        numeventshistos[eventtype].Fit("gaus")
        numeventshistos[eventtype].Draw("EP")
    
    if largeToys :
        geneventcanvas.Print(outputdir+"NumGenByChannel_DsK_Large_Mass.pdf")     
    else :
        geneventcanvas.Print(outputdir+"NumGenByChannel_DsK_Mass.pdf")

nfailed = []

for thistoy in range(0,ntoys) :
    f = open(toysdir+toysresultprefix+str(thistoy)+toysresultsuffix)
    counter = 0 
    counterstop = -100
    badfit = False
    print "Processing toy",thistoy
    for line in f :
        counter += 1
        if line.find('MIGRAD=4') > -1 :
            badfit = True
            nfailed.append(thistoy)
            break
        if line.find('NOT POS-DEF') > -1 :
            badfit = True
        if line.find('ERROR MATRIX ACCURATE') > -1 :
            badfit = False
        if line.find('FinalValue') >  -1 :
            if badfit : 
                nfailed.append(thistoy)
                break
            #print line
            counterstop = counter
        if counter == counterstop + 12 :
            result = line.split()
            numfitted["LMK"][thistoy] =  (float(result[2]), float(result[4])) 
        if counter == counterstop + 13 :
            result = line.split()
            numfitted["LMPi"][thistoy] =  (float(result[2]), float(result[4]))
        if counter == counterstop + 14 :
            result = line.split()
            numfitted["Combo"][thistoy] =  (float(result[2]), float(result[4]))
        if counter == counterstop + 15 :
            result = line.split()
            numfitted["Dsp"][thistoy] =  (float(result[2]), float(result[4]))
        if counter == counterstop + 16:
            result = line.split()
            numfitted["Signal"][thistoy] =  (float(result[2]), float(result[4]))
            break
    if counterstop == -100 and not badfit :
        print "Something went wrong with fit",thistoy
        nfailed.append(thistoy)
    f.close()

if debug : 
    print nfailed
    print '\n\n\n'
    print numfitted
    print "Number of failed toys: ", nfailed.__len__()
    

gen_signal    = TH1F("gen_signal","gen_signal",100,1500,2500)
gen_signal.GetXaxis().SetTitle("Generated signal events")
fitted_signal = TH1F("fitted_signal","fitted_signal",100,1500,2500) 
fitted_signal.GetXaxis().SetTitle("Fitted signal events")
errf_signal   = TH1F("errf_signal","errf_signal",100,0,200)
errf_signal.GetXaxis().SetTitle("Fitted error")
pull_signal   = TH1F("pull_signal","pull_signal",50,-5,5)
pull_signal.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
    if thistoy in nfailed : continue
    gen_signal.Fill(numevents["Signal"][thistoy])
    fitted_signal.Fill(numfitted["Signal"][thistoy][0])
    errf_signal.Fill(numfitted["Signal"][thistoy][1])
    #print "%d %d %d %f"%(thistoy, numgenevt["Signal"][thistoy], numfitted["Signal"][thistoy][0],
    #                     numgenevt["Signal"][thistoy]-numfitted["Signal"][thistoy][0])
    pull_signal.Fill((numgenevt["Signal"][thistoy]-numfitted["Signal"][thistoy][0])/numfitted["Signal"][thistoy][1])
pullcanvassignal = TCanvas("pullcanvassignal","pullcanvassignal",800,800)
pullcanvassignal.Divide(2,2)
pullcanvassignal.cd(1)
gen_signal.Draw("PE")
pullcanvassignal.cd(2)
fitted_signal.Draw("PE")
fitted_signal.Fit("gaus")
pullcanvassignal.cd(3)
errf_signal.Draw("PE")
pullcanvassignal.cd(4)
pull_signal.Fit("gaus")
pull_signal.Draw("PE")

if largeToys :
    pullcanvassignal.Print(outputdir+"PullPlot_DsK_Mass_Large_Signal.pdf")
else :
    pullcanvassignal.Print(outputdir+"PullPlot_DsK_Mass_Signal.pdf")

gen_combo    = TH1F("gen_combo","gen_combo",100,3000,5000)
gen_combo.GetXaxis().SetTitle("Generated combo events")
fitted_combo = TH1F("fitted_combo","fitted_combo",100,3000,5000)
fitted_combo.GetXaxis().SetTitle("Fitted combo events")
errf_combo   = TH1F("errf_combo","errf_combo",100,0,1000)
errf_combo.GetXaxis().SetTitle("Fitted error")
pull_combo   = TH1F("pull_combo","pull_combo",50,-5,5)
pull_combo.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
    if thistoy in nfailed : continue
    gen_combo.Fill(numevents["Combo"][thistoy])
    fitted_combo.Fill(numfitted["Combo"][thistoy][0])
    errf_combo.Fill(numfitted["Combo"][thistoy][1])
    pull_combo.Fill((numgenevt["Combo"][thistoy]-numfitted["Combo"][thistoy][0])/numfitted["Combo"][thistoy][1])

pullcanvascombo = TCanvas("pullcanvascombo","pullcanvascombo",800,800)
pullcanvascombo.Divide(2,2)
pullcanvascombo.cd(1)
gen_combo.Draw("PE")
pullcanvascombo.cd(2)
fitted_combo.Draw("PE")
fitted_combo.Fit("gaus")
pullcanvascombo.cd(3)
errf_combo.Draw("PE")
pullcanvascombo.cd(4)
pull_combo.Fit("gaus")
pull_combo.Draw("PE")

if largeToys :
    pullcanvascombo.Print(outputdir+"PullPlot_DsK_Mass_Large_Combo.pdf")
else :
    pullcanvascombo.Print(outputdir+"PullPlot_DsK_Mass_Combo.pdf")

gen_lmk    = TH1F("gen_lmk","gen_lmk",100,0,600)
gen_lmk.GetXaxis().SetTitle("Generated lmk events")
fitted_lmk = TH1F("fitted_lmk","fitted_lmk",100,0,600)
fitted_lmk.GetXaxis().SetTitle("Fitted lmk events")
errf_lmk   = TH1F("errf_lmk","errf_lmk",100,0,500)
errf_lmk.GetXaxis().SetTitle("Fitted error")
pull_lmk   = TH1F("pull_lmk","pull_lmk",50,-5,5)
pull_lmk.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
    if thistoy in nfailed : continue
    gen_lmk.Fill(numevents["LMK"][thistoy])
    fitted_lmk.Fill(numfitted["LMK"][thistoy][0])
    errf_lmk.Fill(numfitted["LMK"][thistoy][1])
    pull_lmk.Fill((numgenevt["LMK"][thistoy]-numfitted["LMK"][thistoy][0])/numfitted["LMK"][thistoy][1])

pullcanvaslmk = TCanvas("pullcanvaslmk","pullcanvaslmk",800,800)
pullcanvaslmk.Divide(2,2)
pullcanvaslmk.cd(1)
gen_lmk.Draw("PE")
pullcanvaslmk.cd(2)
fitted_lmk.Draw("PE")
fitted_lmk.Fit("gaus")
pullcanvaslmk.cd(3)
errf_lmk.Draw("PE")
pullcanvaslmk.cd(4)
pull_lmk.Fit("gaus")
pull_lmk.Draw("PE")

if largeToys :
    pullcanvaslmk.Print(outputdir+"PullPlot_DsK_Mass_Large_LMK.pdf")
else :
    pullcanvaslmk.Print(outputdir+"PullPlot_DsK_Mass_LMK.pdf")

gen_lmpi    = TH1F("gen_lmpi","gen_lmpi",100,0,500)
gen_lmpi.GetXaxis().SetTitle("Generated lmpi events")
fitted_lmpi = TH1F("fitted_lmpi","fitted_lmpi",100,0,500)
fitted_lmpi.GetXaxis().SetTitle("Fitted lmpi events")
errf_lmpi   = TH1F("errf_lmpi","errf_lmpi",100,0,500)
errf_lmpi.GetXaxis().SetTitle("Fitted error")
pull_lmpi   = TH1F("pull_lmpi","pull_lmpi",50,-5,5)
pull_lmpi.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
    if thistoy in nfailed : continue
    gen_lmpi.Fill(numevents["LMPi"][thistoy])
    fitted_lmpi.Fill(numfitted["LMPi"][thistoy][0])
    errf_lmpi.Fill(numfitted["LMPi"][thistoy][1])
    pull_lmpi.Fill((numgenevt["LMPi"][thistoy]-numfitted["LMPi"][thistoy][0])/numfitted["LMPi"][thistoy][1])

pullcanvaslmpi = TCanvas("pullcanvaslmpi","pullcanvaslmpi",800,800)
pullcanvaslmpi.Divide(2,2)
pullcanvaslmpi.cd(1)
gen_lmpi.Draw("PE")
pullcanvaslmpi.cd(2)
fitted_lmpi.Draw("PE")
fitted_lmpi.Fit("gaus")
pullcanvaslmpi.cd(3)
errf_lmpi.Draw("PE")
pullcanvaslmpi.cd(4)
pull_lmpi.Fit("gaus")
pull_lmpi.Draw("PE")

if largeToys:
    pullcanvaslmpi.Print(outputdir+"PullPlot_DsK_Mass_Large_LMPi.pdf")
else :
    pullcanvaslmpi.Print(outputdir+"PullPlot_DsK_Mass_LMPi.pdf")

gen_dsp    = TH1F("gen_dsp","gen_dsp",100,0,700)
gen_dsp.GetXaxis().SetTitle("Generated Dsp events")
fitted_dsp = TH1F("fitted_dsp","fitted_dsp",100,0,700)
fitted_dsp.GetXaxis().SetTitle("Fitted dsp events")
errf_dsp   = TH1F("errf_dsp","errf_dsp",100,0,500)
errf_dsp.GetXaxis().SetTitle("Fitted error")
pull_dsp   = TH1F("pull_dsp","pull_dsp",50,-5,5)
pull_dsp.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
    if thistoy in nfailed : continue
    gen_dsp.Fill(numevents["Dsp"][thistoy])
    fitted_dsp.Fill(numfitted["Dsp"][thistoy][0])
    errf_dsp.Fill(numfitted["Dsp"][thistoy][1])
    pull_dsp.Fill((numgenevt["Dsp"][thistoy]-numfitted["Dsp"][thistoy][0])/numfitted["Dsp"][thistoy][1])
    
pullcanvasdsp = TCanvas("pullcanvasdsp","pullcanvasdsp",800,800)
pullcanvasdsp.Divide(2,2)
pullcanvasdsp.cd(1)
gen_dsp.Draw("PE")
pullcanvasdsp.cd(2)
fitted_dsp.Draw("PE")
fitted_dsp.Fit("gaus")
pullcanvasdsp.cd(3)
errf_dsp.Draw("PE")
pullcanvasdsp.cd(4)
pull_dsp.Fit("gaus")
pull_dsp.Draw("PE")

if largeToys:
    pullcanvasdsp.Print(outputdir+"PullPlot_DsK_Mass_Large_Dsp.pdf")
else :
    pullcanvasdsp.Print(outputdir+"PullPlot_DsK_Mass_Dsp.pdf")
                                    
