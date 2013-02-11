//---------------------------------------------------------------------------//
//                                                                           //
//  General utilities                                                        //
//                                                                           //
//  Header file                                                              //
//                                                                           //
//  Authors: Agnieszka Dziurda, Eduardo Rodrigues                            //
//  Date   : 12 / 04 / 2012                                                  //
//                                                                           //
//---------------------------------------------------------------------------//

#ifndef B2DXFITTERS_SFITUTILS_H 
#define B2DXFITTERS_SFITUTILS_H 1

// STL includes
#include <iostream>
#include <string>
#include <vector>

// ROOT and RooFit includes
#include "TFile.h"
#include "TString.h"
#include "TH1F.h"
#include "TTree.h"
#include "TCut.h"
#include "RooAbsData.h"
#include "RooAbsPdf.h"
#include "RooRealVar.h"
#include "RooKeysPdf.h"
#include "RooWorkspace.h"
#include "RooDataSet.h"
#include "RooHistPdf.h"
#include "RooDataHist.h"

namespace SFitUtils {

 
  //===========================================================================
  // Read observables tVar, tagVar, tagOmegaVar, idVar from sWeights file
  // Name of file is read from filesDirand signature sig
  // time_{up,down} - range for tVar
  // part means mode (DsPi, DsKand so on)
  //===========================================================================

  RooWorkspace* ReadDataFromSWeights(TString& part, 
				     TString& pathFile,
				     TString& treeName,
				     double time_down, double time_up,
				     TString& tVar,
				     TString& tagVar,
				     TString& tagOmegaVar,
				     TString& idVar,
				     bool        debug = false
				      );

  //===========================================================================
  // Read observables tVar, tagVar, tagOmegaVar, idVar from sWeights file for toys
  // Name of file is read from pathFile, name of tree: treName
  // time_{up,down} - range for tVar
  // part means mode (DsPi, DsKand so on)
  //===========================================================================

  RooWorkspace* ReadDataFromSWeightsToys(TString& part,
                                        TString& pathFile,
                                        TString& treeName,
                                        double time_down, double time_up,
										TString& tVar,
										TString& tagName,
                                        TString& tagOmegaVar,
										TString& idVar, bool nokfactcorr,
										bool        debug = false
                                        );

  //===========================================================================
  // Copy Data for Toys, change RooCategory to RooRealVar
  //===========================================================================
  RooDataSet* CopyDataForToys(TTree* tree,
                              TString& mVar,
                              TString& tVar,
                              TString& tagVar,
                              TString& tagOmegaVar,
                              TString& idVar,
                              TString& trueIDVar,
                              TString& dataName,
			      bool        debug = false);


} // end of namespace

//=============================================================================

#endif  // B2DXFITTERS_SFITUTILS_H
