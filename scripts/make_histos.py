import os, sys
from math import sqrt, pi
from glob import glob
from math import sqrt, pi

EXT = '.pdf'
fnames = glob('fitresult_[0-9][0-9][0-9][0-9].root')
exclude = []

# Load PyROOT
# -----------
pyrootpath = os.environ[ 'ROOTSYS' ]

if os.path.exists(pyrootpath):
   sys.path.append(pyrootpath + os.sep + 'bin')
   sys.path.append(pyrootpath + os.sep + 'lib')
   import ROOT
   print 'PyROOT is loaded.'
else:
   print 'Unable to find ROOT! Nothing done.'
   sys.exit(0)

from ROOT import gROOT, TFile, TH1D
from ROOT import gDirectory, TStyle, TF1, TFile, TCanvas, gROOT
ROOT.SetMemoryPolicy(ROOT.kMemoryStrict)
gROOT.SetBatch(True)

# ----------------------------------------------------------------------------
def getRooFitResultObjects(filenames, exclude):
    from ROOT import RooFitResult
    rooFitResults = []
    for fname in filenames:
        num = number_exp(fname)
        if num in exclude:
	    print 'Experiment #%d excluded!' % num
            continue
        f = TFile(fname, 'READ')
        for key in f.GetListOfKeys():
	    obj = key.ReadObj()
	    ROOT.SetOwnership(obj, True)
	    if obj.InheritsFrom('RooFitResult'):
                if 0 == obj.status() and 3 == obj.covQual():
                    obj = obj.Clone()
		    ROOT.SetOwnership(obj, True)
		    rooFitResults.append(obj)
                else:
		    print 'Experiment #%d excluded based on fit quality!' % num
            del obj
	del f
    return rooFitResults

# ----------------------------------------------------------------------------
def printMinuitQuality() :
   for r in rooFitResults:
      print r.status(), r.covQual()
      print res.Print()
      print '##############################################################'

# ----------------------------------------------------------------------------
def get_vars_names(res):
   params = res.floatParsFinal()
   size = params.getSize()
   vnames = []
   for i in range(size):
      vnames.append(params.at(i).GetName())
   return vnames

# ----------------------------------------------------------------------------
def get_vars_initvals(res):
   initvals   = dict()
   initparams = res.floatParsInit()
   for i in range(initparams.getSize()):
      param = initparams.at(i)
      initvals[ param.GetName() ] = param.getVal()
   return initvals

# ----------------------------------------------------------------------------
def rad2deg(angle):
   return angle * 180. / pi

# ----------------------------------------------------------------------------
def number_exp(file):
   imin = file.find('_')
   imax = file.find('.')
   id   = file[imin+1:imax]
   return int(id)

# ----------------------------------------------------------------------------

fitresults = getRooFitResultObjects(fnames, exclude)
NTOYSGOOD = len(fitresults)

vals = dict()
errs = dict()
vnames = get_vars_names(fitresults[0])
print '--> variable names:', vnames
initvals = get_vars_initvals(fitresults[0])
for name in vnames:
   vals[name] = []
   errs[name] = []

for obj in fitresults:
    params = obj.floatParsFinal()
    for name in vnames:
        vals[ name ].append(params.find(name).getVal())
        errs[ name ].append(params.find(name).getError())
        #print '* %s :' % name
        #print '  %f +/- %f' % (params.find(name).getVal(),
        #                        params.find(name).getError())
        #print 20*'#'
print '-->', len(fnames), 'files analysed,', len(exclude), 'excluded.\n'

# temporary variable to contain histos to be written out to a ROOT file
# (i.e. histos for the floating parameters)
all_histos = []
histos = { }

for name in vnames:
   from math import sqrt
   print 'Figure out ranges for variable ', name, '...'
   values = vals[ name ]
   errors = errs[ name ]
   v = 0.
   p = 0.
   n = 0.
   np = 0.
   for i in range(len(values)) :
      val = values[i]
      err = errors[i]
      if val != val or (abs(val) > 1. and abs(1. / val) == 0.):
	  continue
      v = v * (n / (n + 1.0)) + val / (n + 1.)
      n = n + 1.
      if err != err or (abs(err) > 1. and abs(1. / err) == 0.) or err <= 0.:
	  continue
      pull = (val - initvals[name]) / err
      if abs(pull) > 5.:
        continue
      p = p * (np / (np + 1.0)) +  pull / (np + 1.)
      np = np + 1.
   v2 = 0.
   p2 = 0.
   n = 0.
   np = 0.
   for i in range(len(values)) :
      val = values[i]
      err = errors[i]
      if val != val or (abs(val) > 1. and abs(1. / val) == 0.):
	  continue
      v2 = v2 * (n / (n + 1.0)) + (val - v) * (val - v) / (n + 1.)
      n = n + 1.
      if err != err or (abs(err) > 1. and abs(1. / err) == 0.) or err <= 0.:
	  continue
      pull = (val - initvals[name]) / err
      if abs(pull) > 5.:
        continue
      p2 = p2 * (np / (np + 1.0)) +  (pull - p) * (pull - p) / (np + 1.)
      np = np + 1.
   sigmav = sqrt(v2)
   sigmap = sqrt(p2)
   hv = TH1D('%s value' % name, '%s value' % name,
	   50, v - 3. * sigmav, v + 3. * sigmav)
   hp = TH1D('%s pull' % name, '%s pull' % name,
	       50, p - 3. * sigmap, p + 3. * sigmap)
   histos[name] = [hv, hp]
   all_histos.append(hv)
   all_histos.append(hp)

for name in vnames:
   h = histos[ name ]
   if not (h[0] and h[1]) : continue
   print 'Filling the fit values and pull histograms for the variable', name, '...'
   values = vals[ name ]
   errors = errs[ name ]
   for i in range(len(values)) :
      val = values[i]
      err = errors[i]
      h[0].Fill(val)
      if abs(err) > 1.e-9:
         h[1].Fill((val - initvals[name]) / err)
      else:
         print 'WARNING: skipped entry in pull dist. of', name,\
               'error =', err
   print '... done.'

if 'C' in vals and 'S' in vals and 'D' in vals:
    print 'Filling the histogram for |C|^2+|S|^2+|D|^2 ...'
    h_sum = TH1D('|C|^2+|S|^2+|D|^2 values', '|C|^2+|S|^2+|D|^2',
                  30, 0.0, 0.0)
    all_histos.append(h_sum)
    for i in range(len(vals[ 'C' ])):
       val_c = vals[ 'C' ][i]
       val_s = vals[ 'S' ][i]
       val_d = vals[ 'D' ][i]
       h_sum.Fill(val_c*val_c + val_s*val_s + val_d*val_d)
    print '... done.'

if 'C' in vals and 'Sbar' in vals and 'Dbar' in vals:
    print 'Filling the histogram for |C|^2+|Sbar|^2+|Dbar|^2 ...'
    h_sum2 = TH1D('|C|^2+|Sbar|^2+|Dbar|^2 values', '|C|^2+|Sbar|^2+|Dbar|^2',
                   30, 0.0, 0.0)
    all_histos.append(h_sum2)
    for i in range(len(vals[ 'C' ])):
       val_c = vals[ 'C' ][i]
       val_s = vals[ 'Sbar' ][i]
       val_d = vals[ 'Dbar' ][i]
       h_sum2.Fill(val_c*val_c + val_s*val_s + val_d*val_d)
    print '... done.'

print 'Saving a RooFitResult to store the initial values of the fitted parameters ...'
resfile = TFile('results.root', 'RECREATE')
resfile.WriteTObject(fitresults[0])
print '... done.'

print 'Saving all histograms to results.root ...'
for histo in all_histos:
   histo.Write()
print '... done.'

del resfile

def rootSettings():	
   ROOT.gROOT.SetStyle('Plain')
   ROOT.gStyle.SetCanvasColor(0)
   ROOT.gStyle.SetPadColor(0)
   ROOT.gStyle.SetMarkerColor(0)
   ROOT.gStyle.SetOptStat(111111)
   ROOT.gStyle.SetOptFit(111)
   ROOT.gROOT.ForceStyle()

# ----------------------------------------------------------------------------
def fit_histo(h):
   if h.GetEntries() <= 0.:
      return
   m = h.GetMaximum()
   gaussian = TF1('Gaussian', 'gaus')
   gaussian.SetParameters(m, h.GetMean(), h.GetRMS())
   gaussian.SetLineColor(ROOT.kBlue)
   h.Fit(gaussian, 'ILQ')

# ----------------------------------------------------------------------------
def plot_and_fit_histos(fitvars, evalvars, pullvars):
   from ROOT import gDirectory
   keys = gDirectory.GetListOfKeys()
   for k in keys:
      obj = k.ReadObj()
      if (obj.IsA().InheritsFrom('TH1')) :
         name = obj.GetName()
         print 'Fitting histo "', name, '" ...'
         fit_histo(obj)
         if 'Gamma' in name:
            make_eval_vars(obj, evalvars)
         elif 'pull' in name:
            make_pull_vars(obj, pullvars)
         else:
            make_fit_vars(obj, fitvars)
         print 'Drawing histo "', name, '" ...'
	 obj.SetMarkerColor(ROOT.kBlack)
         obj.SetMarkerStyle(21)
         if ('Gamma' in name) :
            obj.GetXaxis().SetTitle('Evaluated ' + name)
         else:
            obj.GetXaxis().SetTitle('Fitted ' + name)
         obj.GetYaxis().SetTitle('# of toys')
         obj.SetTitle('')
         obj.Draw('E1')
         c.Update()
         stats = obj.GetListOfFunctions().FindObject('stats')
         line = stats.GetLine(0)
         #if '|' in line.GetTitle():
         #print 'line=', line.GetTitle()
         line.SetTitle('')
         stats.Draw()
         obj.GetListOfFunctions().Add(stats)
         stats.SetParent(obj.GetListOfFunctions())
         #obj.GetListOfFunctions().FindObject('stats').Print()
         stats.SetOptStat(111111)
         stats.Draw()
         c.Modified()
         if ('Gamma' in name) or ('Delta' in name) :
            name = name.replace('/', '')
            name = name.replace('^', '')
            name = name.replace('(', '')
            name = name.replace(')', '')
            name = name.replace('.', '')
            name = name.replace('>=', 'ge')
            name = name.replace('=', 'eq')
            name = name.replace('+', 'plus')
            name = name.replace('-', 'minus')
            name = name.replace(', ', '-')
            c.Print(name.replace(' ', '_') + EXT)
         else:
            name = name.replace('|', '')
            name = name.replace('^', '')
            name = name.replace('+', 'plus')
            name = name.replace('(', '_')
            name = name.replace(')', '')
            c.Print(name.replace(' ', '_') + EXT)

# ----------------------------------------------------------------------------
def make_fit_vars(h, fitvars):
   title = h.GetName().replace(' value', '')
   func  = h.GetFunction('Gaussian')
   mean  = func.GetParameter(func.GetParNumber('Mean'))
   sig   = func.GetParameter(func.GetParNumber('Sigma'))
   meanerr  = func.GetParError(func.GetParNumber('Mean'))
   sigerr   = func.GetParError(func.GetParNumber('Sigma'))
   initparams = get_vars_initvals(fitresults[0])
   if title in initparams and h.GetEntries() > 0.:
      fitvars[ title ] = [
         initparams[title], mean, sig, meanerr, sigerr]

# ----------------------------------------------------------------------------
def make_eval_vars(h, evalvars):
   title = h.GetName()
   func  = h.GetFunction('Gaussian')
   mean  = func.GetParameter(func.GetParNumber('Mean'))
   sig   = func.GetParameter(func.GetParNumber('Sigma'))
   initparams = get_vars_initvals(fitresults[0])
   val_l    = initparams['arg_lam'].getVal()
   val_lbar = initparams['arg_lam_bar'].getVal()
   delta = rad2deg(0.5 * (val_l + val_lbar))
   gamma = rad2deg(0.5 * (val_lbar - val_l))
   initvals = { 'Delta': delta, 'Gamma+phi_s': gamma }
   evalvars[ title ] = (initvals[ title ], mean, sig)

# ----------------------------------------------------------------------------
def make_pull_vars(h, pullvars):
   if h.GetEntries() <= 0.:
      return
   title = h.GetName().replace(' pull', '')
   func  = h.GetFunction('Gaussian')
   mean  = func.GetParameter(func.GetParNumber('Mean'))
   sig   = func.GetParameter(func.GetParNumber('Sigma'))
   meanerr = func.GetParError(func.GetParNumber('Mean'))
   sigerr  = func.GetParError(func.GetParNumber('Sigma'))
   pullvars[ title ] = (mean, sig, meanerr, sigerr)

# ----------------------------------------------------------------------------
def print_const_vars(rootfile):
   res         = fitresults[0]
   if None == res:
      return
   constparams = res.constPars()
   print ''
   print '--------------', ' ----------', ' ------------------------------------'
   print ('%14s %11s %s') % ('Const variable', '     Value', ' Description')
   print '--------------', ' ----------', ' ------------------------------------'
   for i in range(constparams.getSize()):
      param = constparams.at(i)
      print('%14s %11.2f  %s')\
             % (param.GetName(), param.getVal(), param.GetTitle())
      print '--------------', ' ----------', ' ------------------------------------'
   print ''
   f.Close()

# ----------------------------------------------------------------------------
def rad2deg(angle):
   return angle * 180. / pi

# ----------------------------------------------------------------------------
    
rootfile = 'results.root'

if os.path.isfile(rootfile):
   from ROOT import TCanvas
   rootSettings()
   f = TFile(rootfile, 'READ')
   c = TCanvas()
   fitvars  = dict()
   evalvars = dict()
   pullvars = dict()
   plot_and_fit_histos(fitvars, evalvars, pullvars)
   print pullvars
   #command =   'gzip -f *.eps'
   #os.system(command)

   print_const_vars(rootfile)
   
   print 'Values: %16s %12s %12s %12s %12s %12s' % \
      ('parameter', 'initial', 'mean', 'mean error', 'precision', 'prec. error')
   print '-----------------------------------------------------------------------------------------'
   for key, val in sorted(fitvars.iteritems()):
      print '%24s %12.5g %12.5g %12.5g %12.5g %12.5g' % \
         (key, val[0], val[1], val[3], val[2], val[4])
   print ''
   print 'Pulls: %17s %12s %12s %12s %12s' % \
      ('parameter', 'mean', 'mean error', 'sigma', 'sigma error')
   print '----------------------------------------------------------------------------'
   for key, val in sorted(pullvars.iteritems()):
      print '%24s %12.5g %12.5g %12.5g %12.5g' % \
         (key, val[0], val[2], val[1], val[3])
   print ''


   print '------------', ' -----------', '  ----------------------'
   for key, val in sorted(evalvars.iteritems()) :
      print('%12s %12.3f %11.3f  +/-  %5.3f')\
             % (key, val[0], val[1], val[2])
   print '------------', ' -----------', '  ----------------------'
   print ''
   print 'Used %d toys' % NTOYSGOOD
   print ''

   print 'Done.'
else:
   print 'File ' + rootfile + ' not found! Nothing done.'
    
# =============================================================================


print 'All done!'

