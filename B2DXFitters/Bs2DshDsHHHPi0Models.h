#ifndef Bs2DshDsHHHPi0Models_H
#define Bs2DshDsHHHPi0Models_H 1


#include "RooRealVar.h"
#include "RooAbsPdf.h"
#include "RooResolutionModel.h"
#include "RooWorkspace.h"
#include "RooAddPdf.h"
#include "RooHistPdf.h"
#include "RooProdPdf.h"
#include "RooArgList.h"

namespace Bs2DshDsHHHPi0Models {
  

  //===============================================================================
  // Background 3D model for Bs->DsPi (Ds --> HHHPi0) mass fitter.
  //===============================================================================

  RooAbsPdf* build_Bs2DsPi_BKG_HHHPi0(	RooAbsReal& mass, RooAbsReal& massDs,
					RooWorkspace* work, RooWorkspace* workInt,
				      	RooAbsPdf* pdf_BdDsPi,
					TString &samplemode, Int_t dim, bool debug = false);

  //===============================================================================
  // Background 3D model for Bs->DsK (Ds --> HHHPi0) mass fitter.
  //===============================================================================

  RooAbsPdf* build_Bs2DsK_BKG_HHHPi0( RooAbsReal& mass, RooAbsReal& massDs,
				      RooWorkspace* work, RooWorkspace* workInt,
				      RooAbsPdf* pdf_Bd2DsK, 
				      TString &samplemode, Int_t dim = 3, bool debug = false);
  
}

#endif
