set dirinput =  '/afs/cern.ch/work/a/adudziak/public/Bs2DsKToys/'
set diroutput = '/afs/cern.ch/work/a/adudziak/public/Bs2DsKToys/'


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
    python runBs2DsKCPAsymmObsFitterOnData.py --debug --pereventmistag --config Bs2DsKConfigForNominalGammaFitToys --pathName $dirinput$inputprefix$thissamplestr$inputsuffix --smearAccept --cat --save $diroutput$timeplotprefix$thissamplestr$inputsuffix >& $diroutput$outputprefix$thissamplestr$outputsuffix
    gzip $diroutput$outputprefix$thissamplestr$outputsuffix
    @ thissample++
    echo $thissample
end
