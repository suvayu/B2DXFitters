set dir =  '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/'

set outputprefix = 'DsPi_Toys_Full_TimeFitResult_'
set outputsuffix = '.log'

set inputprefix = 'DsPi_Toys_Full_sWeights_ForTimeFit_'
set inputsuffix = '.root'

set timeplotprefix = 'DsPi_Toys_Full_Work_TimeFitResult_'

@ thissample = $1

while ($thissample < $2) 
    set thissamplestr = `echo $thissample`
    rm $dir$outputprefix$thissamplestr$outputsuffix
    rm $dir$outputprefix$thissamplestr$outputsuffix.gz
    python ../runBs2DsPiCPAsymmObsFitterOnData.py --toys --pereventmistag --pathToys $dir$inputprefix$thissamplestr$inputsuffix --save $dir$timeplotprefix$thissamplestr$inputsuffix  >& $dir$outputprefix$thissamplestr$outputsuffix 
    gzip $dir$outputprefix$thissamplestr$outputsuffix
    @ thissample++
    echo $thissample
end
