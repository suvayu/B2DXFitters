set diroutput = '/afs/cern.ch/work/a/adudziak/public/Bs2DsPiToys/Gamma70_5M_2T_MD/'

@ thissample = $1
@ ten = $3

set logfile = 'log_gen_'
set logfileext = '.txt'

while ($thissample < $2) 
   set thissamplestr = `echo $thissample`
   @ thissampleU = $thissample
   @ thissampleU += 1
   echo $thissampleU
   rm $diroutput$logfile$thissamplestr$logfileext 
   
   @ seed = 746829245
   @ seed += $thissample
   @ seed += $ten
   echo $seed
 
   python GenerateToySWeights_DsPi_5M.py --debug --dir $diroutput --start $thissample --end $thissampleU --seed $seed >& $diroutput$logfile$thissamplestr$logfileext
   @ thissample++  
    
   echo $thissample

end
