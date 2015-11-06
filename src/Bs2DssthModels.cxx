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
				  TString &samplemode,
				  TString merge, 
			          Int_t dim, 
				  bool debug
			          ){
    if (debug == true)
      {
        cout<<"------------------------------------------------"<<endl;
	cout<<"[INFO] =====> Build background model Bs2DsstPi"<<endl;
        cout<<"-------------------------------------------------"<<endl;
      }

    RooArgList* list = new RooArgList();
    TString charmVarName = massDs.GetName(); 
    TString beautyVarName = mass.GetName();
    if(beautyVarName) { } 

    // --------------------------------- Read PDFs from Workspace -------------------------------------------------//
    RooExtendPdf* epdf_Bs2DsRho = NULL;
    epdf_Bs2DsRho = buildExtendPdfSpecBkgMDFit( workInt, work, samplemode, "Bs2DsRho", "", merge, dim, "", debug);
    Double_t valBs2DsRho = CheckEvts(workInt, samplemode, "Bs2DsRho",debug);
    list = AddEPDF(list, epdf_Bs2DsRho, valBs2DsRho, debug);
      
    RooExtendPdf* epdf_Bs2DsstRho = NULL;
    epdf_Bs2DsstRho = buildExtendPdfSpecBkgMDFit( workInt, work, samplemode, "Bs2DsstRho", "", merge, dim, charmVarName, debug);
    Double_t valBs2DsstRho = CheckEvts(workInt, samplemode, "Bs2DsstRho",debug);
    list = AddEPDF(list, epdf_Bs2DsstRho, valBs2DsstRho, debug);

    RooExtendPdf* epdf_Bd2DsstPi = NULL;
    epdf_Bd2DsstPi = buildExtendPdfSpecBkgMDFit( workInt, work, samplemode, "Bd2DsstPi", "", merge, dim, charmVarName, debug);
    Double_t valBd2DsstPi = CheckEvts(workInt, samplemode, "Bd2DsstPi",debug);
    list = AddEPDF(list, epdf_Bd2DsstPi, valBd2DsstPi, debug);

    RooAbsPdf* pdf_totBkg = NULL;
    TString name = "BkgEPDF_m_"+samplemode;
    pdf_totBkg = new RooAddPdf( name.Data(), name.Data(), *list);
					   
    return pdf_totBkg;
 
}

  //===============================================================================                                                                                                      
  // Background 3D model for Bs->DsstK mass fitter.                                           
  //===============================================================================              

  RooAbsPdf* build_Bs2DsstK_BKG(RooAbsReal& mass,
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
        cout<<"---------------------------------------"<<endl;
        cout<<"=====> Build background model BsDsstK"<<endl;
        cout<<"---------------------------------------"<<endl;
      }

    RooArgList* list = new RooArgList();
    TString charmVarName = massDs.GetName();
    TString beautyVarName = mass.GetName();
    if(beautyVarName) { }
    TString name = ""; 
    TString mode = CheckDMode(samplemode,debug);
    if ( mode == "" ) { mode = CheckKKPiMode(samplemode, debug); }


    TString nBsBd2DsKstName = "nBsBd2DsKst_"+samplemode+"_Evts";
    RooRealVar* nBsBd2DsKstEvts = tryVar(nBsBd2DsKstName, workInt, debug);
    Double_t valnBsBd2DsKst = nBsBd2DsKstEvts->getValV();
    nBsBd2DsKstEvts->Print();

    TString nBsBd2DsstKstName = "nBsBd2DsstKst_"+samplemode+"_Evts";
    RooRealVar* nBsBd2DsstKstEvts = tryVar(nBsBd2DsstKstName, workInt, debug);
    Double_t valnBsBd2DsstKst = nBsBd2DsstKstEvts->getValV();
    nBsBd2DsstKstEvts->Print();

    TString nBs2DsDsstRhoName = "nBs2DsDsstRho_"+samplemode+"_Evts";
    RooRealVar*  nBs2DsDsstRhoEvts = tryVar(nBs2DsDsstRhoName, workInt, debug);
    Double_t valnBs2DsDsstRho = nBs2DsDsstRhoEvts->getValV();
    nBs2DsDsstRhoEvts->Print();
   
    /*
    RooExtendPdf* epdf_Bs2DsstPi = NULL;
    epdf_Bs2DsstPi = buildExtendPdfSpecBkgMDFit( workInt, work, samplemode, "Bs2DsstPi", "", merge, dim, charmVarName, debug);
    Double_t valBs2DsstPi = CheckEvts(workInt, samplemode, "Bs2DsstPi",debug);
    list = AddEPDF(list, epdf_Bs2DsstPi, valBs2DsstPi, debug);
    */
    /*
    RooExtendPdf* epdf_Bd2DsstK = NULL;
    epdf_Bd2DsstK = buildExtendPdfSpecBkgMDFit( workInt, work, samplemode, "Bd2DsstK", "", merge, dim, charmVarName, debug);
    Double_t valBd2DsstK = CheckEvts(workInt, samplemode, "Bd2DsstK",debug);
    list = AddEPDF(list, epdf_Bd2DsstK, valBd2DsstK, debug);
    */

    
    RooProdPdf* pdf_Bs2DsRho_Tot = NULL;
    RooProdPdf* pdf_Bs2DsstRho_Tot = NULL;
    RooProdPdf* pdf_Bs2DsstPi_Tot = NULL;
    RooAddPdf* pdf_Bs2DsDsstRho_Tot = NULL; 
    RooAddPdf* pdf_Bs2DsDsstPiRho_Tot = NULL;
    RooExtendPdf* epdf_Bs2DsDsstRho   = NULL;

    TString g1_f1_Name = "g1_f1_frac_"+samplemode;
    RooRealVar* g1_f1 = tryVar(g1_f1_Name, workInt,debug);
    TString g1_f2_Name = "g1_f2_frac_"+samplemode;
    RooRealVar* g1_f2 = tryVar(g1_f2_Name, workInt,debug);

    if ( valnBs2DsDsstRho != 0.0 )
      {

        pdf_Bs2DsRho_Tot  = buildProdPdfSpecBkgMDFit(workInt, work, samplemode, "Bs2DsRho",  "", merge, dim, "", debug);
        pdf_Bs2DsstRho_Tot = buildProdPdfSpecBkgMDFit(workInt, work, samplemode, "Bs2DsstRho", "", merge, dim, charmVarName, debug);
	pdf_Bs2DsstPi_Tot = buildProdPdfSpecBkgMDFit(workInt, work, samplemode, "Bs2DsstPi", "", merge, dim, charmVarName, debug);

	
        name ="PhysBkgBs2DsDsstRhoPdf_m_"+samplemode+"_Tot";
        pdf_Bs2DsDsstRho_Tot = new RooAddPdf(name.Data(), name.Data(),
					     RooArgList(*pdf_Bs2DsstRho_Tot,*pdf_Bs2DsRho_Tot),
					     RooArgList(*g1_f1), true);
        CheckPDF(pdf_Bs2DsDsstRho_Tot, debug);

	name ="PhysBkgBs2DsDsstPiRhoPdf_m_"+samplemode+"_Tot";
        pdf_Bs2DsDsstPiRho_Tot = new RooAddPdf(name.Data(), name.Data(),
					       RooArgList(*pdf_Bs2DsstPi_Tot, *pdf_Bs2DsDsstRho_Tot),
					       RooArgList(*g1_f2), true);
        CheckPDF(pdf_Bs2DsDsstPiRho_Tot, debug);

	
	/*
	name ="PhysBkgBs2DsDsstRhoPdf_m_"+samplemode+"_Tot";                                                                                                                                        
        pdf_Bs2DsDsstRho_Tot = new RooAddPdf(name.Data(), name.Data(),                                                                                                                             
                                             RooArgList(*pdf_Bs2DsRho_Tot,*pdf_Bs2DsstRho_Tot), 
					     RooArgList(*g1_f1), true);                                                                                                                      
        CheckPDF(pdf_Bs2DsDsstRho_Tot, debug);
	*/
	name = "Bs2DsDsstRhoEPDF_m_"+samplemode;
        epdf_Bs2DsDsstRho = new RooExtendPdf( name.Data() , pdf_Bs2DsDsstPiRho_Tot-> GetTitle(), *pdf_Bs2DsDsstPiRho_Tot  , *nBs2DsDsstRhoEvts   );
	CheckPDF( epdf_Bs2DsDsstRho, debug );
        list = AddEPDF(list, epdf_Bs2DsDsstRho, nBs2DsDsstRhoEvts, debug);
      }


    RooProdPdf* pdf_Bs2DsKst_Tot = NULL;
    RooProdPdf* pdf_Bd2DsKst_Tot = NULL;
    RooAddPdf* pdf_BsBd2DsKst_Tot = NULL;
    RooAddPdf* pdf_BsBd2DsDsstPiRhoKst_Tot = NULL;
    RooExtendPdf* epdf_BsBd2DsKst   = NULL;

    TString g2_f1_Name = "g2_f1_frac_"+samplemode;
    RooRealVar* g2_f1 = tryVar(g2_f1_Name, workInt,debug);

    TString g4_f1_Name = "g4_f1_frac_"+samplemode;
    RooRealVar* g4_f1 = tryVar(g4_f1_Name, workInt,debug);

    if ( valnBsBd2DsKst != 0.0 )
      {

        pdf_Bs2DsKst_Tot = buildProdPdfSpecBkgMDFit(workInt, work, samplemode, "Bs2DsKst", "", merge, dim, "", debug);
        pdf_Bd2DsKst_Tot = buildProdPdfSpecBkgMDFit(workInt, work, samplemode, "Bd2DsKst", "", merge, dim, "", debug);

        name ="PhysBkgBsBd2DsKstPdf_m_"+samplemode+"_Tot";
        pdf_BsBd2DsKst_Tot = new RooAddPdf(name.Data(), name.Data(),
					   RooArgList(*pdf_Bs2DsKst_Tot,*pdf_Bd2DsKst_Tot),
					   RooArgList(*g2_f1), true);
        CheckPDF(pdf_BsBd2DsKst_Tot, debug);

	/*
	name ="PhysBkgBsBd2DsDsstPiRhoKstPdf_m_"+samplemode+"_Tot";
        pdf_BsBd2DsDsstPiRhoKst_Tot = new RooAddPdf(name.Data(), name.Data(),
                                                   RooArgList(*pdf_Bs2DsDsstPiRho_Tot,*pdf_BsBd2DsKst_Tot),
                                                   RooArgList(*g4_f1), true);
        CheckPDF(pdf_BsBd2DsDsstPiRhoKst_Tot, debug);
	*/
	
        name = "BsBd2DsKstEPDF_m_"+samplemode;
        epdf_BsBd2DsKst = new RooExtendPdf( name.Data() , pdf_BsBd2DsKst_Tot-> GetTitle(), *pdf_BsBd2DsKst_Tot  , *nBsBd2DsKstEvts   );
        //epdf_BsBd2DsKst = new RooExtendPdf( name.Data() , pdf_BsBd2DsKst_Tot-> GetTitle(), *pdf_BsBd2DsDsstPiRhoKst_Tot  , *nBsBd2DsKstEvts   );
	CheckPDF( epdf_BsBd2DsKst, debug );
        list = AddEPDF(list, epdf_BsBd2DsKst, nBsBd2DsKstEvts, debug);
      }

    RooAbsPdf* pdf_Bd2DsstK_Bs = NULL;
    RooAbsPdf* pdf_Bd2DsstK_PIDK = NULL;
    RooAbsPdf* pdf_Bd2DsstK_Ds = NULL;
    RooProdPdf* pdf_Bs2DsstKst_Tot = NULL;
    RooProdPdf* pdf_Bd2DsstKst_Tot = NULL;
    RooProdPdf* pdf_Bd2DsstK_Tot = NULL;
    RooAddPdf* pdf_BsBd2DsstKst_Tot = NULL;
    RooAddPdf* pdf_BsBd2DsstKKst_Tot = NULL;
    RooExtendPdf* epdf_BsBd2DsstKst   = NULL;
    

    TString g3_f1_Name = "g3_f1_frac_"+samplemode;
    RooRealVar* g3_f1 = tryVar(g3_f1_Name, workInt,debug);
    TString g3_f2_Name = "g3_f2_frac_"+samplemode;
    RooRealVar* g3_f2 = tryVar(g3_f2_Name, workInt,debug);

    if ( valnBsBd2DsstKst != 0.0 )
      {

        pdf_Bs2DsstKst_Tot = buildProdPdfSpecBkgMDFit(workInt, work, samplemode, "Bs2DsstKst", "", merge, dim, charmVarName, debug);
	pdf_Bd2DsstKst_Tot = buildProdPdfSpecBkgMDFit(workInt, work, samplemode, "Bd2DsstKst", "", merge, dim, charmVarName, debug);
	//pdf_Bd2DsstK_Tot = buildProdPdfSpecBkgMDFit(workInt, work, samplemode, "Bd2DsstK", "", merge, dim, charmVarName, debug);

	pdf_Bd2DsstK_Bs = buildShiftedDoubleCrystalBallPDF(mass, workInt, samplemode, "Bd2DsstK", debug);
        if( dim > 2)
          {
            pdf_Bd2DsstK_PIDK = buildMergedSpecBkgMDFit(workInt, work, samplemode, "Bd2DsstK", "", merge, 3, "", debug);
          }
        if ( dim > 1 )
          {
            pdf_Bd2DsstK_Ds = trySignal(samplemode,charmVarName,workInt, debug);
          }
        TString m = "Bd2DsstK";
        pdf_Bd2DsstK_Tot = GetRooProdPdfDim(m, samplemode, pdf_Bd2DsstK_Bs, pdf_Bd2DsstK_Ds, pdf_Bd2DsstK_PIDK, dim, debug  );


	name ="PhysBkgBsBd2DsstKstPdf_m_"+samplemode+"_Tot";
        pdf_BsBd2DsstKst_Tot = new RooAddPdf(name.Data(), name.Data(),
					     RooArgList(*pdf_Bs2DsstKst_Tot,*pdf_Bd2DsstKst_Tot),
					     RooArgList(*g3_f1), true);
	CheckPDF(pdf_BsBd2DsstKst_Tot, debug);

	name ="PhysBkgBsBd2DsstKKstPdf_m_"+samplemode+"_Tot";
        pdf_BsBd2DsstKKst_Tot = new RooAddPdf(name.Data(), name.Data(),
                                             RooArgList(*pdf_Bd2DsstK_Tot,*pdf_BsBd2DsstKst_Tot),
                                             RooArgList(*g3_f2), true);
        CheckPDF(pdf_BsBd2DsstKst_Tot, debug);	

        name = "BsBd2DsstKstEPDF_m_"+samplemode;
	epdf_BsBd2DsstKst = new RooExtendPdf( name.Data() , pdf_BsBd2DsstKKst_Tot-> GetTitle(), *pdf_BsBd2DsstKKst_Tot  , *nBsBd2DsstKstEvts   );
	CheckPDF( epdf_BsBd2DsstKst, debug );
        list = AddEPDF(list, epdf_BsBd2DsstKst, nBsBd2DsstKstEvts, debug);
      }


    // --------------------------------- Create RooAddPdf -------------------------------------------------/                                                                              
    RooAbsPdf* pdf_totBkg = NULL;
    name = "BkgEPDF_m_"+samplemode;
    //*epdf_combBkg<---fondo non def da template                                                                                                                                         
    pdf_totBkg = new RooAddPdf( name.Data(), name.Data(),*list);

    return pdf_totBkg;

  }

}
