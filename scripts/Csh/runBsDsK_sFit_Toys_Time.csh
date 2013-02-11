set dir =  '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/DsKToys_Full_2ksample_140912/'

set outputprefix = 'DsK_Toys_Full_TimeFitResult_2kSample_'
set outputsuffix = '.log'

set inputprefix = 'DsK_Toys_Full_sWeights_ForTimeFit_2kSample_'
set inputsuffix = '.root'

set timeplotprefix = 'DsK_Toys_Full_Work_TimeFitResult_2kSample_'

@ thissample = $1

while ($thissample < $2) 
    set thissamplestr = `echo $thissample`
    rm $dir$outputprefix$thissamplestr$outputsuffix
    rm $dir$outputprefix$thissamplestr$outputsuffix.gz
    python runBs2DsKCPAsymmObsFitterOnData.py --toys --pereventmistag --pathToys $dir$inputprefix$thissamplestr$inputsuffix --save $dir$timeplotprefix$thissamplestr$inputsuffix  >& $dir$outputprefix$thissamplestr$outputsuffix 
    gzip $dir$outputprefix$thissamplestr$outputsuffix
    @ thissample++
    echo $thissample
end
