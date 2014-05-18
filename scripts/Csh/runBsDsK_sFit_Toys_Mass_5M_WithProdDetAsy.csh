set dirinput =  '/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/For1fbPaper/Gamma70_WProdDetAsy_NoKFactors_5M_2T_MD/GeneratorOutput/'
set diroutput = '/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/For1fbPaper/Gamma70_WProdDetAsy_NoKFactors_5M_2T_MD/MassFitResults/Nominal/'
set sweightsdiroutput = '/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/For1fbPaper/Gamma70_WProdDetAsy_NoKFactors_5M_2T_MD/sWeightsForTimeFit/Nominal/'

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
    python runBsDsKMassFitterOnData3D5M.py --merge -m both -o all --configName Bs2DsKConfigForNominalMassFitToys5M --fileName /afs/cern.ch/work/a/adudziak/public/workspace/DsKNoteV11/work_dsk_pid_53005800_PIDK5_5M_BDTGA_4.root --fileNameToys $dirinput$inputprefix$thissamplestr$inputsuffix --sweightoutputname $sweightsdiroutput$sweightsprefix$thissamplestr$inputsuffix --save $diroutput$massplotprefix$thissamplestr$inputsuffix --sweight >& $diroutput$outputprefix$thissamplestr$outputsuffix 
    gzip $diroutput$outputprefix$thissamplestr$outputsuffix
    @ thissample++
    echo $thissample
end
