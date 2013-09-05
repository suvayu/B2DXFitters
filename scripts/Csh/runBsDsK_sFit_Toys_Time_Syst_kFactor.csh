set dirinput = '/afs/cern.ch/work/a/adudziak/public/Bs2DsKToys/Gamma70_5M/'
set diroutput = '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/Systematics/kFactor/'

set outputprefix = 'DsK_Toys_TimeFitResult_Syst_kFactor_'
set outputsuffix = '.log'

set inputprefix = 'DsK_Toys_sWeights_ForTimeFit_'
set inputsuffix = '.root'

@ thissample = $1

while ($thissample < $2) 
    set thissamplestr = `echo $thissample`
    rm $diroutput$outputprefix$thissamplestr$outputsuffix
    rm $diroutput$outputprefix$thissamplestr$outputsuffix.gz
    python ../runBs2DsKCPAsymmObsFitterOnData.py --toys --pereventmistag --cat --kfactcorr --configName Bs2DsKConfigForNominalGammaFitToys5M --pathName $dirinput$inputprefix$thissamplestr$inputsuffix >& $diroutput$outputprefix$thissamplestr$outputsuffix 
    #gzip $diroutput$outputprefix$thissamplestr$outputsuffix
    @ thissample++
    echo $thissample
end
