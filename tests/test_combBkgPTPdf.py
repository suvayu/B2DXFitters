from ROOT import gROOT, TCanvas
from ROOT import RooRealVar, RooArgSet, RooFit


gROOT.SetStyle( 'Plain' )
gROOT.SetBatch( False )

import GaudiPython
GaudiPython.loaddict( 'B2DXFittersDict' )
from ROOT import CombBkgPTPdf


# Parameters for the combinatorial background PDF in time
CombBkgPdf_a      =  0.1209
CombBkgPdf_f      =  0.996
CombBkgPdf_alpha  =  4.149
CombBkgPdf_beta   =  1.139


time = RooRealVar( 'time', 'time', 0., 10., 'ps' )

combBkgPdf_a     = RooRealVar( 'CombBkgPdf_a'    , 'CombBkgPdf_a'    , CombBkgPdf_a     )
combBkgPdf_f     = RooRealVar( 'CombBkgPdf_f'    , 'CombBkgPdf_f'    , CombBkgPdf_f     )
combBkgPdf_alpha = RooRealVar( 'CombBkgPdf_alpha', 'CombBkgPdf_alpha', CombBkgPdf_alpha )
combBkgPdf_beta  = RooRealVar( 'CombBkgPdf_beta' , 'CombBkgPdf_beta' , CombBkgPdf_beta  )

bkgPDF = CombBkgPTPdf( 'CombBkgPTPdf', 'CombBkgPTPdf',
                       time,
                       combBkgPdf_a, combBkgPdf_f, combBkgPdf_alpha, combBkgPdf_beta )

fr = time.frame()

bkgPDF.plotOn( fr )
bkgPDF.paramOn( fr,
                RooFit.ShowConstants(),
                RooFit.Layout( 0.5, 0.90, 0.85 ),
                RooFit.Format( 'NEU', RooFit.AutoPrecision( 4 ) )
                )

fr.Draw()
