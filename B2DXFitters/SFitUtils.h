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
#include "PlotSettings.h"
#include "MDFitterSettings.h"

namespace SFitUtils {

 
  //===========================================================================
  // Read observables tVar, tagVar, tagOmegaVar, idVar from sWeights file
  // Name of file is read from filesDirand signature sig
  // time_{up,down} - range for tVar
  // part means mode (DsPi, DsK and so on)
  //===========================================================================

  RooWorkspace* ReadDataFromSWeights(TString& pathFile,
                                     TString& treeName,
                                     MDFitterSettings* mdSet,
                                     TString pol,
                                     TString mode,
                                     TString year,
                                     TString hypo,
                                     TString merge,
                                     bool weighted = true,
                                     bool toys = false,
                                     bool applykfactor = false,
                                     bool sWeightsCorr = false,
                                     bool singletagger = false,
                                     bool        debug = false
                                     );
  
  //===========================================================================
  // Create Mistag templates
  //===========================================================================
  RooArgList* CreateMistagTemplates(RooDataSet* data, MDFitterSettings* mdSet, 
				    Int_t bins,
				    bool save = false, bool debug=false);
  

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
				       RooWorkspace* workspace = NULL,
				       PlotSettings* plotSet = NULL,
				       bool        debug = false
				       );
  
  
} // end of namespace

//=============================================================================

#endif  // B2DXFITTERS_SFITUTILS_H
