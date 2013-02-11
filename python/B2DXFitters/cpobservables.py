# --------------------------------------------------------------------------- #
#                                                                             #
#   Python module to deal with CP observables                                 #
#                                                                             #
#                                                                             #
#   Authors: Eduardo Rodrigues                                                #
#   Date   : 15 / 06 / 2011                                                   #
#                                                                             #
# --------------------------------------------------------------------------- #

# -----------------------------------------------------------------------------
# Import statements
# -----------------------------------------------------------------------------
from math import sin, cos


# =============================================================================
# Class to calculate the CP asymmetry observables starting from the
# imaginary lambda and lambda_bar quantities
# 
# Note:
#   1. | lambdaf | = | lambdabarfbar |
#   2. Arguments in radians
# =============================================================================
class AsymmetryObservables :
   def __init__( self, lambdaf_arg, lambdabarfbar_arg, lambda_mod ) :
      self.lambdaf_arg = lambdaf_arg
      self.lambdabarfbar_arg = lambdabarfbar_arg
      self.lambda_mod = lambda_mod
      self.denom = 1. + self.lambda_mod * self.lambda_mod
   
   def Cf( self ) :
      return ( 1. - self.lambda_mod * self.lambda_mod ) / self.denom
   
   def Sf( self ) :
      return 2. * self.lambda_mod * sin( self.lambdaf_arg ) / self.denom
   
   def Df( self ) :
      return 2. * self.lambda_mod * cos( self.lambdaf_arg ) / self.denom
   
   def Sfbar( self ) :
      return 2. * self.lambda_mod * sin( self.lambdabarfbar_arg ) / self.denom
   
   def Dfbar( self ) :
      return 2. * self.lambda_mod * cos( self.lambdabarfbar_arg ) / self.denom
   
   def Af_dir( self ) :
      """Af_dir = Cf"""
      return self.Cf()
   
   def Af_mix( self ) :
      """Af_mix = Sf"""
      return self.Sf()
   
   def Af_DeltaGamma( self ) :
      """Af_DeltaGamma = Df"""
      return self.Df()
   
   def Afbar_mix( self ) :
      """Afbar_mix = Sfbar"""
      return self.Sfbar()
   
   def Afbar_DeltaGamma( self ) :
      """Afbar_DeltaGamma = Dfbar"""
      return self.Dfbar()
   
   def printtable( self, mode = None ) :
      if None == mode:
	  mode = ''
      print 58*'-'
      print '%16s %7s %7s %7s %7s %7s' % ( 'mode', 'Cf', 'Sf', 'Df', 'Sfbar', 'Dfbar' )
      print 58*'-'
      print '%16s %7.3f %7.3f %7.3f %7.3f %7.3f' % \
            ( mode, self.Cf(), self.Sf(), self.Df(), self.Sfbar(), self.Dfbar() )
      print 58*'-'

# =============================================================================
