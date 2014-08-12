# make some things available in all modules in the package

# math
from math import (pi, log)

# ROOT: easier to call ownership fixes in methods
import ROOT

# RooFit: import namespace for convenience
from ROOT import RooFit

# Hack around RooWorkspace.import() and python keyword import clash
ws_import = getattr(ROOT.RooWorkspace, 'import')
