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

namespace WeightingUtils {

  TString CheckWeightLabel(TString& check, bool debug);
  TString CheckTreeLabel(TString& fileCalib, bool debug);
  TString CheckTreeLabel(TString& fileCalib, TString& check, bool debug);

  TH2F*  Get2DHist(RooDataSet* data,
                   RooRealVar* Var1, RooRealVar* Var2,
                   Int_t bin1, Int_t bin2,
                   TString& histName1, bool debug);

  TH3F*  Get3DHist(RooDataSet* data,
                   RooRealVar* Var1, RooRealVar* Var2, RooRealVar* Var3,
		   //                   Int_t bin1, Int_t bin2, Int_t bin3,
                   //TString& histName1, 
		   TH3F* hist, bool debug);
  
  void PlotWeightingSample(TString& nm, RooDataSet* dataCalib, RooDataSet* dataCalibRW,
			   RooRealVar* Var1, RooRealVar* Var2, RooRealVar* PID,
			   Int_t bin1, Int_t bin2, Int_t bin3,
			   TString& label1, TString& label2, TString& label3, 
			   TString& dir, TString& ext,
			   RooWorkspace* work, bool debug );

  void PlotWeightingSample(TString& nm, RooDataSet* dataCalib, RooDataSet* dataCalibRW,
                           RooRealVar* Var1, RooRealVar* Var2, RooRealVar* Var3, RooRealVar* PID,
                           Int_t bin1, Int_t bin2, Int_t bin3, Int_t binPIDK,
                           TString& label1, TString& label2, TString& label3, 
			   TString& dir, TString& ext,
                           RooWorkspace* work, bool debug );

  RooDataSet* GetDataCalibSample(TString& fileName, TString& workName,
				 RooRealVar* Var1, RooRealVar* Var2,
				 bool debug );

  RooDataSet* GetDataCalibSample(TString& fileName, TString& workName,
                                 RooRealVar* Var1, RooRealVar* Var2, RooRealVar* Var3,
                                 bool debug );



  RooAbsPdf* FitPDFShapeForPIDBsDsPiPi(RooDataSet* data, RooRealVar* Var, TString& name, bool debug);
  RooAbsPdf* FitPDFShapeForPIDBsDsPiK(RooDataSet* data, RooRealVar* Var, TString& name, bool debug);
  RooAbsPdf* FitPDFShapeForPIDBsDsKPi(RooDataSet* data, RooRealVar* Var, TString& name, bool debug);
  RooAbsPdf* FitPDFShapeForPIDBsDsKK(RooDataSet* data, RooRealVar* Var, TString& name, bool debug);
  RooAbsPdf* FitPDFShapeForPIDBsDsKP(RooDataSet* data, RooRealVar* Var, TString& name, bool debug);

  //===========================================================================
  // 
  //===========================================================================
  RooWorkspace* ObtainHistRatio(TString& filesDir, TString& sig,
				TString& fileCalibUp, TString& workCalibUp,
				//				TString& fileCalibDown, TString& workCalibDown,
				Int_t bin1, Int_t bin2,
				TString& nameVar1, TString& nameVar2,
				double Var1_down, double Var1_up,
				double Var2_down, double Var2_up,
				TString& type,
				RooWorkspace* work,
				bool debug
				);
  RooWorkspace* ObtainHistRatio(TString& filesDir, TString& sig,
                                TString& fileCalibUp, TString& workCalibUp,
				Int_t bin1, Int_t bin2, Int_t bin3,
                                TString& nameVar1, TString& nameVar2, TString& nameVar3,
                                double Var1_down, double Var1_up,
                                double Var2_down, double Var2_up,
				double Var3_down, double Var3_up,
                                TString& type,
                                RooWorkspace* work,
                                bool debug
                                );


   
  RooWorkspace* ObtainPIDShapeFromCalibSample(TString& filesDir, TString& sig,
                                              TString& fileCalibUp, TString& workCalibUp,
					      //      TString& fileCalibDown, TString& workCalibDown,
                                              TString& PIDVar1, TString& nameVar1, TString nameVar2,
                                              double PID_down, double PID_up,
                                              double Var1_down, double Var1_up,
                                              double Var2_down, double Var2_up,
					      Int_t bin1, Int_t bin2,
                                              TString& type,
					      RooWorkspace* work,
                                              bool debug);

  RooWorkspace* ObtainPIDShapeFromCalibSample(TString& filesDir, TString& sig,
                                              TString& fileCalibUp, TString& workCalibUp,
					      TString& PIDVar1, TString& nameVar1, TString& nameVar2, TString& nameVar3,
                                              double PID_down, double PID_up,
                                              double Var1_down, double Var1_up,
                                              double Var2_down, double Var2_up,
					      double Var3_down, double Var3_up,
                                              Int_t bin1, Int_t bin2, Int_t bin3,
                                              TString& type,
					      RooWorkspace* work,
					      bool debug);


  RooWorkspace* ObtainHistRatioOneSample(TString& fileCalib, TString& workCalib,
                                         Int_t bin1, Int_t bin2,
                                         TString& nameVar1, TString& nameVar2,
                                         double Var1_down, double Var1_up,
                                         double Var2_down, double Var2_up,
                                         TString& type,
                                         RooWorkspace* work,
                                         RooWorkspace* workL,
                                         bool debug
					 );

  RooWorkspace* ObtainHistRatioOneSample(TString& fileCalib, TString& workCalib,
                                         Int_t bin1, Int_t bin2, Int_t bin3,
                                         TString& nameVar1, TString& nameVar2, TString&nameVar3,
                                         double Var1_down, double Var1_up,
                                         double Var2_down, double Var2_up,
                                         double Var3_down, double Var3_up,
                                         TString& type,
                                         RooWorkspace* work,
                                         RooWorkspace* workL,
                                         bool debug
                                         );


  RooWorkspace* ObtainPIDShapeFromCalibSampleOneSample(TString& fileCalib, TString& workCalib,
                                                       TString& namePID, TString& nameVar1, TString& nameVar2,
                                                       double PID_down, double PID_up,
                                                       double Var1_down, double Var1_up,
                                                       double Var2_down, double Var2_up,
                                                       Int_t bin1, Int_t bin2,
                                                       TString& type,
                                                       RooWorkspace* work,
                                                       bool debug);

  RooWorkspace* ObtainPIDShapeFromCalibSampleOneSample(TString& fileCalib, TString& workCalib,
                                                       TString& namePID, TString& nameVar1, TString& nameVar2, TString& nameVar3,
                                                       double PID_down, double PID_up,
                                                       double Var1_down, double Var1_up,
                                                       double Var2_down, double Var2_up,
						       double Var3_down, double Var3_up,
                                                       Int_t bin1, Int_t bin2, Int_t bin3,
                                                       TString& type,
                                                       RooWorkspace* work,
                                                       bool debug);




} // end of namespace

//=============================================================================

#endif  // B2DXFITTERS_SFITUTILS_H
