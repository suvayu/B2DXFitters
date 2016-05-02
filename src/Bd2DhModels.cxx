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
#include "RooGaussian.h"
#include "RooDecay.h"
#include "RooEffProd.h"
#include "RooWorkspace.h"

// B2DXFitters includes
#include "B2DXFitters/Bd2DhModels.h"
#include "B2DXFitters/GeneralUtils.h"
#include "B2DXFitters/RooBinned1DQuinticBase.h"
#include "B2DXFitters/Bs2Dsh2011TDAnaModels.h"
#include "B2DXFitters/RooJohnsonSU.h"

using namespace std;
using namespace GeneralUtils;
using namespace Bs2Dsh2011TDAnaModels;



namespace Bd2DhModels {
  
  RooAbsPdf* build_Bd2DPi_BKG_MDFitter( RooAbsReal& mass,
					RooAbsReal& massDs,
					RooWorkspace* work,
					RooWorkspace* workInt,
					TString &samplemode,
					TString merge,
					Int_t dim,
					bool debug
					){
    if (debug == true)
      {
        cout<<"[INFO] =====> Build background model Bd->DPi --------------"<<endl;
      }

    RooArgList* list = new RooArgList();
    TString charmVarName = massDs.GetName();

    RooExtendPdf* epdf_Bd2DK = NULL;
    epdf_Bd2DK = buildExtendPdfSpecBkgMDFit( workInt, work, samplemode, "Bd2DK", "", merge, dim, charmVarName, debug);
    Double_t valBd2DK = CheckEvts(workInt, samplemode, "Bd2DK",debug);
    list = AddEPDF(list, epdf_Bd2DK, valBd2DK, debug);

    RooExtendPdf* epdf_Bd2DRho = NULL;
    epdf_Bd2DRho = buildExtendPdfSpecBkgMDFit( workInt, work, samplemode, "Bd2DRho", "", merge, dim, charmVarName, debug);
    Double_t valBd2DRho = CheckEvts(workInt, samplemode, "Bd2DRho",debug);
    list = AddEPDF(list, epdf_Bd2DRho, valBd2DRho, debug);

    RooExtendPdf* epdf_Bd2DstPi = NULL;
    epdf_Bd2DstPi = buildExtendPdfSpecBkgMDFit( workInt, work, samplemode, "Bd2DstPi", "", merge, dim, charmVarName, debug);
    Double_t valBd2DstPi = CheckEvts(workInt, samplemode, "Bd2DstPi",debug);
    list = AddEPDF(list, epdf_Bd2DstPi, valBd2DstPi, debug);

    RooExtendPdf* epdf_Lb2LcPi = NULL;
    epdf_Lb2LcPi = buildExtendPdfSpecBkgMDFit( workInt, work, samplemode, "Lb2LcPi", "", merge, dim, "", debug);
    Double_t valLb2LcPi = CheckEvts(workInt, samplemode, "Lb2LcPi",debug);
    list = AddEPDF(list, epdf_Lb2LcPi, valLb2LcPi, debug);

    RooExtendPdf* epdf_Bs2DsPi = NULL;
    epdf_Bs2DsPi = buildExtendPdfSpecBkgMDFit( workInt, work, samplemode, "Bs2DsPi", "", merge, dim, "", debug);
    Double_t valBs2DsPi = CheckEvts(workInt, samplemode, "Bs2DsPi",debug);
    list = AddEPDF(list, epdf_Bs2DsPi, valBs2DsPi, debug);

    RooAbsPdf* pdf_totBkg = NULL;
    TString name = "BkgEPDF_m_"+samplemode;
    pdf_totBkg = new RooAddPdf( name.Data(), name.Data(), *list);
    if (debug == true)
      {
        cout<<endl;
        if( pdf_totBkg != NULL ){ cout<<" ------------- CREATED TOTAL BACKGROUND PDF: SUCCESFULL------------"<<endl; }
        else { cout<<" ---------- CREATED TOTAL BACKGROUND PDF: FAILED ----------------"<<endl;}
      }
    return pdf_totBkg;

  }
  
  //===============================================================================
  // Build JohnsonSU pdf
  //===============================================================================
  
  RooAbsPdf* buildJohnsonSUPDF( RooAbsReal& obs,
                                RooWorkspace* workInt,
                                TString samplemode,
                                TString typemode,
                                bool debug)
  { 
    if ( debug == true )
    {   
      std::cout<<"Bd2DhModels::buildJohnsonSUPDF(..)==> building JohnsonSU pdf... "<<std::endl; 
    }

    RooRealVar* mean = NULL;    
    RooRealVar* sigmaVar =NULL;
    RooRealVar* nuVar =NULL;
    RooRealVar* tauVar =NULL;

    TString varName = obs.GetName();

    TString meanName = typemode+"_"+varName+"_mean_"+samplemode;
    mean = tryVar(meanName, workInt, debug);
    TString sigmaName = typemode+"_"+varName+"_sigma_"+samplemode;
    sigmaVar = tryVar(sigmaName, workInt, debug);
    TString nuName = typemode+"_"+varName+"_nu_"+samplemode;
    nuVar = tryVar(nuName, workInt, debug);
    TString tauName = typemode+"_"+varName+"_tau_"+samplemode;
    tauVar = tryVar(tauName, workInt, debug);
    
    RooJohnsonSU* pdf = NULL;
    TString pdfName = typemode+"_"+varName+"_johnsonSU_"+samplemode;
    pdf = new RooJohnsonSU( pdfName.Data(), pdfName.Data(), obs, *mean, *sigmaVar, *nuVar, *tauVar);    
    CheckPDF( pdf, debug );

    return pdf;  
  }
  
  //===============================================================================
  // Build JohnsonSU + gaussian pdf
  //===============================================================================

  RooAbsPdf* buildJohnsonSUPlusGaussianPDF( RooAbsReal& obs,
                                            RooWorkspace* workInt,
                                            TString samplemode,
                                            TString typemode,
                                            bool debug)
  {
    if ( debug == true )
    {
      std::cout<<"Bd2DhModels::buildJohnsonSUPlusGaussianPDF(..)==> building JohnsonSU + gaussian pdf..."<<std::endl;      
    }

    RooRealVar* meanJ = NULL;
    RooRealVar* sigmaJVar =NULL;
    RooRealVar* nuJVar =NULL;
    RooRealVar* tauJVar =NULL;
    RooRealVar* meanG = NULL;
    RooRealVar* sigmaGVar =NULL;
    RooRealVar* fracVar = NULL;

    TString varName = obs.GetName();
    
    TString meanJName = typemode+"_"+varName+"_meanJ_"+samplemode;
    meanJ = tryVar(meanJName, workInt, debug);
    TString sigmaJName = typemode+"_"+varName+"_sigmaJ_"+samplemode;
    sigmaJVar = tryVar(sigmaJName, workInt, debug);
    TString nuJName = typemode+"_"+varName+"_nuJ_"+samplemode;
    nuJVar = tryVar(nuJName, workInt, debug);
    TString tauJName = typemode+"_"+varName+"_tauJ_"+samplemode;
    tauJVar = tryVar(tauJName, workInt, debug);
    TString meanGName = typemode+"_"+varName+"_meanG_"+samplemode;
    meanG = tryVar(meanGName, workInt, debug);
    TString sigmaGName = typemode+"_"+varName+"_sigmaG_"+samplemode;
    sigmaGVar = tryVar(sigmaGName, workInt, debug);
    TString fracName = typemode+"_"+varName+"_frac_"+samplemode;
    fracVar = tryVar(fracName, workInt, debug);
  
    RooAbsPdf* pdf = NULL; 

    RooGaussian *pdf1 = NULL;
    TString pdf1Name = typemode+"_"+varName+"_gaussian_"+samplemode;
    RooJohnsonSU *pdf2 = NULL;
    TString pdf2Name = typemode+"_"+varName+"_johnsonSU_"+samplemode;
    pdf1 = new RooGaussian( pdf1Name.Data(), pdf1Name.Data(), obs, *meanG, *sigmaGVar);
    pdf2 = new RooJohnsonSU( pdf2Name.Data(), pdf2Name.Data(), obs, *meanJ, *sigmaJVar, *nuJVar, *tauJVar);
    
    TString pdfName = typemode+"_"+varName+"_JohnsonSUPlusGaussian_"+samplemode;
    pdf = new RooAddPdf( pdfName.Data(), pdfName.Data(), *pdf1, *pdf2, *fracVar);
    CheckPDF( pdf, debug );
    
    return pdf;
  }
  
  //===============================================================================
  // Build JohnsonSU + 2 gaussian pdf                                
  //===============================================================================

  RooAbsPdf* buildJohnsonSUPlus2GaussianPDF( RooAbsReal& obs,
                                             RooWorkspace* workInt,
                                             TString samplemode,
                                             TString typemode,
                                             bool sameMean,
                                             bool debug)
  {
    if ( debug == true )
    {
      std::cout<<"Bd2DhModels::buildJohnsonSUPlus2GaussianPDF(..)==> building JohnsonSU + 2 gaussian pdf..."<<std::endl;      
    }

    RooRealVar* meanJ = NULL;
    RooRealVar* sigmaJVar =NULL;
    RooRealVar* nuJVar =NULL; 
    RooRealVar* tauJVar =NULL;
    RooRealVar* meanG1 = NULL;
    RooRealVar* meanG2 = NULL;
    RooRealVar* sigma1GVar =NULL;
    RooRealVar* sigma2GVar = NULL;
    RooRealVar* frac1GVar = NULL;
    RooRealVar* frac2GVar = NULL;

    TString varName = obs.GetName();

    TString meanJName = typemode+"_"+varName+"_meanJ_"+samplemode;
    meanJ = tryVar(meanJName, workInt, debug);
    TString sigmaJName = typemode+"_"+varName+"_sigmaJ_"+samplemode;
    sigmaJVar = tryVar(sigmaJName, workInt, debug);
    TString nuJName = typemode+"_"+varName+"_nuJ_"+samplemode;
    nuJVar = tryVar(nuJName, workInt, debug);
    TString tauJName = typemode+"_"+varName+"_tauJ_"+samplemode;
    tauJVar = tryVar(tauJName, workInt, debug);
    TString meanG1Name = typemode+"_"+varName+"_meanG1_"+samplemode;
    meanG1 = tryVar(meanG1Name, workInt, debug);
    if(!sameMean)
    {
      TString meanG2Name = typemode+"_"+varName+"_meanG2_"+samplemode;
      meanG2 = tryVar(meanG2Name, workInt, debug); 
    }
    TString sigma1GName = typemode+"_"+varName+"_sigma1G_"+samplemode;
    sigma1GVar = tryVar(sigma1GName, workInt, debug);
    TString sigma2GName = typemode+"_"+varName+"_sigma2G_"+samplemode;
    sigma2GVar = tryVar(sigma2GName, workInt, debug);
    TString frac1GName = typemode+"_"+varName+"_frac1G_"+samplemode;
    frac1GVar = tryVar(frac1GName, workInt, debug);
    TString frac2GName = typemode+"_"+varName+"_frac2G_"+samplemode;
    frac2GVar = tryVar(frac2GName, workInt, debug);

    RooAbsPdf* pdf = NULL;

    RooGaussian *pdf1 = NULL;
    TString pdf1Name = typemode+"_"+varName+"_gaussian1_"+samplemode;
    RooGaussian *pdf2 = NULL;
    TString pdf2Name = typemode+"_"+varName+"_gaussian2_"+samplemode;
    RooJohnsonSU *pdf3 = NULL;
    TString pdf3Name = typemode+"_"+varName+"_johnsonSU_"+samplemode;
  
    pdf1 = new RooGaussian( pdf1Name.Data(), pdf1Name.Data(), obs, *meanG1, *sigma1GVar);
    if(sameMean)
    {
      pdf2 = new RooGaussian( pdf2Name.Data(), pdf2Name.Data(), obs, *meanG1, *sigma2GVar);
    }
    else
    {
      pdf2 = new RooGaussian( pdf2Name.Data(), pdf2Name.Data(), obs, *meanG2, *sigma2GVar);
    }
    pdf3 = new RooJohnsonSU( pdf3Name.Data(), pdf3Name.Data(), obs, *meanJ, *sigmaJVar, *nuJVar, *tauJVar);
    CheckPDF( pdf1, debug );
    CheckPDF( pdf2, debug );
    CheckPDF( pdf3, debug );
    
    TString pdfName = typemode+"_"+varName+"_JohnsonSUPlus2Gaussian_"+samplemode;
    pdf = new RooAddPdf( pdfName.Data(), pdfName.Data(), RooArgList(*pdf1, *pdf2, *pdf3), RooArgList(*frac1GVar, *frac2GVar));
    CheckPDF( pdf, debug );
    
    return pdf;
  }

} // end of namespace

//=============================================================================
