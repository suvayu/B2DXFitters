set dirinput =  '/afs/cern.ch/work/a/adudziak/public/Bs2DsKToys/Gamma70_5M/'
set diroutput = '/afs/cern.ch/work/a/adudziak/public/Bs2DsKToys/Gamma70_5M/tagEff_PETE/'


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
    python runBs2DsKCPAsymmObsFitterOnData.py --debug --pereventmistag --configName Bs2DsKConfigForNominalGammaFitToys5M --toys --configNameMD Bs2DsKConfigForNominalMassFitToys5M --cat --idvar lab1_ID_idx --tagvar lab0_BsTaggingTool_TAGDECISION_OS_idx --pathName $dirinput$inputprefix$thissamplestr$inputsuffix --save $diroutput$timeplotprefix$thissamplestr$inputsuffix >& $diroutput$outputprefix$thissamplestr$outputsuffix
    gzip $diroutput$outputprefix$thissamplestr$outputsuffix
    @ thissample++
    echo $thissample
end
