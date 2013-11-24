set dirinput =  '/afs/cern.ch/work/a/adudziak/public/Bs2DsKToys/Gamma70_5M_2T/'
set diroutput = '/afs/cern.ch/work/a/adudziak/public/Bs2DsKToys/Gamma70_5M_2T/'

set outputprefix = 'DsK_Toys_MassFitResult_'
set outputsuffix = '.log'

set inputprefix = 'DsK_Toys_Work_'
set inputsuffix = '.root'

set sweightsprefix = 'DsK_Toys_sWeights_ForTimeFit_'
set massplotprefix = 'DsK_Toys_Work_ForMassPlot_'

@ thissample = $1

while ($thissample < $2) 
    set thissamplestr = `echo $thissample`
    rm $diroutput$outputprefix$thissamplestr$outputsuffix
    rm $diroutput$outputprefix$thissamplestr$outputsuffix.gz
    python runBsDsKMassFitterOnData3D5M.py --debug --merge -m both -o all --configName Bs2DsKConfigForNominalMassFitToys5M --fileName work_dsk_pid_53005800_PIDK5_5M_BDTGA_3.root --fileNameToys $dirinput$inputprefix$thissamplestr$inputsuffix --sweightoutputname $diroutput$sweightsprefix$thissamplestr$inputsuffix --save $diroutput$massplotprefix$thissamplestr$inputsuffix --sweight >& $diroutput$outputprefix$thissamplestr$outputsuffix 
    gzip $diroutput$outputprefix$thissamplestr$outputsuffix
    @ thissample++
    echo $thissample
end
