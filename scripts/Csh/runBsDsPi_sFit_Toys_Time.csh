set dirinput  = '/afs/cern.ch/work/a/adudziak/public/Bs2DsPiToys/'
set diroutput = '/afs/cern.ch/work/a/adudziak/public/Bs2DsPiToys/'

set outputprefix = 'DsPi_Toys_TimeFitResult_'
set outputsuffix = '.log'

set inputprefix = 'DsPi_Toys_sWeights_ForTimeFit_'
set inputsuffix = '.root'

set timeplotprefix = 'DsPi_Toys_Work_TimeFitResult_'

@ thissample = $1

while ($thissample < $2) 
    set thissamplestr = `echo $thissample`
    rm $diroutput$outputprefix$thissamplestr$outputsuffix
    rm $diroutput$outputprefix$thissamplestr$outputsuffix.gz
    python runBs2DsPiCPAsymmObsFitterOnData.py --debug --pereventmistag --config Bs2DsPiConfigForNominalDMSFitToys --pathName $dirinput$inputprefix$thissamplestr$inputsuffix --cat --save $diroutput$timeplotprefix$thissamplestr$inputsuffix  >& $diroutputx$outputprefix$thissamplestr$outputsuffix
    gzip $diroutput$outputprefix$thissamplestr$outputsuffix
    @ thissample++
    echo $thissample
end
