from ROOT import gROOT, TCanvas
from ROOT import RooRealVar, RooArgSet, RooFit


gROOT.SetStyle( 'Plain' )    
gROOT.SetBatch( False )

import GaudiPython
GaudiPython.loaddict( 'B2DXFittersDict' )

GeneralModels = GaudiPython.gbl.GeneralModels

mass = RooRealVar( 'mass', 'mass', 5366, 4800, 5850, 'MeV/c^{2}' )

nBs2DsPiEvts = RooRealVar( 'nBs2DsPiEvts', 'nBs2DsPiEvts', 7000., 0., 10000. )

mepdfBs2DsPi = GeneralModels.buildDoubleCBEPDF( mass, 5366,
                                                40, 1.4, 1.2,
                                                25, -1.05, 1.35,
                                                0.6,
                                                nBs2DsPiEvts,
                                                'Bs2DsPi', 'Bs',
                                                True
                                                )

mepdfBs2DsPi.Print( 't' )

data = mepdfBs2DsPi.generate( RooArgSet(mass) )

fr = mass.frame()

data.plotOn( fr )

mepdfBs2DsPi.plotOn( fr )
mepdfBs2DsPi.paramOn( fr,
                      RooFit.ShowConstants(),
                      RooFit.Layout( 0.6, 0.90, 0.85 ),
                      RooFit.Format( 'NEU', RooFit.AutoPrecision( 2 ) )
                      )

pt = fr.findObject( 'mepdfBs2DsPi_paramBox' )
if pt :
  pt.SetTextSize( 0.02 )
  pt.SetY1NDC( 0.40 )

fr.SetTitle( 'Double DB in mass' )

fr.Draw()
