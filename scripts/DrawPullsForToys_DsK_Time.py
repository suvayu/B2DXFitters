from ROOT import *
import ROOT

splitCharge = False

largeToys = False

saveplots = True

tbtd = False

nbinspull = 50
lowerpullrange = -5
upperpullrange = 5
if tbtd :
    nbinspull = 200
    lowerpullrange = -0.75
    upperpullrange = 0.75   

useavgmistag = False
avgmistagsuffix = "AvgMistag_"

ntoys               = 1000
toysdir             = '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/DsKToys_Full_2ksample_140912/'
toysresultprefix    = 'DsK_Toys_Full_TimeFitResult_2kSample_'
if useavgmistag : toysresultprefix += avgmistagsuffix
if largeToys    : toysresultprefix = 'DsK_Toys_FullLarge_TimeFitResult_'
toysresultsuffix    = '.log'    

additionalsuffix = ""#FixParSyst_p1_"

dmsgenera = {"C" : ntoys*[(0.757,0.)]}
dmsfitted = {"C" : ntoys*[(0,0)]}
dmsgenera["S"]    = ntoys*[(-0.614,0.)]#ntoys*[(-.501,0.)]
dmsfitted["S"]    = ntoys*[(0,0)]
dmsgenera["Sbar"] = ntoys*[(0.113,0.)]#ntoys*[(0.654,0.)]
dmsfitted["Sbar"] = ntoys*[(0,0)]
dmsgenera["D"]    = ntoys*[(-0.224,0.)]#ntoys*[(0.420,0.)]
dmsfitted["D"]    = ntoys*[(0,0)]
dmsgenera["Dbar"] = ntoys*[(-0.644,0.)]#ntoys*[(0.0,0.)]
dmsfitted["Dbar"] = ntoys*[(0,0)]

nfailed = []

for thistoy in range(0,ntoys) :
    if not tbtd : break
    try :
        f = open(toysdir+toysresultprefix+str(thistoy)+toysresultsuffix)
    except :
        print 'Toy number',thistoy,'failed to converge properly!'
        nfailed.append(thistoy)
        continue
    counter = 0
    counterstop = -100
    secondcount = False
    badfit = False
    for line in f :
        counter += 1
        if line.find('MIGRAD=4') > -1 :
            nfailed.append(thistoy)
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
                break
    f.close()

for thistoy in range(0,ntoys) :
    try :
        f = open(toysdir+toysresultprefix+additionalsuffix+str(thistoy)+toysresultsuffix)
    except :
        print 'Toy number',thistoy,'failed to converge properly!'
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
            if counter == counterstop + 3 : 
                result = line.split()
                dmsfitted["D"][thistoy] =  (float(result[2]), float(result[4]))
            if counter == counterstop + 4 : 
                result = line.split()
                dmsfitted["Dbar"][thistoy] =  (float(result[2]), float(result[4]))
            if counter == counterstop + 5 : 
                result = line.split()
                dmsfitted["S"][thistoy] =  (float(result[2]), float(result[4]))
            if counter == counterstop + 6 : 
                result = line.split()
                dmsfitted["Sbar"][thistoy] =  (float(result[2]), float(result[4]))
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
                break
    if counterstop == -100 :
        nfailed.append(thistoy)
    f.close()

print nfailed.__len__(),'toys failed to converge properly'

print nfailed

if tbtd : additionalsuffix += "TBTD_"

additionalsuffix += "14092012_"

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
    pullcanvasC.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_2kSample_"+additionalsuffix+"DsK_Time_C.pdf")
elif not largeToys and saveplots:
    pullcanvasC.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_DsK_Time_"+avgmistagsuffix+"C.pdf")
elif saveplots :
    pullcanvasC.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_DsK_Time_Large_C.pdf")

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
    pullcanvasS.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_2kSample_"+additionalsuffix+"DsK_Time_S.pdf")
elif not largeToys and saveplots:
    pullcanvasS.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_DsK_Time_"+avgmistagsuffix+"S.pdf")
elif saveplots :
    pullcanvasS.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_DsK_Time_Large_S.pdf")

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
    pullcanvasSbar.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_2kSample_"+additionalsuffix+"DsK_Time_Sbar.pdf")
elif not largeToys and saveplots:
    pullcanvasSbar.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_DsK_Time_"+avgmistagsuffix+"Sbar.pdf")
elif saveplots :
    pullcanvasSbar.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_DsK_Time_Large_Sbar.pdf")

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
    pullcanvasD.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_2kSample_"+additionalsuffix+"DsK_Time_D.pdf")
elif not largeToys and saveplots:
    pullcanvasD.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_DsK_Time_"+avgmistagsuffix+"D.pdf")
elif saveplots :
    pullcanvasD.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_DsK_Time_Large_D.pdf")

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
    pullcanvasDbar.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_2kSample_"+additionalsuffix+"DsK_Time_Dbar.pdf")
elif not largeToys and saveplots:
    pullcanvasDbar.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_DsK_Time_"+avgmistagsuffix+"Dbar.pdf")
elif saveplots :
    pullcanvasDbar.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_DsK_Time_Large_Dbar.pdf")
