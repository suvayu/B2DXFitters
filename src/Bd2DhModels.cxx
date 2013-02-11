//---------------------------------------------------------------------------//
//                                                                           //
//  RooFit models for Bd -> D h                                              //
//                                                                           //
//  Source file                                                              //
//                                                                           //
//  Authors: Eduardo Rodrigues                                               //
//  Date   : 18 / 05 / 2011                                                  //
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
#include "RooDecay.h"
#include "RooEffProd.h"
#include "RooWorkspace.h"

// B2DXFitters includes
#include "B2DXFitters/Bd2DhModels.h"
#include "B2DXFitters/CombBkgPTPdf.h"
#include "B2DXFitters/Inverse.h"


namespace Bd2DhModels {
  
  //===========================================================================
  // Extended PDF background models for Bd -> D pi as defined in the
  // Delta m_d analysis
  // - combinatorial backgroud
  // - physical backgrounds
  //===========================================================================
  RooAbsPdf* buildBdBackgroundEPDFInMass( RooAbsReal& mass,
                                          RooStringVar& filesDir,
                                          RooRealVar& nCombBkgEvts,
                                          RooRealVar& nBd2DKEvts,
                                          RooRealVar& nBd2DRhoEvts,
                                          RooRealVar& nBd2DstPiEvts,
                                          RooRealVar& nBd2DXEvts,
                                          bool debug
                                          )
  {
    if ( debug )
      printf( "==> Bd2DhModels::buildBdBackgroundEPDFInMass( ... )\n"); 
    
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
             "Bd2DPiPhysBkg_Bd2DK.root"
             );   // "filesName" or "filesDir/fileName"
    TFile* file_Bd2DK = TFile::Open( fileName );
    RooWorkspace* ws_Bd2DK = (RooWorkspace*) file_Bd2DK -> Get( "PhysBkg_Bd2DK" );
    if ( ! ws_Bd2DK ) {
      printf( "[ERROR] Retrieving the workspace for Bd -> D K!\n" );
      exit( -1 );
    }
    RooAbsPdf* pdf_Bd2DK = (RooAbsPdf*) ws_Bd2DK -> pdf( "PhysBkgBd2DKPdf_m" );
    if ( ! pdf_Bd2DK ) {
      printf( "[ERROR] Retrieving the Bd -> D K PDF from the workspace!\n" );
      exit( -1 );
    }
    pdf_Bd2DK -> SetName( "Bd2DKPDF_m" );
    
    sprintf( fileName, "%s%s%s", filesDir.getVal(),
             ( filesDir.getVal() == NULL ? "" : "/" ),
             "Bd2DPiPhysBkg_Bd2DRho.root"
             );   // "filesName" or "filesDir/fileName"
    TFile* file_Bd2DRho = TFile::Open( fileName );
    RooWorkspace* ws_Bd2DRho = (RooWorkspace*) file_Bd2DRho -> Get( "PhysBkg_Bd2DRho" );
    if ( ! ws_Bd2DRho ) {
      printf( "[ERROR] Retrieving the workspace for Bd -> D rho!\n" );
      exit( -1 );
    }
    RooAbsPdf* pdf_Bd2DRho = (RooAbsPdf*) ws_Bd2DRho -> pdf( "PhysBkgBd2DRhoPdf_m" );
    if ( ! pdf_Bd2DRho ) {
      printf( "[ERROR] Retrieving the Bd -> D rho PDF from the workspace!\n" );
      exit( -1 );
    }
    pdf_Bd2DRho -> SetName( "Bd2DRhoPDF_m" );
    
    sprintf( fileName, "%s%s%s", filesDir.getVal(),
             ( filesDir.getVal() == NULL ? "" : "/" ),
             "Bd2DPiPhysBkg_Bd2DstPi.root"
             );   // "filesName" or "filesDir/fileName"
    TFile* file_Bd2DstPi = TFile::Open( fileName );
    RooWorkspace* ws_Bd2DstPi = (RooWorkspace*) file_Bd2DstPi -> Get( "PhysBkg_Bd2DstPi" );
    if ( ! ws_Bd2DstPi ) {
      printf( "[ERROR] Retrieving the workspace for Bd -> D* pi!\n" );
      exit( -1 );
    }
    RooAbsPdf* pdf_Bd2DstPi = (RooAbsPdf*) ws_Bd2DstPi -> pdf( "PhysBkgBd2DstPiPdf_m" );
    if ( ! pdf_Bd2DstPi ) {
      printf( "[ERROR] Retrieving the Bd -> D* pi PDF from the workspace!\n" );
      exit( -1 );
    }
    pdf_Bd2DstPi -> SetName( "Bd2DstPiPDF_m" );
    
    sprintf( fileName, "%s%s%s", filesDir.getVal(),
             ( filesDir.getVal() == NULL ? "" : "/" ),
             "Bd2DPiPhysBkg_Bd2DX.root"
             );   // "filesName" or "filesDir/fileName"
    TFile* file_Bd2DX = TFile::Open( fileName );
    RooWorkspace* ws_Bd2DX = (RooWorkspace*) file_Bd2DX -> Get( "PhysBkg_Bd2DX" );
    if ( ! ws_Bd2DX ) {
      printf( "[ERROR] Retrieving the workspace for Bd -> D X!\n" );
      exit( -1 );
    }
    RooAbsPdf* pdf_Bd2DX = (RooAbsPdf*) ws_Bd2DX -> pdf( "PhysBkgBd2DXPdf_m" );
    if ( ! pdf_Bd2DX ) {
      printf( "[ERROR] Retrieving the Bd -> D X PDF from the workspace!\n" );
      exit( -1 );
    }
    pdf_Bd2DX -> SetName( "Bd2DXPDF_m" );
    
    RooAbsPdf* pdf_totBkg = NULL;
    RooExtendPdf* epdf_combBkg  = new RooExtendPdf( "CombBkgEPDF_m" , pdf_combBkg  -> GetTitle(), *pdf_combBkg , nCombBkgEvts  );
    RooExtendPdf* epdf_Bd2DK    = new RooExtendPdf( "Bd2DKEPDF_m"   , pdf_Bd2DK    -> GetTitle(), *pdf_Bd2DK   , nBd2DKEvts    );
    RooExtendPdf* epdf_Bd2DRho  = new RooExtendPdf( "Bd2DRhoEPDF_m" , pdf_Bd2DRho  -> GetTitle(), *pdf_Bd2DRho , nBd2DRhoEvts  );
    RooExtendPdf* epdf_Bd2DstPi = new RooExtendPdf( "Bd2DstPiEPDF_m", pdf_Bd2DstPi -> GetTitle(), *pdf_Bd2DstPi, nBd2DstPiEvts );
    RooExtendPdf* epdf_Bd2DX    = new RooExtendPdf( "Bd2DXEPDF_m"   , pdf_Bd2DX    -> GetTitle(), *pdf_Bd2DX   , nBd2DXEvts    );
    pdf_totBkg = new RooAddPdf( "BkgEPDF_m", "Background EPDF (combinatorial + physical) in mass",
                                RooArgList(*epdf_combBkg,*epdf_Bd2DK,*epdf_Bd2DRho,*epdf_Bd2DstPi,*epdf_Bd2DX) );
    
    // Create a local workspace
    RooWorkspace* workSpace = new RooWorkspace( "BkgWS", kTRUE );
    
    Bool_t error_1 = workSpace -> import( mass );
    Bool_t error_2 = workSpace -> import( *pdf_totBkg );
    
    if ( error_1 || error_2 ) {
      printf( "[ERROR] Mass observable or Bd background PDFs in mass failed to be imported to the local workspace!\n" );
      exit( -1 );
    }
    
    // This is necessary since the import statement actually makes a clone
    return workSpace -> pdf( "BkgEPDF_m" );    
  }

  //===========================================================================
  // PDF background models for Bd -> D pi as defined in the
  // Delta m_d analysis
  // - combinatorial backgroud
  // - physical backgrounds
  //===========================================================================
  RooAbsPdf* buildBdBackgroundPDFInMass( RooAbsReal& mass,
                                         RooStringVar& filesDir,
                                         const long fracCombBkgEvts,
                                         const long fracBd2DKEvts,
                                         const long fracBd2DstPiEvts,
                                         const long fracBd2DXEvts,
                                         bool debug
                                         )
  {
    if ( debug )
      printf( "==> Bd2DhModels::buildBdBackgroundPDFInMass( ... )\n"); 
    
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
             "Bd2DPiPhysBkg_Bd2DK.root"
             );   // "filesName" or "filesDir/fileName"
    TFile* file_Bd2DK = TFile::Open( fileName );
    RooWorkspace* ws_Bd2DK = (RooWorkspace*) file_Bd2DK -> Get( "PhysBkg_Bd2DK" );
    if ( ! ws_Bd2DK ) {
      printf( "[ERROR] Retrieving the workspace for Bd -> D K!\n" );
      exit( -1 );
    }
    RooAbsPdf* pdf_Bd2DK = (RooAbsPdf*) ws_Bd2DK -> pdf( "PhysBkgBd2DKPdf_m" );
    if ( ! pdf_Bd2DK ) {
      printf( "[ERROR] Retrieving the Bd -> D K PDF from the workspace!\n" );
      exit( -1 );
    }
    pdf_Bd2DK -> SetName( "Bd2DKPDF_m" );
    
    sprintf( fileName, "%s%s%s", filesDir.getVal(),
             ( filesDir.getVal() == NULL ? "" : "/" ),
             "Bd2DPiPhysBkg_Bd2DRho.root"
             );   // "filesName" or "filesDir/fileName"
    TFile* file_Bd2DRho = TFile::Open( fileName );
    RooWorkspace* ws_Bd2DRho = (RooWorkspace*) file_Bd2DRho -> Get( "PhysBkg_Bd2DRho" );
    if ( ! ws_Bd2DRho ) {
      printf( "[ERROR] Retrieving the workspace for Bd -> D rho!\n" );
      exit( -1 );
    }
    RooAbsPdf* pdf_Bd2DRho = (RooAbsPdf*) ws_Bd2DRho -> pdf( "PhysBkgBd2DRhoPdf_m" );
    if ( ! pdf_Bd2DRho ) {
      printf( "[ERROR] Retrieving the Bd -> D rho PDF from the workspace!\n" );
      exit( -1 );
    }
    pdf_Bd2DRho -> SetName( "Bd2DRhoPDF_m" );
    
    sprintf( fileName, "%s%s%s", filesDir.getVal(),
             ( filesDir.getVal() == NULL ? "" : "/" ),
             "Bd2DPiPhysBkg_Bd2DstPi.root"
             );   // "filesName" or "filesDir/fileName"
    TFile* file_Bd2DstPi = TFile::Open( fileName );
    RooWorkspace* ws_Bd2DstPi = (RooWorkspace*) file_Bd2DstPi -> Get( "PhysBkg_Bd2DstPi" );
    if ( ! ws_Bd2DstPi ) {
      printf( "[ERROR] Retrieving the workspace for Bd -> D* pi!\n" );
      exit( -1 );
    }
    RooAbsPdf* pdf_Bd2DstPi = (RooAbsPdf*) ws_Bd2DstPi -> pdf( "PhysBkgBd2DstPiPdf_m" );
    if ( ! pdf_Bd2DstPi ) {
      printf( "[ERROR] Retrieving the Bd -> D* pi PDF from the workspace!\n" );
      exit( -1 );
    }
    pdf_Bd2DstPi -> SetName( "Bd2DstPiPDF_m" );
    
    sprintf( fileName, "%s%s%s", filesDir.getVal(),
             ( filesDir.getVal() == NULL ? "" : "/" ),
             "Bd2DPiPhysBkg_Bd2DX.root"
             );   // "filesName" or "filesDir/fileName"
    TFile* file_Bd2DX = TFile::Open( fileName );
    RooWorkspace* ws_Bd2DX = (RooWorkspace*) file_Bd2DX -> Get( "PhysBkg_Bd2DX" );
    if ( ! ws_Bd2DX ) {
      printf( "[ERROR] Retrieving the workspace for Bd -> D X!\n" );
      exit( -1 );
    }
    RooAbsPdf* pdf_Bd2DX = (RooAbsPdf*) ws_Bd2DX -> pdf( "PhysBkgBd2DXPdf_m" );
    if ( ! pdf_Bd2DX ) {
      printf( "[ERROR] Retrieving the Bd -> D X PDF from the workspace!\n" );
      exit( -1 );
    }
    pdf_Bd2DX -> SetName( "Bd2DXPDF_m" );
    
    RooAbsPdf* pdf_totBkg = NULL;
    RooRealVar* fracCombBkg  = new RooRealVar( "fracCombBkg" , "fracCombBkg" , fracCombBkgEvts , 0., 1. );
    RooRealVar* fracBd2DK    = new RooRealVar( "fracBd2DK"   , "fracBd2DK"   , fracBd2DKEvts   , 0., 1. );
    RooRealVar* fracBd2DX    = new RooRealVar( "fracBd2DX"   , "fracBd2DX"   , fracBd2DstPiEvts, 0., 1. );
    RooRealVar* fracBd2DstPi = new RooRealVar( "fracBd2DstPi", "fracBd2DstPi", fracBd2DXEvts   , 0., 1. );
    pdf_totBkg = new RooAddPdf( "BkgPDF_m","Background PDF (combinatorial + physical) in mass",
                                RooArgList(*pdf_combBkg,*pdf_Bd2DK,*pdf_Bd2DX,*pdf_Bd2DstPi,*pdf_Bd2DRho),
                                RooArgList(*fracCombBkg,*fracBd2DK,*fracBd2DX,*fracBd2DstPi),
                                kTRUE ); // kTRUE for recursive addition of PDFs
    
    // Create a local workspace
    RooWorkspace* workSpace = new RooWorkspace( "BkgWS", kTRUE );
    
    Bool_t error_1 = workSpace -> import( mass );
    Bool_t error_2 = workSpace -> import( *pdf_totBkg );
    
    if ( error_1 || error_2 ) {
      printf( "[ERROR] Mass observable or Bd background PDFs in mass failed to be imported to the local workspace!\n" );
      exit( -1 );
    }
    
    // This is necessary since the import statement actually makes a clone
    return workSpace -> pdf( "BkgPDF_m" );    
  }
  
  //===========================================================================
  // Extended PDF background models in time for Bd -> D pi as defined in the
  // Delta m_d analysis, when no tagging information is used
  // - combinatorial backgroud
  // - Bd -> D K physical background
  //===========================================================================
  RooAbsPdf* buildBdBackgroundNoTagEPDFInTime( RooAbsReal& time,
                                               RooRealVar& Gamma,
                                               RooRealVar& nCombBkgEvts,
                                               RooRealVar& CombBkgPTPdf_a,
                                               RooRealVar& CombBkgPTPdf_f,
                                               RooRealVar& CombBkgPTPdf_alpha,
                                               RooRealVar& CombBkgPTPdf_beta,
                                               RooRealVar& nBd2DKEvts,
                                               RooResolutionModel* resModel,
                                               RooAbsReal* acceptance,
                                               bool debug
                                               )
  {
    if ( debug )
      printf( "==> Bd2DhModels::buildBdBackgroundNoTagPDFInTime( ... )\n"); 
    
    if ( ! resModel ) {
      printf( "[ERROR] No propertime resolution model set!\n" );
      exit( -1 );
    }
    
    // Create a local workspace
    RooWorkspace* workSpace = new RooWorkspace( "BkgNoTagWS", kTRUE );
    
    Bool_t error_t  = workSpace -> import( time );
    Bool_t error_rm = workSpace -> import( *resModel );
    if ( error_t || error_rm ) {
      printf( "[ERROR] Time observable or resolution model failed to be imported to the local workspace!\n" );
      exit( -1 );
    }
    
    RooRealVar* new_time = workSpace -> var( time.GetName() );
    RooResolutionModel* new_resModel =
      dynamic_cast<RooResolutionModel*>( &( workSpace -> allResolutionModels()[ resModel -> GetName() ] ) );
    
    CombBkgPTPdf* pdf_combBkg = new CombBkgPTPdf( "CombBkgPdf_t", "CombBkgPdf_t",
                                                  *new_time,
                                                  CombBkgPTPdf_a, CombBkgPTPdf_f,
                                                  CombBkgPTPdf_alpha, CombBkgPTPdf_beta
                                                  );
    
    Inverse tau( "Bd2DKPDF_tau", "Bd2DKPDF_tau", Gamma );
    RooDecay* pdf_Bd2DK_noAcc = new RooDecay( "Bd2DKPDF_noAcc_t",
                                              "B_{d} #rightarrow D K background PDF in time (without acc.)",
                                              *new_time,
                                              tau,
                                              *new_resModel,
                                              RooDecay::SingleSided
                                              );
    
    // Include the acceptance function for the phys. bkg. component only, if non NULL!
    // PDF -> PDF * acceptance
    if ( acceptance ) {
      RooEffProd* pdf_Bd2DK = new RooEffProd( "Bd2DKPDF_t",
                                              "B_{d} #rightarrow D K background PDF in time (with acc.)",
                                              *pdf_Bd2DK_noAcc, *acceptance );
      RooAbsPdf* epdf_totBkg = NULL;
      
      RooExtendPdf* epdf_combBkg  = new RooExtendPdf( "CombBkgEPDF_t",
                                                      "Combinatorial background  EPDF in time" ,
                                                      *pdf_combBkg , nCombBkgEvts );
      RooExtendPdf* epdf_Bd2DK    = new RooExtendPdf( "Bd2DKEPDF_t", 
                                                      "B_{d} #rightarrow D K bkg. EPDF in time (with acc.)",
                                                      *pdf_Bd2DK, nBd2DKEvts );
      epdf_totBkg = new RooAddPdf( "BkgEPDF_t", "Background EPDF (combinatorial + physical) in time",
                                   RooArgList( *epdf_combBkg, *epdf_Bd2DK ) );
      
      Bool_t error = workSpace -> import( *epdf_totBkg );
      
      if ( error ) {
        printf( "[ERROR] Bd background PDFs in time failed to be imported to the fitter workspace!\n" );
        exit( -1 );
      }
      
      return workSpace -> pdf( "BkgEPDF_t" );
    }
    else { // no acceptance
      RooAbsPdf* epdf_totBkg = NULL;
      
      RooExtendPdf* epdf_combBkg  = new RooExtendPdf( "CombBkgEPDF_t",
                                                      "Combinatorial background  EPDF in time" ,
                                                      *pdf_combBkg , nCombBkgEvts );
      RooExtendPdf* epdf_Bd2DK    = new RooExtendPdf( "Bd2DKEPDF_t", 
                                                      "B_{d} #rightarrow D K bkg. EPDF in time (with acc.)",
                                                      *pdf_Bd2DK_noAcc, nBd2DKEvts );
      epdf_totBkg = new RooAddPdf( "BkgEPDF_t", "Background EPDF (combinatorial + physical) in time",
                                   RooArgList( *epdf_combBkg, *epdf_Bd2DK ) );
      
      Bool_t error = workSpace -> import( *epdf_totBkg );
      
      if ( error ) {
        printf( "[ERROR] Bd background PDFs in time failed to be imported to the fitter workspace!\n" );
        exit( -1 );
      }
      
      return workSpace -> pdf( "BkgEPDF_t" );
    } 
  }
  
} // end of namespace

//=============================================================================
