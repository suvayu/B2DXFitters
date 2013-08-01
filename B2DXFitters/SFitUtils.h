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
				     TString& terrVar,
				     TString& tagName,
				     TString& tagOmegaVar,
				     TString& idVar,
				     bool weighted,
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
			      TString& mDVar,
			      TString& PIDKVar,
                              TString& tVar,
			      TString& terrVar,
                              TString& tagVar,
                              TString& tagOmegaVar,
                              TString& idVar,
                              TString& trueIDVar,
                              TString& dataName,
			      bool        debug = false);


  RooWorkspace* ReadLbLcPiFromSWeights(TString& pathFile,
				       TString& treeName,
				       double P_down, double P_up,
				       double PT_down, double PT_up,
				       double nTr_down, double nTr_up,
				       double PID_down, double PID_up,
				       TString& mVar,
				       TString& mDVar,
				       TString& pVar,
				       TString& ptVar,
				       TString& nTrVar,
				       TString& pidVar,
				       RooWorkspace* workspace, 
				       bool        debug = false
				       );
  
  
} // end of namespace

//=============================================================================

#endif  // B2DXFITTERS_SFITUTILS_H
