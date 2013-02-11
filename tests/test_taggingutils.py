#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to test the taggingutils module                             #
#                                                                             #
#   Example usage:                                                            #
#      ./test_taggingutils.py                                                 #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 09 / 06 / 2011                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #

from ROOT                     import RooCategory, RooRealVar
from B2DXFitters.taggingutils import tagEfficiencyWeight


mixState = RooCategory( 'mixstate', 'B/Bbar -> D pi mixing state' )
mixState.defineType( "unmixed" ,  1 )
mixState.defineType( "mixed"   , -1 )
mixState.defineType( "untagged",  0 )

SigTagEff =  0.25
sigTagEff = RooRealVar( "sigTagEff", "Signal tagging efficiency",
                        SigTagEff, 0., 1. )

sigTagWeight = tagEfficiencyWeight( mixState, sigTagEff, 'Bd2DPi' )

sigTagWeight.Print( 'v' )

print '\ntafEff =', sigTagEff.getVal()
mixState.setIndex(0)
print 'mixState = %2d  =>  tagWeight = %f' % \
      ( mixState.getIndex(), sigTagWeight.getVal() )
mixState.setIndex(1)
print 'mixState = %2d  =>  tagWeight = %f' % \
      ( mixState.getIndex(), sigTagWeight.getVal() )
mixState.setIndex(-1)
print 'mixState = %2d  =>  tagWeight = %f' % \
      ( mixState.getIndex(), sigTagWeight.getVal() )
