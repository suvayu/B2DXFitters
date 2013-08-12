from optparse import OptionParser
from os.path  import join

import GaudiPython

GaudiPython.loaddict( 'B2DXFittersDict' )

from ROOT import *
import ROOT

gStyle.SetOptStat(0)
gStyle.SetOptFit(1011)

PlotAcceptance = False

ntoys               = 1000
toysdir             = '/afs/cern.ch/work/a/adudziak/public/Bs2DsPiToys/'
toysresultprefix    = 'DsPi_Toys_TimeFitResult_DMS_'
toysresultsuffix    = '.log'    

outputdir = '/afs/cern.ch/work/a/adudziak/public/Bs2DsPiToys/'

dmsgenera = {"Signal" : ntoys*[17.768]}
dmsfitted = {"Signal" : ntoys*[(0,0)]}

if PlotAcceptance:
    expogenera = {"TaccExpo" : ntoys*[1.8627e+00]}
    expofitted = {"TaccExpo" : ntoys*[(0,0)]}
    
    offgenera = {"TaccOff" : ntoys*[1.6710e-02]}
    offfitted = {"TaccOff" : ntoys*[(0,0)]}
    
    betagenera = {"TaccBeta" : ntoys*[3.4938e-02]}
    betafitted = {"TaccBeta" : ntoys*[(0,0)]}
    
    turnongenera = {"TaccTurnOn" : ntoys*[1.3291e+00]}
    turnonfitted = {"TaccTurnOn" : ntoys*[(0,0)]}
    
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
                                                                                                                                        
        if counter == counterstop + 2 :
            result = line.split()
            dmsfitted["Signal"][thistoy] =  (float(result[2]), float(result[4]))
            break
        #if PlotAcceptance:
        #    if counter == counterstop + 3 :
        #        result = line.split()
        #        betafitted["TaccBeta"][thistoy] =  (float(result[2]), float(result[4]))
        #    if counter == counterstop + 4 :
        #        result = line.split()
        #        expofitted["TaccExpo"][thistoy] =  (float(result[2]), float(result[4]))
        #    if counter == counterstop + 5 :
        #        result = line.split()
        #        offfitted["TaccOff"][thistoy] =  (float(result[2]), float(result[4]))
        #    if counter == counterstop + 6 :
        #        result = line.split()
        #        turnonfitted["TaccTurnOn"][thistoy] =  (float(result[2]), float(result[4]))
        #else:
        #    break
    f.close()

print dmsfitted
print "Number of failed toys: ",nfailed.__len__()

fitted_signal = TH1F("fitted_delta_ms","fitted_delta_ms",100,17.5,18.0) 
fitted_signal.GetXaxis().SetTitle("Fitted delta ms")
errf_signal   = TH1F("errf_delta_ms","errf_delta_ms",100,0,0.05)
errf_signal.GetXaxis().SetTitle("Fitted error")
pull_signal   = TH1F("pull_delta_ms","pull_delta_ms",50,-5,5)
pull_signal.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
    if thistoy in nfailed : continue
    fitted_signal.Fill(dmsfitted["Signal"][thistoy][0])
    errf_signal.Fill(dmsfitted["Signal"][thistoy][1])
    pull_signal.Fill((dmsgenera["Signal"][thistoy]-dmsfitted["Signal"][thistoy][0])/dmsfitted["Signal"][thistoy][1])
    

pullcanvassignal = TCanvas("pullcanvassignal","pullcanvassignal",1500,500)
pullcanvassignal.Divide(3,1)
pullcanvassignal.cd(1)
fitted_signal.Draw("PE")
fitted_result = fitted_signal.Fit("gaus","S")
fitted_result.Print()

print "Mean fitted: ",fitted_signal.GetMean()

pullcanvassignal.cd(2)
errf_signal.Draw("PE")
pullcanvassignal.cd(3)
pull_result=pull_signal.Fit("gaus","S")
pull_result.Print()
pull_signal.Draw("PE")

print "Pull mean: ",pull_signal.GetMean()

pullcanvassignal.Print(outputdir+"PullPlot_DsPi_Time_DMS.pdf")


if PlotAcceptance:
    
    fitted_expo = TH1F("fitted_tacc_expo","fitted_tacc_expo",100,1.0,4.0)
    fitted_expo.GetXaxis().SetTitle("Fitted tacc exponential")
    errf_expo   = TH1F("errf_tacc_expo","errf_tacc_expo",100,0,0.2)
    errf_expo.GetXaxis().SetTitle("Fitted error")
    pull_expo   = TH1F("pull_tacc_expo","pull_tacc_expo",50,-5,5)
    pull_expo.GetXaxis().SetTitle("Fitted Pull")

    for thistoy in range(0,ntoys) :
        if thistoy in nfailed : continue
        fitted_expo.Fill(expofitted["TaccExpo"][thistoy][0])
        errf_expo.Fill(expofitted["TaccExpo"][thistoy][1])
        pull_expo.Fill((expogenera["TaccExpo"][thistoy]-expofitted["TaccExpo"][thistoy][0])/expofitted["TaccExpo"][thistoy][1])

    pullcanvasexpo = TCanvas("pullcanvasexpo","pullcanvasexpo",1500,500)
    pullcanvasexpo.Divide(3,1)
    pullcanvasexpo.cd(1)
    fitted_expo.Draw("PE")
    pullcanvasexpo.cd(2)
    errf_expo.Draw("PE")
    pullcanvasexpo.cd(3)
    pull_expo.Fit("gaus")
    pull_expo.Draw("PE")

    pullcanvasexpo.Print(outputdir+"PullPlot_DsPi_Time_TaccExponent.pdf")

    fitted_off = TH1F("fitted_tacc_off","fitted_tacc_off",100,-0.2,0.10)
    fitted_off.GetXaxis().SetTitle("Fitted tacc offset")
    errf_off   = TH1F("errf_tacc_off","errf_tacc_off",100,0,0.1)
    errf_off.GetXaxis().SetTitle("Fitted error")
    pull_off   = TH1F("pull_tacc_off","pull_tacc_off",50,-5,5)
    pull_off.GetXaxis().SetTitle("Fitted Pull")
    
    for thistoy in range(0,ntoys) :
        if thistoy in nfailed : continue
        fitted_off.Fill(offfitted["TaccOff"][thistoy][0])
        errf_off.Fill(offfitted["TaccOff"][thistoy][1])
        pull_off.Fill((offgenera["TaccOff"][thistoy]-offfitted["TaccOff"][thistoy][0])/offfitted["TaccOff"][thistoy][1])

    pullcanvasoff = TCanvas("pullcanvasoff","pullcanvasoff",1500,500)
    pullcanvasoff.Divide(3,1)
    pullcanvasoff.cd(1)
    fitted_off.Draw("PE")
    pullcanvasoff.cd(2)
    errf_off.Draw("PE")
    pullcanvasoff.cd(3)
    pull_off.Fit("gaus")
    pull_off.Draw("PE")
    
    pullcanvasoff.Print(outputdir+"PullPlot_DsPi_Time_TaccOffset.pdf")

    fitted_beta = TH1F("fitted_tacc_beta","fitted_tacc_beta",100,0.00,0.15)
    fitted_beta.GetXaxis().SetTitle("Fitted tacc beta")
    errf_beta   = TH1F("errf_tacc_beta","errf_tacc_beta",100,0,0.01)
    errf_beta.GetXaxis().SetTitle("Fitted error")
    pull_beta   = TH1F("pull_tacc_beta","pull_tacc_beta",50,-5,5)
    pull_beta.GetXaxis().SetTitle("Fitted Pull")
    
    for thistoy in range(0,ntoys) :
        if thistoy in nfailed : continue
        fitted_beta.Fill(betafitted["TaccBeta"][thistoy][0])
        errf_beta.Fill(betafitted["TaccBeta"][thistoy][1])
        pull_beta.Fill((betagenera["TaccBeta"][thistoy]-betafitted["TaccBeta"][thistoy][0])/betafitted["TaccBeta"][thistoy][1])
        
    pullcanvasbeta = TCanvas("pullcanvasbeta","pullcanvasbeta",1500,500)
    pullcanvasbeta.Divide(3,1)
    pullcanvasbeta.cd(1)
    fitted_beta.Draw("PE")
    pullcanvasbeta.cd(2)
    errf_beta.Draw("PE")
    pullcanvasbeta.cd(3)
    pull_beta.Fit("gaus")
    pull_beta.Draw("PE")
    
    pullcanvasbeta.Print(outputdir+"PullPlot_DsPi_Time_TaccBeta.pdf")
    
    
    fitted_on = TH1F("fitted_tacc_turnon","fitted_tacc_turnon",100,0.50,7.0)
    fitted_on.GetXaxis().SetTitle("Fitted tacc turnon")
    errf_on   = TH1F("errf_tacc_turnon","errf_tacc_turnon",100,0,0.1)
    errf_on.GetXaxis().SetTitle("Fitted error")
    pull_on   = TH1F("pull_tacc_turnon","pull_tacc_turnon",50,-5,5)
    pull_on.GetXaxis().SetTitle("Fitted Pull")
    
    for thistoy in range(0,ntoys) :
        if thistoy in nfailed : continue
        fitted_on.Fill(turnonfitted["TaccTurnOn"][thistoy][0])
        errf_on.Fill(turnonfitted["TaccTurnOn"][thistoy][1])
        pull_on.Fill((turnongenera["TaccTurnOn"][thistoy]-turnonfitted["TaccTurnOn"][thistoy][0])/turnonfitted["TaccTurnOn"][thistoy][1])

    pullcanvason = TCanvas("pullcanvason","pullcanvason",1500,500)
    pullcanvason.Divide(3,1)
    pullcanvason.cd(1)
    fitted_on.Draw("PE")
    pullcanvason.cd(2)
    errf_on.Draw("PE")
    pullcanvason.cd(3)
    pull_on.Fit("gaus")
    pull_on.Draw("PE")
    
    pullcanvason.Print(outputdir+"PullPlot_DsPi_Time_TaccTurnOn.pdf")
                                        
