// ROOT and RooFit includes
#include "RooFormulaVar.h"
#include "RooAddPdf.h"
#include "RooKeysPdf.h"
#include "RooExtendPdf.h"
#include "RooEffProd.h"
#include "RooGaussian.h"
#include "RooDecay.h"
#include "RooBDecay.h"
#include "RooCBShape.h"
#include "RooWorkspace.h"
#include "RooRealVar.h"
#include "RooExponential.h"
#include "RooProdPdf.h"
#include "RooGenericPdf.h" 
#include "TFile.h"
#include "TTree.h"
#include "RooDataSet.h"
#include "RooArgSet.h"
#include "RooHistPdf.h"
#include <string>
#include <vector>
#include <fstream>


#include "B2DXFitters/Bs2Dsh2011TDAnaModels.h"
#include "B2DXFitters/GeneralUtils.h"
#include "B2DXFitters/RooBinned1DQuinticBase.h"
#include "B2DXFitters/RooIpatia2.h" 
#include "B2DXFitters/RooApollonios.h"

using namespace std;
using namespace GeneralUtils;

namespace Bs2Dsh2011TDAnaModels {


  //===============================================================================                                                                                                
  // Crystal Ball                                                                                                                                                                        
  //===============================================================================  
  RooAbsPdf* buildCrystalBallPDF( RooAbsReal& obs, 
                                  RooWorkspace* workInt, 
                                  TString samplemode, 
                                  TString typemode, 
                                  bool debug)
  {
    if ( debug == true ) { std::cout<<"[INFO] --------- build double Crystal Ball -------- "<<std::endl; }

    RooRealVar* mean = NULL;
    RooRealVar* alpha1Var = NULL;
    RooRealVar* n1Var = NULL;
    RooRealVar* sigma1Var =NULL;

    TString varName = obs.GetName();

    TString meanName = typemode+"_"+varName+"_mean_"+samplemode;
    mean = tryVar(meanName, workInt, debug);
    TString alpha1Name = typemode+"_"+varName+"_alpha_"+samplemode;
    alpha1Var = tryVar(alpha1Name, workInt, debug);
    TString n1Name = typemode+"_"+varName+"_n_"+samplemode;
    n1Var = tryVar(n1Name, workInt, debug);
    TString sigma1Name = typemode+"_"+varName+"_sigma_"+samplemode;
    sigma1Var = tryVar(sigma1Name, workInt, debug);
    
    RooCBShape* pdf = NULL;
    TString pdfName = typemode+"_"+varName+"_crystalBall_"+samplemode;
    pdf = new RooCBShape( pdfName.Data(), pdfName.Data(), obs, *mean, *sigma1Var, *alpha1Var, *n1Var);
       
    CheckPDF( pdf, debug );
    return pdf; 
  }

  //===============================================================================
  // Double crystal ball function
  //===============================================================================

  RooAbsPdf* buildDoubleCrystalBallPDF( RooAbsReal& obs,
                                        RooWorkspace* workInt,
                                        TString samplemode,
                                        TString type,
                                        bool widthRatio,
                                        bool sharedMean,
                                        bool debug)
  {

    if ( debug == true ) { std::cout<<"[INFO] --------- build double Crystal Ball -------- "<<std::endl; }

    RooRealVar* mean = NULL;
    RooRealVar* alpha1Var = NULL;
    RooRealVar* alpha2Var =NULL;
    RooRealVar* n1Var = NULL;
    RooRealVar* n2Var =NULL;
    RooRealVar* sigma1Var =NULL;
    RooRealVar* sigma2Var = NULL;
    RooRealVar* fracVar = NULL;
    RooFormulaVar* sigma1For = NULL;
    RooFormulaVar* sigma2For = NULL;
    RooRealVar* R = NULL;

    TString varName = obs.GetName();

    TString meanName = type+"_"+varName+"_mean_"+samplemode;
    if ( sharedMean) { meanName = "Signal_"+varName+"_mean_"+samplemode; }
    mean = tryVar(meanName, workInt, debug);
    TString alpha1Name = type+"_"+varName+"_alpha1_"+samplemode;
    alpha1Var = tryVar(alpha1Name, workInt, debug);
    TString alpha2Name = type+"_"+varName+"_alpha2_"+samplemode;
    alpha2Var = tryVar(alpha2Name, workInt, debug);
    TString n1Name = type+"_"+varName+"_n1_"+samplemode;
    n1Var = tryVar(n1Name, workInt, debug);
    TString n2Name = type+"_"+varName+"_n2_"+samplemode;
    n2Var = tryVar(n2Name, workInt, debug);
    TString sigma1Name = type+"_"+varName+"_sigma1_"+samplemode;
    sigma1Var = tryVar(sigma1Name, workInt, debug);
    TString sigma2Name = type+"_"+varName+"_sigma2_"+samplemode;
    sigma2Var = tryVar(sigma2Name, workInt, debug);
    TString fracName = type+"_"+varName+"_frac_"+samplemode;
    fracVar = tryVar(fracName, workInt, debug);

    if ( widthRatio )
    {
      TString RName = type+TString("_")+varName+TString("_R_")+samplemode;
      R = tryVar(RName, workInt, debug);
      TString name = type+TString("_") + varName + TString("_sigmafcb1_")+samplemode;
      sigma1For = new RooFormulaVar(name.Data(), name.Data(),"@0*@1", RooArgList(*sigma1Var,*R));
      if ( debug == true ) { std::cout<<"[INFO] Create/read "<<name<<std::endl; }
      name = type+TString("_") + varName + TString("_sigmafcb2_")+samplemode;
      sigma2For = new RooFormulaVar(name.Data(), name.Data(),"@0*@1", RooArgList(*sigma2Var,*R));
      if ( debug == true ) { std::cout<<"[INFO] Create/read "<<name<<std::endl; }
    }
    
    RooAbsPdf* pdf = NULL;

    RooCBShape* pdf1 = NULL;
    TString pdf1Name = type+"_"+varName+"_crystalBall1_"+samplemode;
    RooCBShape* pdf2 = NULL;
    TString pdf2Name = type+"_"+varName+"_crystalBall2_"+samplemode;
    
    if ( widthRatio )
    {
      pdf1 = new RooCBShape( pdf1Name.Data(), pdf1Name.Data(), obs, *mean, *sigma1For, *alpha1Var, *n1Var);
      pdf2 = new RooCBShape( pdf2Name.Data(), pdf2Name.Data(), obs, *mean, *sigma2For, *alpha2Var, *n2Var);
    }
    else
    {
      pdf1 = new RooCBShape( pdf1Name.Data(), pdf1Name.Data(), obs, *mean, *sigma1Var, *alpha1Var, *n1Var);
      pdf2 = new RooCBShape( pdf2Name.Data(), pdf2Name.Data(), obs, *mean, *sigma2Var, *alpha2Var, *n2Var);
    }
    CheckPDF( pdf1, debug );
    CheckPDF( pdf2, debug);

    TString pdfName = type+"_"+varName+"_doubleCrystalBall_"+samplemode;
    pdf = new RooAddPdf( pdfName.Data(), pdfName.Data(), *pdf1, *pdf2, *fracVar);
    CheckPDF( pdf, debug );
    
    return pdf; 
  }


  //===============================================================================  
  // Gaussian                                                                         
  //===============================================================================
  RooAbsPdf* buildGaussPDF( RooAbsReal& obs, 
                            RooWorkspace* workInt, 
                            TString samplemode, 
                            TString typemode,
                            bool shiftMean,
                            bool debug)
  {
    if ( debug == true ) { std::cout<<"[INFO] --------- build Gaussian -------- "<<std::endl; }
    RooRealVar* mean = NULL;
    RooRealVar* sigma1Var =NULL;
    RooRealVar* shiftVar = NULL;
    RooFormulaVar *meanShiftVar = NULL;

    TString varName = obs.GetName();

    TString meanName = typemode+"_"+varName+"_mean_"+samplemode;
    mean = tryVar(meanName, workInt, debug);
    if(mean == NULL) mean = tryVar("Signal_"+varName+"_mean_"+samplemode, workInt, debug);
    if (shiftMean)
    {  
      TString shiftVarName = typemode+"_"+varName+"_shift_"+samplemode; 
      shiftVar = tryVar(shiftVarName, workInt, debug);
      TString meanShiftVarName = typemode+"_"+varName+"_meanShift_"+samplemode;
      meanShiftVar = new RooFormulaVar(meanShiftVarName.Data(), meanShiftVarName.Data(), "@0+@1", RooArgList(*mean,*shiftVar));
    }
    
    TString sigma1Name = typemode+"_"+varName+"_sigma_"+samplemode;
    sigma1Var = tryVar(sigma1Name, workInt, debug);

    RooGaussian* pdf = NULL;
    TString pdfName = typemode+"_"+varName+"_gauss_"+samplemode;
    if(shiftMean)
      pdf = new RooGaussian( pdfName.Data(), pdfName.Data(), obs, *meanShiftVar, *sigma1Var);
    else
      pdf = new RooGaussian( pdfName.Data(), pdfName.Data(), obs, *mean, *sigma1Var);
    
    CheckPDF( pdf, debug );
    
    return pdf; 
  }


  //===============================================================================                                                                                                      
  // Double Gaussian 
  //=============================================================================== 
  RooAbsPdf* buildDoubleGaussPDF( RooAbsReal& obs,
                                  RooWorkspace* workInt,
                                  TString samplemode,
                                  TString typemode,
                                  bool widthRatio, 
                                  bool sharedMean,
                                  bool shiftMean,
                                  bool debug)
  {

    if ( debug == true ) { std::cout<<"[INFO] --------- build double Gaussian -------- "<<std::endl; } 

    RooRealVar* mean = NULL;
    RooRealVar* shiftVar = NULL;
    RooFormulaVar *meanShiftVar = NULL;
    RooRealVar* sigma1Var =NULL;
    RooRealVar* sigma2Var = NULL;
    RooRealVar* fracVar = NULL;
    RooFormulaVar* sigma1For = NULL;
    RooFormulaVar* sigma2For = NULL;
    RooRealVar* R = NULL;
    TString varName = obs.GetName();

    TString meanName = typemode+"_"+varName+"_mean_"+samplemode;
    if ( sharedMean ) { meanName = "Signal_"+varName+"_mean_"+samplemode; }
    mean = tryVar(meanName, workInt, debug);
    if (shiftMean)
    {      
      TString shiftVarName = typemode+"_"+varName+"_shift_"+samplemode; 
      shiftVar = tryVar(shiftVarName, workInt, debug);
      TString meanShiftVarName = typemode+"_"+varName+"_meanShift_"+samplemode;
      meanShiftVar = new RooFormulaVar(meanShiftVarName.Data(), meanShiftVarName.Data(), "@0+@1", RooArgList(*mean,*shiftVar));
    }
    TString sigma1Name = typemode+"_"+varName+"_sigma1_"+samplemode;
    sigma1Var = tryVar(sigma1Name, workInt, debug);
    TString sigma2Name = typemode+"_"+varName+"_sigma2_"+samplemode;
    sigma2Var = tryVar(sigma2Name, workInt, debug);
    TString fracName = typemode+"_"+varName+"_frac_"+samplemode;
    fracVar = tryVar(fracName, workInt, debug);

    if ( widthRatio )
    {
      TString name = typemode+TString("_")+varName+TString("_R");
      R = new RooRealVar(name.Data(),name.Data(), 1.0, 0.8, 1.2);
      name = typemode+TString("_") + varName + TString("_sigmafg1_")+samplemode;
      sigma1For = new RooFormulaVar(name.Data(), name.Data(),"@0*@1", RooArgList(*sigma1Var,*R));
      if ( debug == true ) { std::cout<<"[INFO] Create/read "<<name<<std::endl; }
      name = typemode+TString("_") + varName + TString("_sigmafg2_")+samplemode;
      sigma2For = new RooFormulaVar(name.Data(), name.Data(),"@0*@1", RooArgList(*sigma2Var,*R));
      if ( debug == true ) { std::cout<<"[INFO] Create/read "<<name<<std::endl; }
    }
    
    RooGaussian* pdf1 = NULL;
    TString pdf1Name = typemode+"_"+varName+"_Gauss1_"+samplemode;
    RooGaussian* pdf2 = NULL;
    TString pdf2Name = typemode+"_"+varName+"_Gauss2_"+samplemode;

    if(shiftMean)
    {
      if (widthRatio)
      {  
        pdf1 = new RooGaussian( pdf1Name.Data(), pdf1Name.Data(), obs, *meanShiftVar, *sigma1For); 
        pdf2 = new RooGaussian( pdf2Name.Data(), pdf2Name.Data(), obs, *meanShiftVar, *sigma2For);
      }
      else
      { 
        pdf1 = new RooGaussian( pdf1Name.Data(), pdf1Name.Data(), obs, *meanShiftVar, *sigma1Var); 
        pdf2 = new RooGaussian( pdf2Name.Data(), pdf2Name.Data(), obs, *meanShiftVar, *sigma2Var);
      }
    }
    else
    {  
      if (widthRatio) 
      {
        pdf1 = new RooGaussian( pdf1Name.Data(), pdf1Name.Data(), obs, *mean, *sigma1For);
        pdf2 = new RooGaussian( pdf2Name.Data(), pdf2Name.Data(), obs, *mean, *sigma2For);
      } 
      else
      {
        pdf1 = new RooGaussian( pdf1Name.Data(), pdf1Name.Data(), obs, *mean, *sigma1Var);
        pdf2 = new RooGaussian( pdf2Name.Data(), pdf2Name.Data(), obs, *mean, *sigma2Var);
      }
    }

    CheckPDF( pdf1, debug );
    CheckPDF( pdf2, debug);

    RooAddPdf* pdf = NULL;
    TString pdfName = typemode+"_"+varName+"_doubleGauss_"+samplemode;
    pdf = new RooAddPdf( pdfName.Data(), pdfName.Data(),  *pdf1, *pdf2, *fracVar);
    CheckPDF( pdf, debug );

    return pdf;

  }

  RooAbsPdf* buildExponentialPlusGaussPDF(RooAbsReal& obs,
                                          RooWorkspace* workInt,
                                          TString samplemode,
                                          TString typemode,
                                          bool sharedMean, 
                                          bool debug)
  {
    if ( debug == true ) { std::cout<<"[INFO] --------- build Exponential plus Gaussian -------- "<<std::endl; }

    RooRealVar* mean = NULL;
    RooRealVar* sigma1Var =NULL;
    RooRealVar* fracVar = NULL;
    RooRealVar* cB1Var = NULL; 
    
    TString varName = obs.GetName();

    TString meanName = typemode+"_"+varName+"_mean_"+samplemode;
    if ( sharedMean ) { meanName = "Signal_"+varName+"_mean_"+samplemode; }
    mean = tryVar(meanName, workInt, debug);
    TString sigma1Name = typemode+"_"+varName+"_sigma_"+samplemode;
    sigma1Var = tryVar(sigma1Name, workInt, debug);
    TString fracName = typemode+"_"+varName+"_frac_"+samplemode;
    fracVar = tryVar(fracName, workInt, debug);
    TString cB1VarName = typemode+"_"+varName+"_cB_"+samplemode;
    cB1Var = tryVar(cB1VarName, workInt, debug);

    RooExponential* pdf1 = NULL;
    TString pdf1Name = typemode+"_"+varName+"_expo1_"+samplemode; 
    pdf1 = new RooExponential( pdf1Name.Data(), pdf1Name.Data(), obs, *cB1Var);
    CheckPDF( pdf1, debug );

    RooGaussian* pdf2 = NULL;
    TString pdf2Name = typemode+"_"+varName+"_gauss1_"+samplemode;
    pdf2 = new RooGaussian(pdf2Name.Data(),pdf2Name.Data(), obs,*mean,*sigma1Var);
    CheckPDF( pdf2, debug );

    RooAddPdf* pdf = NULL;
    TString pdfName = typemode+"_"+varName+"_expoGauss_"+samplemode;
    pdf = new RooAddPdf(pdfName.Data(), pdfName.Data(), RooArgList(*pdf1,*pdf2),*fracVar);
    CheckPDF( pdf, debug );

    return pdf; 
  }

  RooAbsPdf* buildExponentialPDF(RooAbsReal& obs, 
                                 RooWorkspace* workInt, 
                                 TString samplemode, 
                                 TString typemode, 
                                 bool debug)
  {
    if ( debug == true ) { std::cout<<"[INFO] --------- build Exponential -------- "<<std::endl; }
    
    RooRealVar* cB1Var = NULL;
    
    TString varName = obs.GetName();

    TString cB1VarName = typemode+"_"+varName+"_cB_"+samplemode;
    cB1Var = tryVar(cB1VarName, workInt, debug);

    RooAbsPdf* pdf = NULL;
    TString pdfName = typemode+"_"+varName+"_expo_"+samplemode;
    pdf = new RooExponential( pdfName.Data(), pdfName.Data(), obs, *cB1Var);
    CheckPDF( pdf, debug );

    return pdf; 
  }

  RooAbsPdf* buildDoubleExponentialPDF(RooAbsReal& obs, 
                                       RooWorkspace* workInt, 
                                       TString samplemode, 
                                       TString typemode, 
                                       bool debug)
  {
    if ( debug == true ) { std::cout<<"[INFO] --------- build double Exponential -------- "<<std::endl; }

    RooRealVar* cB1Var = NULL;
    RooRealVar* cB2Var = NULL;
    RooRealVar* fracVar = NULL;

    TString varName = obs.GetName();

    TString cB1VarName = typemode+"_"+varName+"_cB1_"+samplemode;
    cB1Var = tryVar(cB1VarName, workInt, debug);
    TString cB2VarName = typemode+"_"+varName+"_cB2_"+samplemode;
    cB2Var = tryVar(cB2VarName, workInt, debug);
    TString fracName = typemode+"_"+varName+"_frac_"+samplemode;
    fracVar = tryVar(fracName, workInt, debug);

    RooAbsPdf* pdf1 = NULL;
    TString pdf1Name = typemode+"_"+varName+"_expo1_"+samplemode;
    pdf1 = new RooExponential( pdf1Name.Data(), pdf1Name.Data(), obs, *cB1Var);
    CheckPDF( pdf1, debug );

    RooAbsPdf* pdf2 = NULL;
    TString pdf2Name = typemode+"_"+varName+"_expo2_"+samplemode;
    pdf2 = new RooExponential( pdf2Name.Data(), pdf2Name.Data(), obs, *cB2Var);
    CheckPDF( pdf2, debug );

    RooAddPdf* pdf = NULL;
    TString pdfName = typemode+"_"+varName+"_doubleExpo_"+samplemode;
    pdf = new RooAddPdf(pdfName.Data(), pdfName.Data(), RooArgList(*pdf1,*pdf2),*fracVar);
    CheckPDF( pdf, debug );

    return pdf; 

  }

  RooAbsPdf* buildExponentialTimesLinearPDF(RooAbsReal& obs, 
                                            RooWorkspace* workInt, 
                                            TString samplemode, 
                                            TString typemode, 
                                            bool debug)
  {

    if ( debug == true ) { std::cout<<"[INFO] --------- build Exponential times Linear -------- "<<std::endl; }

    RooRealVar* cB1Var = NULL;
    RooRealVar* shiftComb = NULL; 
    TString varName = obs.GetName();
    TString shiftCombName = typemode+"_"+varName+"_shiftComb_"+samplemode;                                                                                                              
    TString cB1VarName = typemode+"_"+varName+"_cB_"+samplemode;                                                                        

    cB1Var = tryVar(cB1VarName, workInt, debug);                                                                                          
    shiftComb = tryVar(shiftCombName, workInt, debug);   

    RooAbsPdf* pdf1 = NULL;
    TString pdf1Name = typemode+"_"+varName+"_expo_"+samplemode;
    pdf1 = new RooExponential( pdf1Name.Data(), pdf1Name.Data(), obs, *cB1Var);
    CheckPDF( pdf1, debug );

    RooAbsPdf* pdf2 = NULL;
    TString pdf2Name = typemode+"_"+varName+"_linear_"+samplemode;
    pdf2 = new RooGenericPdf( pdf2Name.Data(), "(@0 - @1)", RooArgList(obs,*shiftComb));
    CheckPDF( pdf2, debug );

    RooAbsPdf* pdf = NULL;
    TString pdfName = typemode+"_"+varName+"_expoLinear_"+samplemode;
    pdf = new RooProdPdf(pdfName.Data(), pdfName.Data(), RooArgList(*pdf1,*pdf2));
    CheckPDF( pdf, debug );
    
    return pdf; 
  }

  RooAbsPdf* buildExponentialPlusSignalPDF(RooAbsReal& obs, 
                                           RooWorkspace* workInt, 
                                           TString samplemode, 
                                           TString typemode,
                                           bool debug)
  {
    if ( debug == true ) { std::cout<<"[INFO] --------- build Exponential plus Signal -------- "<<std::endl; }
    RooRealVar* cDVar = NULL;
    RooRealVar* fracVar = NULL;
    RooAbsPdf* pdf0 = NULL; 

    TString varName = obs.GetName();
    TString cDVarName = typemode+"_"+varName+"_cD_"+samplemode;                                                                                                  
    cDVar = tryVar(cDVarName, workInt, debug); 
    
    TString fracDsCombName = typemode+"_"+varName+"_fracD_"+samplemode;                                                                                                      
    fracVar = tryVar(fracDsCombName, workInt, debug); 

    pdf0 = trySignal(samplemode,varName,workInt, debug);

    RooExponential* pdf1 = NULL;
    TString pdf1Name = typemode+"_"+varName+"_Expo_"+samplemode; 
    pdf1 = new RooExponential( pdf1Name.Data(), pdf1Name.Data(), obs, *cDVar );
    CheckPDF(pdf1, debug);

    RooAddPdf* pdf = NULL;
    TString pdfName = typemode+"_"+varName+"_expoSignal_"+samplemode;
    pdf = new RooAddPdf( pdfName.Data(), pdfName.Data(),  RooArgList(*pdf1,*pdf0), *fracVar );
    CheckPDF(pdf, debug);

    return pdf;
    
  }

  RooAbsPdf* buildExponentialPlusDoubleCrystalBallPDF(RooAbsReal& obs, RooWorkspace* workInt,
                                                      TString samplemode, TString typemode, bool widthRatio, bool sharedMean, bool debug)
  {
    RooAbsPdf* pdf0 = buildExponentialPDF(obs, workInt, samplemode, typemode, debug);
    RooAbsPdf* pdf1 = buildDoubleCrystalBallPDF( obs, workInt, samplemode, typemode, widthRatio, sharedMean, debug);

    RooRealVar* fracVar = NULL;
    TString varName = obs.GetName();
    TString fracDsCombName = typemode+"_"+varName+"_fracD_"+samplemode;
    fracVar = tryVar(fracDsCombName, workInt, debug);

    RooAddPdf* pdf = NULL;
    TString pdfName = typemode+"_"+varName+"_expodCB_"+samplemode;
    pdf = new RooAddPdf( pdfName.Data(), pdfName.Data(),  RooArgList(*pdf1,*pdf0), *fracVar );
    CheckPDF(pdf, debug);

    return pdf;

  }


  RooAbsPdf* buildIpatiaPDF(RooAbsReal& mass, 
                            RooWorkspace* workInt, 
                            TString samplemode, 
                            TString typemode,
                            bool shiftMean,
                            bool scaleTails,
                            bool debug)
  {
    if ( debug == true ) { std::cout<<"[INFO] --------- build Ipatia -------- "<<std::endl; }

    RooRealVar* lVar = NULL;
    RooRealVar* zetaVar = NULL;
    RooRealVar* fbVar = NULL; 
    RooRealVar* meanVar = NULL;
    RooRealVar* shiftVar = NULL;
    RooFormulaVar *meanShiftVar = NULL;
    RooRealVar* sigmaVar = NULL; 
    
    RooRealVar* a1Var = NULL; 
    RooRealVar* n1Var = NULL;
    RooRealVar* a2Var = NULL; 
    RooRealVar* n2Var = NULL; 

    RooRealVar* scaleaVar = NULL;
    RooRealVar* scalenVar = NULL;

    RooFormulaVar* a1VarScaled = NULL;
    RooFormulaVar* n1VarScaled = NULL;
    RooFormulaVar* a2VarScaled = NULL;
    RooFormulaVar* n2VarScaled = NULL;

    TString varName = mass.GetName();

    TString lVarName = typemode+"_"+varName+"_l_"+samplemode;
    lVar = tryVar(lVarName, workInt, debug);
    TString zetaVarName = typemode+"_"+varName+"_zeta_"+samplemode;
    zetaVar = tryVar(zetaVarName, workInt, debug);
    TString fbVarName = typemode+"_"+varName+"_fb_"+samplemode;
    fbVar = tryVar(fbVarName, workInt, debug);
    
    TString meanVarName = typemode+"_"+varName+"_mean_"+samplemode;
    meanVar = tryVar(meanVarName, workInt, debug);
    if (meanVar == NULL) meanVar = tryVar("Signal_"+varName+"_mean_"+samplemode, workInt, debug);
    if (shiftMean)
    {
      TString shiftVarName = typemode+"_"+varName+"_shift_"+samplemode;
      shiftVar = tryVar(shiftVarName, workInt, debug);
      TString meanShiftVarName = typemode+"_"+varName+"_meanShift_"+samplemode;
      meanShiftVar = new RooFormulaVar(meanShiftVarName.Data(), meanShiftVarName.Data(), "@0+@1", RooArgList(*meanVar,*shiftVar));
    }
    
    TString sigmaVarName = typemode+"_"+varName+"_sigma_"+samplemode;
    sigmaVar = tryVar(sigmaVarName, workInt, debug);
    if (sigmaVar == NULL) sigmaVar = tryVar("Signal_"+varName+"_sigma_"+samplemode, workInt, debug);
    
    
    TString a1VarName = typemode+"_"+varName+"_a1_"+samplemode;
    a1Var = tryVar(a1VarName, workInt, debug);
    if (a1Var == NULL) a1Var = tryVar("Signal_"+varName+"_a1_"+samplemode, workInt, debug);
    TString n1VarName = typemode+"_"+varName+"_n1_"+samplemode;
    n1Var = tryVar(n1VarName, workInt, debug);
    if (n1Var == NULL) a1Var = tryVar("Signal_"+varName+"_n1_"+samplemode, workInt, debug);
    TString a2VarName = typemode+"_"+varName+"_a2_"+samplemode;
    a2Var = tryVar(a2VarName, workInt, debug);
    if (a2Var == NULL) a1Var = tryVar("Signal_"+varName+"_a2_"+samplemode, workInt, debug);
    TString n2VarName = typemode+"_"+varName+"_n2_"+samplemode;
    n2Var = tryVar(n2VarName, workInt, debug);
    if (n2Var == NULL) n2Var = tryVar("Signal_"+varName+"_n2_"+samplemode, workInt, debug);

    if(scaleTails)
    {
      TString scaleaVarName = typemode+"_"+varName+"_ascale_"+samplemode;
      scaleaVar = tryVar(scaleaVarName, workInt, debug);
      if(scaleaVar == NULL) scaleaVar = tryVar("Signal_"+varName+"_ascale_"+samplemode, workInt, debug);

      TString scalenVarName = typemode+"_"+varName+"_nscale_"+samplemode;
      scalenVar = tryVar(scalenVarName, workInt, debug);
      if(scalenVar == NULL) scalenVar = tryVar("Signal_"+varName+"_nscale_"+samplemode, workInt, debug);

      TString a1VarScaledName = typemode+"_"+varName+"_a1scaled_"+samplemode;
      a1VarScaled = new RooFormulaVar(a1VarScaledName.Data(), a1VarScaledName.Data(), "@0*@1", RooArgList(*a1Var,*scaleaVar));

      TString a2VarScaledName = typemode+"_"+varName+"_a2scaled_"+samplemode;
      a2VarScaled = new RooFormulaVar(a2VarScaledName.Data(), a2VarScaledName.Data(), "@0*@1", RooArgList(*a2Var,*scaleaVar));

      TString n1VarScaledName = typemode+"_"+varName+"_n1scaled_"+samplemode;
      n1VarScaled = new RooFormulaVar(n1VarScaledName.Data(), n1VarScaledName.Data(), "@0*@1", RooArgList(*n1Var,*scalenVar));

      TString n2VarScaledName = typemode+"_"+varName+"_n2scaled_"+samplemode;
      n2VarScaled = new RooFormulaVar(n2VarScaledName.Data(), n2VarScaledName.Data(), "@0*@1", RooArgList(*n2Var,*scalenVar));

    }
    

    RooAbsPdf* pdf = NULL;
    TString pdfName = typemode+"_"+varName+"_ipatia_"+samplemode;
    if(shiftMean)
    {
      if(scaleTails)
        pdf = new RooIpatia2( pdfName.Data(), pdfName.Data(), mass, *lVar, *zetaVar, *fbVar, *sigmaVar, *meanShiftVar, *a1VarScaled, *n1VarScaled, *a2VarScaled, *n2VarScaled);
      else
        pdf = new RooIpatia2( pdfName.Data(), pdfName.Data(), mass, *lVar, *zetaVar, *fbVar, *sigmaVar, *meanShiftVar, *a1Var, *n1Var, *a2Var, *n2Var);
    }
    else
    {
      if(scaleTails)
        pdf = new RooIpatia2( pdfName.Data(), pdfName.Data(), mass, *lVar, *zetaVar, *fbVar, *sigmaVar, *meanVar, *a1VarScaled, *n1VarScaled, *a2VarScaled, *n2VarScaled);
      else
        pdf = new RooIpatia2( pdfName.Data(), pdfName.Data(), mass, *lVar, *zetaVar, *fbVar, *sigmaVar, *meanVar, *a1Var, *n1Var, *a2Var, *n2Var);
    }
    
    CheckPDF( pdf, debug );

    return pdf;

  }

  RooAbsPdf* buildApolloniosPDF(RooAbsReal& mass,
				RooWorkspace* workInt,
				TString samplemode,
				TString typemode,
				bool debug)
  {
    if ( debug == true ) { std::cout<<"[INFO] --------- build Apollonios -------- "<<std::endl; }

    RooRealVar* meanVar = NULL;
    RooRealVar* sigmaVar = NULL;
    RooRealVar* bVar = NULL;
    RooRealVar* aVar = NULL;
    RooRealVar* nVar = NULL;

    TString varName = mass.GetName();

    TString meanVarName = typemode+"_"+varName+"_mean_"+samplemode;
    meanVar = tryVar(meanVarName, workInt, debug);
    TString sigmaVarName = typemode+"_"+varName+"_sigma_"+samplemode;
    sigmaVar = tryVar(sigmaVarName, workInt, debug);
    TString aVarName = typemode+"_"+varName+"_a_"+samplemode;
    aVar = tryVar(aVarName, workInt, debug);
    TString bVarName = typemode+"_"+varName+"_b_"+samplemode;
    bVar = tryVar(bVarName, workInt, debug);
    TString nVarName = typemode+"_"+varName+"_n_"+samplemode;
    nVar = tryVar(nVarName, workInt, debug);

    RooAbsPdf* pdf = NULL;
    TString pdfName = typemode+"_"+varName+"_apollonios_"+samplemode;
    pdf = new RooApollonios( pdfName.Data(), pdfName.Data(), mass, *meanVar, *sigmaVar, *bVar, *aVar, *nVar);
    CheckPDF( pdf, debug );

    return pdf;

  }




  RooAbsPdf* buildComboPIDKPDF(RooAbsReal& obs, 
                               RooWorkspace* work, 
                               RooWorkspace* workInt, 
                               TString samplemode, 
                               TString typemode,
                               std::vector <TString> pidk,
                               TString merge,
                               bool debug)
  {
    RooArgList* listPDF = new RooArgList();
    RooArgList* listFrac = new RooArgList();

    RooAbsPdf* pdf_pidk[3];
    RooAbsPdf* pdf = NULL; 
    RooRealVar* fracPIDK1 = NULL;
    RooRealVar* fracPIDK2 = NULL;

    TString varName = obs.GetName();

    Int_t num = 0; 
    for( int i = 0; i<3; i++ )
    {
      if ( pidk[i] == "True" || pidk[i] == "true" ) { num++; }
    }

    if (num > 1 )
    {
      TString fracPIDK1Name = typemode+"_"+varName+"_fracPIDK1_"+samplemode;
      fracPIDK1 =tryVar(fracPIDK1Name, workInt, debug);  
    }
    if ( num > 2 )
    {
      TString fracPIDK2Name = typemode+"_"+varName+"_fracPIDK2_"+samplemode;
      fracPIDK2 = tryVar(fracPIDK2Name, workInt, debug); 
    }

    TString m[] = {"CombPi","CombK","CombP"};

    TString y = CheckDataYear(samplemode,debug);
    TString sam = CheckPolarity(samplemode,debug);
    TString mode = CheckDMode(samplemode, debug);
    if ( mode == "" ) { mode == CheckKKPiMode(samplemode,debug);}
    RooRealVar lum;

    for (int i = 0; i<3; i++ )
    {
      if ( pidk[i] == "True" || pidk[i] == "true")
      {

	pdf_pidk[i] =  buildPIDKShapeMDFit(work,samplemode, m[i], "",debug);
       
        if ( pdf_pidk[i] != NULL )
	      {
		std::cout<<"[INFO] Adding pdf: "<<pdf_pidk[i]->GetName()<<" to PIDK PDFs"<<std::endl;
		listPDF->add(*pdf_pidk[i]);
	      }
      }
    }

    if ( num > 1 ) { listFrac->add(*fracPIDK1); if (debug == true ) { std::cout<<"[INFO] Adding fraction: "<<fracPIDK1->GetName()<<std::endl;} }
    if ( num > 2 ) { listFrac->add(*fracPIDK2); if (debug == true ) { std::cout<<"[INFO] Adding fraction: "<<fracPIDK2->GetName()<<std::endl;}}

    TString pdfName = typemode+"_"+varName+"_PIDKShape_"+samplemode;
    if ( num == 2 )
    {
      pdf = new RooAddPdf( pdfName.Data(), pdfName.Data(), *listPDF, *listFrac);
    }
    else if ( num == 3 )
    {
      pdf = new RooAddPdf( pdfName.Data(), pdfName.Data(), *listPDF, *listFrac, true);
    }
    else
    {
      pdf = pdf_pidk[0]; 
    }
    CheckPDF(pdf, debug);

    return pdf; 
  }

  RooAbsPdf* buildShiftedDoubleCrystalBallPDF(RooAbsReal& obs, RooWorkspace* workInt,
                                              TString samplemode, TString typemode, bool debug)
  {

    if ( debug == true ) { std::cout<<"[INFO] --------- build Shifted double Crystal Ball -------- "<<std::endl; }
    
    RooRealVar* mean = NULL;
    RooRealVar* alpha1Var = NULL;
    RooRealVar* alpha2Var =NULL;
    RooRealVar* n1Var = NULL;
    RooRealVar* n2Var =NULL;
    RooRealVar* sigma1Var =NULL;
    RooRealVar* sigma2Var = NULL;
    RooRealVar* fracVar = NULL;
    RooRealVar* shift = NULL; 
    RooRealVar* scale1 = NULL;
    RooRealVar* scale2 = NULL;
    RooFormulaVar* meanShift= NULL;
    RooFormulaVar* sigma1For = NULL;
    RooFormulaVar* sigma2For = NULL;


    TString varName = obs.GetName();

    TString meanName = "Signal_"+varName+"_mean_"+samplemode;
    mean = tryVar(meanName, workInt, debug);
    TString alpha1Name = "Signal_"+varName+"_alpha1_"+samplemode;
    alpha1Var = tryVar(alpha1Name, workInt, debug);
    TString alpha2Name = "Signal_"+varName+"_alpha2_"+samplemode;
    alpha2Var = tryVar(alpha2Name, workInt, debug);
    TString n1Name = "Signal_"+varName+"_n1_"+samplemode;
    n1Var = tryVar(n1Name, workInt, debug);
    TString n2Name = "Signal_"+varName+"_n2_"+samplemode;
    n2Var = tryVar(n2Name, workInt, debug);
    TString sigma1Name = "Signal_"+varName+"_sigma1_"+samplemode;
    sigma1Var = tryVar(sigma1Name, workInt, debug);
    TString sigma2Name = "Signal_"+varName+"_sigma2_"+samplemode;
    sigma2Var = tryVar(sigma2Name, workInt, debug);
    TString fracName = "Signal_"+varName+"_frac_"+samplemode;
    fracVar = tryVar(fracName, workInt, debug);

    TString shiftName = typemode+"_"+varName+"_shift_"+samplemode;
    shift = tryVar(shiftName, workInt, debug);
    TString scale1Name = typemode+"_"+varName+"_scale1_"+samplemode;
    scale1 = tryVar(scale1Name, workInt, debug);
    TString scale2Name = typemode+"_"+varName+"_scale2_"+samplemode;
    scale2 = tryVar(scale2Name, workInt, debug);

    TString meanShiftName = typemode+"_"+varName+"_meanShift_"+samplemode;
    meanShift = new RooFormulaVar(meanShiftName.Data() , meanShiftName.Data(),"@0-@1", RooArgList(*mean,*shift));
    TString sigma1ForName = typemode+"_"+varName+"_sigma1For_"+samplemode;
    sigma1For = new RooFormulaVar(sigma1ForName.Data(), sigma1ForName.Data(),"@0*@1", RooArgList(*sigma1Var,*scale1));
    TString sigma2ForName = typemode+"_"+varName+"_sigma2For_"+samplemode;
    sigma2For = new RooFormulaVar(sigma2ForName.Data(), sigma2ForName.Data(),"@0*@1", RooArgList(*sigma2Var,*scale2));

    RooAbsPdf* pdf = NULL;

    RooCBShape* pdf1 = NULL;
    TString pdf1Name = typemode+"_"+varName+"_shiftedCrystalBall1_"+samplemode;
    RooCBShape* pdf2 = NULL;
    TString pdf2Name = typemode+"_"+varName+"_shiftedCrystalBall2_"+samplemode;

    pdf1 = new RooCBShape( pdf1Name.Data(), pdf1Name.Data(), obs, *meanShift, *sigma1For, *alpha1Var, *n1Var);
    pdf2 = new RooCBShape( pdf2Name.Data(), pdf2Name.Data(), obs, *meanShift, *sigma2For, *alpha2Var, *n2Var);
   
    CheckPDF( pdf1, debug );
    CheckPDF( pdf2, debug);

    TString pdfName = typemode+"_"+varName+"_shiftedCrystalBall_"+samplemode;
    pdf = new RooAddPdf( pdfName.Data(), pdfName.Data(), *pdf1, *pdf2, *fracVar);
    CheckPDF( pdf, debug );

    return pdf; 

  }
 
  //===============================================================================
  // Read Bs (or Ds for dsMass == true ) shape from workspace
  //===============================================================================
  
  RooAbsPdf* ObtainMassShape(RooWorkspace* work,
                             TString mode,
                             TString year,
                             bool dsMass,
                             RooRealVar& lumRatio,
                             bool debug)
  {
    RooAbsPdf* pdf_Mass = NULL;
    RooAbsPdf* pdf_Mass1 = NULL;
    RooAbsPdf* pdf_Mass2 = NULL;

    TString name = "";
    TString Ds = "";

    TString dsFS = CheckDMode(mode,debug);
    if ( dsFS == "" ) { dsFS = CheckKKPiMode(mode, debug); }
   
    if (dsMass == true ) { Ds = "_Ds"; }
    if ( year.Contains("_")  == false ) { year = "_"+year;} 

    if ( mode.Contains("Bd2DPi")== true && dsFS == "kpipi")
    {
        
      name = "PhysBkgBd2DPiPdf_m_down_kpipi"+year+Ds;
      pdf_Mass1 = (RooKeysPdf*)work->pdf(name.Data());
      CheckPDF( pdf_Mass1, debug);
	
      name = "PhysBkgBd2DPiPdf_m_up_kpipi"+year+Ds;
      pdf_Mass2 = (RooKeysPdf*)work->pdf(name.Data());
      CheckPDF( pdf_Mass2, debug);

      name = "PhysBkgBd2DPiPdf_m_both_kpipi"+year+Ds;
      pdf_Mass = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Mass2,*pdf_Mass1), RooArgList(lumRatio));
    }
    else if ( (mode.Contains("BsDsPi") == true || mode.Contains("Bs2DsPi") ) && dsFS != "" )
    {
      TString sam = CheckPolarity(mode,debug);
      TString dsfs = CheckDMode(mode,debug);
      if ( dsfs == "" ) { dsfs = CheckKKPiMode(mode, debug); }

      name = "PhysBkgBs2DsPiPdf_m_down_"+dsfs+year+Ds;
      pdf_Mass1 = (RooKeysPdf*)work->pdf(name.Data());
      CheckPDF( pdf_Mass1, debug);

      name = "PhysBkgBs2DsPiPdf_m_up_"+dsfs+year+Ds;
      pdf_Mass2 = (RooKeysPdf*)work->pdf(name.Data());
      CheckPDF( pdf_Mass2, debug);

      name = "PhysBkgBs2DsPiPdf_m_both_"+dsfs+year+Ds;
      pdf_Mass = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_Mass2,*pdf_Mass1), RooArgList(lumRatio));
    }
    else
    {
      name = "PhysBkg"+mode+"Pdf_m_both"+year+Ds;
      pdf_Mass = (RooKeysPdf*)work->pdf(name.Data());
        
    }
    CheckPDF( pdf_Mass, debug);
    return pdf_Mass;
  }

  //===============================================================================
  // Read PIDK shape from workspace
  //===============================================================================

  RooAbsPdf* ObtainPIDKShape(RooWorkspace* work,
                             TString mode,
                             TString pol,
                             TString year,
                             RooRealVar& lumRatio,
                             bool DsMode,
                             bool debug)
  {
    RooAbsPdf* pdf_PIDK = NULL;
    RooAbsPdf* pdf_PIDK1 = NULL;
    RooAbsPdf* pdf_PIDK2 = NULL;

    TString name = "";

    if ( pdf_PIDK ) {}
    if ( pdf_PIDK1 ) {}
    if ( pdf_PIDK2 ) {}

    TString mode2 = "";
    TString dsFinalState = "";
    if ( year != "" ) { year = "_"+year; }
    if ( DsMode == true ) 
    { 
      TString dsFS = CheckDMode(mode,debug);
      if ( dsFS == "" ) { dsFS = CheckKKPiMode(mode, debug); }
      if ( dsFS != "" ) { dsFinalState = "_"+dsFS;}

      if( mode.Contains("DsPi") == true ) { mode2 = "Bs2DsPi";}
      else if ( mode.Contains("DsK") == true ) { mode2 = "Bs2DsK";}
      else if ( mode.Contains("DsstPi") == true ) { mode2 = "Bs2DsstPi"; }
      else if ( mode.Contains("DsstK") == true ) { mode2 = "Bs2DsstK"; } 
    }
    else
    {
      mode2 = mode;
    }

    
    
    if ( pol == "both")
    {
      name ="PIDKShape_"+mode2+"_down"+dsFinalState+year; 
      pdf_PIDK1 = GetRooBinned1DFromWorkspace(work, name, debug);

      name ="PIDKShape_"+mode2+"_up"+dsFinalState+year; 
      pdf_PIDK2 = GetRooBinned1DFromWorkspace(work, name, debug);

      name = "PIDKShape_"+mode2+"_both"+dsFinalState+year;
      pdf_PIDK = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf_PIDK2,*pdf_PIDK1), RooArgList(lumRatio));

    }
    else
    {
      name = "PIDKShape_"+mode2+"_"+pol+dsFinalState+year;

      pdf_PIDK = (RooAddPdf*)work->pdf(name.Data());
    }

    CheckPDF( pdf_PIDK, debug );    
    return pdf_PIDK;
  }

  
  //===============================================================================
  // Create RooProdPdf with (Bs, Ds, PIDK) shapes from workspace
  //===============================================================================

  RooProdPdf* ObtainRooProdPdfForMDFitter(RooWorkspace* work,
                                          TString mode,
                                          TString pol,
                                          TString year, 
                                          RooRealVar& lumRatio,
                                          RooAbsPdf* pdf_DsMass,
                                          Int_t dim, 
                                          bool debug)
  {

    RooAbsPdf* pdf_Bs = NULL;
    RooAbsPdf* pdf_Ds = NULL;
    RooAbsPdf* pdf_PIDK = NULL;

    TString name = "";
    TString mode2 = "";
    TString modeDs = "";
    TString Var = "";

    pdf_Bs = ObtainMassShape(work, mode, year, false, lumRatio, debug);  

    if ( dim > 1 )
    {
      if ( pdf_DsMass == NULL )
      {
        pdf_Ds = ObtainMassShape(work, mode, year, true, lumRatio, debug);
      }
      else
      {
        pdf_Ds = pdf_DsMass;
        TString namePDF = pdf_DsMass->GetName();
        Var = CheckDMode(namePDF,debug);
        if ( Var == "" ) { Var = CheckKKPiMode(namePDF, debug); }
        modeDs = "_"+Var;
	    
      }
    }

    if ( mode.Contains("Bs2DsPi") == true || (mode.Contains("Bs2DsK") ==true && mode.Contains("Bs2DsKst") == false) )
    {
      if ( dim > 2) 
      {
        pdf_PIDK = ObtainPIDKShape(work, mode, pol, year, lumRatio, true, debug);
      }
      if ( mode.Contains("Bs2DsPi") == true) { mode2 = "Bs2DsPi"; } else { mode2 = "Bs2DsK"; }
      //Var = CheckDMode(mode,debug);
      //if ( Var == "" ) { Var = CheckKKPiMode(mode, debug); }
      //modeDs = "_"+Var;
    }
    else
    {
      
      if( mode.Contains("Bd2DPi") ) { mode2 = "Bd2DPi"; } else {mode2 = mode; }
      if (dim > 2)
      {
        pdf_PIDK = ObtainPIDKShape(work, mode2, pol, year, lumRatio, false, debug);
      }
    }
    
    RooProdPdf* pdf_Tot = NULL;
    TString samplemode = pol+modeDs; 
    pdf_Tot = GetRooProdPdfDim(mode2, samplemode, pdf_Bs, pdf_Ds, pdf_PIDK, dim, debug);

    /*
      name="PhysBkg"+mode2+"Pdf_m_"+pol+modeDs+"_Tot";
      pdf_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bs,*pdf_Ds,*pdf_PIDK));
      CheckPDF( pdf_Tot, debug );
    */
    
    return pdf_Tot;
  }

  RooProdPdf* GetRooProdPdfDim(TString& mode, TString& samplemode, 
                               RooAbsPdf* pdf_Bs, RooAbsPdf* pdf_Ds, RooAbsPdf* pdf_PIDK,
                               Int_t dim, bool debug)
  {
    RooProdPdf* pdf_Tot = NULL;
    TString name="PhysBkg"+mode+"Pdf_m_"+samplemode+"_Tot";
    if ( dim == 1 )
    {
      if ( debug == true ) { std::cout<<"[INFO] 1 dimensional pdf "; }
      pdf_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bs));
    }
    else if ( dim == 2) 
    {
      if (debug == true ) { std::cout<<"[INFO] 2 dimensional pdf "; }
      pdf_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bs,*pdf_Ds));
    }
    else if ( dim == 3 )
    {
      if (debug == true ) { std::cout<<"[INFO] 3 dimensional pdf "; }
      pdf_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bs,*pdf_Ds,*pdf_PIDK));
    }
    CheckPDF( pdf_Tot, debug );
    if ( debug )
    {
      std::cout<<"[INFO] with components: "<<std::endl;
      if ( pdf_Bs != NULL ) { std::cout<<"[INFO]   BeautyMass: "<<pdf_Bs->GetName()<<std::endl; } 
      if ( pdf_Ds != NULL ) { std::cout<<"[INFO]   CharmMass: "<<pdf_Ds->GetName()<<std::endl; }
      if ( pdf_PIDK != NULL ) { std::cout<<"[INFO]   BacPIDK: "<<pdf_PIDK->GetName()<<std::endl; }
    }
    return pdf_Tot; 
  }

  //===============================================================================
  // Create RooProdPdf with (Bs mass, Ds mass, PIDK, time) shapes from workspace
  //===============================================================================

  RooProdPdf* ObtainRooProdPdfForFullFitter(RooWorkspace* work,
                                            TString mode,
                                            TString pol,
                                            TString year,
                                            RooRealVar& lumRatio,
                                            RooAbsPdf* pdf_Time,
                                            RooAbsPdf* pdf_DsMass,
                                            bool debug)
  {
    RooAbsPdf* pdf_Bs = NULL;
    RooAbsPdf* pdf_Ds = NULL;
    RooAbsPdf* pdf_PIDK = NULL;

    pdf_Bs = ObtainMassShape(work, mode, year, false, lumRatio, debug);
    if ( pdf_DsMass == NULL )
    {
      pdf_Ds = ObtainMassShape(work, mode, year, true,  lumRatio, debug);
    }
    else
    {
      pdf_Ds = pdf_DsMass;
    }

    TString dmode = CheckDMode(mode, debug);
    if ( dmode == "" ) { dmode == CheckKKPiMode(mode,debug);}

    if ( dmode != "" )
    {
      pdf_PIDK = ObtainPIDKShape(work, mode, pol, year, lumRatio, true, debug);
    }
    else
    {
      pdf_PIDK = ObtainPIDKShape(work, mode, pol, year, lumRatio, false, debug);
    }

    RooProdPdf* pdf_Tot = NULL;
    TString name="PhysBkg"+mode+"Pdf_m_"+pol+"_Tot";
    pdf_Tot = new RooProdPdf(name.Data(), name.Data(), RooArgList(*pdf_Bs,*pdf_Ds,*pdf_PIDK,*pdf_Time));
    CheckPDF( pdf_Tot, debug );

    return pdf_Tot;
  }


  RooExtendPdf* buildExtendPdfSpecBkgMDFit( RooWorkspace* workInt, RooWorkspace* work,
                                            TString samplemode, TString typemode, TString typemodeDs, 
                                            TString merge, int dim, TString signalDs, bool debug)
  {
    RooExtendPdf* epdf = NULL; 
    RooProdPdf* pdf_Tot = NULL;

    TString nName = "n"+typemode+"_"+samplemode+"_Evts";
    RooRealVar* nEvts = tryVar(nName, workInt, debug);
    Double_t val = nEvts->getValV();

    if ( val != 0.0 )
    {
      pdf_Tot = buildProdPdfSpecBkgMDFit(workInt, work, samplemode, typemode, typemodeDs, merge, dim, signalDs, debug);

      TString epdfName = typemode+"EPDF_m_"+samplemode;
      epdf = new RooExtendPdf(epdfName.Data() , pdf_Tot->GetTitle(), *pdf_Tot, *nEvts );
      CheckPDF(epdf, debug);
    }
    return epdf;    
  }

 

  RooProdPdf* buildProdPdfSpecBkgMDFit( RooWorkspace* workInt, RooWorkspace* work,
                                        TString samplemode, TString typemode, TString typemodeDs, 
                                        TString merge, int dim, 
                                        TString signalDs, bool debug)
  {
    if (debug == true)
    {
      cout<<"[INFO] build RooProdPdf for: "<<typemode<<endl;
    }

    RooProdPdf* pdf_Tot = NULL;

    std::vector<RooAbsPdf*> pdf_pBs;
    std::vector<RooAbsPdf*> pdf_pDs;
    std::vector<RooAbsPdf*> pdf_pPIDK;
    RooAbsPdf* pdf_Bs = NULL;
    RooAbsPdf* pdf_Ds = NULL;
    RooAbsPdf* pdf_PIDK = NULL;

    TString t = "_";
    TString mode, Mode;
    std::vector<TString> y, sam;
    mode = CheckDMode(samplemode,debug);
    if ( mode == "" ) { mode = CheckKKPiMode(samplemode, debug); }
    Mode = GetModeCapital(mode,debug);

    y = GetDataYear(samplemode, merge, debug);
    sam = GetPolarity(samplemode, merge, debug);


    for(unsigned int i = 0; i < sam.size(); i++ )
    {
      for (unsigned int j =0; j < y.size(); j++ )
      {

        TString smp = sam[i]+"_"+mode+"_"+y[j];
        pdf_pBs.push_back(buildMassPdfSpecBkgMDFit(work, smp, typemode, typemodeDs, false, debug));
        if ( dim > 1)
	      {
          if ( signalDs == "" )
          {  
            pdf_pDs.push_back(buildMassPdfSpecBkgMDFit(work, smp, typemode, typemodeDs, true, debug));
          }
          else
          {
            RooAbsPdf* pdfTmp = NULL; 
            pdfTmp = trySignal(samplemode,signalDs,workInt, debug);
            if ( pdfTmp == NULL ) { pdfTmp = trySignal(smp,signalDs,workInt, debug); } 
            pdf_pDs.push_back(pdfTmp);
          }
	      }	    
        if ( dim > 2 )
	      {
          if ( typemode == "Bd2DPi" && typemodeDs == "kpipi" )
          {
            pdf_pPIDK.push_back(buildPIDKShapeMDFit(work, smp, typemode, "", debug));
          }
          else
          {
            pdf_pPIDK.push_back(buildPIDKShapeMDFit(work, smp, typemode, typemodeDs, debug));
          }
	      }
      }
    }

    if  ( merge == "pol" )
    {

      pdf_Bs = mergePdf(pdf_pBs[1], pdf_pBs[0], merge, y[0], workInt, debug);
      if ( dim > 1 ) { pdf_Ds = mergePdf(pdf_pDs[1], pdf_pDs[0], merge, y[0], workInt, debug); }
      if ( dim > 2 ) { pdf_PIDK = mergePdf(pdf_pPIDK[1], pdf_pPIDK[0], merge, y[0], workInt, debug); }
    }
    else if ( merge == "year" )
    {
      pdf_Bs = mergePdf(pdf_pBs[1], pdf_pBs[0], merge, sam[0], workInt, debug);
      if ( dim > 1 ) { pdf_Ds = mergePdf(pdf_pDs[1], pdf_pDs[0], merge, sam[0], workInt, debug); }
      if ( dim > 2 ) { pdf_PIDK = mergePdf(pdf_pPIDK[1], pdf_pPIDK[0], merge, sam[0], workInt, debug);}
    }
    else if ( merge == "both" )
    {
      pdf_pBs.push_back(mergePdf(pdf_pBs[2], pdf_pBs[0], "pol", y[0], workInt, debug));
      if ( dim > 1 ) { pdf_pDs.push_back(mergePdf(pdf_pDs[2], pdf_pDs[0], "pol", y[0], workInt, debug)); }
      if ( dim > 2 ) { pdf_pPIDK.push_back(mergePdf(pdf_pPIDK[2], pdf_pPIDK[0], "pol", y[0], workInt, debug));}

      pdf_pBs.push_back(mergePdf(pdf_pBs[3], pdf_pBs[1], "pol", y[1], workInt, debug));
      if ( dim > 1 ) { pdf_pDs.push_back(mergePdf(pdf_pDs[3], pdf_pDs[1], "pol", y[1], workInt, debug));}
      if ( dim > 2 ) { pdf_pPIDK.push_back(mergePdf(pdf_pPIDK[3], pdf_pPIDK[1], "pol", y[1], workInt, debug));}

      pdf_Bs = mergePdf(pdf_pBs[5], pdf_pBs[4], "year", "run1", workInt, debug);
      if ( dim > 1 ) { pdf_Ds = mergePdf(pdf_pDs[5], pdf_pDs[4], "year", "run1", workInt, debug);}
      if ( dim > 2 ) { pdf_PIDK = mergePdf(pdf_pPIDK[5], pdf_pPIDK[4], "year", "run1", workInt, debug);}
    }
    else
    {
      pdf_Bs = pdf_pBs[0];
      if ( dim > 1 ) { pdf_Ds = pdf_pDs[0];}
      if ( dim > 2 ) { pdf_PIDK = pdf_pPIDK[0];}
    }
    /*
      else
      {
      pdf_PIDK = ObtainPIDKShape(work, mode, pol, year, lumRatio, false, debug);
      }
    */

    pdf_Tot = GetRooProdPdfDim(typemode, samplemode, pdf_Bs, pdf_Ds, pdf_PIDK, dim, debug  );
    CheckPDF( pdf_Tot, debug );

    return pdf_Tot;

    
  }

  
  RooAbsPdf* buildMergedSpecBkgMDFit(RooWorkspace* workInt, RooWorkspace* work,
                                     TString samplemode, TString typemode, TString typemodeDs, TString merge,
                                     int dim, TString signalDs, bool debug)
  {

    if (debug == true)
    {
      cout<<"[INFO] build merged RooAbsPdf for: "<<typemode<<" "<<typemodeDs<<endl;
    }

    std::vector<RooAbsPdf*> pdf_part; 
    RooAbsPdf* pdf = NULL; 

    TString t = "_";
    TString mode, Mode;
    std::vector<TString> y, sam;
    mode = CheckDMode(samplemode,debug);
    if ( mode == "" ) { mode = CheckKKPiMode(samplemode, debug); }
    Mode = GetModeCapital(mode,debug);

    y = GetDataYear(samplemode, merge, debug);
    sam = GetPolarity(samplemode, merge, debug);


    for(unsigned int i = 0; i < sam.size(); i++ )
    {
      for (unsigned int j =0; j < y.size(); j++ )
      {

        TString smp = sam[i]+"_"+mode+"_"+y[j];
        if ( dim == 1 )
	      {
          pdf_part.push_back(buildMassPdfSpecBkgMDFit(work, smp, typemode, typemodeDs, false, debug));
	      }
        if ( dim == 2)
        {
          if ( signalDs == "" )
          {
            pdf_part.push_back(buildMassPdfSpecBkgMDFit(work, smp, typemode, typemodeDs, true, debug));
          }
          else
          {
            RooAbsPdf* pdfTmp = NULL;
            pdfTmp = trySignal(samplemode,signalDs,workInt, false);
            if ( pdfTmp == NULL ) { pdfTmp = trySignal(smp,signalDs,workInt, false); }
            CheckPDF( pdfTmp, debug);
            pdf_part.push_back(pdfTmp);
          }
        }

        if ( dim == 3 )
        {
          RooAbsPdf* pdfTmp = NULL;
	        pdfTmp = buildPIDKShapeMDFit(work, smp, typemode, typemodeDs, false);
          if( pdfTmp == NULL ) { pdfTmp =  buildPIDKShapeMDFit(work, smp, typemode, mode, false); }
          if( pdfTmp == NULL ) { pdfTmp =  buildPIDKShapeMDFit(work, smp, typemode, "", false);}
          CheckPDF( pdfTmp, debug); 
          pdf_part.push_back(pdfTmp);
        }
      }
    }

    if ( pdf_part[0] != NULL && pdf_part[1] != NULL ) 
    {
      if  ( merge == "pol" )
      {
        pdf  = mergePdf(pdf_part[1], pdf_part[0], merge, y[0], workInt, debug);
      }
      else if ( merge == "year" )
      {
        pdf  = mergePdf(pdf_part[1], pdf_part[0], merge, sam[0], workInt, debug);
      }
      else if ( merge == "both" )
      {
        pdf_part.push_back(mergePdf(pdf_part[2], pdf_part[0], "pol", y[0], workInt, debug));
        pdf_part.push_back(mergePdf(pdf_part[3], pdf_part[1], "pol", y[1], workInt, debug));
        pdf = mergePdf(pdf_part[5], pdf_part[4], "year", "run1", workInt, debug);
      }
      else
      {
        pdf = pdf_part[0];
      }
    }
    CheckPDF( pdf, debug );

    return pdf;
  }

  RooAbsPdf* buildMassPdfSpecBkgMDFit(RooWorkspace* work,
                                      TString samplemode, TString typemode, TString typemodeDs,
                                      bool charmShape, bool debug)
  {

    
    TString p = CheckPolarity(samplemode,false);
    TString y = CheckDataYear(samplemode,false);

    RooAbsPdf* pdf_Mass = NULL;
    TString name = "";
    TString Ds = "";
    if (charmShape == true ) { Ds = "_Ds"; }

    if ( typemodeDs != "" )
    {
      name = "PhysBkg"+typemode+"Pdf_m_"+p+"_"+typemodeDs+"_"+y+Ds;	 
    }
    else
    {
      name = "PhysBkg"+typemode+"Pdf_m_both_"+y+Ds;
    }
    
    pdf_Mass = tryPdf(name, work, debug);
    CheckPDF( pdf_Mass, debug);
    return pdf_Mass;
    
  }


  RooAbsPdf* buildPIDKShapeMDFit(RooWorkspace* work,
                                 TString samplemode, TString typemode, TString typemodeDs,
                                 bool debug)
  {
    TString p = CheckPolarity(samplemode,false);
    TString y = CheckDataYear(samplemode,false);

    RooAbsPdf* pdf_PIDK = NULL;
    TString name = "";

    if ( typemodeDs != "" )
    {
      name = "PIDKShape_"+typemode+"_"+p+"_"+typemodeDs+"_"+y;
    }
    else
    {
      name = "PIDKShape_"+typemode+"_"+p+"_"+y;
    }

    pdf_PIDK = tryPdf(name, work, debug);
    CheckPDF( pdf_PIDK, debug);
    return pdf_PIDK;

  }


  //===============================================================================
  // Background 2D model for Bs->DsPi mass fitter.
  //===============================================================================

  RooAbsPdf* build_Bs2DsPi_BKG_MDFitter( RooAbsReal& mass,
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
      cout<<"[INFO] =====> Build background model Bs->DsPi --------------"<<endl;
    }

    RooArgList* list = new RooArgList();
    TString charmVarName = massDs.GetName();

    TString nBs2DsDsstPiRhoName = "nBs2DsDsstPiRho_"+samplemode+"_Evts";
    RooRealVar* nBs2DsDsstPiRhoEvts = tryVar(nBs2DsDsstPiRhoName, workInt,debug);
    Double_t valBs2DsDsstPiRho = nBs2DsDsstPiRhoEvts->getValV();

    TString g1_f1_Name = "g1_f1_frac_"+samplemode;
    RooRealVar* g1_f1 = tryVar(g1_f1_Name, workInt,debug); 

    TString mode = CheckDMode(samplemode,debug);
    if ( mode == "" ) { mode = CheckKKPiMode(samplemode, debug); }

    TString name="";
    TString m = "";

    RooAbsPdf* pdf_Bd2DsPi_Bs = NULL; 
    RooAbsPdf* pdf_Bd2DsPi_PIDK = NULL;
    RooAbsPdf* pdf_Bd2DsPi_Ds = NULL;
    RooProdPdf* pdf_Bd2DsPi_Tot = NULL;

    if ( valBs2DsDsstPiRho != 0.0 )
    {
      pdf_Bd2DsPi_Bs = buildShiftedDoubleCrystalBallPDF(mass, workInt, samplemode, "Bd2DsPi", debug);
      if( dim > 2)
      {
        pdf_Bd2DsPi_PIDK = buildMergedSpecBkgMDFit(workInt, work, samplemode, "Bs2DsPi", mode, merge, 3, "", debug);
      }
      if ( dim > 1 )
      {
        pdf_Bd2DsPi_Ds = trySignal(samplemode,charmVarName,workInt, debug);
      }
      TString m = "Bd2DsPi";
      pdf_Bd2DsPi_Tot = GetRooProdPdfDim(m, samplemode, pdf_Bd2DsPi_Bs, pdf_Bd2DsPi_Ds, pdf_Bd2DsPi_PIDK, dim, debug  );
    }

    // --------------------------------- Read PDFs from Workspace -------------------------------------------------//

    if (debug == true) cout<<endl;
    if (debug == true) cout<<"---------------  Read PDF's from the workspace -----------------"<<endl;
    
    RooExtendPdf* epdf_Bd2DPi = NULL;
    epdf_Bd2DPi = buildExtendPdfSpecBkgMDFit( workInt, work, samplemode, "Bd2DPi", "", merge, dim, "", debug);
    Double_t valBd2DPi = CheckEvts(workInt, samplemode, "Bd2DPi",debug);
    list = AddEPDF(list, epdf_Bd2DPi, valBd2DPi, debug);

    //-----------------------------------------//
    
    RooExtendPdf* epdf_Lb2LcPi = NULL;
    epdf_Lb2LcPi = buildExtendPdfSpecBkgMDFit( workInt, work, samplemode, "Lb2LcPi", "", merge, dim, "", debug);
    Double_t valLb2LcPi = CheckEvts(workInt, samplemode, "Lb2LcPi",debug);
    list = AddEPDF(list, epdf_Lb2LcPi, valLb2LcPi, debug);

    //-----------------------------------------//

    RooExtendPdf* epdf_Bs2DsK = NULL;
    epdf_Bs2DsK = buildExtendPdfSpecBkgMDFit( workInt, work, samplemode, "Bs2DsK", "", merge, dim, charmVarName, debug);
    Double_t valBs2DsK = CheckEvts(workInt, samplemode, "Bs2DsK",debug);
    list = AddEPDF(list, epdf_Bs2DsK, valBs2DsK, debug);

    // --------------------------------- Create RooAddPdf -------------------------------------------------//
    
    RooAbsPdf* pdf_Bs2DsstPi_Bs = NULL;
    RooAbsPdf* pdf_Bs2DsstPi_Ds = NULL;
    RooAbsPdf* pdf_Bs2DsstPi_PIDK = NULL;
    RooProdPdf* pdf_Bs2DsstPi_Tot = NULL;
    RooAddPdf* pdf_Bs2DsDsstPiRho_Tot = NULL;
    RooExtendPdf* epdf_Bs2DsDsstPiRho   = NULL;

    if ( valBs2DsDsstPiRho!= 0)
    {
      
      pdf_Bs2DsstPi_Bs = buildMergedSpecBkgMDFit(workInt, work, samplemode, "Bs2DsstPi", "", merge, 1, "", debug);
      if( dim > 2)
      {
        pdf_Bs2DsstPi_PIDK = buildMergedSpecBkgMDFit(workInt, work, samplemode, "Bs2DsPi", mode, merge, 3, "", debug);
      }
      if ( dim > 1 )
      {
        pdf_Bs2DsstPi_Ds = trySignal(samplemode,charmVarName,workInt, debug);
      }

      m = "Bs2DsstPi";
      pdf_Bs2DsstPi_Tot = GetRooProdPdfDim(m, samplemode, pdf_Bs2DsstPi_Bs, pdf_Bs2DsstPi_Ds, pdf_Bs2DsstPi_PIDK, dim, debug  );
	
      name="PhysBkgBs2DsDsstPiPdf_m_"+samplemode+"_Tot";
      pdf_Bs2DsDsstPiRho_Tot = new RooAddPdf( name.Data(),
                                              name.Data(),
                                              RooArgList(*pdf_Bs2DsstPi_Tot, *pdf_Bd2DsPi_Tot), //, *pdf_Bs2DsRho), //,*pdf_Bs2DsstRho),
                                              RooArgList(*g1_f1) //,g1_f2), rec
                                              );
      CheckPDF(pdf_Bs2DsDsstPiRho_Tot, debug);

      name = "Bs2DsDsstPiRhoEPDF_m_"+samplemode;
      epdf_Bs2DsDsstPiRho = new RooExtendPdf( name.Data() , pdf_Bs2DsDsstPiRho_Tot-> GetTitle(), *pdf_Bs2DsDsstPiRho_Tot  , *nBs2DsDsstPiRhoEvts);
      CheckPDF(epdf_Bs2DsDsstPiRho, debug);
      list = AddEPDF(list, epdf_Bs2DsDsstPiRho, nBs2DsDsstPiRhoEvts, debug);
    }
    
    RooAbsPdf* pdf_totBkg = NULL;
    name = "BkgEPDF_m_"+samplemode;
    pdf_totBkg = new RooAddPdf( name.Data(), name.Data(),*list);
    
    if (debug == true)
    {
      cout<<endl;
      if( pdf_totBkg != NULL ){ cout<<" ------------- CREATED TOTAL BACKGROUND PDF: SUCCESFULL------------"<<endl; }
      else { cout<<" ---------- CREATED TOTAL BACKGROUND PDF: FAILED ----------------"<<endl;}
    }
    return pdf_totBkg;
    
  }



  //===============================================================================
  // Background MD model for Bs->DsPi mass fitter.
  //===============================================================================

  RooAbsPdf* build_Bs2DsK_BKG_MDFitter(RooAbsReal& mass,
                                       RooAbsReal& massDs,
                                       RooWorkspace* work,
                                       RooWorkspace* workInt,
                                       TString &samplemode,
                                       TString merge,
                                       Int_t dim, 
                                       bool debug){
    

    if (debug == true)
    {
      cout<<"--------------------------------------------------------"<<endl;
      cout<<"=====> Build background model BsDsK for simultaneous fit"<<endl;
      cout<<"--------------------------------------------------------"<<endl;
    }

    RooArgList* list = new RooArgList();
    TString charmVarName = massDs.GetName();
    TString mode = CheckDMode(samplemode,debug);
    if ( mode == "" ) { mode = CheckKKPiMode(samplemode, debug); }
    
    TString nBsLb2DsDsstPPiRhoName = "nBsLb2DsDsstPPiRho_"+samplemode+"_Evts"; 
    RooRealVar* nBsLb2DsDsstPPiRhoEvts = tryVar(nBsLb2DsDsstPPiRhoName, workInt,debug); //GetObservable(workInt, nBsLb2DsDsstPPiRhoName, debug); 
    Double_t valBsLb2DsDsstPPiRho = nBsLb2DsDsstPPiRhoEvts->getValV(); 

    TString nBs2DsDssKKstName = "nBs2DsDsstKKst_"+samplemode+"_Evts";
    RooRealVar* nBs2DsDssKKstEvts = tryVar(nBs2DsDssKKstName, workInt,debug); //GetObservable(workInt, nBs2DsDssKKstName, debug);                                                     
    Double_t valBs2DsDssKKst = nBs2DsDssKKstEvts->getValV(); 

    TString g2_f1_Name = "g2_f1_frac_"+samplemode;
    RooRealVar* g2_f1 = tryVar(g2_f1_Name, workInt,debug); //GetObservable(workInt, g2_f1_Name, debug);
    
    TString g2_f2_Name = "g2_f2_frac_"+samplemode;
    RooRealVar* g2_f2 = tryVar(g2_f2_Name, workInt,debug); //GetObservable(workInt, g2_f2_Name, debug);

    TString g3_f1_Name = "g3_f1_frac_"+samplemode;
    RooRealVar* g3_f1 = tryVar(g3_f1_Name, workInt,debug); //GetObservable(workInt, g3_f1_Name, debug);

    TString g5_f1_Name = "g5_f1_frac_"+samplemode;
    RooRealVar* g5_f1 = tryVar(g5_f1_Name, workInt,debug); //GetObservable(workInt, g5_f1_Name, debug);

    // ------------------------------------------ Read BdDsK ----------------------------------------------------//
    TString name="";
    RooAbsPdf* pdf_Bd2DsK_Bs = NULL; 
    RooAbsPdf* pdf_Bd2DsK_PIDK = NULL;
    RooAbsPdf* pdf_Bd2DsK_Ds = NULL;
    RooProdPdf* pdf_Bd2DsK_Tot = NULL;

    if ( valBs2DsDssKKst != 0.0 )
    {
      pdf_Bd2DsK_Bs = buildShiftedDoubleCrystalBallPDF(mass, workInt, samplemode, "Bd2DsK", debug);
      if( dim > 2)
      {
        pdf_Bd2DsK_PIDK = buildMergedSpecBkgMDFit(workInt, work, samplemode, "Bs2DsK", mode, merge, 3, "", debug);
      }
      if ( dim > 1 )
      {
        pdf_Bd2DsK_Ds = trySignal(samplemode,charmVarName,workInt, debug);
      }
      TString m = "Bd2DsK"; 
      pdf_Bd2DsK_Tot = GetRooProdPdfDim(m, samplemode, pdf_Bd2DsK_Bs, pdf_Bd2DsK_Ds, pdf_Bd2DsK_PIDK, dim, debug  );
    }

    RooExtendPdf* epdf_Bs2DsDsstKKst = NULL;
    if ( valBs2DsDssKKst != 0.0 )
    {
      name = "Bs2DsDsstKKstEPDF_m_"+samplemode;
      epdf_Bs2DsDsstKKst = new RooExtendPdf( name.Data() , pdf_Bd2DsK_Tot->GetTitle(), *pdf_Bd2DsK_Tot, *nBs2DsDssKKstEvts   );
      CheckPDF( epdf_Bs2DsDsstKKst, debug );
      list = AddEPDF(list, epdf_Bs2DsDsstKKst, nBs2DsDssKKstEvts, debug);
    }

    // --------------------------------- Read PDFs from Workspace -------------------------------------------------//                      
    
    RooExtendPdf* epdf_Bd2DK = NULL;
    epdf_Bd2DK = buildExtendPdfSpecBkgMDFit( workInt, work, samplemode, "Bd2DK", "", merge, dim, "", debug);
    Double_t valBd2DK = CheckEvts(workInt, samplemode, "Bd2DK",debug);
    list = AddEPDF(list, epdf_Bd2DK, valBd2DK, debug);

    RooExtendPdf* epdf_Bd2DPi = NULL;
    epdf_Bd2DPi = buildExtendPdfSpecBkgMDFit( workInt, work, samplemode, "Bd2DPi", "", merge, dim, "", debug);
    Double_t valBd2DPi = CheckEvts(workInt, samplemode, "Bd2DPi",debug);
    list = AddEPDF(list, epdf_Bd2DPi, valBd2DPi, debug);

    RooExtendPdf* epdf_Lb2LcK = NULL;
    epdf_Lb2LcK = buildExtendPdfSpecBkgMDFit( workInt, work, samplemode, "Lb2LcK", "", merge, dim, "", debug);
    Double_t valLb2LcK = CheckEvts(workInt, samplemode, "Lb2LcK",debug);
    list = AddEPDF(list, epdf_Lb2LcK, valLb2LcK, debug);

    RooExtendPdf* epdf_Lb2LcPi = NULL;
    epdf_Lb2LcPi = buildExtendPdfSpecBkgMDFit( workInt, work, samplemode, "Lb2LcPi", "", merge, dim, "", debug);
    Double_t valLb2LcPi = CheckEvts(workInt, samplemode, "Lb2LcPi",debug);
    list = AddEPDF(list, epdf_Lb2LcPi, valLb2LcPi, debug);

    //-----------------------------------------//
  	  
    if (debug == true){
      cout<<"---------------  Group 2 -----------------"<<endl;
      cout<<"Bs->Ds*Pi"<<endl;
      cout<<"Bs->DsRho"<<endl;
    }
    
    RooProdPdf* pdf_Bs2DsRho_Tot = NULL;
    RooProdPdf* pdf_Bs2DsstPi_Tot = NULL;
    RooProdPdf* pdf_Bs2DsPi_Tot = NULL;
    RooAddPdf*  pdf_Bs2DsDsstPiRho_Tot = NULL;
    
    if ( valBsLb2DsDsstPPiRho != 0.0 )
    {
      pdf_Bs2DsRho_Tot  = buildProdPdfSpecBkgMDFit(workInt, work, samplemode, "Bs2DsRho",  "", merge, dim, charmVarName, debug);
      pdf_Bs2DsstPi_Tot = buildProdPdfSpecBkgMDFit(workInt, work, samplemode, "Bs2DsstPi", "", merge, dim, charmVarName, debug); 
      pdf_Bs2DsPi_Tot   = buildProdPdfSpecBkgMDFit(workInt, work, samplemode, "Bs2DsPi",   "", merge, dim, charmVarName, debug);

	//pdf_Bs2DsPi_Tot   = buildProdPdfSpecBkgMDFit(workInt, work, samplemode, "Bs2DsPi", mode, merge, dim, charmVarName, debug);
      
      name="PhysBkgBs2DsDsstPiRhoPdf_m_"+samplemode+"_Tot";
      pdf_Bs2DsDsstPiRho_Tot = new RooAddPdf(name.Data(), name.Data(), 
                                             RooArgList(*pdf_Bs2DsPi_Tot,*pdf_Bs2DsstPi_Tot, *pdf_Bs2DsRho_Tot), 
                                             RooArgList(*g2_f1,*g2_f2), true);
      CheckPDF(pdf_Bs2DsDsstPiRho_Tot, debug);
    }
    
    RooProdPdf* pdf_Lb2Dsp_Tot = NULL;
    RooProdPdf* pdf_Lb2Dsstp_Tot = NULL;
    RooAddPdf* pdf_Lb2DsDsstP_Tot = NULL;
    RooAddPdf* pdf_BsLb2DsDsstPPiRho_Tot = NULL;
    RooExtendPdf* epdf_BsLb2DsDsstPPiRho   = NULL;

    if ( valBsLb2DsDsstPPiRho != 0.0 )
    {

      pdf_Lb2Dsp_Tot = buildProdPdfSpecBkgMDFit(workInt, work, samplemode, "Lb2Dsp",  "", merge, dim, charmVarName, debug);
      pdf_Lb2Dsstp_Tot = buildProdPdfSpecBkgMDFit(workInt, work, samplemode, "Lb2Dsstp",  "", merge, dim, charmVarName, debug);	

      name="PhysBkgLb2DsDsstPPdf_m_"+samplemode+"_Tot";
      pdf_Lb2DsDsstP_Tot = new RooAddPdf(name.Data(), name.Data(), *pdf_Lb2Dsp_Tot, *pdf_Lb2Dsstp_Tot, *g3_f1);
      CheckPDF(pdf_Lb2DsDsstP_Tot, debug);
	
      name="PhysBkgBsLb2DsDsstPPiRhoPdf_m_"+samplemode+"_Tot";
      pdf_BsLb2DsDsstPPiRho_Tot = new RooAddPdf(name.Data(), name.Data(),
                                                RooArgList(*pdf_Bs2DsDsstPiRho_Tot, *pdf_Lb2DsDsstP_Tot),
                                                RooArgList(*g5_f1));
      CheckPDF(pdf_BsLb2DsDsstPPiRho_Tot, debug);
    
      name = "BsLb2DsDsstPPiRhoEPDF_m_"+samplemode;
      epdf_BsLb2DsDsstPPiRho = new RooExtendPdf( name.Data() , pdf_BsLb2DsDsstPPiRho_Tot-> GetTitle(),
                                                 *pdf_BsLb2DsDsstPPiRho_Tot  , *nBsLb2DsDsstPPiRhoEvts   );
      CheckPDF( epdf_BsLb2DsDsstPPiRho, debug );
      list = AddEPDF(list, epdf_BsLb2DsDsstPPiRho, nBsLb2DsDsstPPiRhoEvts, debug);
    }
    
    //--------------------------------- FULL PDF --------------------------//
    
    RooAbsPdf* pdf_totBkg = NULL;
    name = "BkgEPDF_m_"+samplemode;
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
  // Load RooKeysPdf from workspace.
  //===============================================================================

  RooKeysPdf* GetRooKeysPdfFromWorkspace(RooWorkspace* work, TString& name, bool debug) {

    RooKeysPdf* pdf = NULL;
    pdf = (RooKeysPdf*)work->pdf(name.Data());
    if (debug == true) {if( pdf != NULL ){ cout<<"[INFO] Read "<<pdf->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}
    return pdf;

  }

  //===============================================================================
  // Load RooHistPdf from workspace.
  //===============================================================================

  RooHistPdf* GetRooHistPdfFromWorkspace(RooWorkspace* work, TString& name, bool debug) {

    RooHistPdf* pdf = NULL;
    pdf = (RooHistPdf*)work->pdf(name.Data());
    if (debug == true) {if( pdf != NULL ){ cout<<"[INFO] Read "<<pdf->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}
    return pdf;

  }

  //===============================================================================
  // Load RooAddPdf from workspace.
  //===============================================================================

  RooAddPdf* GetRooAddPdfFromWorkspace(RooWorkspace* work, TString& name, bool debug) {

    RooAddPdf* pdf = NULL;
    pdf = (RooAddPdf*)work->pdf(name.Data());
    if (debug == true) {if( pdf != NULL ){ cout<<"[INFO] Read "<<pdf->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}
    return pdf;

  }

  //===============================================================================
  // Load RooBinned1DPdf from workspace.
  //===============================================================================

  RooAbsPdf* GetRooBinned1DFromWorkspace(RooWorkspace* work, TString& name, bool debug)
  {
    RooBinned1DQuinticBase<RooAbsPdf>* pdf = NULL;
    pdf = (RooBinned1DQuinticBase<RooAbsPdf>*)work->pdf(name.Data());
    RooAbsPdf* pdf2 = pdf;
    if (debug == true) {if( pdf2 != NULL ){ cout<<"[INFO] Read "<<pdf2->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}
    return pdf2;
  }

  //===============================================================================
  // Load RooAbsPdf from workspace.
  //===============================================================================

  RooAbsPdf* GetRooAbsPdfFromWorkspace(RooWorkspace* work, TString& name, bool debug)
  {
    RooAbsPdf* pdf = NULL;
    pdf = (RooAbsPdf*)work->pdf(name.Data());
    if (debug == true) {if( pdf != NULL ){ cout<<"[INFO] Read "<<pdf->GetName()<<endl;} else { cout<<"Cannot read PDF"<<endl;}}
    return pdf;
  }

  Double_t  CheckEvts( RooWorkspace* workInt, TString samplemode, TString typemode, bool debug)
  {
 
    Double_t val = 0.0; 
    TString nName = "n"+typemode+"_"+samplemode+"_Evts";
    RooRealVar* nEvts = tryVar(nName, workInt, debug);
    val = nEvts->getValV();
   
    if ( debug == true  ) { std::cout<<"[INFO] check number of events: "<<nName<<" value: "<<val<<std::endl; } 
    return val; 
  }
    

  //===============================================================================
  // Check PDF (whether is null).
  //===============================================================================

  bool CheckPDF(RooAbsPdf* pdf, bool debug)
  {
    if( pdf != NULL )
    { 
      if (debug == true) cout<<"[INFO] Create/Read "<<pdf->GetName()<<endl;
      return true;
    }
    else 
    { 
      if (debug == true) cout<<"[ERROR] Cannot create/read PDF"<<endl;
      return false;
    }
  }

  //===============================================================================
  // Check RooRealVar (whether is null).
  //===============================================================================

  bool CheckVar(RooRealVar* var, bool debug)
  {
    if (var != NULL)
    {
      if (debug == true) cout<<"[INFO] Create RooRealVar: "<<var->GetName()<<endl;
      return true;
    }
    else {
      if (debug == true) cout<<"[ERROR] Cannot create RooRealVar"<<endl;
      return false;
    }
  }


  RooArgList* AddEPDF(RooArgList* list, RooExtendPdf* pdf, RooRealVar *numEvts, bool debug)
  {
    Double_t ev = numEvts->getValV();
    if ( ev != 0.0 )
    {
      list->add(*pdf);
      if (debug == true )
      {
        std::cout<<"[INFO] "<<pdf->GetName()<<" added to pdf list with inital number of events:"<<ev<<std::endl; 
      }
    }
    else
    {
      if (debug == true )
      {
        std::cout<<"[INFO] "<<pdf->GetName()<<" NOT added to pdf list, number of events:"<<ev<<std::endl;
      }
    }
    return list; 
  }

  RooArgList* AddEPDF(RooArgList* list, RooExtendPdf* pdf, Double_t ev, bool debug)
  {
    if ( ev != 0.0 )
    {
      list->add(*pdf);
      if (debug == true )
      {
        std::cout<<"[INFO] "<<pdf->GetName()<<" added to pdf list with inital number of events:"<<ev<<std::endl;
      }
    }
    else
    {
      if (debug == true )
      {
        std::cout<<"[INFO] PDF NOT added to pdf list, number of events:"<<ev<<std::endl;
      }
    }
    return list;
  }


  RooAbsPdf* ObtainSignalMassShape(RooAbsReal& mass,
                                   RooWorkspace* work,
                                   RooWorkspace* workInt,
                                   TString samplemode,
                                   TString typemode, 
                                   TString type,
                                   TString pdfName, 
                                   bool extended, 
                                   bool debug)
  {

    RooAbsPdf* pdf = NULL;
    RooAbsPdf* epdf = NULL;
    RooRealVar* nEvts = NULL; 
    Double_t val = 10.0; 
    TString varName = mass.GetName(); 

    Bool_t sharedMean = false;
    if ( type.Contains("SharedMean") == true ) { sharedMean = true; }
    Bool_t widthRatio = false;
    if ( type.Contains("WithWidthRatio") == true ) { widthRatio = true; }

    if ( extended == true )
    {
      TString nName = "nSig_"+samplemode+"_Evts";
      nEvts = GetObservable(workInt, nName, debug);
      val = nEvts->getValV();
    }
    else
    {
      nEvts = new RooRealVar("fake","fake",val); 
    }
    
    if ( type == "RooKeysPdf" )
    {
      pdf = (RooKeysPdf*)work->pdf(pdfName.Data());
      if ( debug == true ) 
      {
        if ( pdf != NULL ) { std::cout<<"[INFO] PDF taken as RooKeyPdf: "<<pdfName<<std::endl;}
        else { std::cout<<"[ERROR] Cannot read pdf: "<<pdfName<<std::endl;} 
      }
    }
    else if ( type.Contains("Ipatia") or type.Contains("Hypatia") )
    {
      pdf =  buildIpatiaPDF( mass, workInt, samplemode, typemode, false, debug); //don't consider rescaled tails, for now
    }
    else if ( type.Contains("Apollonios") == true )
    {
      pdf =  buildApolloniosPDF( mass, workInt, samplemode, typemode, debug);
    }
    else if ( type.Contains("CrystalBall" ) )
    {
      if ( type.Contains("Exponential") )
      {
        pdf= buildExponentialPlusDoubleCrystalBallPDF(mass, workInt, samplemode, typemode, widthRatio, sharedMean, debug);
      }
      else if ( type.Contains("DoubleCrystalBall") )
      {
        pdf =  buildDoubleCrystalBallPDF( mass, workInt, samplemode, typemode, widthRatio, sharedMean, debug);
      }
      else if ( type == "CrystalBall" )
      {
        pdf =  buildCrystalBallPDF( mass, workInt, samplemode, typemode, debug);
      }
      else
      {
        std::cout<<"[ERROR] function: "<<type<<" not defined"<<std::endl; 
      }
    }
    else if ( type.Contains("Gaussian") )
    {
      if ( type.Contains("DoubleGaussian")) 
      {
        pdf = buildDoubleGaussPDF( mass, workInt, samplemode, typemode, widthRatio, sharedMean, debug);
      }
      else if ( type == "Gaussian" )
      {
        pdf = buildGaussPDF( mass, workInt, samplemode, typemode, debug);
      }
      else
      {
        std::cout<<"[ERROR] function: "<<type<<" not defined"<<std::endl;
      }
    }
    else if ( type.Contains("Exponential") ) 
    {
      if ( type == "ExponentialPlusGaussian" )
      {
        pdf = buildExponentialPlusGaussPDF(mass, workInt, samplemode, typemode, debug);
      }
      else if ( type == "Exponential" ) 
      {
        pdf = buildExponentialPDF(mass, workInt, samplemode, typemode, debug);
      }
      else if ( type == "DoubleExponential" )
      {
        pdf = buildDoubleExponentialPDF(mass, workInt, samplemode, typemode, debug);
      }
      else if ( type == "ExponentialTimesLinear" )
      {
        pdf = buildExponentialTimesLinearPDF(mass, workInt, samplemode, typemode, debug);
      }
      else if ( type == "ExponentialPlusSignal")
      {
        pdf = buildExponentialPlusSignalPDF(mass, workInt, samplemode, typemode, debug);
      }
      else
      {
        std::cout<<"[ERROR] function: "<<type<<" not defined"<<std::endl;
      }
    }
    else
    {
      std::cout<<"[ERROR] Type of PDF: "<<type<<" is not specified. Please add to 'build_Signal_MDFitter' function."<<std::endl;  
      return NULL;
    }
    
    TString name = ""; 
    if ( extended == true )
    {
      name = "SigEPDF_"+samplemode;
      epdf = new RooExtendPdf( name.Data() , pdf->GetTitle(), *pdf  , *nEvts   );
      CheckPDF( epdf, debug );
    }
    else
    {
      epdf  = pdf;
    }
    
    return epdf; 
  }
  
  
  RooAbsPdf* build_SigOrCombo(RooAbsReal& mass,
                              RooAbsReal& massDs,
                              RooAbsReal& pidkVar, 
                              RooWorkspace* work,
                              RooWorkspace* workInt,
                              TString samplemode,
                              TString typemode, 
                              TString merge, 
                              TString decay, 
                              std::vector <TString> types,
                              std::vector <std::vector <TString> > pdfNames,
                              std::vector <TString> pidk,
                              Int_t dim,
                              bool debug)
  {


    if (debug == true)
    {
      cout<<"[INFO] =====> Build "<<typemode<<" model with merge: "<<merge<<endl;
      cout<<"[INFO] Types of shapes: "<<std::endl;
      cout<<"[INFO] BeautyMass: "<<types[0]<<std::endl;
      cout<<"[INFO] CharmMass: "<<types[1]<<std::endl;
      cout<<"[INFO] BacPIDK: "<<types[2]<<" with components: Kaon = "<<pidk[0]<<" Pion = "<<pidk[1]<<" Proton = "<<pidk[2]<<std::endl;
    }

    RooExtendPdf* epdf   = NULL;
    TString nName = ""; 
    RooRealVar* nEvts = NULL;

    std::vector<RooAbsPdf*> pdf_pBs;
    std::vector<RooAbsPdf*> pdf_pDs;
    std::vector<RooAbsPdf*> pdf_pPIDK;
    RooAbsPdf* pdf_Bs = NULL;
    RooAbsPdf* pdf_Ds = NULL;
    RooAbsPdf* pdf_PIDK = NULL;

    RooProdPdf* pdf_Tot = NULL;

    if ( typemode == "Signal" )
    {
      nName = "nSig_"+samplemode+"_Evts";
    }
    else
    {
      nName = "n"+typemode+"_"+samplemode+"_Evts";
    }
     
    nEvts = tryVar(nName, workInt, debug);
    Double_t val = nEvts->getValV();

    TString t = "_"; 
    TString mode, Mode;
    std::vector<TString> y, sam; 
    mode = CheckDMode(samplemode,debug);
    if ( mode == "" ) { mode = CheckKKPiMode(samplemode, debug); }
    Mode = GetModeCapital(mode,debug);
    
    y = GetDataYear(samplemode, merge, debug);
    sam = GetPolarity(samplemode, merge, debug);
    std::cout<<"mode: "<<mode<<std::endl; 
    if ( val != 0.0 )
    {
      for(unsigned int i = 0; i < sam.size(); i++ )
      {
        for (unsigned int j =0; j < y.size(); j++ )
	      {
		
          TString smp = sam[i]+"_"+mode+"_"+y[j];
          TString pdfNameBs = findRooKeysPdf(pdfNames, TString(mass.GetName()), smp, debug); 
          pdf_pBs.push_back(ObtainSignalMassShape(mass, work, workInt, smp, typemode, types[0], pdfNameBs, false, debug));
          if ( dim > 1)
          {
            TString pdfNameDs = findRooKeysPdf(pdfNames, TString(massDs.GetName()), smp, debug);
            pdf_pDs.push_back(ObtainSignalMassShape(massDs, work, workInt, smp, typemode, types[1], pdfNameDs, false, debug));
          }
		
          if ( dim > 2 )
          {
            if ( typemode == "CombBkg" || typemode == "Combinatorial" ) 
            {
              pdf_pPIDK.push_back(buildComboPIDKPDF(pidkVar, work, workInt, smp, "CombBkg", pidk, merge,debug));
            }
            else
            {
              pdf_pPIDK.push_back(buildPIDKShapeMDFit(work,smp,decay, mode, debug));
            }
          }	
	      }
      }
    }
 

    if  ( merge == "pol" ) 
    {
	
      pdf_Bs = mergePdf(pdf_pBs[1], pdf_pBs[0], merge, y[0], workInt, debug);
      if ( dim > 1 ) { pdf_Ds = mergePdf(pdf_pDs[1], pdf_pDs[0], merge, y[0], workInt, debug); }
      if ( dim > 2 ) { pdf_PIDK = mergePdf(pdf_pPIDK[1], pdf_pPIDK[0], merge, y[0], workInt, debug); }
    }
    else if ( merge == "year" )
    {
      pdf_Bs = mergePdf(pdf_pBs[1], pdf_pBs[0], merge, sam[0], workInt, debug);
      if ( dim > 1 ) { pdf_Ds = mergePdf(pdf_pDs[1], pdf_pDs[0], merge, sam[0], workInt, debug); }
      if ( dim > 2 ) { pdf_PIDK = mergePdf(pdf_pPIDK[1], pdf_pPIDK[0], merge, sam[0], workInt, debug);}
    }
    else if ( merge == "both" )
    {
      pdf_pBs.push_back(mergePdf(pdf_pBs[2], pdf_pBs[0], "pol", y[0], workInt, debug));
      if ( dim > 1 ) { pdf_pDs.push_back(mergePdf(pdf_pDs[2], pdf_pDs[0], "pol", y[0], workInt, debug)); }
      if ( dim > 2 ) { pdf_pPIDK.push_back(mergePdf(pdf_pPIDK[2], pdf_pPIDK[0], "pol", y[0], workInt, debug));}
	
      pdf_pBs.push_back(mergePdf(pdf_pBs[3], pdf_pBs[1], "pol", y[1], workInt, debug));
      if ( dim > 1 ) { pdf_pDs.push_back(mergePdf(pdf_pDs[3], pdf_pDs[1], "pol", y[1], workInt, debug));}
      if ( dim > 2 ) { pdf_pPIDK.push_back(mergePdf(pdf_pPIDK[3], pdf_pPIDK[1], "pol", y[1], workInt, debug));}

      pdf_Bs = mergePdf(pdf_pBs[5], pdf_pBs[4], "year", "run1", workInt, debug);
      if ( dim > 1 ) { pdf_Ds = mergePdf(pdf_pDs[5], pdf_pDs[4], "year", "run1", workInt, debug);}
      if ( dim > 2 ) { pdf_PIDK = mergePdf(pdf_pPIDK[5], pdf_pPIDK[4], "year", "run1", workInt, debug);}
	
    }
    else 
    {
      pdf_Bs = pdf_pBs[0];
      if ( dim > 1 ) { pdf_Ds = pdf_pDs[0];}
      if ( dim > 2 ) { pdf_PIDK = pdf_pPIDK[0];}
    }

     
    pdf_Tot = GetRooProdPdfDim(typemode, samplemode, pdf_Bs, pdf_Ds, pdf_PIDK, dim, debug  );
    if ( typemode == "Signal" )
    {
      TString name = typemode+"ProdPDF_"+samplemode;  
      pdf_Tot->SetName(name); 
    }
    TString epdfName=""; 
    if ( typemode == "Signal") 
    {
      epdfName = "SigEPDF_"+samplemode;
    }
    else
    {
      epdfName = typemode+"EPDF_"+samplemode;
    }

    epdf = new RooExtendPdf( epdfName.Data() , pdf_Tot->GetTitle(), *pdf_Tot  , *nEvts   );
    CheckPDF( epdf, debug );
    
    return epdf; 
  }

  RooAbsPdf* mergePdf(RooAbsPdf* pdf1, RooAbsPdf* pdf2, TString merge, TString lum,RooWorkspace* workInt, bool debug)
  {

    if ( pdf1->GetName() == pdf2->GetName() ) 
    {
      if(debug == true ) { std::cout<<"[INFO] Pdfs the same: "<<pdf1->GetName()<<" = "<<pdf2->GetName()<<". Nothing done."<<std::endl; }
      return pdf1; 
    }
    TString lumRatioName = "lumRatio_"+lum;
    RooRealVar* lumRatio = GetObservable(workInt, lumRatioName, false);
    RooAbsPdf* pdf = NULL; 
    
    TString name = pdf1->GetName();
    
    
    if ( merge == "pol" )
    {
      if ( name.Contains("down") ) { name.ReplaceAll("down","both"); }
      else if ( name.Contains("up") ) { name.ReplaceAll("up","both"); }
    }
    else if ( merge == "year" ) 
    {
      if ( name.Contains("2011") ) { name.ReplaceAll("2011","run1");}
      else if ( name.Contains("2012") ){ name.ReplaceAll("2012","run1");}
    }
    name = name + "_" + merge; 
    pdf = new RooAddPdf( name.Data(), name.Data(),RooArgList(*pdf1,*pdf2), RooArgList(*lumRatio));

    if ( debug == true )
    {
      std::cout<<"[INFO] Adding "<<pdf1->GetName()<<" to "<<pdf2->GetName()<<" = "<<pdf->GetName()<<" with fraction: "<<lumRatio->getValV()<<std::endl; 
    }
    return pdf; 
  }

  RooAbsPdf* tryPdf(TString name, RooWorkspace* work, bool debug )
  {
    TString p = CheckPolarity(name,false);
    TString y = CheckDataYear(name,false);
    TString m = CheckDMode(name,false);
    if ( m == "") { m = CheckKKPiMode(name, false);}
    TString h = CheckHypo(name,false);
    TString t = "_";

    TString name_prev = name;
    TString name2 = name;

    RooAbsPdf* pdf = (RooKeysPdf*)work->pdf(name.Data()); 

    TString yy[] = {y,"run1"};
    TString mm[] = {m,"all","kkpi"};
    TString pp[] = {p,"both"};
    TString hh[] = {h,"Bd2DPi","Bd2DK","Bs2DsK","Bs2DsPi"};
    int s = 3;
    if ( m == "pipipi" || m == "kpipi" )
    {
      s = 2;
    }
    
    if ( pdf == NULL )
    {
      for( int i = 0; i<2; i++)
      {

        for (int j = 0; j<s; j++ )
        {
          for (int k =0; k<2; k++ )
          {
            for (int l=0; l<5; l++)
            {  
              TString nName = name_prev;
              //std::cout<<"prev: "<<name_prev<<std::endl;                                                                                                                          
              nName = nName.ReplaceAll(y,yy[i]);
              nName = nName.ReplaceAll(m,mm[j]);
              nName = nName.ReplaceAll(p,pp[k]);
              if(h!=""){nName = nName.ReplaceAll(h,hh[l]);}
              pdf = (RooKeysPdf*)work->pdf(nName.Data());
              //std::cout<<"name: "<<nName<<std::endl;
              if ( pdf != NULL ) { break; }
            }            
            if ( pdf != NULL ) { break; }
          }
          if ( pdf != NULL ) { break; }
        }
        if ( pdf != NULL ) { break; }
      }
    }

    if( pdf != NULL ){ if ( debug == true) {std::cout<<"[INFO] Read pdf: "<<pdf->GetName()<<std::endl;} return pdf; }
    else{ std::cout<<"[ERROR] Cannot read pdf."<<std::endl; return NULL;}

  }

  RooRealVar* tryVar(TString name, RooWorkspace* workInt, bool debug) 
  {
    TString p = CheckPolarity(name,false);
    TString y = CheckDataYear(name,false);
    TString m = CheckDMode(name,false);
    if ( m == "") { m = CheckKKPiMode(name, false);}
    TString h = CheckHypo(name,false);
    TString t = "_";
    
    TString name_prev = name;
    TString name2 = name; 
    
    RooRealVar* nEvts = GetObservable(workInt, name_prev, false);

    TString yy[] = {y,"run1"}; 
    TString mm[] = {m,"all","kkpi"};
    TString pp[] = {p,"both"}; 
    TString hh[] = {h,"Bd2DPi","Bd2DK","Bs2DsK","Bs2DsPi"};
    int s = 3; 
    if ( m == "pipipi" || m == "kpipi" ) 
    {
      s = 2; 
    }
    
    if ( nEvts == NULL )
    {
      for( int i = 0; i<2; i++)
      {
	      
        for (int j = 0; j<s; j++ )
	      {
          for (int k =0; k<2; k++ )
          {
            for (int l=0; l<5; l++)
            { 
              TString nName = name_prev;
              //std::cout<<"prev: "<<name_prev<<std::endl;
              nName = nName.ReplaceAll(y,yy[i]);
              nName = nName.ReplaceAll(m,mm[j]);
              nName = nName.ReplaceAll(p,pp[k]);
              if(h!=""){nName = nName.ReplaceAll(h,hh[l]);}
              nEvts = GetObservable(workInt, nName, false);
              if ( nEvts != NULL ) { break; }
            }
            if ( nEvts != NULL ) { break; } 
          }
          if ( nEvts != NULL ) { break; }
	      }
        if ( nEvts != NULL ) { break; }
      }
    }

    if( nEvts != NULL ){ if ( debug == true) {std::cout<<"[INFO] Read observable: "<<nEvts->GetName()<<std::endl;} return nEvts; }
    else{ std::cout<<"[ERROR] Cannot read observable."<<std::endl; return NULL;}    
  
  }

  RooAbsPdf* trySignal(TString samplemode, TString varName, RooWorkspace* workInt, bool debug)
  {
    RooAbsPdf* pdf= NULL;
    
    std::vector<TString> suffix;
    suffix.push_back("_crystalBall_");
    suffix.push_back("_doubleCrystalBall_");
    suffix.push_back("_gauss_");
    suffix.push_back("_doubleGauss_");
    suffix.push_back("_expoGauss_");
    suffix.push_back("_doubleExpo_");
    suffix.push_back("_expoLinear_");
    suffix.push_back("_expoSignal_"); 
    
    std::vector<TString> suffix2;
    suffix2.push_back(""); 
    suffix2.push_back("_pol"); 
    suffix2.push_back("_year"); 
    suffix2.push_back("_pol_year"); 

    for ( unsigned i = 0; i < suffix.size(); i++) 
    {
      for ( unsigned j = 0; j <suffix2.size(); j++ )
      {
        TString pdfName = "Signal_"+varName+suffix[i]+samplemode+suffix2[j];
        pdf = (RooAbsPdf*) workInt -> pdf(pdfName.Data()); 
        if ( pdf != NULL ){ break; }
      }
      if ( pdf != NULL ){ break; }
    }

    CheckPDF(pdf,debug); 
    return pdf; 
  }
  
  TString findRooKeysPdf(std::vector <std::vector <TString> > pdfNames, TString var, TString smp, bool debug)
  {
    TString pdfName = "";

    TString p = CheckPolarity(smp,false);
    TString y = CheckDataYear(smp,false);
    TString m = CheckDMode(smp,false);
    if ( m == "") { m = CheckKKPiMode(smp, false);}
    TString h = CheckHypo(smp,false);
    TString t = "_";

    int pdfID = -1.0; 
    for (unsigned int g = 0; g<pdfNames.size(); g++ )
    {
      if(h!="")
      {   
        if ( pdfNames[g][1].Contains(m)  == true  && pdfNames[g][1].Contains(y) == true     
             && pdfNames[g][1].Contains(p)  == true && pdfNames[g][1].Contains(var)== true && pdfNames[g][1].Contains(h) == true)
        {
          pdfID =g; 
          break;
        }
      }
      else
      {
        if ( pdfNames[g][1].Contains(m)  == true  && pdfNames[g][1].Contains(y) == true
             && pdfNames[g][1].Contains(p)  == true && pdfNames[g][1].Contains(var)== true)
        {
          pdfID =g;
          break; 
        } 
      }
    }
    
    if ( pdfID == -1 )
    {
      TString yy[] = {y,"run1"};
      TString mm[] = {m,"all","kkpi"};
      TString pp[] = {p,"both"};
      TString hh[] = {h,"Bd2DPi","Bd2DK","Bs2DsK","Bs2DsPi"};
      int s = 3;
      if ( m == "pipipi" || m == "kpipi" )
      {
        s = 2;
      }

      for (unsigned int g = 0; g<pdfNames.size(); g++ )
      {
        for( int i = 0; i<2; i++)
	      {
          for (int j = 0; j<s; j++ )
          {
            for (int k =0; k<2; k++ )
            {
              for (int l =0; l<5; l++ )
              { 
                if(h!="")
                { 
                  if ( pdfNames[g][1].Contains(mm[j])  == true  && pdfNames[g][1].Contains(yy[i]) == true
                       && pdfNames[g][1].Contains(pp[k])  == true && pdfNames[g][1].Contains(var)  == true && pdfNames[g][1].Contains(hh[l]) == true)
                  {
                    pdfID =g;
                    break;
                  }
                }
                else
                {
                  if ( pdfNames[g][1].Contains(mm[j])  == true  && pdfNames[g][1].Contains(yy[i]) == true
                       && pdfNames[g][1].Contains(pp[k])  == true && pdfNames[g][1].Contains(var)  == true)
                  {
                    pdfID =g;
                    break; 
                  }
                }
                if ( pdfID>-1 ) { break; }
              }
              if ( pdfID>-1 ) { break; }
            }
            if ( pdfID>-1 ) { break; }
          }
          if ( pdfID>-1 ) { break; }
        }
      }
    }

    if ( pdfID > -1) 
    {
      if ( debug == true ) { std::cout<<"[INFO] Found PDF with pdfId: "<<pdfID<<" and name: "<<pdfNames[pdfID][0]<<std::endl;}
      pdfName = pdfNames[pdfID][0];
    }
    
    return pdfName; 
  }
  
  
}
