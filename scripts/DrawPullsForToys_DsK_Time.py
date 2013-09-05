from optparse import OptionParser
from os.path  import join

from ROOT import *
import ROOT
ROOT.gROOT.SetBatch()

gStyle.SetOptStat(0)
gStyle.SetOptFit(1011)

def makeprintout(canvas,name) :
    # set all the different types of plots to make
    plottypestomake = [".pdf",".eps",".png",".root",".C"]
    for plottype in plottypestomake :
        canvas.Print(name+plottype)

import sys 
sys.path.append("../data/")

# Get the configuration file
myconfigfilegrabber = __import__("Bs2DsKConfigForGenerator5M",fromlist=['getconfig']).getconfig
myconfigfile = myconfigfilegrabber()

splitCharge = False
largeToys = False
saveplots = True
tbtd = True
tagEffPlot = False

nbinspull = 50
lowerpullrange = -5
upperpullrange = 5
if tbtd :
    nbinspull = 200
    lowerpullrange = -0.75
    upperpullrange = 0.75   

useavgmistag = False
avgmistagsuffix = "AvgMistag_"

ntoys                   = 200
toysdir                 = '/afs/cern.ch/work/a/adudziak/public/Bs2DsKToys/Gamma70_5M/tagEff_PETE/'
toysdir_md              = '/afs/cern.ch/work/a/adudziak/public/Bs2DsKToys/Gamma70_5M/' 
toysdir_tbtd            = '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/Systematics/kFactor/'
toysresultprefix        = 'DsK_Toys_TimeFitResult_'
toysresultprefix_md     = 'DsK_Toys_MassFitResult_'
toysresultprefix_tbtd   = 'DsK_Toys_TimeFitResult_Syst_kFactor_'

if useavgmistag : toysresultprefix += avgmistagsuffix
if largeToys    : toysresultprefix = 'DsK_Toys_FullLarge_TimeFitResult_'
toysresultsuffix    = '.log'    
outputdir = '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/Systematics/PullPlots/'
#outputdir = '/afs/cern.ch/work/a/adudziak/public/Bs2DsKToys/Gamma70_5M/tagEff_PETE/'

additionalsuffix = 'kFactor'

from B2DXFitters import taggingutils, cpobservables
theseobservables = cpobservables.AsymmetryObservables(myconfigfile["ArgLf_s"],myconfigfile["ArgLbarfbar_s"],myconfigfile["ModLf_s"])
print theseobservables.Cf(),theseobservables.Sf(),theseobservables.Sfbar(),theseobservables.Df(),theseobservables.Dfbar()

dmsgenera = {"C" : ntoys*[(theseobservables.Cf(),0.)]}
dmsfitted = {"C" : ntoys*[(0,0)]}
dmsgenera["S"]    = ntoys*[(theseobservables.Sf(),0.)]#ntoys*[(-.501,0.)]
dmsfitted["S"]    = ntoys*[(0,0)]
dmsgenera["Sbar"] = ntoys*[(theseobservables.Sfbar(),0.)]#ntoys*[(0.654,0.)]
dmsfitted["Sbar"] = ntoys*[(0,0)]
dmsgenera["D"]    = ntoys*[(theseobservables.Df(),0.)]#ntoys*[(0.420,0.)]
dmsfitted["D"]    = ntoys*[(0,0)]
dmsgenera["Dbar"] = ntoys*[(theseobservables.Dfbar(),0.)]#ntoys*[(0.0,0.)]
dmsfitted["Dbar"] = ntoys*[(0,0)]
dmsgenera["tagEff"] = ntoys*[(0.403,0.0)] #403,0.)]
dmsfitted["tagEff"] = ntoys*[(0,0)]
nfailed = []

for thistoy in range(0,ntoys) :
    f = open(toysdir_md+toysresultprefix_md+str(thistoy)+toysresultsuffix)
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
            break                                                                                                                                        

print nfailed.__len__(),'toys failed to converge properly at the mass fit stage'
print nfailed

#exit(0)

for thistoy in range(0,ntoys) :
    if not tbtd : break
    if thistoy in nfailed :
        print 'Toy number',thistoy,'failed to converge properly!'
        continue
    try :
        f = open(toysdir_tbtd+toysresultprefix_tbtd+str(thistoy)+toysresultsuffix)
    except :
        print 'Toy number',thistoy,'file not found!'
        print 'I looked for',toysdir_tbtd+toysresultprefix_tbtd+str(thistoy)+toysresultsuffix
        nfailed.append(thistoy)
        continue
    counter = 0
    counterstop = -100
    secondcount = False
    badfit = False
    for line in f :
        counter += 1
        if line.find('MIGRAD=4') > -1 :
            print 'Toy number',thistoy,'failed to converge properly!'
            break
        if line.find('NOT POS-DEF') > -1 :
            badfit = True
        if line.find('ERROR MATRIX ACCURATE') > -1 :
            badfit = False
        if line.find('FinalValue') >  -1 :
            if badfit : break
            #print line
            if counterstop > -100 :
                secondcount = True
            counterstop = counter
        if not splitCharge :
            if counter == counterstop + 2 :
                result = line.split()
                dmsgenera["C"][thistoy] =  (float(result[2]), float(result[4]))
            if counter == counterstop + 3 :
                result = line.split()
                dmsgenera["D"][thistoy] =  (float(result[2]), float(result[4]))
            if counter == counterstop + 4 :
                result = line.split()
                dmsgenera["Dbar"][thistoy] =  (float(result[2]), float(result[4]))
            if counter == counterstop + 5 :
                result = line.split()
                dmsgenera["S"][thistoy] =  (float(result[2]), float(result[4]))
            if counter == counterstop + 6 :
                result = line.split()
                dmsgenera["Sbar"][thistoy] =  (float(result[2]), float(result[4]))
                
            if counter == counterstop + 7 :
                if tagEffPlot:
                    result = line.split()
                    dmsfitted["tagEff"][thistoy] =  (float(result[2]), float(result[4]))
                    break
                else:
                    break
    if counterstop == -100 :
        nfailed.append(thistoy)
    f.close()

for thistoy in range(0,ntoys) :
    if thistoy in nfailed :
        print 'Toy number',thistoy,'failed to converge properly!'
        continue
    try :
        f = open(toysdir+toysresultprefix+str(thistoy)+toysresultsuffix)
    except :
        print 'Toy number',thistoy,'file not found!'
        print 'I looked for',toysdir+toysresultprefix+str(thistoy)+toysresultsuffix
        nfailed.append(thistoy)
        continue
    counter = 0 
    counterstop = -100
    secondcount = False
    badfit = False
    for line in f :
        counter += 1
        if line.find('MIGRAD=4') > -1 :
            print 'Toy number',thistoy,'failed to converge properly!'
            break
        if line.find('NOT POS-DEF') > -1 :
            badfit = True
        if line.find('ERROR MATRIX ACCURATE') > -1 :
            badfit = False
        if line.find('FinalValue') >  -1 : 
            #print line
            if badfit : break
            if counterstop > -100 :
                secondcount = True
            counterstop = counter
        if not splitCharge :
            
            if counter == counterstop + 2 :
                result = line.split()
                dmsfitted["C"][thistoy] =  (float(result[2]), float(result[4]))
#                print dmsfitted["C"][thistoy]
            if counter == counterstop + 3 : 
                result = line.split()
                dmsfitted["D"][thistoy] =  (float(result[2]), float(result[4]))
#                print dmsfitted["D"][thistoy] 
            if counter == counterstop + 4 : 
                result = line.split()
                dmsfitted["Dbar"][thistoy] =  (float(result[2]), float(result[4]))
#                print dmsfitted["Dbar"][thistoy]
            if counter == counterstop + 5 : 
                result = line.split()
                dmsfitted["S"][thistoy] =  (float(result[2]), float(result[4]))
#                print dmsfitted["S"][thistoy]
            if counter == counterstop + 6 : 
                result = line.split()
                dmsfitted["Sbar"][thistoy] =  (float(result[2]), float(result[4]))
#                print dmsfitted["Sbar"][thistoy]
            if counter == counterstop + 7 :
                if tagEffPlot:
                    result = line.split()
                    dmsfitted["tagEff"][thistoy] =  (float(result[2]), float(result[4]))
                    #                print dmsfitted["tagEff"][thistoy]
                    #                exit(0)
                    break
                else:
                    break
            
        else :
            if not secondcount and counter == counterstop + 2 : 
                result = line.split()
                dmsfitted["C"][thistoy] =  (float(result[2]), float(result[4]))
            if not secondcount and counter == counterstop + 3 :
                result = line.split()
                dmsfitted["D"][thistoy] =  (float(result[2]), float(result[4]))
            if not secondcount and counter == counterstop + 4 :
                result = line.split()
                dmsfitted["Sbar"][thistoy] =  (float(result[2]), float(result[4]))
            if secondcount and counter == counterstop + 2 : 
                result = line.split()
                dmsfitted["C"][thistoy] =  ((float(result[2])+dmsfitted["C"][thistoy][0])/2.,dmsfitted["C"][thistoy][1]/sqrt(2.))
            if secondcount and counter == counterstop + 3 : 
                result = line.split()
                dmsfitted["Dbar"][thistoy] =  (float(result[2]), float(result[4]))
            if secondcount and counter == counterstop + 4 : 
                result = line.split()
                dmsfitted["S"][thistoy] =  (float(result[2]), float(result[4]))
            if counter == counterstop + 7 :
                result = line.split()
                dmsfitted["tagEff"][thistoy] =  (float(result[2]), float(result[4]))
                
                break
    if counterstop == -100 :
        nfailed.append(thistoy)
    f.close()

            
print nfailed.__len__(),'toys failed to converge properly at the time fit stage'
print nfailed
#exit(0)

if tbtd : 
    additionalsuffix += "_TBTD_"

fitted_C = TH1F("fitted_C","fitted_C",100,-3.,3.0) 
fitted_C.GetXaxis().SetTitle("Fitted C events")
errf_C   = TH1F("errf_C","errf_C",100,0,1.)
errf_C.GetXaxis().SetTitle("Fitted error")
pull_C   = TH1F("pull_C","pull_C",nbinspull,lowerpullrange,upperpullrange)
pull_C.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
    if thistoy in nfailed : continue 
    if dmsfitted["C"][thistoy][1] == 0 : continue
    fitted_C.Fill(dmsfitted["C"][thistoy][0])
    errf_C.Fill(dmsfitted["C"][thistoy][1])
    pull_C.Fill((dmsgenera["C"][thistoy][0]-dmsfitted["C"][thistoy][0])/dmsfitted["C"][thistoy][1])

pullcanvasC = TCanvas("pullcanvasC","pullcanvasC",1500,500)
pullcanvasC.Divide(3,1)
pullcanvasC.cd(1)
fitted_C.Fit("gaus")
fitted_C.Draw("PE")
pullcanvasC.cd(2)
errf_C.Fit("gaus")
errf_C.Draw("PE")
pullcanvasC.cd(3)
pull_C.Fit("gaus")
pull_C.Draw("PE")

if not useavgmistag and not largeToys and saveplots:
    makeprintout(pullcanvasC,outputdir+"PullPlot_"+additionalsuffix+"DsK_Time_C")
elif not largeToys and saveplots:
    makeprintout(pullcanvasC,outputdir+"PullPlot_DsK_Time_"+avgmistagsuffix+"C")
elif saveplots :
    makeprintout(pullcanvasC,outputdir+"PullPlot_DsK_Time_Large_C")

fitted_S = TH1F("fitted_S","fitted_S",100,-3.,3.0)     
fitted_S.GetXaxis().SetTitle("Fitted S events")
errf_S   = TH1F("errf_S","errf_S",100,0,1.)
errf_S.GetXaxis().SetTitle("Fitted error")
pull_S   = TH1F("pull_S","pull_S",nbinspull,lowerpullrange,upperpullrange)
pull_S.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
    if thistoy in nfailed : continue
    if dmsfitted["S"][thistoy][1] == 0 : continue
    fitted_S.Fill(dmsfitted["S"][thistoy][0])
    errf_S.Fill(dmsfitted["S"][thistoy][1])
    pull_S.Fill((dmsgenera["S"][thistoy][0]-dmsfitted["S"][thistoy][0])/dmsfitted["S"][thistoy][1])

pullcanvasS = TCanvas("pullcanvasS","pullcanvasS",1500,500)
pullcanvasS.Divide(3,1)
pullcanvasS.cd(1)
fitted_S.Fit("gaus")
fitted_S.Draw("PE")
pullcanvasS.cd(2)
errf_S.Fit("gaus")
errf_S.Draw("PE")
pullcanvasS.cd(3)
pull_S.Fit("gaus")
pull_S.Draw("PE")

if not useavgmistag and not largeToys and saveplots:
    makeprintout(pullcanvasS,outputdir+"PullPlot_"+additionalsuffix+"DsK_Time_S")
elif not largeToys and saveplots:
    makeprintout(pullcanvasS,outputdir+"PullPlot_DsK_Time_"+avgmistagsuffix+"S")
elif saveplots :
    makeprintout(pullcanvasS,outputdir+"PullPlot_DsK_Time_Large_S")

fitted_Sbar = TH1F("fitted_Sbar","fitted_Sbar",100,-3.,3.0)     
fitted_Sbar.GetXaxis().SetTitle("Fitted Sbar events")
errf_Sbar   = TH1F("errf_Sbar","errf_Sbar",100,0,1.)
errf_Sbar.GetXaxis().SetTitle("Fitted error")
pull_Sbar   = TH1F("pull_Sbar","pull_Sbar",nbinspull,lowerpullrange,upperpullrange)
pull_Sbar.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
    if thistoy in nfailed : continue
    if dmsfitted["Sbar"][thistoy][1] == 0 : continue
    fitted_Sbar.Fill(dmsfitted["Sbar"][thistoy][0])
    errf_Sbar.Fill(dmsfitted["Sbar"][thistoy][1])
    pull_Sbar.Fill((dmsgenera["Sbar"][thistoy][0]-dmsfitted["Sbar"][thistoy][0])/dmsfitted["Sbar"][thistoy][1])

pullcanvasSbar = TCanvas("pullcanvasSbar","pullcanvasSbar",1500,500)
pullcanvasSbar.Divide(3,1)
pullcanvasSbar.cd(1)
fitted_Sbar.Fit("gaus")
fitted_Sbar.Draw("PE")
pullcanvasSbar.cd(2)
errf_Sbar.Fit("gaus")
errf_Sbar.Draw("PE")
pullcanvasSbar.cd(3)
pull_Sbar.Fit("gaus")
pull_Sbar.Draw("PE")

if not useavgmistag and not largeToys and saveplots:
    makeprintout(pullcanvasSbar,outputdir+"PullPlot_"+additionalsuffix+"DsK_Time_Sbar")
elif not largeToys and saveplots:
    makeprintout(pullcanvasSbar,outputdir+"PullPlot_DsK_Time_"+avgmistagsuffix+"Sbar")
elif saveplots :
    makeprintout(pullcanvasSbar,outputdir+"PullPlot_DsK_Time_Large_Sbar")

fitted_D = TH1F("fitted_D","fitted_D",100,-3.,3.0)     
fitted_D.GetXaxis().SetTitle("Fitted D events")
errf_D   = TH1F("errf_D","errf_D",100,0,1.)
errf_D.GetXaxis().SetTitle("Fitted error")
pull_D   = TH1F("pull_D","pull_D",nbinspull,lowerpullrange,upperpullrange)
pull_D.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
    if thistoy in nfailed : continue
    if dmsfitted["D"][thistoy][1] == 0 : continue
    fitted_D.Fill(dmsfitted["D"][thistoy][0])
    errf_D.Fill(dmsfitted["D"][thistoy][1])
    pull_D.Fill((dmsgenera["D"][thistoy][0]-dmsfitted["D"][thistoy][0])/dmsfitted["D"][thistoy][1])

pullcanvasD = TCanvas("pullcanvasD","pullcanvasD",1500,500)
pullcanvasD.Divide(3,1)
pullcanvasD.cd(1)
fitted_D.Fit("gaus")
fitted_D.Draw("PE")
pullcanvasD.cd(2)
errf_D.Fit("gaus")
errf_D.Draw("PE")
pullcanvasD.cd(3)
pull_D.Fit("gaus")
pull_D.Draw("PE")

if not useavgmistag and not largeToys  and saveplots:
    makeprintout(pullcanvasD,outputdir+"PullPlot_"+additionalsuffix+"DsK_Time_D")
elif not largeToys and saveplots:
    makeprintout(pullcanvasD,outputdir+"PullPlot_DsK_Time_"+avgmistagsuffix+"D")
elif saveplots :
    makeprintout(pullcanvasD,outputdir+"PullPlot_DsK_Time_Large_D")

fitted_Dbar = TH1F("fitted_Dbar","fitted_Dbar",100,-3.,3.0)     
fitted_Dbar.GetXaxis().SetTitle("Fitted Dbar events")
errf_Dbar   = TH1F("errf_Dbar","errf_Dbar",100,0,1.)
errf_Dbar.GetXaxis().SetTitle("Fitted error")
pull_Dbar   = TH1F("pull_Dbar","pull_Dbar",nbinspull,lowerpullrange,upperpullrange)
pull_Dbar.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
    if thistoy in nfailed : continue
    if dmsfitted["Dbar"][thistoy][1] == 0 : continue
    fitted_Dbar.Fill(dmsfitted["Dbar"][thistoy][0])
    errf_Dbar.Fill(dmsfitted["Dbar"][thistoy][1])
    pull_Dbar.Fill((dmsgenera["Dbar"][thistoy][0]-dmsfitted["Dbar"][thistoy][0])/dmsfitted["Dbar"][thistoy][1])

pullcanvasDbar = TCanvas("pullcanvasDbar","pullcanvasDbar",1500,500)
pullcanvasDbar.Divide(3,1)
pullcanvasDbar.cd(1)
fitted_Dbar.Fit("gaus")
fitted_Dbar.Draw("PE")
pullcanvasDbar.cd(2)
errf_Dbar.Fit("gaus")
errf_Dbar.Draw("PE")
pullcanvasDbar.cd(3)
pull_Dbar.Fit("gaus")
pull_Dbar.Draw("PE")

if not useavgmistag and not largeToys and saveplots:
    makeprintout(pullcanvasDbar,outputdir+"PullPlot_"+additionalsuffix+"DsK_Time_Dbar")
elif not largeToys and saveplots:
    makeprintout(pullcanvasDbar,outputdir+"PullPlot_DsK_Time_"+avgmistagsuffix+"Dbar")
elif saveplots :
    makeprintout(pullcanvasDbar,outputdir+"PullPlot_DsK_Time_Large_Dbar")

if tagEffPlot:
    fitted_tagEff = TH1F("fitted_tagEff","fitted_tagEff",100,0.0,1.0)
    fitted_tagEff.GetXaxis().SetTitle("Fitted tagEff events")
    errf_tagEff   = TH1F("errf_tagEff","errf_tagEff",100,0.0,0.1)
    errf_tagEff.GetXaxis().SetTitle("Fitted error")
    pull_tagEff   = TH1F("pull_tagEff","pull_tagEff",nbinspull,lowerpullrange,upperpullrange)
    pull_tagEff.GetXaxis().SetTitle("Fitted Pull")
    
    for thistoy in range(0,ntoys) :
        if thistoy in nfailed : continue
        if dmsfitted["tagEff"][thistoy][1] == 0 : continue
        fitted_tagEff.Fill(dmsfitted["tagEff"][thistoy][0])
        errf_tagEff.Fill(dmsfitted["tagEff"][thistoy][1])
        #print dmsfitted["tagEff"][thistoy]
        pull_tagEff.Fill((dmsgenera["tagEff"][thistoy][0]-dmsfitted["tagEff"][thistoy][0])/dmsfitted["tagEff"][thistoy][1])
    
    pullcanvastagEff = TCanvas("pullcanvastagEff","pullcanvastagEff",1500,500)
    pullcanvastagEff.Divide(3,1)
    pullcanvastagEff.cd(1)
    fitted_tagEff.Fit("gaus")
    fitted_tagEff.Draw("PE")
    pullcanvastagEff.cd(2)
    errf_tagEff.Fit("gaus")
    errf_tagEff.Draw("PE")
    pullcanvastagEff.cd(3)
    pull_tagEff.Fit("gaus")
    pull_tagEff.Draw("PE")
    
    if not useavgmistag and not largeToys and saveplots:
        makeprintout(pullcanvastagEff,outputdir+"PullPlot_"+additionalsuffix+"DsK_Time_tagEff")
    elif not largeToys and saveplots:
        makeprintout(pullcanvastagEff,outputdir+"PullPlot_DsK_Time_"+avgmistagsuffix+"tagEff")
    elif saveplots :
        makeprintout(pullcanvastagEff,outputdir+"PullPlot_DsK_Time_Large_tagEff")
    
