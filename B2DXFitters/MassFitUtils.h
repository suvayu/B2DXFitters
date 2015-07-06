
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

#ifndef B2DXFITTERS_MASSFITUTILS_H 
#define B2DXFITTERS_MASSFITUTILS_H 1

// STL includes
#include <iostream>
#include <string>
#include <vector>

// ROOT and RooFit includes
#include "TFile.h"
#include "TString.h"
#include "TString.h"
#include "TH1F.h"
#include "TH2F.h"
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

namespace MassFitUtils {

  void InitializeRealObs(TString tB,
			 std::vector <Double_t> &varD, std::vector <Int_t> &varI, std::vector <Float_t> &varF
			 , Bool_t debug); 
  Double_t GetValue( TString tB, Double_t &varD, Int_t &varI, Float_t &varF ); 
  Double_t SetValRealObs(MDFitterSettings* mdSet, RooArgSet* obsVar,
			 TString tN, TString tB,
			 Double_t &varD, Int_t &varI, Float_t &varF,
			 TString mode, Double_t shift=0.0);
  
  Double_t SetValCatObs(MDFitterSettings* mdSet, RooArgSet* obsVar,
			TString tN, TString tB,
			Double_t &varD, Int_t &varI, Float_t &varF);
  
  void SetBranchAddress(TTree* tr, TString tB, TString tN,
                        Double_t &varD, Int_t &varI, Float_t &varF,
			Bool_t debug = false);

  //===========================================================================
  // Obtain data set
  // filesDir - name of config .txt file from where data are loaded
  // sig - signature which data should be loaded
  // PIDcut - cut for bachelor particle (depends of mode)
  // BDTGCut - cut on BDTGResponse_1
  // Pcut_down, Pcut_up - range (Pcut_down, Pcut_up) for bachelor momentum
  // Dmass_down, Dmass_up - range (Dmass_down, Dmass_up) for D(s)
  // mVar - name of mass observable (for example lab0_MM)
  // tVar - name of time observable
  // tagVar - name of tag observable
  // tagOmegaVar - name of mistag observable
  // idVar - name of idobservable
  // mProbVar - variable using in PID cut (for example lab1_PIDK)
  // mode - mode of decay
  // tagtool - add to workspace RooHistPdf with mistag distribution
  // workspace - workspace where data set should be saved
  //==========================================================================
  RooWorkspace* ObtainData(TString& fileDir, TString& sig,
			   MDFitterSettings* mdSet,
			   TString& mode,
			   PlotSettings* plotSet = NULL,
			   RooWorkspace* workspace = NULL,
			   bool        debug = false);

    //===========================================================================
  // Obtain Bs->DsPi under Bs->DsK
  // filesDir - name of config .txt file from where data are loaded
  // sig - signature which data should be loaded
  // PIDcut - cut for bachelor particle (depends of mode)
  // BDTGCut - cut on BDTGResponse_1
  // Pcut_down, Pcut_up - range (Pcut_down, Pcut_up) for bachelor momentum
  // Dmass_down, Dmass_up - range (Dmass_down, Dmass_up) for D(s)
  // mVar -  observable (for example lab0_MM)
  // mProbVar - variable using in PID cut (for example lab1_PIDK)
  // mode - mode of decay
  // workspace - workspace where data set should be saved
  // mistag - bool variable, if set "yes" then create RooKeysPdf for TagOmega
  //==========================================================================
  RooWorkspace* ObtainMissForBsDsK(TString& filesDir, TString& sig,
				   MDFitterSettings* mdSet,
				   TString& mode,
				   RooWorkspace* workspace = NULL, 
				   PlotSettings* plotSet = NULL,
				   bool  pdf = true,
				   bool        debug = false);

  //===========================================================================
  // Obtain Bd->DPi under Bs->DsPi
  // filesDir - name of config .txt file from where data are loaded
  // sig - signature which data should be loaded
  // PIDcut - cut for bachelor particle (depends of mode)
  // BDTGCut - cut on BDTGResponse_1
  // Pcut_down, Pcut_up - range (Pcut_down, Pcut_up) for bachelor momentum
  // Dmass_down, Dmass_up - range (Dmass_down, Dmass_up) for D(s)
  // mVar -  observable (for example lab0_MM)
  // mProbVar - variable using in PID cut (for example lab1_PIDK)
  // mode - mode of decay
  // workspace - workspace where data set should be saved
  // mistag - bool variable, ifset "yes" then create RooKeysPdf for TagOmega
  //==========================================================================
  RooWorkspace* ObtainMissForBsDsPi(TString& filesDir, TString& sig,
				    TString& namehypo, 
				    MDFitterSettings* mdSet,
				    TString& mode,
				    RooWorkspace* workspace = NULL, 
				    PlotSettings* plotSet = NULL,
				    bool pdf = true, 
				    bool        debug = false);

  //===========================================================================                                                                                                            
  // Get background category cut for background MC                                                                                                                                         
  //===========================================================================                                                                                                            
  TCut GetBKGCATCutBkg( MDFitterSettings* mdSet, TString mode, TString hypo, bool debug  = false);

  //===========================================================================                                                                                                            
  // Get MCID cut for background MC                                                                                                                                         
  //===========================================================================                                                                                                            
  TCut GetMCIDCutBkg( MDFitterSettings* mdSet, TString hypo, bool debug  = false);

  //===========================================================================
  // Get cut for background MC 
  //===========================================================================

  TCut GetCutMCBkg( MDFitterSettings* mdSet, TString mode, TString hypo, TString modeD, bool debug = false );

  //===========================================================================
  // Get name of PID hist for bachelor  - background MC
  //===========================================================================
  TString GetHistNameBachPIDBkgMC(MDFitterSettings* mdSet, TString hypo, bool debug = false );

  //===========================================================================
  // Get name of PID hist for Ds child -  background MC
  //===========================================================================
  TString GetHistNameChildPIDBkgMC(MDFitterSettings* mdSet, TString hypo, bool debug = false );

  //===========================================================================
  // Get name of PID hist for proton veto - background MC
  //===========================================================================
  TString GetHistNameProtonPIDBkgMC(MDFitterSettings* mdSet, TString hypo, bool debug = false);

  //===========================================================================
  // Get name of PID hist for bachelor eff -  background MC
  //===========================================================================
  TString GetHistNameBachPIDEffBkgMC(MDFitterSettings* mdSet, TString hypo, bool debug = false);

  //===========================================================================                                                                               
  // Get correlation factor between observables                                                                                                    
  //===========================================================================                                    
  Double_t CheckCorr(RooDataSet* data, RooRealVar* obs1, RooRealVar* obs2, TString corrName,
		     PlotSettings* plotSet = NULL, bool debug = false );
  
  TH2F* GetCorrHist(RooDataSet* data, RooDataSet* dataPID, RooArgSet* obs, std::vector <TString> &obsName,
                    TString corrName, PlotSettings* plotSet, bool debug );
  //===========================================================================
  // Obtain dataSets for all partially reconstructed backgrounds
  // filesDir - name of config .txt file from where data are loaded
  // sig - signature which data should be loaded
  // sigtree - signature for tree name
  // PIDcut - cut for bachelor particle (depends of mode)
  // BDTGCut - cut on BDTGResponse_1
  // Pcut_down, Pcut_up - range (Pcut_down, Pcut_up) for bachelor momentum
  // Dmass_down, Dmass_up - range (Dmass_down, Dmass_up) for D(s)
  // mVar -  observable (for example lab0_MM)
  // mProbVar - variable using in PID cut (for example lab1_PIDK)
  // mode - mode of decay
  // workspace - workspace where data set should be saved
  //==========================================================================
  RooWorkspace* ObtainSpecBack(TString& filesDir, TString& sig,
			       MDFitterSettings* mdSet,
			       TString& hypo,
			       RooWorkspace* workspace = NULL,
			       Bool_t corr = false, 
			       double globalWeight = 1.0,
			       PlotSettings* plotSet = NULL,
			       bool        debug = false);


  /** 
   * Get a workspace with correction factors from MC.
   *
   * Calculates and returns correction factors for the B lifetime of
   * partially reconstructed background events using LHCb Monte Carlo.
   *
   *   k factor = m(true)*p(reco) / m(reco)*p(true)
   *
   * @param filesDir Directory with text file with list of samples
   * @param sig Token to read file names
   * @param sigtree Token to read tree names
   * @param mdSet MD fitter settings
   * @param hypo Mass hypothesis
   * @param workspace Workspace to save templates
   * @param ffile Dump file
   * @param mass_win Apply mass window (default: true)
   * @param debug Debug mode (default: falsex)
   *
   * @return Return filled workspace
   */
  RooWorkspace* getSpecBkg4kfactor(TString& filesDir, TString& sig, TString& sigtree,
				   MDFitterSettings* mdSet,
				   TString& hypo,
				   RooWorkspace* workspace,
				   double globalWeight,
				   TFile &ffile, bool debug=true);


  //===========================================================================                                                                                                            
  // Get background category cut for signal MC                                                                                                                                         
  //===========================================================================                                                                                                            
  TCut GetBKGCATCutSig( MDFitterSettings* mdSet, bool debug = false);

  //===========================================================================                                                                                                            
  // Get MCID cut for signal MC                                                                                                                                                        
  //===========================================================================                                                                                                            
  TCut GetMCIDCutSig( MDFitterSettings* mdSet, TString hypo, TString modeD, bool debug  = false);
  
  //===========================================================================                                                                                                            
  // Get MC TRUEID cut for signal MC                                                                                                                                                       
  //===========================================================================                                                                                                            
  TCut GetMCTRUEIDCutSig( MDFitterSettings* mdSet, TString hypo, TString modeD, bool debug = false);

  //===========================================================================                                                                                                            
  // Get Ds Hypo cut for signal MC                                                                                                                                                       
  //===========================================================================                                                                                                            
  TCut GetDsHypoCutSig( MDFitterSettings* mdSet, TString modeD, bool debug = false);


  //===========================================================================
  // Get cut for signal MC
  //===========================================================================
  TCut GetCutMCSig( MDFitterSettings* mdSet, TString modeB, TString modeD, bool debug = false );


  //===========================================================================
  // Obtain Signal sample
  // filesDir - name of config .txt file from where data are loaded
  // sig - signature which data should be loaded
  // sigtree - signature for tree name
  // PIDcut - cut for bachelor particle (depends of mode)
  // BDTGCut - cut on BDTGResponse_1
  // Pcut_down, Pcut_up - range (Pcut_down, Pcut_up) for bachelor momentum
  // Dmass_down, Dmass_up - range (Dmass_down, Dmass_up) for D(s)
  // mVar -  observable (for example lab0_MM)
  // mProbVar - variable using in PID cut (for example lab1_PIDK)
  // mode - mode of decay
  // workspace - workspace where data set should be saved
  //==========================================================================
  RooWorkspace* ObtainSignal(   TString& filesDir, TString& sig, 
				MDFitterSettings *mdSet,
				TString& mode,
				Bool_t reweight,
				Bool_t veto,
				RooWorkspace* work = NULL,
				Bool_t mistag = false,
				double globalWeightMD = 1.0,
				double globalWeightMU = 1.0,
				PlotSettings* plotSet = NULL,
				bool debug = false);

  //===========================================================================
  // Create final RooKeysPdf for Part Reco background
  // filesDirMU - name of config .txt file from where Monte Carlo MU are loaded
  // filesDirMU - name of config .txt file from where Monte Carlo MD are loaded
  // sigMu - signature Monte Carlo MU which should be loaded
  // sigMu - signature Monte Carlo MD which should be loaded
  // mVar -  observable (for example lab0_MM)
  // workspace - workspace where Part Reco background are saved
  // mistag - bool variable, ifset "yes" then create RooKeysPdf for TagOmega
  //==========================================================================
  RooWorkspace* CreatePdfSpecBackground(TString& filesDirMU, TString& sigMU,
					TString& filesDirMD, TString& sigMD,
					TString mVar,
					TString mDVar,
					TString tagVar,
					TString tagOmegaVar,
					RooWorkspace* workspace = NULL, 
					Bool_t mistag = false,
					PlotSettings* plotSet = NULL,
					bool debug = false); 
					
  RooWorkspace* CreatePdfSpecBackground(TString filesDirMU, TString sigMU,
                                        TString filesDirMD, TString sigMD,
					MDFitterSettings* mdSet,
                                        RooWorkspace* work=NULL,
					Bool_t mistag=false,
					PlotSettings* plotSet=NULL,
                                        bool debug=false);

  RooWorkspace* CreatePdfSpecBackground(MDFitterSettings* mdSet,
                                        TString& filesDir, TString& sig,
                                        TString obsName,
                                        TString mode,
                                        Double_t rho = 1.5,
                                        TString mirror = "Both",
                                        RooWorkspace* work = NULL,
                                        PlotSettings* plotSet = NULL,
                                        bool debug = false
                                        );

  //===========================================================================
  // Calculate expected number of yields and misID
  // filesDirMU - name of config .txt file from where data are loaded
  // sigBs  - signature Monte Carlo which should be loaded (Bs hypo)
  // sigBd - signature Monte Carlo which should be loaded (Bd hypo)
  // PIDcut - PID cut
  // PIDmisscut - PID miss cut
  // sigPID - signature PID histogram which should be loaded
  // BDTGCut - cut on BDTGResponse_1
  // Pcut_down, Pcut_up - range (Pcut_down, Pcut_up) for bachelor momentum
  // Dmass_down, Dmass_up - range (Dmass_down, Dmass_up) for D(s)
  // mVar -  observable (for example lab0_MM)
  // mProbVar - variable using in PID cut (for example lab1_PIDK)
  // mode - mode of decay
  //==========================================================================
  void ExpectedYield(TString& filesDir, TString& sigBs, TString& sigBd, 
		     TString& sigPID_lab4, TString& PIDcut_lab4,
		     TString& sigPID_lab51, TString& PIDcut_lab51,
		     TString& sigPID_lab52, TString& PIDcut_lab52,
		     double Pcut_down, double Pcut_up,
		     double BDTG_down, double BDTG_up,
		     double Dmass_down, double Dmass_up,
		     TString &mVar, TString& mProbVar,
		     TString& mode,TString &mode2
		     );

  //==========================================================================
  //Function calculate efficieny of selection
  // Note:Function is not used in TD CP Bs->DsK analysis
  //==========================================================================

  RooWorkspace* ObtainBDPi(TString& filesDir, TString& sigBs,
			   int PIDcut,
			   double Pcut_down, double Pcut_up,
			   double BDTG_down, double BDTG_up,
			   double Bmass_down, double Bmass_up,
			   double Dmass_down, double Dmass_up,
			   TString &mVar, TString& mProbVar,
			   TString& mode, Bool_t MC, TString& hypo
			   );


  RooWorkspace* ObtainLbLcPi( TString& filesDir, TString& sig,
                              int PIDcut,
			      double Pcut_down, double Pcut_up,
			      double PT_down, double PT_up,
			      double nTr_down, double nTr_up,
			      TString &mVar,
                              TString& mDVar,
                              TString& mode,
                              RooWorkspace* workspace,
                              bool debug
                              );


} // end of namespace

//=============================================================================

#endif  // B2DXFITTERS_MASSFITUTILS_H
