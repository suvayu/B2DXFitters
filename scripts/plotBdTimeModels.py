#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#                                                                             #
#   Python script to plot the Bd -> D pi time models                          #
#                                                                             #
#   Example usage:                                                            #
#      python -i plotBdTimeModels.py                                          #
#                                                                             #
#   Author: Eduardo Rodrigues                                                 #
#   Date  : 01 / 06 / 2011                                                    #
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

# MODELS
signalModelOnly = False

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
    
    if not signalModelOnly :
        model.plotOn( frame,
                      RooFit.Components('Bd2DKEPDF_t'),
                      RooFit.LineColor(kYellow+1),
                      RooFit.LineStyle(kDashed),
                      RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                      )
        model.plotOn( frame,
                      RooFit.Components('CombBkgEPDF_t'),
                      RooFit.LineColor( kGreen ),
                      RooFit.LineStyle(kDashed),
                      RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                      )
        model.plotOn( frame,
                      RooFit.Components('CombBkgEPDF_t,Bd2DKEPDF_t'),
                      RooFit.DrawOption( 'F' ),
                      RooFit.FillStyle( 3002 ),
                      RooFit.FillColor( 30 ),
                      RooFit.VLines(),
                      RooFit.Normalization( 1., RooAbsReal.RelativeExpected )
                      )
        model.plotOn( frame,
                      RooFit.Components('SigEPDF_t'),
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

#------------------------------------------------------------------------------
def legends( model, frame ):
    stat = frame.findObject( 'data_statBox' )
    prefix = 'Sig' if signalModelOnly else 'Tot'
    if not stat: stat = frame.findObject( '%sEPDF_tData_statBox' % prefix )
    if stat :
        stat.SetTextSize( 0.025 )
    pt = frame.findObject( '%sEPDF_t_paramBox' % prefix )
    if pt :
        pt.SetTextSize( 0.02 )
    # Legend of EPDF components
    leg = TLegend( 0.56, 0.42, 0.87, 0.62 )
    leg.SetFillColor( 0 )
    leg.SetTextSize( 0.02 )
    comps = model.getComponents()    
    if signalModelOnly :
        pdfName = 'SigEPDF_t'
        pdf = comps.find( pdfName )
        curve = frame.findObject( pdfName + '_Norm[time]' )
        if curve : leg.AddEntry( curve, pdf.GetTitle(), 'l' )
        return leg, curve
    else :
        pdf1 = comps.find( 'SigEPDF_t' )
        pdfName = 'TotEPDF_t_Norm[time]_Comp[%s]' % 'SigEPDF_t'
        curve1 = frame.findObject( pdfName )
        if curve1 : leg.AddEntry( curve1, pdf1.GetTitle(), 'l' )
        pdf = comps.find( 'Bd2DKEPDF_t' )
        pdfName = 'TotEPDF_t_Norm[time]_Comp[%s]' % 'Bd2DKEPDF_t'
        curve2 = frame.findObject( pdfName )
        if curve2 : leg.AddEntry( curve2, pdf.GetTitle(), 'l' )
        pdf = comps.find( 'CombBkgEPDF_t' )
        pdfName = 'TotEPDF_t_Norm[time]_Comp[%s]' % 'CombBkgEPDF_t'
        curve3 = frame.findObject( pdfName )
        if curve3 : leg.AddEntry( curve3, pdf.GetTitle(), 'l' )
        pdfName = 'TotEPDF_t_Norm[time]_Comp[%s]' % 'CombBkgEPDF_t,Bd2DKEPDF_t'
        curve4 = frame.findObject( pdfName )
        if curve4 :
            leg.AddEntry( curve4, 'All but %s' % pdf1.GetTitle(), 'f' )
            curve4.SetLineColor(0)
        pdfName = 'TotEPDF_t_Norm[time]'
        pdf = comps.find( 'TotEPDF_t' )
        curve5 = frame.findObject( pdfName )
        #if curve5 : leg.AddEntry( curve5, pdf.GetTitle(), 'l' )
        if curve5 : leg.AddEntry( curve5, 'Model (signal & background) EPDF', 'l' )
        return leg, curve4

#------------------------------------------------------------------------------
_usage = '%prog [options] <filename>'

parser = OptionParser( _usage )

parser.add_option( '-w', '--workspace',
                   dest = 'wsname',
                   metavar = 'WSNAME',
                   default = 'FitterWS',
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
    
    import GaudiPython
    GaudiPython.loaddict( 'B2DXFittersDict' )
    
    from ROOT import CombBkgPTPdf
    from ROOT import BdPTAcceptance
    
    gROOT.SetStyle( 'Plain' )    
    gROOT.SetBatch( False )
    
    f = TFile( FILENAME )
    
    w = f.Get( options.wsname )
    if not w :
        parser.error( 'Workspace "%s" not found in file "%s"! Nothing plotted.' %\
                      ( options.wsname, FILENAME ) )
    
    f.Close()
    
    time = w.var( 'time' )
    time = RooRealVar( 'time', '%s propertime' % bName, 0., 0., 8., 'ps' )
    
    modelPDF = w.pdf( 'TotEPDF_t' )
    if not modelPDF: modelPDF = w.pdf( 'SigEPDF_t' )
    dataset = w.data( 'data' )
    if not dataset : dataset = w.data( 'TotEPDF_tData' )
    if not dataset : dataset = w.data( 'SigEPDF_tData' )
    
    if not ( modelPDF and dataset ) :
        w.Print( 'v' )
        exit( 0 )
    
    canvas = TCanvas( 'TimeCanvas', 'Propertime canvas', 1200, 800 )
    canvas.SetTitle( 'Fit in propertime' )
    canvas.cd()
    
    frame_t = time.frame()
    
    frame_t.SetTitle( 'Fit in reconstructed %s propertime' % bName )
    
    frame_t.GetXaxis().SetLabelSize( 0.03 )
    frame_t.GetYaxis().SetLabelSize( 0.03 )
    
    if plotData : plotDataSet( dataset, frame_t )
    
    if plotModel : plotFitModel( modelPDF, frame_t )
    
    leg, curve = legends( modelPDF, frame_t )
    frame_t.addObject( leg )
    
    frame_t.Draw()

#------------------------------------------------------------------------------
