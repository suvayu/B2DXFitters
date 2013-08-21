# --------------------------------------------------------------------------- #
#                                                                             #
#   Python helper module for tagging                                          #
#                                                                             #
#                                                                             #
#   Authors: Eduardo Rodrigues                                                #
#   Date   : 09 / 06 / 2011                                                   #
#                                                                             #
# --------------------------------------------------------------------------- #

# -----------------------------------------------------------------------------
# Import statements
# -----------------------------------------------------------------------------
import B2DXFitters, os, sys
import ROOT
from ROOT import RooFit


# -----------------------------------------------------------------------------
# Values of the head_TAGGER variable as stored by TupleToolTagging
# -----------------------------------------------------------------------------
Tagger_none         = 0
Tagger_unknown      = 1
Tagger_OS_Muon      = 2
Tagger_OS_Electron  = 3
Tagger_OS_Kaon      = 4
Tagger_SS_Kaon      = 5
Tagger_SS_Pion      = 6
Tagger_jetCharge    = 7
Tagger_OS_jetCharg  = 8
Tagger_SS_jetCharge = 9
Tagger_VtxCharge    = 10
Tagger_Topology     = 11

# =============================================================================
# The 4 coefficients of the B decay rate equations
# weight = |q|*eff_tag + (1-|q|)*(1-eff_tag)
#        = 1 - eff_tag for untagged events (q=0)
#        = eff_tag     for tagged   events (q=+/-1)
# where
#    q = tagState is the tagging value (RooAbsCategory)
#    eff_tag = tagEfficiency is the tagging efficiency (RooAbsReal)
# =============================================================================
def tagEfficiencyWeight( tagState, tagEfficiency, prefix = 'Sig' ) :
    tagEffWeight = TagEfficiencyWeight(
	    '%sTagEffWeight' % prefix,
	    "'%s' tag efficiency weight" % prefix,
	    tagState, tagEfficiency)
    return tagEffWeight

# =============================================================================
