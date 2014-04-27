set dirinput =  '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/For1fbPaper/Gamma70_WProdDetAsy_5M_2T_MD/sWeightsForTimeFit/'
set diroutput = '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/For1fbPaper/Gamma70_WProdDetAsy_5M_2T_MD/TimeFitResults/'

set outputprefix = 'DsK_Toys_TimeFitResult_'
set outputsuffix = '.log'

set inputprefix = 'DsK_Toys_sWeights_ForTimeFit_'
set inputsuffix = '.root'

set timeplotprefix = 'DsK_Toys_Work_TimeFitResult_'

@ thissample = $1

while ($thissample < $2) 
    set thissamplestr = `echo $thissample`
    rm $diroutput$outputprefix$thissamplestr$outputsuffix
    rm $diroutput$outputprefix$thissamplestr$outputsuffix.gz
    python runBs2DsKCPAsymmObsFitterOnData.py --pereventmistag --configName Bs2DsKConfigForNominalGammaFitToys5M --toys --configNameMD Bs2DsKConfigForNominalMassFitToys5M --pathName $dirinput$inputprefix$thissamplestr$inputsuffix --save $diroutput$timeplotprefix$thissamplestr$inputsuffix >& $diroutput$outputprefix$thissamplestr$outputsuffix
    gzip $diroutput$outputprefix$thissamplestr$outputsuffix
    @ thissample++
    echo $thissample
end
