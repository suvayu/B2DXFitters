echo $1
echo $2
python prepareWorkspace.py --Data --debug -s $1 --configName $2
python prepareWorkspace.py --DataBkg --debug -i $1 -s $1 --configName $2
python prepareWorkspace.py --DataBkgPID --debug -i $1 -s $1 --configName $2
python prepareWorkspace.py --MC --debug -i $1 -s $1 --configName $2
python prepareWorkspace.py --MCPID --debug -i $1 -s $1 --configName $2
python prepareWorkspace.py --Signal --debug -i $1 -s $1 --configName $2
python prepareWorkspace.py --SignalPID --debug -i $1 -s $1 --configName $2
python prepareWorkspace.py --Comb --debug -i $1 -s $1 --configName $2
python prepareWorkspace.py --CombPID --debug -i $1 -s $1 --configName $2
