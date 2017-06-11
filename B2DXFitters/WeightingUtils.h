//---------------------------------------------------------------------------//
//                                                                           //
//  General utilities                                                        //
//                                                                           //
//  Header file                                                              //
//                                                                           //
//  Authors: Agnieszka Dziurda                                               //
//  Date   : 21 / 01 / 2013                                                  //
//                                                                           //
//---------------------------------------------------------------------------//

#ifndef B2DXFITTERS_WEIGHTINGUTILS_H 
#define B2DXFITTERS_WEIGHTINGUTILS_H 1

// STL includes
#include <iostream>
#include <string>
#include <vector>

// ROOT and RooFit includes
#include "TFile.h"
#include "TString.h"
#include "TH1.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TH3F.h"
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
#include "PIDCalibrationSample.h"

namespace WeightingUtils {

  TString CheckWeightLabel(TString& check, bool debug = false);
  TString CheckTreeLabel(TString& fileCalib, bool debug = false);
  TString CheckTreeLabel(TString& fileCalib, TString& check, bool debug = false);
  std::vector <TString> CheckWeightNames(TString type, bool debug = false);

  TH2F*  Get2DHist(RooDataSet* data,
                   RooRealVar* Var1, RooRealVar* Var2,
                   Int_t bin1, Int_t bin2,
                   TString& histName1, 
		   bool debug = false);

  TH3F*  Get3DHist(RooDataSet* data,
                   RooRealVar* Var1, RooRealVar* Var2, RooRealVar* Var3,
		   TH3F* hist, 
		   bool debug = false);
  
  void PlotWeightingSample(TString& nm, RooDataSet* dataCalib, RooDataSet* dataCalibRW,
			   RooRealVar* Var1, RooRealVar* Var2, RooRealVar* PID,
			   Int_t bin1, Int_t bin2, Int_t bin3,
			   TString& label1, TString& label2, TString& label3, 
			   RooWorkspace* work, 
			   PlotSettings* plotSet = NULL,
			   bool debug = false);

  RooAbsPdf* FitPDFShapeForPIDBsDsKPi(RooDataSet* data, RooRealVar* Var, TString& name, PlotSettings* plotSet = NULL, bool debug = false);
  RooAbsPdf* FitPDFShapeForPIDBsDsKP(RooDataSet* data, RooRealVar* Var, TString& name, PlotSettings* plotSet = NULL, bool debug = false);

  //===========================================================================
  // 
  //===========================================================================
 
  
  RooWorkspace* ObtainHistRatio(TString& filesDir, TString& sig,
                                MDFitterSettings* md,
                                TString& type,
                                RooWorkspace* work = NULL,
                                PlotSettings* plotSet = NULL,
                                bool debug = false
                                );

   
  RooWorkspace* ObtainPIDShapeFromCalibSample(TString& filesDir, TString& sig,
                                              MDFitterSettings* md,
                                              TString& type,
                                              RooWorkspace* work = NULL,
                                              PlotSettings* plotSet = NULL,
                                              bool debug = false);

  RooWorkspace* ObtainHistRatioOneSample(MDFitterSettings* md,
                                         TString& type,
                                         RooWorkspace* work,
                                         PlotSettings* plotSet = NULL,
                                         bool debug = false
					 );
  
  RooWorkspace* ObtainPIDShapeFromCalibSampleOneSample(MDFitterSettings* md,
                                                       TString& type,
                                                       RooWorkspace* work = NULL,
                                                       PlotSettings* plotSet = NULL,
						       bool debug = false);
  

  TH1* GetHist(RooDataSet* data, RooRealVar* obs, Int_t bin, bool debug);

  TH1* GetHistRatio(RooDataSet* data1,RooDataSet* data2, RooRealVar* obs, 
		    TString name, Int_t bin, bool debug = false);
  
  TH1* GetHistRatio(TH1* hist1, TH1* hist2, RooRealVar* obs, TString histName,bool debug  = false);
  
  TH1* MultiplyHist(TH1* hist1, TH1* hist2, RooRealVar* obs, TString histName,bool debug = false);


} // end of namespace

//=============================================================================

#endif  // B2DXFITTERS_SFITUTILS_H
