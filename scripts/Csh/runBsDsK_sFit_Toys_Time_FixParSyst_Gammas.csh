set dirinput = '/afs/cern.ch/work/a/adudziak/public/Bs2DsKToys/Gamma70_5M/'
set diroutput = '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/Systematics/Gammas_'
set diroutputsuffix = "/" 

set outputprefix = 'DsK_Toys_TimeFitResult_FixParSyst_Gammas_'
set outputsuffix = '.log'

set inputprefix = 'DsK_Toys_sWeights_ForTimeFit_'
set inputsuffix = '.root'

set configname = 'Bs2DsKConfigForFixedParamSyst_Gammas_'

set posorneg = $3
set diroutput = $diroutput$posorneg$diroutputsuffix
set outputprefix = $outputprefix$posorneg"_"
set configname = $configname$posorneg

@ thissample = $1

while ($thissample < $2) 
    set thissamplestr = `echo $thissample`
    rm $diroutput$outputprefix$thissamplestr$outputsuffix
    rm $diroutput$outputprefix$thissamplestr$outputsuffix.gz
    python ../runBs2DsKCPAsymmObsFitterOnData.py --toys --pereventmistag --cat --configName $configname --pathName $dirinput$inputprefix$thissamplestr$inputsuffix >& $diroutput$outputprefix$thissamplestr$outputsuffix 
    #gzip $diroutput$outputprefix$thissamplestr$outputsuffix
    @ thissample++
    echo $thissample
end

