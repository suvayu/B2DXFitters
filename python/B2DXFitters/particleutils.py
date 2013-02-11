# --------------------------------------------------------------------------- #
#                                                                             #
#   Python helper module with particle properties and related info            #
#                                                                             #
#                                                                             #
#   Authors: Eduardo Rodrigues                                                #
#   Date   : 25 / 11 / 2011                                                   #
#                                                                             #
# --------------------------------------------------------------------------- #

# -----------------------------------------------------------------------------
# All particle masses in MeV
# -----------------------------------------------------------------------------
MassD  = 1869.60
MassDs = 1968.47
MassBd = 5279.50
MassBs = 5366.3
MassLb = 5620.2
MassLc = 2286.46
MassP  = 938.27
MassPi = 139.57
MassK  = 493.677

# D, Ds, B and Bs signal regions
SigRegionD  = ( 1844., 1890. )
SigRegionDs = ( 1944., 1990. )
SigRegionBd = ( 5180., 5325. )
SigRegionBs = ( 5300., 5420. )

# Mass peak shifts observed in the data for magnet up/down
MassShiftOnData = { 'up'   : -7.1 ,
                    'down' : -7.1
                    }
# Extra shift for the Lb to be applied on top of massShiftOnData
LbExtraMassShiftOnData = { 'up'   : -2.3 ,
                           'down' : -2.3
                           }

# -----------------------------------------------------------------------------
# Decay names in LaTex
# -----------------------------------------------------------------------------
DecayName = { 'Bd2DPi'  : '\\ensuremath{B^0   \\to D^\\pm   \\pi^\\mp\\,}' ,
              'Bs2DsPi' : '\\ensuremath{B^0_s \\to D_s^\\pm \\pi^\\mp\\,}' ,
              'Bs2DsK'  : '\\ensuremath{B^0_s \\to D_s^\\pm K^\\mp\\,}'
              }

# =============================================================================
