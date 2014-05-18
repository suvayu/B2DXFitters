set diroutput = '/afs/cern.ch/work/g/gligorov//public/Bs2DsKToys/For1fbPaper/Gamma70_WProdDetAsy_NoKFactors_5M_2T_MD/GeneratorOutput/'
set configfile = 'Bs2DsKConfigForGenerator5M_WithProdDetAsy'

@ thissample = $1
@ ten = 100

set logfile = 'log_gen_'
set logfileext = '.txt'

@ seed = $3

while ($thissample < $2) 
   set thissamplestr = `echo $thissample`
   @ thissampleU = $thissample + 1
   echo $thissample
   echo $thissampleU
   
   @ seed += $ten
   echo $seed

   rm $diroutput$logfile$thissamplestr$logfileext 
 
   python GenerateToySWeights_DsK_5M.py --configName $configfile --dir $diroutput --start $thissample --end $thissampleU --seed $seed >& $diroutput$logfile$thissamplestr$logfileext
   @ thissample++  

end
