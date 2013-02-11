from ROOT import *
import ROOT

ntoys               = 200
toysdir             = '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/'
toysresultprefix    = 'DsPi_Toys_Full_TimeFitResult_'
toysresultsuffix    = '.log'    

dmsgenera = {"Signal" : ntoys*[17.7]}
dmsfitted = {"Signal" : ntoys*[(0,0)]}

for thistoy in range(0,ntoys) :
    f = open(toysdir+toysresultprefix+str(thistoy)+toysresultsuffix)
    counter = 0 
    counterstop = -100
    for line in f :
        counter += 1
        if line.find('FinalValue') >  -1 : 
            #print line
            counterstop = counter
        if counter == counterstop + 2 :
            result = line.split()
            dmsfitted["Signal"][thistoy] =  (float(result[2]), float(result[4]))
            break
    f.close()

print dmsfitted

fitted_signal = TH1F("fitted_signal","fitted_signal",100,17.5,18.0) 
fitted_signal.GetXaxis().SetTitle("Fitted signal events")
errf_signal   = TH1F("errf_signal","errf_signal",100,0,0.05)
errf_signal.GetXaxis().SetTitle("Fitted error")
pull_signal   = TH1F("pull_signal","pull_signal",50,-5,5)
pull_signal.GetXaxis().SetTitle("Fitted Pull")

for thistoy in range(0,ntoys) :
    fitted_signal.Fill(dmsfitted["Signal"][thistoy][0])
    errf_signal.Fill(dmsfitted["Signal"][thistoy][1])
    pull_signal.Fill((dmsgenera["Signal"][thistoy]-dmsfitted["Signal"][thistoy][0])/dmsfitted["Signal"][thistoy][1])

pullcanvassignal = TCanvas("pullcanvassignal","pullcanvassignal",1500,500)
pullcanvassignal.Divide(3,1)
pullcanvassignal.cd(1)
fitted_signal.Draw("PE")
pullcanvassignal.cd(2)
errf_signal.Draw("PE")
pullcanvassignal.cd(3)
pull_signal.Fit("gaus")
pull_signal.Draw("PE")

pullcanvassignal.Print("/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/sWeightToys/PullPlot_DsPi_Time_Signal.pdf")
