from ROOT import *
import ROOT

ntoys               = 200
toysdir             = '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/'
toystupleprefix     = 'DsPi_Toys_Full_Tree_'
toystuplesuffix     = '.root'
toysresultprefix    = 'DsPi_Toys_Full_MassFitResult_'
toysresultsuffix    = '.log'    

numgenevt = {"Signal" : ntoys*[25000*.975],"Lb2LcPi" : ntoys*[1000*.975],"Combo" : ntoys*[15000*.975], "LM" : ntoys*[33000*.975]}
numevents = {"Signal" : ntoys*[25000*.975],"Lb2LcPi" : ntoys*[1000*.975],"Combo" : ntoys*[15000*.975], "LM" : ntoys*[33000*.975]}
numfitted = {"Signal" : ntoys*[(0,0)], "Lb2LcPi" : ntoys*[0], "Combo" : ntoys*[0], "LM" : ntoys*[0] }

for thistoy in range(0,ntoys) :
    thistoyfile = TFile(toysdir+toystupleprefix+str(thistoy)+toystuplesuffix)
    thistoytree = thistoyfile.Get('total_pdfData') 
    numevents["Signal"][thistoy] = 0
    numevents["Lb2LcPi"][thistoy] = 0
    numevents["Combo"][thistoy] = 0
    numevents["LM"][thistoy] = 0
    for thisentry in range(0,thistoytree.GetEntries()) :
        thistoytree.GetEntry(thisentry)
        if thistoytree.lab0_TRUEID < 1.5 :
            numevents["Signal"][thistoy] += 1 
        if (thistoytree.lab0_TRUEID > 3.5) and (thistoytree.lab0_TRUEID < 4.5) :
            numevents["Lb2LcPi"][thistoy] += 1
        if (thistoytree.lab0_TRUEID > 9.5) and (thistoytree.lab0_TRUEID < 10.5) :
            numevents["Combo"][thistoy] += 1
        if (thistoytree.lab0_TRUEID > 4.5) and (thistoytree.lab0_TRUEID < 5.5) :
            numevents["LM"][thistoy] += 1  

print numevents

for thistoy in range(0,ntoys) :
    f = open(toysdir+toysresultprefix+str(thistoy)+toysresultsuffix)
    counter = 0 
    counterstop = -100
    for line in f :
        counter += 1
        if line.find('FinalValue') >  -1 : 
            #print line
            counterstop = counter
        if counter == counterstop + 7 : 
            result = line.split()
            numfitted["LM"][thistoy] =  (float(result[2]), float(result[4]))
        if counter == counterstop + 8 :
            result = line.split()
            numfitted["Combo"][thistoy] =  (float(result[2]), float(result[4]))    
        if counter == counterstop + 9 :
            result = line.split()
            numfitted["Lb2LcPi"][thistoy] =  (float(result[2]), float(result[4]))
        if counter == counterstop + 10 :
            result = line.split()
            numfitted["Signal"][thistoy] =  (float(result[2]), float(result[4]))
            break
    f.close()

print numfitted

gen_signal    = TH1F("gen_signal","gen_signal",100,23500,25500)
gen_signal.GetXaxis().SetTitle("Generated signal events")
fitted_signal = TH1F("fitted_signal","fitted_signal",100,23500,25500) 
fitted_signal.GetXaxis().SetTitle("Fitted signal events")
errf_signal   = TH1F("errf_signal","errf_signal",100,100,300)
errf_signal.GetXaxis().SetTitle("Fitted signal error")
pull_signal   = TH1F("pull_signal","pull_signal",50,-5,5)
pull_signal.GetXaxis().SetTitle("Fitted Signal Pull")

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

pullcanvassignal.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_DsPi_Mass_Signal.pdf")

gen_lb2lcpi    = TH1F("gen_lb2lcpi","gen_lb2lcpi",100,0,2000)
gen_lb2lcpi.GetXaxis().SetTitle("Generated lb2lcpi events")
fitted_lb2lcpi = TH1F("fitted_lb2lcpi","fitted_lb2lcpi",100,0,2000) 
fitted_lb2lcpi.GetXaxis().SetTitle("Fitted lb2lcpi events")
errf_lb2lcpi   = TH1F("errf_lb2lcpi","errf_lb2lcpi",100,0,300)
errf_lb2lcpi.GetXaxis().SetTitle("Fitted lb2lcpi error")
pull_lb2lcpi   = TH1F("pull_lb2lcpi","pull_lb2lcpi",50,-5,5)
pull_lb2lcpi.GetXaxis().SetTitle("Fitted Lb2LcPi Pull")

for thistoy in range(0,ntoys) :
    gen_lb2lcpi.Fill(numevents["Lb2LcPi"][thistoy])
    fitted_lb2lcpi.Fill(numfitted["Lb2LcPi"][thistoy][0])
    errf_lb2lcpi.Fill(numfitted["Lb2LcPi"][thistoy][1])
    pull_lb2lcpi.Fill((numgenevt["Lb2LcPi"][thistoy]-numfitted["Lb2LcPi"][thistoy][0])/numfitted["Lb2LcPi"][thistoy][1])

pullcanvaslb2lcpi = TCanvas("pullcanvaslb2lcpi","pullcanvaslb2lcpi",800,800)
pullcanvaslb2lcpi.Divide(2,2)
pullcanvaslb2lcpi.cd(1)
gen_lb2lcpi.Draw("PE")
pullcanvaslb2lcpi.cd(2)
fitted_lb2lcpi.Draw("PE")
pullcanvaslb2lcpi.cd(3)
errf_lb2lcpi.Draw("PE")
pullcanvaslb2lcpi.cd(4)
pull_lb2lcpi.Fit("gaus")
pull_lb2lcpi.Draw("PE")

pullcanvaslb2lcpi.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_DsPi_Mass_Lb2LcPi.pdf")

gen_combo    = TH1F("gen_combo","gen_combo",100,13000,15000)
gen_combo.GetXaxis().SetTitle("Generated combo events")
fitted_combo = TH1F("fitted_combo","fitted_combo",100,13000,15000) 
fitted_combo.GetXaxis().SetTitle("Fitted combo events")
errf_combo   = TH1F("errf_combo","errf_combo",100,0,300)
errf_combo.GetXaxis().SetTitle("Fitted combo error")
pull_combo   = TH1F("pull_combo","pull_combo",50,-5,5)
pull_combo.GetXaxis().SetTitle("Fitted Combo Pull")

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

pullcanvascombo.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_DsPi_Mass_Combo.pdf")

gen_lm    = TH1F("gen_lm","gen_lm",100,31000,34000)
gen_lm.GetXaxis().SetTitle("Generated lm events")
fitted_lm = TH1F("fitted_lm","fitted_lm",100,31000,34000) 
fitted_lm.GetXaxis().SetTitle("Fitted lm events")
errf_lm   = TH1F("errf_lm","errf_lm",100,0,300)
errf_lm.GetXaxis().SetTitle("Fitted lm error")
pull_lm   = TH1F("pull_lm","pull_lm",50,-5,5)
pull_lm.GetXaxis().SetTitle("Fitted LM Pull")

for thistoy in range(0,ntoys) :
    gen_lm.Fill(numevents["LM"][thistoy])
    fitted_lm.Fill(numfitted["LM"][thistoy][0])
    errf_lm.Fill(numfitted["LM"][thistoy][1])
    pull_lm.Fill((numgenevt["LM"][thistoy]-numfitted["LM"][thistoy][0])/numfitted["LM"][thistoy][1])

pullcanvaslm = TCanvas("pullcanvaslm","pullcanvaslm",800,800)
pullcanvaslm.Divide(2,2)
pullcanvaslm.cd(1)
gen_lm.Draw("PE")
pullcanvaslm.cd(2)
fitted_lm.Draw("PE")
pullcanvaslm.cd(3)
errf_lm.Draw("PE")
pullcanvaslm.cd(4)
pull_lm.Fit("gaus")
pull_lm.Draw("PE")

pullcanvaslm.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_DsPi_Mass_LM.pdf")
