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

namespace MassFitUtils {

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
			   int PIDcut,
			   double Pcut_down, double Pcut_up,
			   double BDTGCut,
			   double Dmass_down, double Dmass_up,
			   double Bmass_down, double Bmass_up,
			   double time_down, double time_up,
			   TString& mVar, 
			   TString& tVar,
			   TString& tagVar,
			   TString& tagOmegaVar,
			   TString& idVar,
			   TString& mProbVar,
			   TString& mode,
			   Bool_t tagtool,
			   RooWorkspace* workspace,
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
				   int PIDmisscut,
				   double Pcut_down, double Pcut_up,
				   double BDTGCut,
				   double Dmass_down, double Dmass_up,
				   double Bmass_down, double Bmass_up,
				   TString& mVar, TString& mProbVar,
				   TString& mode,
				   RooWorkspace* workspace, Bool_t mistag,
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
				    int PIDmisscut,
				    double Pcut_down, double Pcut_up,
				    double BDTGCut,
				    double Dmass_down, double Dmass_up,
				    double Bmass_down, double Bmass_up,
				    TString& mVar, TString& mProbVar,
				    TString& mode,
				    RooWorkspace* workspace, Bool_t mistag,
				    bool        debug = false);

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
  RooWorkspace* ObtainSpecBack(TString& filesDir, TString& sig, TString& sigtree,
			       int PIDcut,
			       int PIDmisscut,
			       int pPIDcut,
			       double Pcut_down, double Pcut_up,
			       double BDTGCut,
			       double Dmass_down, double Dmass_up,
			       double Bmass_down, double Bmass_up,
			       TString& mVar, TString& mProbVar,
			       TString& hypo,
			       RooWorkspace* workspace, 
			       Bool_t save, Bool_t mistag,
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
   * @param PIDcut
   * @param PIDmisscut
   * @param pPIDcut
   * @param Pcut_down
   * @param Pcut_up
   * @param BDTGCut
   * @param Dmass_down
   * @param Dmass_up
   * @param mVar
   * @param hypo
   * @param workspace
   * @param ffile
   *
   * @return workspace
   */
  RooWorkspace* getSpecBkg4kfactor(TString& filesDir, TString& sig,
				   TString& sigtree, int PIDcut,
				   int PIDmisscut, int pPIDcut,
				   double Pcut_down, double Pcut_up,
				   double BDTGCut, double Dmass_down,
				   double Dmass_up, TString& mVar,
				   TString& hypo, RooWorkspace* workspace,
				   TFile &ffile, bool mass_win=true,
				   bool debug = false);


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
				int PIDcut2, 
				double Pcut_down2, double Pcut_up2,
				double BDTGCut2,
				double Dmass_down, double Dmass_up,
				double Bmass_down, double Bmass_up,
				double time_down,double time_up,
				TString& mVar,
				TString& tVar,
				TString& tagVar,
				TString& tagOmegaVar,
				TString& idVar,
				TString &mProbVar,
				TString& mode,
				RooWorkspace* work,
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
					TString &mVar,
					double Bmass_down, double Bmass_up,
					RooWorkspace* workspace, 
					Bool_t mistag,
					bool debug); 
					

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
		     TString& sigPID_lab5, TString& PIDcut_lab5,
		     double Pcut_down, double Pcut_up,
		     double BDTGCut,
		     double Dmass_down, double Dmass_up,
		     TString &mVar, TString& mProbVar,
		     TString& mode,TString &mode2
		     );

  //==========================================================================
  //Function calculate efficieny of selection
  // Note:Function is not used in TD CP Bs->DsK analysis
  //==========================================================================

  RooWorkspace* Blabla(TString& filesDir, TString& sigBs,
		       int PIDcut,
		       double Pcut_down, double Pcut_up,
		       double BDTGCut,
		       double Dmass_down, double Dmass_up,
		       TString &mVar, TString& mProbVar,
		       TString& mode, Bool_t MC, TString& hypo
		       );



} // end of namespace

//=============================================================================

#endif  // B2DXFITTERS_MASSFITUTILS_H
