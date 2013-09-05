set torun = $1
@ startsample   = $2
@ endsample     = $3
@ samplesperjob = $4
if ($#argv == 5) then
    set posneg = $5
endif

set logdir = '/tmp/gligorov/log'

while ($startsample < $endsample)
    @ thisendsample = $startsample + $samplesperjob
    set logpref = `echo $startsample`
    set logsuff = `echo $thisendsample`
    if ($#argv == 5) then
        nohup source $torun $logpref $logsuff $posneg >& $logdir$torun$logpref$logsuff$posneg &
    else
        nohup source $torun $logpref $logsuff  >& $logdir$torun$logpref$logsuff &
    endif
    @ startsample += $samplesperjob
end
