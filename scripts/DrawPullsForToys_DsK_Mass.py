from ROOT import *
import ROOT

debug = False
largeToys = False

ntoys               = 200
toysdir             = '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/'
toystupleprefix     = 'DsK_Toys_Full_Tree_'
if largeToys : toystupleprefix     = 'DsK_Toys_FullLarge_Tree_'
toystuplesuffix     = '.root'
toysresultprefix    = 'DsK_Toys_Full_MassFitResult_'
if largeToys : toysresultprefix    = 'DsK_Toys_FullLarge_MassFitResult_'
toysresultsuffix    = '.log'    

eventtypes = {"Signal" : 1.0, 
              "DK"     : 2.0,
              "Bd2DK"  : 3.0,
              "DsPi"   : 4.0,
              "LcK"    : 5.0,
              "Dsp"    : 6.0,
              "LMK"    : 7.0,
              "LMPi"   : 8.0,
              "Combo"  : 10.0 }

numgenevt = {"Signal" : ntoys*[1325.]}
numfitted = {"Signal" : ntoys*[(0,0)]}
numgenevt["Combo"] = ntoys*[1584.]
numfitted["Combo"] = ntoys*[(0,0)]
numgenevt["LMK"] = ntoys*[2324.]
numfitted["LMK"] = ntoys*[(0,0)]
numgenevt["LMPi"] = ntoys*[424.]
numfitted["LMPi"] = ntoys*[(0,0)]

numevents       = {}
numeventshistos = {}

for eventtype in eventtypes :
    numevents[eventtype]    = ntoys*[0]
    maxevents = 2000
    if eventtype in ["DK","LcK","Dsp","DsPi","LMPi"] :
        maxevents = 400
    if largeToys :
        maxevents *= 10
    numeventshistos[eventtype] = TH1F("genhist"+eventtype,"genhist"+eventtype,400,0,maxevents)
    numeventshistos[eventtype].GetXaxis().SetTitle("Number of generated "+eventtype+" events")

for thistoy in range(0,ntoys) :
    thistoyfile = TFile(toysdir+toystupleprefix+str(thistoy)+toystuplesuffix)
    thistoytree = thistoyfile.Get('total_pdfData') 
    for thisentry in range(0,thistoytree.GetEntries()) :
        thistoytree.GetEntry(thisentry)
        for eventtype in eventtypes :
            if abs(thistoytree.lab0_TRUEID-eventtypes[eventtype]) < 0.5 :
                numevents[eventtype][thistoy] += 1
    for eventtype in eventtypes :
        if eventtype == "LMK" :
            numeventshistos[eventtype].Fill(numevents["LMK"][thistoy]+numevents["Bd2DK"][thistoy])
        else :
            numeventshistos[eventtype].Fill(numevents[eventtype][thistoy])
    numevents["LMK"][thistoy] += numevents["Bd2DK"][thistoy]

if debug : print numevents

geneventcanvas = TCanvas("geneventcanvas","geneventcanvas",1600,1600)
geneventcanvas.Divide(3,3)
for i,eventtype in enumerate(eventtypes) :
    print "Fitting number of generated",eventtype,"events now!"
    geneventcanvas.cd(i+1) 
    numeventshistos[eventtype].Fit("gaus")
    numeventshistos[eventtype].Draw("EP")

if largeToys :
    geneventcanvas.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/NumGenByChannel_DsK_Large_Mass.pdf")     
else :
    geneventcanvas.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/NumGenByChannel_DsK_Mass.pdf")

for thistoy in range(0,ntoys) :
    f = open(toysdir+toysresultprefix+str(thistoy)+toysresultsuffix)
    counter = 0 
    counterstop = -100
    for line in f :
        counter += 1
        if line.find('FinalValue') >  -1 : 
            #print line
            counterstop = counter
        if counter == counterstop + 8 :
            result = line.split()
            numfitted["LMK"][thistoy] =  (float(result[2]), float(result[4])) 
        if counter == counterstop + 9 :
            result = line.split()
            numfitted["LMPi"][thistoy] =  (float(result[2]), float(result[4]))
        if counter == counterstop + 10 :
            result = line.split()
            numfitted["Combo"][thistoy] =  (float(result[2]), float(result[4]))
        if counter == counterstop + 11 :
            result = line.split()
            numfitted["Signal"][thistoy] =  (float(result[2]), float(result[4]))
            break
    f.close()

if debug : print numfitted

gen_signal    = TH1F("gen_signal","gen_signal",100,500,1500)
gen_signal.GetXaxis().SetTitle("Generated signal events")
fitted_signal = TH1F("fitted_signal","fitted_signal",100,500,1500) 
fitted_signal.GetXaxis().SetTitle("Fitted signal events")
errf_signal   = TH1F("errf_signal","errf_signal",100,0,200)
errf_signal.GetXaxis().SetTitle("Fitted error")
pull_signal   = TH1F("pull_signal","pull_signal",50,-5,5)
pull_signal.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
    gen_signal.Fill(numevents["Signal"][thistoy])
    fitted_signal.Fill(numfitted["Signal"][thistoy][0])
    errf_signal.Fill(numfitted["Signal"][thistoy][1])
    pull_signal.Fill((numgenevt["Signal"][thistoy]-numfitted["Signal"][thistoy][0])/numfitted["Signal"][thistoy][1])

pullcanvassignal = TCanvas("pullcanvassignal","pullcanvassignal",800,800)
pullcanvassignal.Divide(2,2)
pullcanvassignal.cd(1)
gen_signal.Draw("PE")
pullcanvassignal.cd(2)
fitted_signal.Draw("PE")
pullcanvassignal.cd(3)
errf_signal.Draw("PE")
pullcanvassignal.cd(4)
pull_signal.Fit("gaus")
pull_signal.Draw("PE")

if largeToys :
    pullcanvassignal.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_DsK_Mass_Large_Signal.pdf")
else :
    pullcanvassignal.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_DsK_Mass_Signal.pdf")

gen_combo    = TH1F("gen_combo","gen_combo",100,1000,2000)
gen_combo.GetXaxis().SetTitle("Generated combo events")
fitted_combo = TH1F("fitted_combo","fitted_combo",100,1000,2000)
fitted_combo.GetXaxis().SetTitle("Fitted combo events")
errf_combo   = TH1F("errf_combo","errf_combo",100,0,500)
errf_combo.GetXaxis().SetTitle("Fitted error")
pull_combo   = TH1F("pull_combo","pull_combo",50,-5,5)
pull_combo.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
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
pullcanvascombo.cd(3)
errf_combo.Draw("PE")
pullcanvascombo.cd(4)
pull_combo.Fit("gaus")
pull_combo.Draw("PE")

if largeToys :
    pullcanvascombo.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_DsK_Mass_Large_Combo.pdf")
else :
    pullcanvascombo.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_DsK_Mass_Combo.pdf")

gen_lmk    = TH1F("gen_lmk","gen_lmk",100,1500,2500)
gen_lmk.GetXaxis().SetTitle("Generated lmk events")
fitted_lmk = TH1F("fitted_lmk","fitted_lmk",100,1500,2500)
fitted_lmk.GetXaxis().SetTitle("Fitted lmk events")
errf_lmk   = TH1F("errf_lmk","errf_lmk",100,0,500)
errf_lmk.GetXaxis().SetTitle("Fitted error")
pull_lmk   = TH1F("pull_lmk","pull_lmk",50,-5,5)
pull_lmk.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
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
pullcanvaslmk.cd(3)
errf_lmk.Draw("PE")
pullcanvaslmk.cd(4)
pull_lmk.Fit("gaus")
pull_lmk.Draw("PE")

if largeToys :
    pullcanvaslmk.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_DsK_Mass_Large_LMK.pdf")
else :
    pullcanvaslmk.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_DsK_Mass_LMK.pdf")

gen_lmpi    = TH1F("gen_lmpi","gen_lmpi",100,0,1000)
gen_lmpi.GetXaxis().SetTitle("Generated lmpi events")
fitted_lmpi = TH1F("fitted_lmpi","fitted_lmpi",100,0,1000)
fitted_lmpi.GetXaxis().SetTitle("Fitted lmpi events")
errf_lmpi   = TH1F("errf_lmpi","errf_lmpi",100,0,500)
errf_lmpi.GetXaxis().SetTitle("Fitted error")
pull_lmpi   = TH1F("pull_lmpi","pull_lmpi",50,-5,5)
pull_lmpi.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
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
pullcanvaslmpi.cd(3)
errf_lmpi.Draw("PE")
pullcanvaslmpi.cd(4)
pull_lmpi.Fit("gaus")
pull_lmpi.Draw("PE")

if largeToys:
    pullcanvaslmpi.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_DsK_Mass_Large_LMPi.pdf")
else :
    pullcanvaslmpi.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_DsK_Mass_LMPi.pdf")
