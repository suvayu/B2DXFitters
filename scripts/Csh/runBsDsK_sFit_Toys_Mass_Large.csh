set dir =  '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/'

set outputprefix = 'DsK_Toys_FullLarge_MassFitResult_'
set outputsuffix = '.log'

set inputprefix = 'DsK_Toys_FullLarge_Work_'
set inputsuffix = '.root'

set sweightsprefix = 'DsK_Toys_FullLarge_sWeights_ForTimeFit_'
set massplotprefix = 'DsK_Toys_FullLarge_Work_ForMassPlot_'

@ thissample = $1

while ($thissample < $2) 
    set thissamplestr = `echo $thissample`
    rm $dir$outputprefix$thissamplestr$outputsuffix
    rm $dir$outputprefix$thissamplestr$outputsuffix.gz
    python ../runBsDsKMassFitterOnData.py -w --toys --LargeToys --filename $dir$inputprefix$thissamplestr$inputsuffix --save $dir$massplotprefix$thissamplestr$inputsuffix  --sweightoutputname $dir$sweightsprefix$thissamplestr$inputsuffix >& $dir$outputprefix$thissamplestr$outputsuffix 
    gzip $dir$outputprefix$thissamplestr$outputsuffix
    @ thissample++
    echo $thissample
end
