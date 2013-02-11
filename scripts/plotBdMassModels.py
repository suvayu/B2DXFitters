#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to plot the Bd -> D pi mass models                          #
#                                                                             #
#   Example usage:                                                            #
#      python -i plotBdMassModels.py                                          #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 27 / 05 / 2011                                                    #
#                                                                             #
# --------------------------------------------------------------------------- #

# -----------------------------------------------------------------------------
# Load necessary libraries
# -----------------------------------------------------------------------------
from optparse import OptionParser
from os.path  import exists


# -----------------------------------------------------------------------------
# Configuration settings
# -----------------------------------------------------------------------------

# PLOTTING CONFIGURATION
plotData  =  True
plotModel =  True

# MISCELLANEOUS
debug = True
bName = 'B_{d}'


#------------------------------------------------------------------------------
def plotDataSet( dataset, frame ) :
    dataset.plotOn( frame,
                    RooFit.Binning( 70 ) )
    dataset.statOn( frame,
                    RooFit.Layout( 0.56, 0.90, 0.90 ),
                    RooFit.What('N') )

#------------------------------------------------------------------------------
def plotFitModel( model, frame ) :
    if debug :
        model.Print( 't' )
        frame.Print( 'v' )
    
    model.plotOn( frame,
                  RooFit.Components('Bd2DKEPDF_m'),
                  RooFit.LineColor(kYellow+1),
                  RooFit.LineStyle(kDashed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame,
                  RooFit.Components('Bd2DstPiEPDF_m'),
                  RooFit.LineColor(kMagenta),
                  RooFit.LineStyle(kDashed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame,
                  RooFit.Components('Bd2DRhoEPDF_m'),
                  RooFit.LineColor(kOrange+2),
                  RooFit.LineStyle(kDashed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame,
                  RooFit.Components('Bd2DXEPDF_m'),
                  RooFit.LineColor(kCyan-8),
                  RooFit.LineStyle(kDashed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame,
                  RooFit.Components('CombBkgEPDF_m'),
                  RooFit.LineColor( kGreen ),
                  RooFit.LineStyle(kDashed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame,
                  RooFit.Components('CombBkgEPDF_m,Bd2DKEPDF_m,Bd2DRhoEPDF_m,Bd2DstPiEPDF_m,Bd2DXEPDF_m'),
                  RooFit.DrawOption( 'F' ),
                  RooFit.FillStyle( 3002 ),
                  RooFit.FillColor( 30 ),
                  RooFit.VLines(),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame,
                  RooFit.Components('SigEPDF'),
                  RooFit.LineColor(kRed-7),
                  RooFit.LineStyle(kDashed),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    model.plotOn( frame,
                  RooFit.LineColor(kBlue),
                  RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                  )
    
    model.paramOn( frame,
                   RooFit.Layout( 0.56, 0.90, 0.85 ),
                   RooFit.Format( 'NEU', RooFit.AutoPrecision( 2 ) )
                   )
    
    stat = frame.findObject( 'data_statBox' )
    if not stat:
        stat = frame.findObject( 'TotEPDF_mData_statBox' )
    if stat :
        stat.SetTextSize( 0.025 )
    pt = frame.findObject( 'TotEPDF_m_paramBox' )
    if pt :
        pt.SetTextSize( 0.02 )
    # Legend of EPDF components
   # leg = TLegend( 0.13, 0.57, 0.44, 0.87 )
   # leg.SetFillColor( 0 )
   # leg.SetTextSize( 0.02 )
   # comps = model.getComponents()
   # pdf = comps.find( 'Bd2DKEPDF_m' )
   # pdfName = 'TotEPDF_m_Norm[mass]_Comp[%s]' % 'Bd2DKEPDF_m'
   # curve = frame.findObject( pdfName )
   # leg.AddEntry( curve, pdf.GetTitle(), 'l' )
   # frame.addObject( leg )
   # pdf = comps.find( 'Bd2DstPiEPDF_m' )
   # pdfName = 'TotEPDF_m_Norm[mass]_Comp[%s]' % 'Bd2DstPiEPDF_m'
   # curve2 = frame.findObject( pdfName )
   # leg.AddEntry( curve2, pdf.GetTitle(), 'l' )
   # frame.addObject( leg )
   #  pdf = comps.find( 'Bd2DRhoEPDF_m' )
   # pdfName = 'TotEPDF_m_Norm[mass]_Comp[%s]' % 'Bd2DRhoEPDF_m'
   # curve3 = frame.findObject( pdfName )
   # leg.AddEntry( curve3, pdf.GetTitle(), 'l' )
   # frame.addObject( leg )
   # pdf = comps.find( 'Bd2DXEPDF_m' )
   # pdfName = 'TotEPDF_m_Norm[mass]_Comp[%s]' % 'Bd2DXEPDF_m'
   # curve4 = frame.findObject( pdfName )
   # leg.AddEntry( curve4, pdf.GetTitle(), 'l' )
   # frame.addObject( leg )
   # pdf = comps.find( 'CombBkgEPDF_m' )
   # pdfName = 'TotEPDF_m_Norm[mass]_Comp[%s]' % 'CombBkgEPDF_m'
   # curve5 = frame.findObject( pdfName )
   # leg.AddEntry( curve5, pdf.GetTitle(), 'l' )
   # frame.addObject( leg )
   # pdf = comps.find( 'SigEPDF' )
   # pdfName = 'TotEPDF_m_Norm[mass]_Comp[%s]' % 'SigEPDF'
   # curve6 = frame.findObject( pdfName )
   # leg.AddEntry( curve6, pdf.GetTitle(), 'l' )
   # frame.addObject( leg )
   # pdfName = 'TotEPDF_m_Norm[mass]_Comp[%s]' % 'CombBkgEPDF_m,Bd2DKEPDF_m,Bd2DRhoEPDF_m,Bd2DstPiEPDF_m,Bd2DXEPDF_m'
   # curve7 = frame.findObject( pdfName )
   # leg.AddEntry( curve7, 'All but %s' % pdf.GetTitle(), 'f' )
   # curve7.SetLineColor(0)

#------------------------------------------------------------------------------
_usage = '%prog [options] <filename>'

parser = OptionParser( _usage )

parser.add_option( '-w', '--workspace',
                   dest = 'wsname',
                   metavar = 'WSNAME',
                   default = 'FitMeToolWS',
                   #default = 'FitterWS',
                   help = 'RooWorkspace name as stored in ROOT file'
                   )

#------------------------------------------------------------------------------

if __name__ == '__main__' :
    ( options, args ) = parser.parse_args()
    
    if len( args ) != 1 :
        parser.print_help()
        exit( -1 )

    FILENAME = ( args[ 0 ] )
    if not exists( FILENAME ) :
        parser.error( 'ROOT file "%s" not found! Nothing plotted.' % FILENAME )
        parser.print_help()
    
    from ROOT import TFile, TCanvas, gROOT, TLegend
    from ROOT import kYellow, kMagenta, kOrange, kCyan, kGreen, kRed, kBlue, kDashed
    from ROOT import RooFit, RooRealVar, RooAbsReal

    gROOT.SetStyle( 'Plain' )    
    gROOT.SetBatch( False )
    
    f = TFile( FILENAME )

    w = f.Get( options.wsname )
    if not w :
        parser.error( 'Workspace "%s" not found in file "%s"! Nothing plotted.' %\
                      ( options.wsname, FILENAME ) )
    
    f.Close()
        
    mass = w.var( 'mass' )
    mean  = 5279.5
    mass = RooRealVar( "mass", "%s mass" % bName, mean, 4800, 5850, "MeV/c^{2}" )
    
    modelPDF = w.pdf( 'TotEPDF_m' )
    dataset = w.data( 'data' )
    if not dataset : dataset = w.data( 'TotEPDF_mData' )
    
    if not ( modelPDF and dataset ) :
        w.Print( 'v' )
        exit( 0 )
    
    canvas = TCanvas( 'MassCanvas', 'Mass canvas', 1200, 800 )
    canvas.SetTitle( 'Fit in mass' )
    canvas.cd()
    
    frame_m = mass.frame()
    
    frame_m.SetTitle( 'Fit in reconstructed %s mass' % bName )
    
    frame_m.GetXaxis().SetLabelSize( 0.03 )
    frame_m.GetYaxis().SetLabelSize( 0.03 )
    
    if plotData : plotDataSet( dataset, frame_m )
    
    if plotModel : plotFitModel( modelPDF, frame_m )
    
    frame_m.Draw()
        
    pt = canvas.FindObject( 'TotEPDF_m_paramBox' )
    if pt :
        print ''
        pt.SetY1NDC( 0.40 )
    canvas.Modified()
    canvas.Update()
    
#------------------------------------------------------------------------------
