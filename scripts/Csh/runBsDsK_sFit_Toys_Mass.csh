set dir =  '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/DsKToys_Full_2ksample_140912/'

set outputprefix = 'DsK_Toys_Full_MassFitResult_2kSample_'
set outputsuffix = '.log'

set inputprefix = 'DsK_Toys_Full_Work_2kSample_'
set inputsuffix = '.root'

set sweightsprefix = 'DsK_Toys_Full_sWeights_ForTimeFit_2kSample_'
set massplotprefix = 'DsK_Toys_Full_Work_ForMassPlot_2kSample_'

@ thissample = $1

while ($thissample < $2) 
    set thissamplestr = `echo $thissample`
    rm $dir$outputprefix$thissamplestr$outputsuffix
    rm $dir$outputprefix$thissamplestr$outputsuffix.gz
    python runBsDsKMassFitterOnData.py -w --toys --filename $dir$inputprefix$thissamplestr$inputsuffix --save $dir$massplotprefix$thissamplestr$inputsuffix  --sweightoutputname $dir$sweightsprefix$thissamplestr$inputsuffix >& $dir$outputprefix$thissamplestr$outputsuffix 
    gzip $dir$outputprefix$thissamplestr$outputsuffix
    @ thissample++
    echo $thissample
end
