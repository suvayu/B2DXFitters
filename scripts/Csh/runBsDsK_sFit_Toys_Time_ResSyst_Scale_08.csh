set dir =  '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/'

set outputprefix = 'DsK_Toys_Full_TimeFitResult_2kSample_ResSyst_Scale_08_'
set outputsuffix = '.log'

set inputprefix = 'DsK_Toys_Full_sWeights_ForTimeFit_2kSample_'
set inputsuffix = '.root'

@ thissample = $1

while ($thissample < $2) 
    set thissamplestr = `echo $thissample`
    rm $dir$outputprefix$thissamplestr$outputsuffix
    rm $dir$outputprefix$thissamplestr$outputsuffix.gz
    python ../runBs2DsKCPAsymmObsFitterOnData.py --toys --pereventmistag --configName Bs2DsKConfigForResSyst_Scale_08 --pathToys $dir$inputprefix$thissamplestr$inputsuffix >& $dir$outputprefix$thissamplestr$outputsuffix 
    gzip $dir$outputprefix$thissamplestr$outputsuffix
    @ thissample++
    echo $thissample
end
