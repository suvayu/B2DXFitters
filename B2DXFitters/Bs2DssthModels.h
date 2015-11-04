#ifndef Bs2DssthModels_H
#define Bs2DssthModels_H 1


#include "RooRealVar.h"
#include "RooAbsPdf.h"
#include "RooResolutionModel.h"
#include "RooWorkspace.h"
#include "RooAddPdf.h"
#include "RooHistPdf.h"
#include "RooProdPdf.h"
#include "RooArgList.h"

namespace Bs2DssthModels {
  

  //===============================================================================
  // Background 3D model for Bs->DsstPi mass fitter.
  //===============================================================================

  RooAbsPdf* build_Bs2DsstPi_BKG(	RooAbsReal& mass, RooAbsReal& massDs,
					RooWorkspace* work, RooWorkspace* workInt,
					TString &samplemode, TString merge, 
					Int_t dim, bool debug = false);
  
  //===============================================================================                                                                                                       
  // Background 3D model for Bs->DsstK mass fitter.                                                                                                                                    
  //===============================================================================                                                                                                       

  RooAbsPdf* build_Bs2DsstK_BKG( RooAbsReal& mass,
				 RooAbsReal& massDs,
				 RooWorkspace* work,
				 RooWorkspace* workInt,
				 TString &samplemode,
				 TString merge,
				 Int_t dim,
                                  bool debug = false);


}

#endif
