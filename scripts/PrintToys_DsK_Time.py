from ROOT import *
import ROOT

splitCharge = False

largeToys = False

saveplots = True

tbtd = True

nbinspull = 50
lowerpullrange = -5
upperpullrange = 5
if tbtd :
    nbinspull = 200
    lowerpullrange = -0.75
    upperpullrange = 0.75   

useavgmistag = False
avgmistagsuffix = "AvgMistag_"

ntoys               = 2000 
#ntoys               = 1000 
toysdir             = '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/DsKToys_Full_2ksample_010812/'
#toysdir             = '/afs/cern.ch/work/g/gligorov/public/Bs2DsKToys/sWeightToys/DsKToys_Full_2ksample_140912/'
toysresultprefix    = 'DsK_Toys_Full_TimeFitResult_2kSample_'
if useavgmistag : toysresultprefix += avgmistagsuffix
if largeToys    : toysresultprefix = 'DsK_Toys_FullLarge_TimeFitResult_'
toysresultsuffix    = '.log'    

additionalsuffix = ""

dmsgenera = {"C" : ntoys*[(0.757,0.)]}
dmsfitted = {"C" : ntoys*[(0,0)]}
dmsgenera["S"]    = ntoys*[(-.501,0.)]
dmsfitted["S"]    = ntoys*[(0,0)]
dmsgenera["Sbar"] = ntoys*[(0.654,0.)]
dmsfitted["Sbar"] = ntoys*[(0,0)]
dmsgenera["D"]    = ntoys*[(0.420,0.)]
dmsfitted["D"]    = ntoys*[(0,0)]
dmsgenera["Dbar"] = ntoys*[(0.0,0.)]
dmsfitted["Dbar"] = ntoys*[(0,0)]

nfailed = []

for thistoy in range(0,ntoys) :
    try :
    	print toysdir+toysresultprefix+additionalsuffix+str(thistoy)+toysresultsuffix
        f = open(toysdir+toysresultprefix+additionalsuffix+str(thistoy)+toysresultsuffix)
    except :
        print 'Toy number',thistoy,'failed to converge properly!'
        nfailed.append(thistoy)
        continue
    counter = 0 
    counterstop = -100
    secondcount = False
    badfit = False
    for line in f :
        counter += 1
        if line.find('MIGRAD=4') > -1 :
            print 'Toy number',thistoy,'failed to converge properly!'
            break
        if line.find('NOT POS-DEF') > -1 :
            badfit = True
        if line.find('ERROR MATRIX ACCURATE') > -1 :
            badfit = False
        if line.find('FinalValue') >  -1 : 
            #print line
            if badfit : 
	    	print "Toy number",thistoy,"is bad."
		break
            if counterstop > -100 :
                secondcount = True
            counterstop = counter
        if not splitCharge :
            if counter == counterstop + 2 :
                result = line.split()
                dmsfitted["C"][thistoy] =  (float(result[2]), float(result[4]))
            if counter == counterstop + 3 : 
                result = line.split()
                dmsfitted["D"][thistoy] =  (float(result[2]), float(result[4]))
            if counter == counterstop + 4 : 
                result = line.split()
                dmsfitted["Dbar"][thistoy] =  (float(result[2]), float(result[4]))
            if counter == counterstop + 5 : 
                result = line.split()
                dmsfitted["S"][thistoy] =  (float(result[2]), float(result[4]))
            if counter == counterstop + 6 : 
                result = line.split()
                dmsfitted["Sbar"][thistoy] =  (float(result[2]), float(result[4]))
                break
        else :
            if not secondcount and counter == counterstop + 2 : 
                result = line.split()
                dmsfitted["C"][thistoy] =  (float(result[2]), float(result[4]))
            if not secondcount and counter == counterstop + 3 :
                result = line.split()
                dmsfitted["D"][thistoy] =  (float(result[2]), float(result[4]))
            if not secondcount and counter == counterstop + 4 :
                result = line.split()
                dmsfitted["Sbar"][thistoy] =  (float(result[2]), float(result[4]))
            if secondcount and counter == counterstop + 2 : 
                result = line.split()
                dmsfitted["C"][thistoy] =  ((float(result[2])+dmsfitted["C"][thistoy][0])/2.,dmsfitted["C"][thistoy][1]/sqrt(2.))
            if secondcount and counter == counterstop + 3 : 
                result = line.split()
                dmsfitted["Dbar"][thistoy] =  (float(result[2]), float(result[4]))
            if secondcount and counter == counterstop + 4 : 
                result = line.split()
                dmsfitted["S"][thistoy] =  (float(result[2]), float(result[4]))
                break
    if counterstop == -100 :
        nfailed.append(thistoy)
    f.close()


def printVar(varCpp, var, valOrErr):
	print "float %s [] = {" %varCpp,
	first = 0
	for thistoy in range(0,ntoys) :
		if dmsfitted["C"][thistoy][1] == 0: continue
		if dmsfitted["D"][thistoy][1] == 0: continue
		if dmsfitted["Dbar"][thistoy][1] == 0: continue
		if dmsfitted["S"][thistoy][1] == 0: continue
		if dmsfitted["Sbar"][thistoy][1] == 0: continue
		if ( first>0 ) : print ",",
		print "%5.2f" % dmsfitted[var][thistoy][valOrErr],
		first += 1
		if ( first%10==0 ) : print
	print "};"
	print " // %i" % first

printVar("s", "S", 0);
printVar("sb", "Sbar", 0);
printVar("d", "D", 0);
printVar("db", "Dbar", 0);
printVar("c", "C", 0);

print

printVar("es", "S", 1);
printVar("esb", "Sbar", 1);
printVar("ed", "D", 1);
printVar("edb", "Dbar", 1);
printVar("ec", "C", 1);
