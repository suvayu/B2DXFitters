set dir =  '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/'

set outputprefix = 'DsPi_Toys_Full_MassFitResult_'
set outputsuffix = '.log'

set inputprefix = 'DsPi_Toys_Full_Work_'
set inputsuffix = '.root'

set sweightsprefix = 'DsPi_Toys_Full_sWeights_ForTimeFit_'
set massplotprefix = 'DsPi_Toys_Full_Work_ForMassPlot_'

@ thissample = $1

while ($thissample < $2) 
    set thissamplestr = `echo $thissample`
    rm $dir$outputprefix$thissamplestr$outputsuffix
    rm $dir$outputprefix$thissamplestr$outputsuffix.gz
    python ../runBsDsPiMassFitterOnData.py --toys --filename $dir$inputprefix$thissamplestr$inputsuffix --save $dir$massplotprefix$thissamplestr$inputsuffix  --sweightoutputname $dir$sweightsprefix$thissamplestr$inputsuffix >& $dir$outputprefix$thissamplestr$outputsuffix 
    gzip $dir$outputprefix$thissamplestr$outputsuffix
    @ thissample++
    echo $thissample
end
