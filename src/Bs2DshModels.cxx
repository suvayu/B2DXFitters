//---------------------------------------------------------------------------//
//                                                                           //
//  RooFit models for Bs -> Ds h                                             //
//                                                                           //
//  Source file                                                              //
//                                                                           //
//  Authors: Eduardo Rodrigues                                               //
//  Date   : 24 / 05 / 2011                                                  //
//                                                                           //
//---------------------------------------------------------------------------//

// STL includes


// ROOT and RooFit includes
#include "TFile.h"
#include "RooArgList.h"
#include "RooAbsPdf.h"
#include "RooAddPdf.h"
#include "RooExtendPdf.h"
#include "RooExponential.h"
#include "RooWorkspace.h"

// B2DXFitters includes
#include "B2DXFitters/Bs2DshModels.h"


namespace Bs2DshModels {
  
  //===========================================================================
  // Extended PDF background models for Bs -> Ds pi as defined in the
  // Delta m_s analysis
  // - combinatorial backgroud
  // - physical backgrounds
  //===========================================================================
  RooAbsPdf* buildBsBackgroundEPDFInMass( RooAbsReal& mass,
                                          RooStringVar& filesDir,
                                          RooRealVar& nCombBkgEvts,
                                          RooRealVar& nBd2DPiEvts,
                                          RooRealVar& nBs2DsRhoEvts,
                                          RooRealVar& nBs2DsstPiEvts,
                                          RooRealVar& nBs2DsXEvts,
                                          RooRealVar& nLb2LcPiEvts,
                                          bool debug
                                          )
  {
    if ( debug )
      printf( "==> Bs2DshModels::buildBsBackgroundEPDFInMass()\n"); 
    
    // Create the background PDFs in mass: combinatorial and physical
    // ==============================================================
    RooRealVar* pdf_combBkg_slope = new RooRealVar( "CombBkgPDF_slope",
                                                    "Combinatorial background PDF in mass - exponential slope",
                                                    -0.002, -0.01, 0., "[MeV/c^{2}]^{-1}" );
    RooExponential* pdf_combBkg = new RooExponential( "CombBkgPDF_m", "Combinatorial background PDF in mass",
                                                      mass, *pdf_combBkg_slope );
    
    // Physical background from partially reconstructed decays
    // -------------------------------------------------------
    char fileName[200];
    sprintf( fileName, "%s%s%s", filesDir.getVal(),
             ( filesDir.getVal() == NULL ? "" : "/" ),
             "Bs2DsPiPhysBkg_Bd2DPi.root"
             );   // "filesName" or "filesDir/fileName"
    TFile* file_Bd2DPi = TFile::Open( fileName );
    RooWorkspace* ws_Bd2DPi = (RooWorkspace*) file_Bd2DPi -> Get( "PhysBkg_Bd2DPi" );
    if ( ! ws_Bd2DPi ) {
      printf( "[ERROR] Retrieving the workspace for Bd -> D Pi!\n" );
      exit( -1 );
    }
    RooAbsPdf* pdf_Bd2DPi = (RooAbsPdf*) ws_Bd2DPi -> pdf( "PhysBkgBd2DPiPdf_m" );
    if ( ! pdf_Bd2DPi ) {
      printf( "[ERROR] Retrieving the Bd -> D Pi PDF from the workspace!\n" );
      exit( -1 );
    }
    
    sprintf( fileName, "%s%s%s", filesDir.getVal(),
             ( filesDir.getVal() == NULL ? "" : "/" ),
             "Bs2DsPiPhysBkg_Bs2DsRho.root"
             );   // "filesName" or "filesDir/fileName"
    TFile* file_Bs2DsRho = TFile::Open( fileName );
    RooWorkspace* ws_Bs2DsRho = (RooWorkspace*) file_Bs2DsRho -> Get( "PhysBkg_Bs2DsRho" );
    if ( ! ws_Bs2DsRho ) {
      printf( "[ERROR] Retrieving the workspace for Bs -> Ds rho!\n" );
      exit( -1 );
    }
    RooAbsPdf* pdf_Bs2DsRho = (RooAbsPdf*) ws_Bs2DsRho -> pdf( "PhysBkgBs2DsRhoPdf_m" );
    if ( ! pdf_Bs2DsRho ) {
      printf( "[ERROR] Retrieving the Bs -> Ds rho PDF from the workspace!\n" );
      exit( -1 );
    }
    
    sprintf( fileName, "%s%s%s", filesDir.getVal(),
             ( filesDir.getVal() == NULL ? "" : "/" ),
             "Bs2DsPiPhysBkg_Bs2DsstPi.root"
             );   // "filesName" or "filesDir/fileName"
    TFile* file_Bs2DsstPi = TFile::Open( fileName );
    RooWorkspace* ws_Bs2DsstPi = (RooWorkspace*) file_Bs2DsstPi -> Get( "PhysBkg_Bs2DsstPi" );
    if ( ! ws_Bs2DsstPi ) {
      printf( "[ERROR] Retrieving the workspace for Bs -> Ds* pi!\n" );
      exit( -1 );
    }
    RooAbsPdf* pdf_Bs2DsstPi = (RooAbsPdf*) ws_Bs2DsstPi -> pdf( "PhysBkgBs2DsstPiPdf_m" );
    if ( ! pdf_Bs2DsstPi ) {
      printf( "[ERROR] Retrieving the Bs -> Ds* pi PDF from the workspace!\n" );
      exit( -1 );
    }
    
    sprintf( fileName, "%s%s%s", filesDir.getVal(),
             ( filesDir.getVal() == NULL ? "" : "/" ),
             "Bs2DsPiPhysBkg_Bs2DsX.root"
             );   // "filesName" or "filesDir/fileName"
    TFile* file_Bs2DsX = TFile::Open( fileName );
    RooWorkspace* ws_Bs2DsX = (RooWorkspace*) file_Bs2DsX -> Get( "PhysBkg_Bs2DsX" );
    if ( ! ws_Bs2DsX ) {
      printf( "[ERROR] Retrieving the workspace for Bs -> Ds X!\n" );
      exit( -1 );
    }
    RooAbsPdf* pdf_Bs2DsX = (RooAbsPdf*) ws_Bs2DsX -> pdf( "PhysBkgBs2DsXPdf_m" );
    if ( ! pdf_Bs2DsX ) {
      printf( "[ERROR] Retrieving the Bs -> Ds X PDF from the workspace!\n" );
      exit( -1 );
    }
    
    sprintf( fileName, "%s%s%s", filesDir.getVal(),
             ( filesDir.getVal() == NULL ? "" : "/" ),
             "Bs2DsPiPhysBkg_Lb2LcPi.root"
             );
    TFile* file_Lb2LcPi = TFile::Open( fileName );
    RooWorkspace* ws_Lb2LcPi = (RooWorkspace*) file_Lb2LcPi -> Get( "PhysBkg_Lb2LcPi" );
    RooAbsPdf* pdf_Lb2LcPi = (RooAbsPdf*) ws_Lb2LcPi -> pdf( "PhysBkgLb2LcPiPdf_m" );
    if ( ! pdf_Lb2LcPi ) {
      printf( "[ERROR] Retrieving the Lambda_b -> Lambda_c pi PDF from the workspace!\n" );
      exit( -1 );
    }
    
    RooAbsPdf* pdf_totBkg = NULL;

    RooExtendPdf* epdf_combBkg   = new RooExtendPdf( "CombBkgEPDF_m"  , pdf_combBkg   -> GetTitle(), *pdf_combBkg  , nCombBkgEvts   );
    RooExtendPdf* epdf_Bd2DPi    = new RooExtendPdf( "Bd2DPiEPDF_m"   , pdf_Bd2DPi    -> GetTitle(), *pdf_Bd2DPi   , nBd2DPiEvts    );
    RooExtendPdf* epdf_Bs2DsRho  = new RooExtendPdf( "Bs2DsRhoEPDF_m" , pdf_Bs2DsRho  -> GetTitle(), *pdf_Bs2DsRho , nBs2DsRhoEvts  );
    RooExtendPdf* epdf_Bs2DsstPi = new RooExtendPdf( "Bs2DsstPiEPDF_m", pdf_Bs2DsstPi -> GetTitle(), *pdf_Bs2DsstPi, nBs2DsstPiEvts );
    RooExtendPdf* epdf_Bs2DsX    = new RooExtendPdf( "Bs2DsXEPDF_m"   , pdf_Bs2DsX    -> GetTitle(), *pdf_Bs2DsX   , nBs2DsXEvts    );
    RooExtendPdf* epdf_Lb2LcPi   = new RooExtendPdf( "Lb2LcPiEPDF_m"  , pdf_Lb2LcPi   -> GetTitle(), *pdf_Lb2LcPi  , nLb2LcPiEvts   );
    pdf_totBkg = new RooAddPdf( "BkgEPDF_m", "BkgEPDF_m",
                                RooArgList(*epdf_combBkg,
                                           *epdf_Bd2DPi,*epdf_Bs2DsRho,*epdf_Bs2DsstPi,*epdf_Bs2DsX,*epdf_Lb2LcPi) );
    
    // Create a local workspace
    RooWorkspace* workSpace = new RooWorkspace( "BkgWS", kTRUE );
    
    Bool_t error_1 = workSpace -> import( mass );
    Bool_t error_2 = workSpace -> import( *pdf_totBkg );
    
    if ( error_1 || error_2 ) {
      printf( "[ERROR] Mass observable or Bs background PDFs in mass failed to be imported to the local workspace!\n" );
      exit( -1 );
    }
    
    // This is necessary since the import statement actually makes a clone
    return workSpace -> pdf( "BkgEPDF_m" );
  }
  
} // end of namespace

//=============================================================================
