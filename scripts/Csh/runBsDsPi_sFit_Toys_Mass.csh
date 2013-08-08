set dirinput =  '/afs/cern.ch/work/a/adudziak/public/Bs2DsPiToys/'
set diroutput = '/afs/cern.ch/work/a/adudziak/public/Bs2DsPiToys/'

set outputprefix = 'DsPi_Toys_MassFitResult_'
set outputsuffix = '.log'

set inputprefix = 'DsPi_Toys_Work_'
set inputsuffix = '.root'

set sweightsprefix = 'DsPi_Toys_sWeights_ForTimeFit_'
set massplotprefix = 'DsPi_Toys_Work_ForMassPlot_'

@ thissample = $1

while ($thissample < $2) 
    set thissamplestr = `echo $thissample`
    rm $diroutput$outputprefix$thissamplestr$outputsuffix
    rm $diroutput$outputprefix$thissamplestr$outputsuffix.gz
    python runBsDsPiMassFitterOnData3D5M.py --sweight --merge -m both -o phipi --configName Bs2DsPiConfigForNominalMassFitToys --fileNameToys $dirinput$inputprefix$thissamplestr$inputsuffix --fileName /afs/cern.ch/work/a/adudziak/public/workspace/MDFitter/work_dspi_pid_53005800_PIDK0_5M_BDTGA.root --sweightoutputname $diroutput$sweightsprefix$thissamplestr$inputsuffix >& $diroutput$outputprefix$thissamplestr$outputsuffix
    gzip $diroutput$outputprefix$thissamplestr$outputsuffix
    @ thissample++
    echo $thissample
end
