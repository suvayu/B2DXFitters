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
#include "B2DXFitters/GeneralUtils.h"
#include "B2DXFitters/RooBinned1DQuinticBase.h"
#include "B2DXFitters/Bs2Dsh2011TDAnaModels.h"

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
  
} // end of namespace

//=============================================================================
