@ startsample   = $1
@ endsample     = $2
@ samplesperjob = $3

set logdir = '/tmp/gligorov/log'

while ($startsample < $endsample)
    @ thisendsample = $startsample + $samplesperjob
    set logpref = `echo $startsample`
    set logsuff = `echo $thisendsample`
    nohup source runBsDsK_sFit_Toys_Time_FixParSyst_Acceptance_Offset.csh $logpref $logsuff >& $logdir$logpref$logsuff &
    @ startsample += $samplesperjob
end
