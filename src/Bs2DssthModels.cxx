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
#include "TFile.h"
#include "TTree.h"
#include "RooDataSet.h"
#include "RooArgSet.h"
#include "RooHistPdf.h"
#include <string>
#include <vector>
#include <fstream>


#include "B2DXFitters/Bs2Dsh2011TDAnaModels.h"
#include "B2DXFitters/Bs2DssthModels.h"
#include "B2DXFitters/GeneralUtils.h"
#include "B2DXFitters/RooBinned1DQuinticBase.h"

using namespace std;
using namespace GeneralUtils;
using namespace Bs2Dsh2011TDAnaModels;

namespace Bs2DssthModels {

  //===============================================================================
  // Background 3D model for Bs->DsstPi mass fitter.
  //===============================================================================
  RooAbsPdf* build_Bs2DsstPi_BKG( RooAbsReal& mass,
				  RooAbsReal& massDs,
				  RooWorkspace* work,
				  RooWorkspace* workInt,
				  //RooAbsPdf* pdf_Bd2DsstPi,
				  //Bool_t RooKeysPdfForCombo,
				  TString &samplemode,
			          Int_t dim, 
				  bool debug
			          ){
    if (debug == true)
      {
        cout<<"------------------------------------"<<endl;
	cout<<"=====> Build background model BsstDsPi"<<endl;
        cout<<"------------------------------------"<<endl;
      }

    RooArgList* list = new RooArgList();
    //:::::::::::::::::::::::::::::::DsstPi:::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    /*
    TString nBd2DsPiName = "nBd2DsPi_"+samplemode+"_Evts";
    RooRealVar* nBd2DsPiEvts = GetObservable(workInt, nBd2DsPiName, debug);
    Double_t valBd2DsPi = nBd2DsPiEvts->getValV();
    nBd2DsPiEvts->Print();
    
    TString nBd2DsstPiName = "nBd2DsstPi_"+samplemode+"_Evts";
    RooRealVar* nBd2DsstPiEvts = GetObservable(workInt, nBd2DsstPiName, debug);
    Double_t valBd2DsstPi = nBd2DsstPiEvts->getValV();
    nBd2DsstPiEvts->Print();
    
    TString nBs2CombinatorialName = "nBs2Combinatorial_"+samplemode+"_Evts";
    RooRealVar* nBs2CombinatorialEvts = GetObservable(workInt,nBs2CombinatorialName, debug);
    Double_t valnBs2Combinatorial = nBs2CombinatorialEvts->getValV();
    nBs2CombinatorialEvts->Print();
    */
    
    TString nBs2DsRhoName = "nBs2DsRho_"+samplemode+"_Evts";
    RooRealVar*  nBs2DsRhoEvts = GetObservable(workInt, nBs2DsRhoName, debug);    
    Double_t valnBs2DsRho = nBs2DsRhoEvts->getValV();
    nBs2DsRhoEvts->Print();

    TString nBs2DsstRhoName = "nBs2DsstRho_"+samplemode+"_Evts";
    RooRealVar*  nBs2DsstRhoEvts = GetObservable(workInt, nBs2DsstRhoName, debug); 
    Double_t valnBs2DsstRho = nBs2DsstRhoEvts->getValV();
    nBs2DsstRhoEvts->Print();

    /*
    TString nLb2LcPiName = "nLb2LcPi_"+samplemode+"_Evts";
    RooRealVar* nLb2LcPiEvts =  GetObservable(workInt, nLb2LcPiName, debug);
    Double_t valnLb2LcPi = nLb2LcPiEvts->getValV();
    nLb2LcPiEvts->Print();  
    */

    //TString g1_f1_Name = "g1_f1_frac";
    //RooRealVar* g1_f1 = GetObservable(workInt, g1_f1_Name, debug);

    TString Mode = CheckDMode(samplemode,debug);
    TString Year = CheckDataYear(samplemode,debug); 
    if ( Year != "") { Year = "_"+Year; }
    if ( Mode == "") { Mode = CheckKKPiMode(samplemode, debug);}
    /*
    RooRealVar* cDVar = NULL;
    if (dim > 1)
      {
	TString cDVarName = "CombBkg_slope_Ds_"+Mode+Year;
	cDVar =GetObservable(workInt, cDVarName, debug);
      }
    
    RooRealVar* cB1Var = NULL;
    RooRealVar* fracBsComb = NULL;
    RooRealVar* widthComb = NULL;
    RooRealVar* meanComb = NULL;

    if (  RooKeysPdfForCombo == false )
      {
	TString fracBsCombName = "CombBkg_fracBsComb_"+Mode+Year;
	TString widthCombName = "CombBkg_widthComb_"+Mode+Year;
	TString meanCombName = "CombBkg_meanComb_"+Mode+Year;
	TString cB1VarName = "CombBkg_slope_Bs1_"+Mode+Year;
	
	cB1Var = GetObservable(workInt, cB1VarName, debug);
	fracBsComb =GetObservable(workInt, fracBsCombName, debug);
	widthComb =GetObservable(workInt, widthCombName, debug);
	meanComb =GetObservable(workInt, meanCombName, debug);
      }
    RooRealVar* fracDsComb = NULL;
    if (dim>1)
      {
	TString fracDsCombName = "CombBkg_fracDsComb_"+Mode+Year;
	fracDsComb =GetObservable(workInt, fracDsCombName, debug);
      }
    
    RooRealVar* fracPIDComb = NULL;
    if ( dim > 2)
      {
	TString fracPIDCombName = "CombBkg_fracPIDKComb";
	fracPIDComb =GetObservable(workInt, fracPIDCombName, debug);
      }
    */
    TString lumRatioName = "lumRatio"+Year;
    RooRealVar* lumRatio =GetObservable(workInt, lumRatioName, debug);
    lumRatio->Print();

    TString name="";
    TString m = "";
    TString sam = CheckPolarity(samplemode,debug);
    TString y = CheckDataYear(samplemode,debug); 
    
    RooAbsPdf* pdf_SignalDs = NULL;
    if (dim>1)
      {
	TString signalDsName = "sigDs_"+samplemode;
	pdf_SignalDs = GetRooAbsPdfFromWorkspace(workInt, signalDsName, debug);
	CheckPDF(pdf_SignalDs, debug);
      }
// -------------------------------- Create Combinatorial Background --------------------------------------------//
  
    if (debug == true) cout<<"---------------  Create combinatorial background PDF -----------------"<<endl;

    /*
    RooAbsPdf* pdf_combBkg1 = NULL;
    RooAbsPdf* pdf_combBkg2 = NULL;
    RooAbsPdf* pdf_combBkg = NULL;
    RooAddPdf* pdf_combBkg_Ds = NULL;
    RooAbsPdf* pdf_combBkg_PIDK1 = NULL;
    RooAbsPdf* pdf_combBkg_PIDK2 = NULL;
    RooAddPdf* pdf_combBkg_PIDK = NULL;
    RooProdPdf* pdf_combBkg_Tot = NULL;
    RooExtendPdf* epdf_Bs2Combinatorial = NULL;

    if ( valnBs2Combinatorial != 0 )
      {
	if (  RooKeysPdfForCombo == true )
	  {
	    m = "CombPi";                                                                                                                                                             
	    pdf_combBkg = ObtainMassShape(work, m, y, false, *lumRatio, debug); 
	  }
	else
	  {
	    name="CombBkgExpoPDF_"+Mode+Year;
	    pdf_combBkg1 = new RooExponential( name.Data(), "Combinatorial background PDF in mass", mass, *cB1Var);
	    name="CombBkgGaussPDF_"+Mode+Year;
	    pdf_combBkg2 = new RooGaussian(name.Data(),name.Data(),mass,*meanComb,*widthComb);
	    
	    name="CombBkgPDF_"+Mode+Year;
	    pdf_combBkg = new RooAddPdf(name.Data(),name.Data(), RooArgList(*pdf_combBkg1,*pdf_combBkg2),*fracBsComb);
	  }
	if ( dim > 1)
	  {
	    pdf_combBkg_Ds = ObtainComboDs(massDs, *cDVar, *fracDsComb, pdf_SignalDs, Mode, debug); 
	  }
	
	if (dim >2)
	  {
	    m = "Comb";
	    pdf_combBkg_PIDK1 = ObtainPIDKShape(work, m, sam, y, *lumRatio, false, debug);
	    m = "CombK";
	    pdf_combBkg_PIDK2 = ObtainPIDKShape(work, m, sam, y, *lumRatio, false, debug);
	    
	    name = "ShapePIDKAll_Comb_"+samplemode;
	    pdf_combBkg_PIDK = new RooAddPdf( name.Data(),
					      name.Data(),
					      RooArgList(*pdf_combBkg_PIDK1,*pdf_combBkg_PIDK2), *fracPIDComb);
	    CheckPDF(pdf_combBkg_PIDK,debug);
	  }

	m = "CombBkg";
	pdf_combBkg_Tot = GetRooProdPdfDim(m, samplemode, pdf_combBkg, pdf_combBkg_Ds, pdf_combBkg_PIDK, dim, debug  );
   
	name = "Bs2CombinatorialEPDF_m_"+samplemode;
	epdf_Bs2Combinatorial = new RooExtendPdf( name.Data() , pdf_combBkg   -> GetTitle(), *pdf_combBkg_Tot  , *nBs2CombinatorialEvts   );
	CheckPDF( epdf_Bs2Combinatorial, debug);
	list = AddEPDF(list, epdf_Bs2Combinatorial, nBs2CombinatorialEvts, debug);
      }
    */
    // --------------------------------- Read PDFs from Workspace -------------------------------------------------//

 

//Bd2DsPi//
/*
    RooProdPdf* pdf_Bd2DsPi_Tot = NULL;
    RooExtendPdf* epdf_Bd2DsPi = NULL;
    if ( valBd2DsPi != 0 )
      {
	m = "Bd2DsPi";
	pdf_Bd2DsPi_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, y,*lumRatio, pdf_SignalDs, dim, debug);
	
	name = "Bd2DsPiEPDF_m_"+samplemode;
	epdf_Bd2DsPi = new RooExtendPdf(name.Data() , pdf_Bd2DsPi_Tot->GetTitle(), *pdf_Bd2DsPi_Tot, *nBd2DsPiEvts );
	CheckPDF(epdf_Bd2DsPi, debug);
	list = AddEPDF(list, epdf_Bd2DsPi, nBd2DsPiEvts, debug);
      }
*/
//Bs2DsRho//
    RooProdPdf* pdf_Bs2DsRho_Tot = NULL;
    RooExtendPdf* epdf_Bs2DsRho = NULL;

    if ( valnBs2DsRho != 0 )
      {
	m = "Bs2DsRho";
	pdf_Bs2DsRho_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, pdf_SignalDs, dim, debug);
	
	name = "Bs2DsRhoEPDF_m_"+samplemode;
	epdf_Bs2DsRho = new RooExtendPdf(name.Data() , pdf_Bs2DsRho_Tot->GetTitle(), *pdf_Bs2DsRho_Tot, *nBs2DsRhoEvts );
	CheckPDF(epdf_Bs2DsRho, debug);  
	list = AddEPDF(list, epdf_Bs2DsRho, nBs2DsRhoEvts, debug);
      }

//Bs2DsstRho//
    RooProdPdf* pdf_Bs2DsstRho_Tot = NULL;
    RooExtendPdf* epdf_Bs2DsstRho = NULL;

    if (  valnBs2DsstRho != 0 )
      {
	m = "Bs2DsstRho";
	pdf_Bs2DsstRho_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, pdf_SignalDs, dim, debug);
	
	name = "Bs2DsstRhoEPDF_m_"+samplemode;
	epdf_Bs2DsstRho = new RooExtendPdf(name.Data() , pdf_Bs2DsstRho_Tot->GetTitle(), *pdf_Bs2DsstRho_Tot, *nBs2DsstRhoEvts );
	CheckPDF(epdf_Bs2DsstRho, debug);
	list = AddEPDF(list, epdf_Bs2DsstRho, nBs2DsstRhoEvts, debug);
      }

 //pdf_Lb2LcPi_Tot//
    /*
    RooProdPdf* pdf_Lb2LcPi_Tot = NULL;
    RooExtendPdf* epdf_Lb2LcPi = NULL;

    if ( valnLb2LcPi != 0 )
      {
	m = "Lb2LcPi";
	pdf_Lb2LcPi_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, NULL, dim, debug);
	
	name = "Lb2LcPiEPDF_m_"+samplemode;
	epdf_Lb2LcPi = new RooExtendPdf(name.Data() , pdf_Lb2LcPi_Tot->GetTitle(), *pdf_Lb2LcPi_Tot, *nLb2LcPiEvts );
	list = AddEPDF(list, epdf_Lb2LcPi, nLb2LcPiEvts, debug);
      }
    */
    // --------------------------------- Create RooAddPdf -------------------------------------------------/
    /*
    RooAbsPdf* pdf_Bd2DsstPi_PIDK = NULL;
    RooAbsPdf* pdf_Bd2DsstPi_Ds = NULL;
    RooProdPdf* pdf_Bd2DsstPi_Tot = NULL;
    RooExtendPdf* epdf_Bd2DsstPi = NULL;

    if( valBd2DsstPi != 0 )
      {
	m = "Bs2DsstPi_"+samplemode;
	if ( dim > 2 )
	  {
	    pdf_Bd2DsstPi_PIDK = ObtainPIDKShape(work, m, sam, y, *lumRatio, true, debug);
	  }
	if (dim > 1)
	  {
	    pdf_Bd2DsstPi_Ds = pdf_SignalDs;
	  }
	
	m = "Bd2DsstPi";
	pdf_Bd2DsstPi_Tot = GetRooProdPdfDim(m, samplemode, pdf_Bd2DsstPi, pdf_Bd2DsstPi_Ds, pdf_Bd2DsstPi_PIDK, dim, debug  );
	
	name = "Bd2DsstPiEPDF_m_"+samplemode;
	epdf_Bd2DsstPi = new RooExtendPdf(name.Data() , pdf_Bd2DsstPi_Tot->GetTitle(), *pdf_Bd2DsstPi_Tot, *nBd2DsstPiEvts );
	list = AddEPDF(list, epdf_Bd2DsstPi, nBd2DsstPiEvts, debug);
      }
    */
    RooAbsPdf* pdf_totBkg = NULL;
    name = "BkgEPDF_m_"+samplemode;
    pdf_totBkg = new RooAddPdf( name.Data(), name.Data(), *list);
					   
    return pdf_totBkg;
 
}

  //===============================================================================                                                                                                       
  // Background 3D model for Bs->DsstK mass fitter.                                           
  //===============================================================================              

  RooAbsPdf* build_Bs2DsstK_BKG( RooAbsReal& mass,
				 RooAbsReal& massDs,
				 RooWorkspace* work,
				 RooWorkspace* workInt,
				 Bool_t RooKeysPdfForCombo,
				 TString &samplemode,
				 Int_t dim,
				 bool debug
				 ){
    if (debug == true)
      {
        cout<<"---------------------------------------"<<endl;
        cout<<"=====> Build background model BsDsstK"<<endl;
        cout<<"---------------------------------------"<<endl;
      }

    RooArgList* list = new RooArgList();

    TString nBs2CombinatorialName = "nBs2Combinatorial_"+samplemode+"_Evts";
    RooRealVar* nBs2CombinatorialEvts = GetObservable(workInt,nBs2CombinatorialName, debug);
    Double_t valnBs2Combinatorial = nBs2CombinatorialEvts->getValV();
    nBs2CombinatorialEvts->Print();

    TString nBs2DsstPiName = "nBs2DsstPi_"+samplemode+"_Evts";
    RooRealVar*  nBs2DsstPiEvts = GetObservable(workInt, nBs2DsstPiName, debug);
    Double_t valnBs2DsstPi = nBs2DsstPiEvts->getValV();
    nBs2DsstPiEvts->Print();

    TString nBs2DsKstName = "nBs2DsKst_"+samplemode+"_Evts";
    RooRealVar* nBs2DsKstEvts = GetObservable(workInt, nBs2DsKstName, debug);
    Double_t valnBs2DsKst = nBs2DsKstEvts->getValV();
    nBs2DsKstEvts->Print();

    TString nBs2DsstKstName = "nBs2DsstKst_"+samplemode+"_Evts";
    RooRealVar* nBs2DsstKstEvts = GetObservable(workInt, nBs2DsstKstName, debug);
    Double_t valnBs2DsstKst = nBs2DsstKstEvts->getValV();
    nBs2DsstKstEvts->Print();

    TString nBs2DsstRhoName = "nBs2DsstRho_"+samplemode+"_Evts";
    RooRealVar*  nBs2DsstRhoEvts = GetObservable(workInt, nBs2DsstRhoName, debug);
    Double_t valnBs2DsstRho = nBs2DsstRhoEvts->getValV();
    nBs2DsstRhoEvts->Print();

    TString g1_f1_Name = "g1_f1_frac";
    //    RooRealVar* g1_f1 = GetObservable(workInt, g1_f1_Name, debug);                                                                                                                
     
    TString Mode = CheckDMode(samplemode,debug);
    TString Year = CheckDataYear(samplemode,debug);
    TString y = CheckDataYear(samplemode,debug);
    if ( Year != "") { Year = "_"+Year; }
    if ( Mode == "") { Mode = CheckKKPiMode(samplemode, debug);}

    RooRealVar* cDVar = NULL;
    if (dim > 1)
      {
        TString cDVarName = "CombBkg_slope_Ds_"+Mode+Year;
        cDVar =GetObservable(workInt, cDVarName, debug);
      }

    RooRealVar* cB1Var = NULL;
    RooRealVar* fracBsComb = NULL;
    RooRealVar* widthComb = NULL;
    RooRealVar* meanComb = NULL;

    if (  RooKeysPdfForCombo == false )
      {
        TString fracBsCombName = "CombBkg_fracBsComb_"+Mode+Year;
        TString widthCombName = "CombBkg_widthComb_"+Mode+Year;
        TString meanCombName = "CombBkg_meanComb_"+Mode+Year;
        TString cB1VarName = "CombBkg_slope_Bs1_"+Mode+Year;

        cB1Var = GetObservable(workInt, cB1VarName, debug);
        fracBsComb =GetObservable(workInt, fracBsCombName, debug);
        widthComb =GetObservable(workInt, widthCombName, debug);
        meanComb =GetObservable(workInt, meanCombName, debug);
      }

    RooRealVar* fracDsComb = NULL;
    if (dim>1)
      {
        TString fracDsCombName = "CombBkg_fracDsComb_"+Mode+Year;
        fracDsComb =GetObservable(workInt, fracDsCombName, debug);
      }

    RooRealVar* fracPIDComb = NULL;
    if ( dim > 2)
      {
        TString fracPIDCombName = "CombBkg_fracPIDKComb";
        fracPIDComb =GetObservable(workInt, fracPIDCombName, debug);
      }

    TString lumRatioName = "lumRatio";
    RooRealVar* lumRatio =GetObservable(workInt, lumRatioName, debug);
    lumRatio->Print();

    TString name="";
    TString m = "";
    TString sam = CheckPolarity(samplemode,debug);

    RooAbsPdf* pdf_SignalDs = NULL;
    if (dim>1)
      {
	TString signalDsName = "sigDs_"+samplemode;
        pdf_SignalDs = GetRooAbsPdfFromWorkspace(workInt, signalDsName, debug);
        CheckPDF(pdf_SignalDs, debug);
      }
    RooAbsPdf* pdf_Bs2DsstK_PIDK = NULL;

    // -------------------------------- Create Combinatorial Background --------------------------------------------//                                    

    if (debug == true) cout<<"---------------  Create combinatorial background PDF -----------------"<<endl;

    
    RooAbsPdf* pdf_combBkg1 = NULL;
    RooAbsPdf* pdf_combBkg2 = NULL;
    RooAbsPdf* pdf_combBkg = NULL;
    RooAbsPdf* pdf_combBkg_PIDK1 = NULL;
    RooAbsPdf* pdf_combBkg_PIDK2 = NULL;
    RooAddPdf* pdf_combBkg_PIDK = NULL;
    RooAddPdf* pdf_combBkg_Ds = NULL;
    RooProdPdf* pdf_combBkg_Tot = NULL;
    RooExtendPdf* epdf_Bs2Combinatorial = NULL;

    if ( valnBs2Combinatorial != 0 )
      {
	if (  RooKeysPdfForCombo == true )
          {
            m = "CombK";
            pdf_combBkg = ObtainMassShape(work, m, y, false, *lumRatio, debug);
          }
	else
	  {
	    name="CombBkgExpoPDF_"+Mode;
	    pdf_combBkg1 = new RooExponential( name.Data(), "Combinatorial background PDF in mass", mass, *cB1Var);
	    name="CombBkgGaussPDF_"+Mode;
	    pdf_combBkg2 = new RooGaussian("gauss","gauss",mass,*meanComb,*widthComb);
	
	    name="CombBkgPDF_"+Mode;
	    pdf_combBkg = new RooAddPdf(name.Data(),name.Data(), RooArgList(*pdf_combBkg1,*pdf_combBkg2),*fracBsComb);
	  }

	if ( dim > 1)
	  {
	    pdf_combBkg_Ds = ObtainComboDs(massDs, *cDVar, *fracDsComb, pdf_SignalDs, Mode, debug);
	  }

	m = "CombBkg";
	pdf_combBkg_Tot = GetRooProdPdfDim(m, samplemode, pdf_combBkg, pdf_combBkg_Ds, pdf_combBkg_PIDK, dim, debug  );
	
	name = "Bs2CombinatorialEPDF_m_"+samplemode;
	epdf_Bs2Combinatorial = new RooExtendPdf( name.Data() , pdf_combBkg   -> GetTitle(), *pdf_combBkg_Tot  , *nBs2CombinatorialEvts   );
	CheckPDF( epdf_Bs2Combinatorial, debug);
	list = AddEPDF(list, epdf_Bs2Combinatorial, nBs2CombinatorialEvts, debug);
      }

    // --------------------------------- Read PDFs from Workspace -------------------------------------------------                                                                       

    //Bs2DsstPi//                                                                                                                                                                       
    RooProdPdf* pdf_Bs2DsstPi_Tot = NULL;
    RooExtendPdf* epdf_Bs2DsstPi = NULL;
    if ( valnBs2DsstPi != 0 )
      {
	m = "Bs2DsstPi";
	pdf_Bs2DsstPi_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, pdf_SignalDs, dim, debug);
	
	name = "Bs2DsstPiEPDF_m_"+samplemode;
	epdf_Bs2DsstPi = new RooExtendPdf(name.Data() , pdf_Bs2DsstPi_Tot->GetTitle(), *pdf_Bs2DsstPi_Tot, *nBs2DsstPiEvts );
	CheckPDF(epdf_Bs2DsstPi, debug);
	list = AddEPDF(list, epdf_Bs2DsstPi, nBs2DsstPiEvts, debug);
      }
    //Bs2DsKst//                                                                                                                                            
    RooProdPdf* pdf_Bs2DsKst_Tot = NULL;
    RooExtendPdf* epdf_Bs2DsKst = NULL;
    if ( valnBs2DsKst != 0 )
      {
	m = "Bs2DsKst";
	pdf_Bs2DsKst_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, pdf_SignalDs, dim, debug);
	
	name = "Bs2DsKstEPDF_m_"+samplemode;
	epdf_Bs2DsKst = new RooExtendPdf(name.Data() , pdf_Bs2DsKst_Tot->GetTitle(), *pdf_Bs2DsKst_Tot, *nBs2DsKstEvts );
	CheckPDF(epdf_Bs2DsKst, debug);
	list = AddEPDF(list, epdf_Bs2DsKst, nBs2DsKstEvts, debug);
      }

    //Bs2DsstKst//                                                                                                                                                        
    RooProdPdf* pdf_Bs2DsstKst_Tot = NULL;
    RooExtendPdf* epdf_Bs2DsstKst = NULL;
    if ( valnBs2DsstKst != 0 )
      {
	m = "Bs2DsstKst";
	std::cout<<" ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"<<sam<<endl;
	pdf_Bs2DsstKst_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, pdf_SignalDs, dim, debug);
	std::cout<<" ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"<<sam<<endl;
	name = "Bs2DsstKstEPDF_m_"+samplemode;
	std::cout<<" ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"<<pdf_Bs2DsstKst_Tot->GetTitle() <<" "<<nBs2DsstKstEvts<<endl;

	epdf_Bs2DsstKst = new RooExtendPdf(name.Data() , pdf_Bs2DsstKst_Tot->GetTitle(), *pdf_Bs2DsstKst_Tot, *nBs2DsstKstEvts );
	CheckPDF(epdf_Bs2DsstKst, debug);
	list = AddEPDF(list, epdf_Bs2DsstKst, nBs2DsstKstEvts, debug);
      }
    //Bs2DsstRho//                                                                                                                                     
    RooProdPdf* pdf_Bs2DsstRho_Tot = NULL;
    RooExtendPdf* epdf_Bs2DsstRho = NULL;

    if ( valnBs2DsstRho != 0 )
      {
	m = "Bs2DsstRho";
	pdf_Bs2DsstRho_Tot =  ObtainRooProdPdfForMDFitter(work, m, sam, y, *lumRatio, pdf_SignalDs, dim, debug);
	
	name = "Bs2DsstRhoEPDF_m_"+samplemode;
	epdf_Bs2DsstRho = new RooExtendPdf(name.Data() , pdf_Bs2DsstRho_Tot->GetTitle(), *pdf_Bs2DsstRho_Tot, *nBs2DsstRhoEvts );
	CheckPDF(epdf_Bs2DsstRho, debug);
	list = AddEPDF(list, epdf_Bs2DsstRho, nBs2DsstRhoEvts, debug);
      }

    // --------------------------------- Create RooAddPdf -------------------------------------------------/                                                                              
    RooAbsPdf* pdf_totBkg = NULL;
    name = "BkgEPDF_m_"+samplemode;
    //*epdf_combBkg<---fondo non def da template                                                                                                                                         
    pdf_totBkg = new RooAddPdf( name.Data(), name.Data(),*list);

    return pdf_totBkg;

  }

}
