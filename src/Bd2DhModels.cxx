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
#include "RooPolynomial.h"
#include "RooGaussian.h"
#include "RooCBShape.h"
#include "RooFFTConvPdf.h"
#include "RooDecay.h"
#include "RooEffProd.h"
#include "RooWorkspace.h"

// B2DXFitters includes
#include "B2DXFitters/Bd2DhModels.h"
#include "B2DXFitters/GeneralUtils.h"
#include "B2DXFitters/RooBinned1DQuinticBase.h"
#include "B2DXFitters/Bs2Dsh2011TDAnaModels.h"
#include "B2DXFitters/RooJohnsonSU.h"
#include "B2DXFitters/RooIpatia2.h"

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

    /*This is quite obsolete and will be fixed at some point (hopefully...)*/

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
  // Build Exponential + constant
  //===============================================================================
  
  RooAbsPdf* buildExponentialPlusConstantPDF( RooAbsReal& obs,
                                              RooWorkspace* workInt,
                                              TString samplemode,
                                              TString typemode,
                                              bool debug)
  {
    if ( debug == true )
    {
      std::cout<<"Bd2DhModels::buildExponentialPlusConstantPDF(..)==> building exponential plus constant pdf... "<<std::endl; 
    }
    
    RooRealVar* cBVar = NULL;
    RooRealVar* fracExpoVar = NULL;
    
    TString varName = obs.GetName();
    
    TString cBName = typemode+"_"+varName+"_cB_"+samplemode;
    cBVar = tryVar(cBName, workInt, debug);
    TString fracExpoName = typemode+"_"+varName+"_fracExpo_"+samplemode;
    fracExpoVar = tryVar(fracExpoName, workInt, debug);
    
    RooAbsPdf* pdf = NULL;
    
    RooExponential *pdf1 = NULL;
    TString pdf1Name = typemode+"_"+varName+"_exponential_"+samplemode;
    RooPolynomial *pdf2 = NULL;
    TString pdf2Name = typemode+"_"+varName+"_constant_"+samplemode;
    
    pdf1 = new RooExponential( pdf1Name.Data(), pdf1Name.Data(), obs, *cBVar);
    pdf2 = new RooPolynomial( pdf2Name.Data(), pdf2Name.Data(), obs);

    TString pdfName = typemode+"_"+varName+"_ExponentialPlusConstant_"+samplemode;
    pdf = new RooAddPdf( pdfName.Data(), pdfName.Data(), RooArgList(*pdf1, *pdf2), *fracExpoVar);
    CheckPDF( pdf, debug );

    return pdf;
  }  

  //===============================================================================
  // Build JohnsonSU pdf
  //===============================================================================
  
  RooAbsPdf* buildJohnsonSUPDF( RooAbsReal& obs,
                                RooWorkspace* workInt,
                                TString samplemode,
                                TString typemode,
                                bool shiftMean,
                                bool debug)
  { 
    if ( debug == true )
    {   
      std::cout<<"Bd2DhModels::buildJohnsonSUPDF(..)==> building JohnsonSU pdf... "<<std::endl; 
    }

    RooRealVar* mean = NULL;    
    RooRealVar* shiftVar = NULL;
    RooFormulaVar *meanShiftVar = NULL;
    RooRealVar* sigmaVar =NULL;
    RooRealVar* nuVar =NULL;
    RooRealVar* tauVar =NULL;

    TString varName = obs.GetName();

    TString meanName = typemode+"_"+varName+"_mean_"+samplemode;
    mean = tryVar(meanName, workInt, debug);
    if (mean == NULL) mean = tryVar("Signal_"+varName+"_mean_"+samplemode, workInt, debug);
    if (shiftMean)
    {  
      TString shiftVarName = typemode+"_"+varName+"_shift_"+samplemode; 
      shiftVar = tryVar(shiftVarName, workInt, debug);
      TString meanShiftVarName = typemode+"_"+varName+"_meanShift_"+samplemode;
      meanShiftVar = new RooFormulaVar(meanShiftVarName.Data(), meanShiftVarName.Data(), "@0+@1", RooArgList(*mean,*shiftVar));
    }
    TString sigmaName = typemode+"_"+varName+"_sigma_"+samplemode;
    sigmaVar = tryVar(sigmaName, workInt, debug);
    TString nuName = typemode+"_"+varName+"_nu_"+samplemode;
    nuVar = tryVar(nuName, workInt, debug);
    TString tauName = typemode+"_"+varName+"_tau_"+samplemode;
    tauVar = tryVar(tauName, workInt, debug);
    
    RooJohnsonSU* pdf = NULL;
    TString pdfName = typemode+"_"+varName+"_johnsonSU_"+samplemode;
    if(shiftMean)
      pdf = new RooJohnsonSU( pdfName.Data(), pdfName.Data(), obs, *meanShiftVar, *sigmaVar, *nuVar, *tauVar);
    else
      pdf = new RooJohnsonSU( pdfName.Data(), pdfName.Data(), obs, *mean, *sigmaVar, *nuVar, *tauVar);    
    CheckPDF( pdf, debug );

    return pdf;  
  }

  //===============================================================================
  // Build Crystal Ball + Exponential
  //===============================================================================

  RooAbsPdf* buildCrystalBallPlusExponentialPDF( RooAbsReal& obs,
                                                 RooWorkspace* workInt,
                                                 TString samplemode,
                                                 TString typemode,
                                                 bool shiftMean,
                                                 bool debug)
  {
    if ( debug == true )
    {
      std::cout<<"Bd2DhModels::buildCrystalBallPlusExponentialPDF(..)==> building crystal ball + exponential pdf..."<<std::endl; 
    } 

    RooRealVar* mean = NULL;
    RooRealVar* alphaVar = NULL;
    RooRealVar* nVar = NULL;
    RooRealVar* sigmaCBVar =NULL;
    RooRealVar* shiftVar = NULL;
    RooFormulaVar* meanShiftVar = NULL;
    RooRealVar* cBVar = NULL;
    RooRealVar* fracExpoVar = NULL;

    TString varName = obs.GetName();
    TString alphaName = typemode+"_"+varName+"_alpha_"+samplemode;
    alphaVar = tryVar(alphaName, workInt, debug);
    TString nName = typemode+"_"+varName+"_n_"+samplemode;
    nVar = tryVar(nName, workInt, debug);
    TString sigmaCBName = typemode+"_"+varName+"_sigmaCB_"+samplemode;
    sigmaCBVar = tryVar(sigmaCBName, workInt, debug);
    TString meanName = typemode+"_"+varName+"_mean_"+samplemode;
    mean = tryVar(meanName, workInt, debug);
    if(mean == NULL) mean = tryVar("Signal_"+varName+"_mean_"+samplemode, workInt, debug);
    if(shiftMean)
    {
      TString shiftVarName = typemode+"_"+varName+"_shift_"+samplemode;
      shiftVar = tryVar(shiftVarName, workInt, debug);
      TString meanShiftVarName = typemode+"_"+varName+"_meanShift_"+samplemode;
      meanShiftVar = new RooFormulaVar(meanShiftVarName.Data(), meanShiftVarName.Data(), "@0+@1", RooArgList(*mean,*shiftVar)); 
    } 
    TString cBName = typemode+"_"+varName+"_cB_"+samplemode;
    cBVar = tryVar(cBName, workInt, debug);
    TString fracExpoName = typemode+"_"+varName+"_fracExpo_"+samplemode;
    fracExpoVar = tryVar(fracExpoName, workInt, debug);
    
    RooAbsPdf* pdf = NULL;

    RooCBShape *pdf1 = NULL;
    TString pdf1Name = typemode+"_"+varName+"_crystalball_"+samplemode;
    RooExponential *pdf2 = NULL;
    TString pdf2Name = typemode+"_"+varName+"_exponential_"+samplemode;

    if(shiftMean)
    {
      pdf1 = new RooCBShape( pdf1Name.Data(), pdf1Name.Data(), obs, *meanShiftVar, *sigmaCBVar, *alphaVar, *nVar);
    }    
    else
    {
      pdf1 = new RooCBShape( pdf1Name.Data(), pdf1Name.Data(), obs, *mean, *sigmaCBVar, *alphaVar, *nVar);
    }

    pdf2 = new RooExponential(pdf2Name.Data(), pdf2Name.Data(), obs, *cBVar);

    TString pdfName = typemode+"_"+varName+"_CrystalBallPlusExponential_"+samplemode;
    pdf = new RooAddPdf( pdfName.Data(), pdfName.Data(), *pdf2, *pdf1, *fracExpoVar);
    CheckPDF( pdf, debug );

    return pdf;

  }
  

  //===============================================================================  
  // Build Crystal Ball + gaussian pdf
  //===============================================================================

  RooAbsPdf* buildCrystalBallPlusGaussianPDF( RooAbsReal& obs,
                                              RooWorkspace* workInt,
                                              TString samplemode,
                                              TString typemode,
                                              bool shiftMean,
                                              bool scaleWidths,
                                              bool debug)
  {
    if ( debug == true )
    {  
      std::cout<<"Bd2DhModels::buildCrystalBallPlusGaussianPDF(..)==> building crystal ball + gaussian pdf..."<<std::endl; 
    }

    RooRealVar* mean = NULL;
    RooRealVar* alphaVar = NULL;
    RooRealVar* nVar = NULL;
    RooRealVar* sigmaCBVar = NULL;
    RooRealVar* shiftVar = NULL;
    RooFormulaVar* meanShiftVar = NULL;
    RooRealVar* sigmaGVar = NULL;
    RooRealVar* scaleSigmaVar = NULL;
    RooFormulaVar* scaledSigmaCBVar = NULL;
    RooFormulaVar* scaledSigmaGVar = NULL;
    RooRealVar* fracGVar = NULL;

    TString varName = obs.GetName();
    TString alphaName = typemode+"_"+varName+"_alpha_"+samplemode;
    alphaVar = tryVar(alphaName, workInt, debug);
    TString nName = typemode+"_"+varName+"_n_"+samplemode;
    nVar = tryVar(nName, workInt, debug);

    TString sigmaCBName = typemode+"_"+varName+"_sigmaCB_"+samplemode;
    sigmaCBVar = tryVar(sigmaCBName, workInt, debug);
    if (sigmaCBVar == NULL) sigmaCBVar = tryVar("Signal_"+varName+"_sigmaCB_"+samplemode, workInt, debug);
    TString sigmaGName = typemode+"_"+varName+"_sigmaG_"+samplemode;
    sigmaGVar = tryVar(sigmaGName, workInt, debug);
    if (sigmaGVar == NULL) sigmaGVar = tryVar("Signal_"+varName+"_sigmaG_"+samplemode, workInt, debug);
    if(scaleWidths)
    {
      TString scaleSigmaVarName = typemode+"_"+varName+"_scaleSigma_"+samplemode;
      scaleSigmaVar = tryVar(scaleSigmaVarName, workInt, debug);
      if(scaleSigmaVar == NULL) scaleSigmaVar = tryVar("Signal_"+varName+"_scaleSigma_"+samplemode, workInt, debug);
      
      TString scaledSigmaCBVarName = typemode+"_"+varName+"_scaledSigmaCB_"+samplemode;
      scaledSigmaCBVar = new RooFormulaVar(scaledSigmaCBVarName.Data(), scaledSigmaCBVarName.Data(), "@0*@1", RooArgList(*scaleSigmaVar,*sigmaCBVar));
      
      TString scaledSigmaGVarName = typemode+"_"+varName+"_scaledSigmaG_"+samplemode;
      scaledSigmaGVar = new RooFormulaVar(scaledSigmaGVarName.Data(), scaledSigmaGVarName.Data(), "@0*@1", RooArgList(*scaleSigmaVar,*sigmaGVar));

    }    

    TString meanName = typemode+"_"+varName+"_mean_"+samplemode;
    mean = tryVar(meanName, workInt, debug);
    if(mean == NULL) mean = tryVar("Signal_"+varName+"_mean_"+samplemode, workInt, debug);
    if(shiftMean)
    {
      TString shiftVarName = typemode+"_"+varName+"_shift_"+samplemode;
      shiftVar = tryVar(shiftVarName, workInt, debug);
      TString meanShiftVarName = typemode+"_"+varName+"_meanShift_"+samplemode;
      meanShiftVar = new RooFormulaVar(meanShiftVarName.Data(), meanShiftVarName.Data(), "@0+@1", RooArgList(*mean,*shiftVar));
    }
    
    TString fracGName = typemode+"_"+varName+"_fracG_"+samplemode;
    fracGVar = tryVar(fracGName, workInt, debug);
    
    RooAbsPdf* pdf = NULL;
    
    RooCBShape *pdf1 = NULL;
    TString pdf1Name = typemode+"_"+varName+"_crystalball_"+samplemode;
    RooGaussian *pdf2 = NULL;
    TString pdf2Name = typemode+"_"+varName+"_gaussian_"+samplemode;

    if(scaleWidths)
    {
      if(shiftMean)
      {
        pdf1 = new RooCBShape( pdf1Name.Data(), pdf1Name.Data(), obs, *meanShiftVar, *scaledSigmaCBVar, *alphaVar, *nVar);
        pdf2 = new RooGaussian( pdf2Name.Data(), pdf2Name.Data(), obs, *meanShiftVar, *scaledSigmaGVar); 
      }
      else
      {
        pdf1 = new RooCBShape( pdf1Name.Data(), pdf1Name.Data(), obs, *mean, *scaledSigmaCBVar, *alphaVar, *nVar);
        pdf2 = new RooGaussian( pdf2Name.Data(), pdf2Name.Data(), obs, *mean, *scaledSigmaGVar); 
      }
    }
    else
    {
      if(shiftMean)
      {
        pdf1 = new RooCBShape( pdf1Name.Data(), pdf1Name.Data(), obs, *meanShiftVar, *sigmaCBVar, *alphaVar, *nVar);
        pdf2 = new RooGaussian( pdf2Name.Data(), pdf2Name.Data(), obs, *meanShiftVar, *sigmaGVar);
      }
      else
      {
        pdf1 = new RooCBShape( pdf1Name.Data(), pdf1Name.Data(), obs, *mean, *sigmaCBVar, *alphaVar, *nVar);
        pdf2 = new RooGaussian( pdf2Name.Data(), pdf2Name.Data(), obs, *mean, *sigmaGVar);
      }
    }
    

    TString pdfName = typemode+"_"+varName+"_CrystalBallPlusGaussian_"+samplemode;
    pdf = new RooAddPdf( pdfName.Data(), pdfName.Data(), *pdf1, *pdf2, *fracGVar);
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
                                            bool sameMean,
                                            bool shiftMean,
                                            bool debug)
  {
    if ( debug == true )
    {
      std::cout<<"Bd2DhModels::buildJohnsonSUPlusGaussianPDF(..)==> building JohnsonSU + gaussian pdf..."<<std::endl;
    }

    RooRealVar* meanJ = NULL;
    RooRealVar* shiftVar = NULL;
    RooFormulaVar* meanShiftVar = NULL;
    RooRealVar* sigmaJVar =NULL;
    RooRealVar* nuJVar =NULL;
    RooRealVar* tauJVar =NULL;
    RooRealVar* meanGshift = NULL;
    RooFormulaVar* meanG = NULL;
    RooRealVar* sigmaGVar =NULL;
    RooRealVar* fracVar = NULL;

    TString varName = obs.GetName();
    
    TString meanJName = typemode+"_"+varName+"_meanJ_"+samplemode;
    meanJ = tryVar(meanJName, workInt, debug);
    if (meanJ == NULL) meanJ = tryVar("Signal_"+varName+"_mean_"+samplemode, workInt, debug);
    if(shiftMean)
    {  
      TString shiftVarName = typemode+"_"+varName+"_shift_"+samplemode; 
      shiftVar = tryVar(shiftVarName, workInt, debug);
      TString meanShiftVarName = typemode+"_"+varName+"_meanShift_"+samplemode;
      meanShiftVar = new RooFormulaVar(meanShiftVarName.Data(), meanShiftVarName.Data(), "@0+@1", RooArgList(*meanJ,*shiftVar));
    }
    
    TString sigmaJName = typemode+"_"+varName+"_sigmaJ_"+samplemode;
    sigmaJVar = tryVar(sigmaJName, workInt, debug);
    TString nuJName = typemode+"_"+varName+"_nuJ_"+samplemode;
    nuJVar = tryVar(nuJName, workInt, debug);
    TString tauJName = typemode+"_"+varName+"_tauJ_"+samplemode;
    tauJVar = tryVar(tauJName, workInt, debug);
    if(!sameMean)
    { 
      TString meanGshiftName = typemode+"_"+varName+"_meanGshift_"+samplemode;
      meanGshift = tryVar(meanGshiftName, workInt, debug);
      TString meanGName = typemode+"_"+varName+"_meanG_"+samplemode;
      if(shiftMean)
        meanG = new RooFormulaVar(meanGName.Data(), meanGName.Data(),"@0+@1+@2",RooArgList(*meanJ,*shiftVar,*meanGshift));
      else
        meanG = new RooFormulaVar(meanGName.Data(), meanGName.Data(),"@0+@1",RooArgList(*meanJ,*meanGshift));
    }
    TString sigmaGName = typemode+"_"+varName+"_sigmaG_"+samplemode;
    sigmaGVar = tryVar(sigmaGName, workInt, debug);
    TString fracName = typemode+"_"+varName+"_frac_"+samplemode;
    fracVar = tryVar(fracName, workInt, debug);
  
    RooAbsPdf* pdf = NULL; 

    RooGaussian *pdf1 = NULL;
    TString pdf1Name = typemode+"_"+varName+"_gaussian_"+samplemode;
    RooJohnsonSU *pdf2 = NULL;
    TString pdf2Name = typemode+"_"+varName+"_johnsonSU_"+samplemode;
    if(sameMean)
    {
      if(shiftMean)
        pdf1 = new RooGaussian( pdf1Name.Data(), pdf1Name.Data(), obs, *meanShiftVar, *sigmaGVar);
      else
        pdf1 = new RooGaussian( pdf1Name.Data(), pdf1Name.Data(), obs, *meanJ, *sigmaGVar);
    }
    else
    {
      pdf1 = new RooGaussian( pdf1Name.Data(), pdf1Name.Data(), obs, *meanG, *sigmaGVar);     
    }

    if(shiftMean)
      pdf2 = new RooJohnsonSU( pdf2Name.Data(), pdf2Name.Data(), obs, *meanShiftVar, *sigmaJVar, *nuJVar, *tauJVar);
    else
      pdf2 = new RooJohnsonSU( pdf2Name.Data(), pdf2Name.Data(), obs, *meanJ, *sigmaJVar, *nuJVar, *tauJVar);
    

    TString pdfName = typemode+"_"+varName+"_JohnsonSUPlusGaussian_"+samplemode;
    pdf = new RooAddPdf( pdfName.Data(), pdfName.Data(), *pdf1, *pdf2, *fracVar);
    CheckPDF( pdf, debug );
    
    return pdf;
  }
  
  //===============================================================================
  // Build JohnsonSU + gaussian + exponential pdf
  //===============================================================================

  RooAbsPdf* buildJohnsonSUPlusGaussianPlusExponentialPDF( RooAbsReal& obs,
                                                           RooWorkspace* workInt,
                                                           TString samplemode,
                                                           TString typemode,
                                                           bool sameMean,
                                                           bool debug)
  {
    
    if ( debug == true )
    {
      std::cout<<"Bd2DhModels::buildJohnsonSUPlusGaussianPlusExponentialPDF(..)==> building JohnsonSU + gaussian + exponential pdf..."<<std::endl;
    }
    

    RooRealVar* meanJ = NULL;
    RooRealVar* sigmaJVar =NULL;
    RooRealVar* nuJVar =NULL;
    RooRealVar* tauJVar =NULL;
    RooRealVar* meanGshift = NULL;
    RooFormulaVar* meanG = NULL;
    RooRealVar* sigmaGVar =NULL;
    RooRealVar* cBVar = NULL;
    RooRealVar* fracSignalVar = NULL;
    RooRealVar* fracExpoVar = NULL;

    TString varName = obs.GetName();

    TString meanJName = typemode+"_"+varName+"_meanJ_"+samplemode;
    meanJ = tryVar(meanJName, workInt, debug);
    TString sigmaJName = typemode+"_"+varName+"_sigmaJ_"+samplemode;
    sigmaJVar = tryVar(sigmaJName, workInt, debug);
    TString nuJName = typemode+"_"+varName+"_nuJ_"+samplemode;
    nuJVar = tryVar(nuJName, workInt, debug);
    TString tauJName = typemode+"_"+varName+"_tauJ_"+samplemode;
    tauJVar = tryVar(tauJName, workInt, debug);
    if(!sameMean)
    {
      TString meanGshiftName = typemode+"_"+varName+"_meanGshift_"+samplemode;
      meanGshift = tryVar(meanGshiftName, workInt, debug);
      TString meanGName = typemode+"_"+varName+"_meanG_"+samplemode;
      meanG = new RooFormulaVar(meanGName.Data(), meanGName.Data(),"@0+@1",RooArgList(*meanJ,*meanGshift));
    }
    TString sigmaGName = typemode+"_"+varName+"_sigmaG_"+samplemode;
    sigmaGVar = tryVar(sigmaGName, workInt, debug);
    TString cBName = typemode+"_"+varName+"_cB_"+samplemode;
    cBVar = tryVar(cBName, workInt, debug);
    TString fracSignalName = typemode+"_"+varName+"_relFracSignal_"+samplemode;
    fracSignalVar = tryVar(fracSignalName, workInt, debug);
    TString fracExpoName = typemode+"_"+varName+"_fracExpo_"+samplemode;
    fracExpoVar = tryVar(fracExpoName, workInt, debug);

    RooAbsPdf* pdf = NULL;

    RooGaussian *pdf1 = NULL;    
    TString pdf1Name = typemode+"_"+varName+"_gaussian_"+samplemode;
    RooJohnsonSU *pdf2 = NULL;
    TString pdf2Name = typemode+"_"+varName+"_johnsonSU_"+samplemode;
    RooExponential *pdf3 = NULL;
    TString pdf3Name = typemode+"_"+varName+"_exponential_"+samplemode;
    if(sameMean)
    {
      pdf1 = new RooGaussian( pdf1Name.Data(), pdf1Name.Data(), obs, *meanJ, *sigmaGVar);
    }
    else
    {
      pdf1 = new RooGaussian( pdf1Name.Data(), pdf1Name.Data(), obs, *meanG, *sigmaGVar);
    }
    pdf2 = new RooJohnsonSU( pdf2Name.Data(), pdf2Name.Data(), obs, *meanJ, *sigmaJVar, *nuJVar, *tauJVar);
    pdf3 = new RooExponential( pdf3Name.Data(), pdf3Name.Data(), obs, *cBVar);

    RooAddPdf *pdfSignal = NULL;
    TString pdfSignalName = typemode+"_"+varName+"_signal_"+samplemode;
    pdfSignal = new RooAddPdf( pdfSignalName.Data(), pdfSignalName.Data(), *pdf1, *pdf2, *fracSignalVar);

    TString pdfName = typemode+"_"+varName+"_JohnsonSUPlusGaussianPlusExponential_"+samplemode;
    pdf = new RooAddPdf( pdfName.Data(), pdfName.Data(), RooArgList(*pdf3, *pdfSignal), *fracExpoVar);
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
    RooRealVar* meanG1shift = NULL;
    RooRealVar* meanG2shift = NULL;
    RooFormulaVar* meanG1 = NULL;
    RooFormulaVar* meanG2 = NULL;
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
    if(!sameMean)
    {
      TString meanG1shiftName = typemode+"_"+varName+"_meanG1shift_"+samplemode;
      meanG1shift = tryVar(meanG1shiftName, workInt, debug);
      TString meanG1Name = typemode+"_"+varName+"_meanG1_"+samplemode;
      meanG1 = new RooFormulaVar(meanG1Name.Data(), meanG1Name.Data(),"@0+@1",RooArgList(*meanJ,*meanG1shift));
      TString meanG2shiftName = typemode+"_"+varName+"_meanG2shift_"+samplemode;
      meanG2shift = tryVar(meanG2shiftName, workInt, debug);
      TString meanG2Name = typemode+"_"+varName+"_meanG2_"+samplemode;
      meanG2 = new RooFormulaVar(meanG2Name.Data(), meanG2Name.Data(),"@0+@1",RooArgList(*meanJ,*meanG2shift));
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

    if(sameMean)
    {
      pdf1 = new RooGaussian( pdf1Name.Data(), pdf1Name.Data(), obs, *meanJ, *sigma1GVar);
      pdf2 = new RooGaussian( pdf2Name.Data(), pdf2Name.Data(), obs, *meanJ, *sigma2GVar);
    }
    else
    {
      pdf1 = new RooGaussian( pdf1Name.Data(), pdf1Name.Data(), obs, *meanG1, *sigma1GVar);
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

  //===============================================================================                                                                                                          
  // Build Ipatia + exponential pdf                          
  //===============================================================================

  RooAbsPdf* buildIpatiaPlusExponentialPDF(RooAbsReal& obs,
                                           RooWorkspace* workInt,
                                           TString samplemode,
                                           TString typemode,
                                           bool debug)
  {
    if ( debug == true )
    {
      std::cout<<"Bd2DhModels::buildIpatiaPlusExponentialPDF(..)==> building Ipatia + Exponential pdf..."<<std::endl; 
    }

    RooRealVar* lVar = NULL;
    RooRealVar* zetaVar = NULL;
    RooRealVar* fbVar = NULL;
    RooRealVar* meanVar = NULL;
    RooRealVar* sigmaVar = NULL;
    RooRealVar* a1Var = NULL;
    RooRealVar* n1Var = NULL;
    RooRealVar* a2Var = NULL;
    RooRealVar* n2Var = NULL;
    RooRealVar* cBVar = NULL;
    RooRealVar* fracVar = NULL;
    
    TString varName = obs.GetName();

    TString lVarName = typemode+"_"+varName+"_l_"+samplemode;
    lVar = tryVar(lVarName, workInt, debug);
    TString zetaVarName = typemode+"_"+varName+"_zeta_"+samplemode;
    zetaVar = tryVar(zetaVarName, workInt, debug);
    TString fbVarName = typemode+"_"+varName+"_fb_"+samplemode;
    fbVar = tryVar(fbVarName, workInt, debug);
    TString meanVarName = typemode+"_"+varName+"_mean_"+samplemode;
    meanVar = tryVar(meanVarName, workInt, debug);
    if (meanVar == NULL) meanVar = tryVar("Signal_"+varName+"_mean_"+samplemode, workInt, debug);
    TString sigmaVarName = typemode+"_"+varName+"_sigma_"+samplemode;
    sigmaVar = tryVar(sigmaVarName, workInt, debug);
    if (sigmaVar == NULL) sigmaVar = tryVar("Signal_"+varName+"_sigma_"+samplemode, workInt, debug);;
    TString a1VarName = typemode+"_"+varName+"_a1_"+samplemode;
    a1Var = tryVar(a1VarName, workInt, debug);
    TString n1VarName = typemode+"_"+varName+"_n1_"+samplemode;
    n1Var = tryVar(n1VarName, workInt, debug);
    TString a2VarName = typemode+"_"+varName+"_a2_"+samplemode;
    a2Var = tryVar(a2VarName, workInt, debug);
    TString n2VarName = typemode+"_"+varName+"_n2_"+samplemode;
    n2Var = tryVar(n2VarName, workInt, debug);
    TString cBVarName = typemode+"_"+varName+"_cB_"+samplemode;
    cBVar = tryVar(cBVarName, workInt, debug);
    TString fracVarName = typemode+"_"+varName+"_frac_"+samplemode;
    fracVar = tryVar(fracVarName, workInt, debug);

    RooIpatia2* pdf1 = NULL;
    TString pdf1Name = typemode+"_"+varName+"_ipatia_"+samplemode;
    pdf1 = new RooIpatia2( pdf1Name.Data(), pdf1Name.Data(), obs, *lVar, *zetaVar, *fbVar, *sigmaVar, *meanVar, *a1Var, *n1Var, *a2Var, *n2Var);
  
    RooExponential* pdf2 = NULL;
    TString pdf2Name = typemode+"_"+varName+"_exponential_"+samplemode;
    pdf2 = new RooExponential( pdf2Name.Data(), pdf2Name.Data(), obs, *cBVar);

    TString pdfName = typemode+"_"+varName+"_IpatiaPlusExponential_"+samplemode;
    RooAddPdf* pdf = NULL;
    pdf = new RooAddPdf( pdfName.Data(), pdfName.Data(), RooArgList(*pdf1, *pdf2), *fracVar);
    CheckPDF( pdf, debug );

    return pdf;
  }
  

  //===============================================================================
  // Build Ipatia * gaussian pdf                                                                                                             
  //===============================================================================

  RooAbsPdf* buildIpatiaGaussConvPDF(RooRealVar& obs,
                                     RooWorkspace* workInt,
                                     TString samplemode,
                                     TString typemode,
                                     bool shiftMean,
                                     bool debug)
  {
    
    if ( debug == true ) 
    {
      std::cout<<"Bd2DhModels::buildIpatiaGaussConvPDF(..)==> building Ipatia * Gaussian pdf..."<<std::endl;
    }

    RooRealVar* lVar = NULL;    
    RooRealVar* zetaVar = NULL;
    RooRealVar* fbVar = NULL;
    RooRealVar* meanVar = NULL;
    RooRealVar* sigmaIVar = NULL;
    RooRealVar* sigmaGVar = NULL;
    RooRealVar* shiftVar = NULL;
    RooFormulaVar *meanShiftVar = NULL;
    RooRealVar* a1Var = NULL;
    RooRealVar* n1Var = NULL;
    RooRealVar* a2Var = NULL;
    RooRealVar* n2Var = NULL;

    TString varName = obs.GetName();

    TString lVarName = typemode+"_"+varName+"_l_"+samplemode;
    lVar = tryVar(lVarName, workInt, debug);
    TString zetaVarName = typemode+"_"+varName+"_zeta_"+samplemode;
    zetaVar = tryVar(zetaVarName, workInt, debug);
    TString fbVarName = typemode+"_"+varName+"_fb_"+samplemode;
    fbVar = tryVar(fbVarName, workInt, debug);
    TString meanVarName = typemode+"_"+varName+"_mean_"+samplemode;
    meanVar = tryVar(meanVarName, workInt, debug);
    if(meanVar == NULL) meanVar = tryVar("Signal_"+varName+"_mean_"+samplemode, workInt, debug);
    if (shiftMean)
    {
      TString shiftVarName = typemode+"_"+varName+"_shift_"+samplemode;
      shiftVar = tryVar(shiftVarName, workInt, debug);
      TString meanShiftVarName = typemode+"_"+varName+"_meanShift_"+samplemode;
      meanShiftVar = new RooFormulaVar(meanShiftVarName.Data(), meanShiftVarName.Data(), "@0+@1", RooArgList(*meanVar,*shiftVar)); 
    }
    TString sigmaIVarName = typemode+"_"+varName+"_sigmaI_"+samplemode;
    sigmaIVar = tryVar(sigmaIVarName, workInt, debug);
    if(sigmaIVar == NULL) meanVar = tryVar("Signal_"+varName+"_sigmaI_"+samplemode, workInt, debug);
    TString sigmaGVarName = typemode+"_"+varName+"_sigmaG_"+samplemode;
    sigmaGVar = tryVar(sigmaGVarName, workInt, debug);
    TString a1VarName = typemode+"_"+varName+"_a1_"+samplemode;
    a1Var = tryVar(a1VarName, workInt, debug);
    TString n1VarName = typemode+"_"+varName+"_n1_"+samplemode;
    n1Var = tryVar(n1VarName, workInt, debug);
    TString a2VarName = typemode+"_"+varName+"_a2_"+samplemode;
    a2Var = tryVar(a2VarName, workInt, debug);
    TString n2VarName = typemode+"_"+varName+"_n2_"+samplemode;
    n2Var = tryVar(n2VarName, workInt, debug);

    RooIpatia2* pdf1 = NULL;
    TString pdf1Name = typemode+"_"+varName+"_ipatia_"+samplemode;
    if(shiftMean)
      pdf1 = new RooIpatia2( pdf1Name.Data(), pdf1Name.Data(), obs, *lVar, *zetaVar, *fbVar, *sigmaIVar, *meanShiftVar, *a1Var, *n1Var, *a2Var, *n2Var);
    else
      pdf1 = new RooIpatia2( pdf1Name.Data(), pdf1Name.Data(), obs, *lVar, *zetaVar, *fbVar, *sigmaIVar, *meanVar, *a1Var, *n1Var, *a2Var, *n2Var);
    
    RooGaussian* pdf2 = NULL;
    TString pdf2Name = typemode+"_"+varName+"_gauss_"+samplemode;
    RooRealVar *mean0 = new RooRealVar(typemode+"_"+varName+"_mean0_"+samplemode,
                                       typemode+"_"+varName+"_mean0_"+samplemode,
                                       0.0);
    pdf2 = new RooGaussian( pdf2Name.Data(), pdf2Name.Data(), obs, *mean0, *sigmaGVar);

    RooFFTConvPdf* pdf = NULL;
    TString pdfName = typemode+"_"+varName+"_ipatiagauss_"+samplemode;
    pdf = new RooFFTConvPdf( pdfName.Data(), pdfName.Data(), obs, *pdf1, *pdf2);
    
    CheckPDF( pdf, debug );

    return pdf;
    

  }
  

} // end of namespace

//=============================================================================
