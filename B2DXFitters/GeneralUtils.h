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

#ifndef B2DXFITTERS_GENERALUTILS_H 
#define B2DXFITTERS_GENERALUTILS_H 1

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
#include "RooCategory.h"
#include "RooAbsRealLValue.h"

namespace GeneralUtils {

  //===========================================================================
  // Save the data and corresponding template PDF, if given, on a file
  // Note: data/PDF need to depend on the observable, obviously ;-)!
  // "extension" is the file extension. Typically: root, png, pdf, eps
  // "mode" uniquely identifies the decay mode, e.g. "Bs2DsPi"
  // "suffix" can be used e.g. to separed magnet up from down plots
  //===========================================================================
  void saveDataTemplateToFile( RooAbsData* data,
                               RooAbsPdf*  pdf,
                               RooRealVar* observable,
                               const char* mode,
                               const char* extension = "pdf",
                               const char* suffix = NULL,
                               bool        debug = false
                               );
  //===========================================================================
  // Read PID histogram,
  // FilePID - collect path and file names to the mu and md root files
  // nameHist - is the name of histogram which should be read
  // sample - determines from which root file histogram should be read
  //===========================================================================
  TH1F* ReadPIDHist( std::vector<std::string> &FilePID,
                     TString &nameHist,
                     int sample,
		     bool        debug = false
                     );
  TH2F* Read2DHist( std::vector<std::string> &FilePID,
		    TString &nameHist,
		    int sample,
		    bool        debug = false
		    );

  TH3F* Read3DHist( std::vector<std::string> &FilePID,
                    TString &nameHist,
                    int sample,
                    bool        debug = false
                    );

  void Save2DHist(TH2F* hist, TString& ext);
  void Save3DHist(TH3F* hist, TString& ext);

  void Save2DComparison(TH2F* hist1, TString& l1,
                        TH2F* hist2, TString& l2,
                        TH2F* hist3, TString& l3,
                        TString& ext);


  //===========================================================================
  // Add PID histogram with weights,
  // hist1 - first histogram;
  // w1 - weight 1
  // hist2 - first histogram;
  // w2 - weight 1
  //===========================================================================
  TH1F* AddHist(TH1F* hist1, Double_t w1, TH1F* hist2, Double_t w2, bool        debug = false );

  //===========================================================================
  // Read one name from config.txt file
  // filesDir - path to the file
  // FileName - output
  // sig - signature which should be read from file, for example sig="#DsPi"
  // to FileName will be read everything what is between sig and "###"
  //===========================================================================
  void ReadOneName(TString& filesDir,
		   std::vector <std::string> &FileName, 
		   TString &sig, bool        debug = false);

  //===========================================================================
  // Read tree from TFile. The convention which should be in the .txt file:
  // line 1: path to directory for example: /afs/cern.ch/work/g/gligorov/public/Bs2DsKFitTuples/
  // line 2: name of the first file, for example: FitTuple_MergedTree_Bd2DPi_D2KPiPi_MD_BDTG_MINI.root
  // line 3: name of the second file, for example: FitTuple_MergedTree_Bd2DPi_D2KPiPi_MU_BDTG_MINI.root
  // line 4: name of tree for the first file, for example: DecayTree
  // line 5: name of tree for the second file, for example: DecayTree
  //===========================================================================
  TTree* ReadTreeData(std::vector <std::string> &FileName,int  sample, bool debug = false);

  //===========================================================================
  // Read tree from TFile.
  // fileName - path to the TFile
  // treeName - name of the TTree
  //===========================================================================
  TTree* ReadTreeMC(const char* fileName, const char* treeName, bool        debug = false);

  //===========================================================================
  // Read one name (mode) for MC2011-March
  // if the path to the MC file: /afs/cern.ch/project/lbcern/vol0/adudziak/MCAddBDTG/Merged_Bd2DstPi_Dst2D-Pi0_MD_BsHypo_BDTG.root then
  // 1. find last / and cut only file name
  // 2. cut between first "_" and second "_", here: Bd2DstPi
  //===========================================================================
  TString ReadOneMode( TString path, bool        debug = false );

  //===========================================================================
  // Read all modes for MC2011-March
  // MCFileName - collects all paths to the MC files
  // mode - output
  // Please not that we dont have MC Bd2DsstPi and Bs2DsstKst and they are
  // loaded from Bs2DsstPi and Bd2DKst, respectively. But the mode is change
  // only if Bs2DsstPi ( or Bd2DKst ) are used twice in MCFileName
  //==========================================================================
  void ReadMode(std::vector <std::string> &MCFileName, 
		std::vector <std::string> &mode, bool iskfactor=false, bool        debug = false);

 
  //===========================================================================
  // Obtain new tree from the old tree using TCut cut
  // Sample and mode are used to create name
  //==========================================================================
  TTree* TreeCut(TTree* tree, 
		 TCut &cut, 
		 TString &sample, 
		 TString &mode,
		 bool        debug = false);

  //===========================================================================
  // Save template to the pdf file
  //==========================================================================
  void SaveTemplate(RooDataSet* dataSet, 
		    RooKeysPdf* pdf,
		    RooRealVar* mass,
		    TString &sample,
		    TString &mode,
		    bool        debug = false);

  //===========================================================================
  // Save histogram template to the pdf file
  //==========================================================================
  void SaveTemplateHist(RooDataHist* dataSet,
			RooHistPdf* pdf,
			RooRealVar* mass,
			TString &sample,
			TString &mode,
			bool        debug = false);


  //===========================================================================
  // Save projection of data set  to the pdf file
  // Sample and mode are used to create name
  //==========================================================================
  void SaveDataSet(RooDataSet* dataSet, 
		   RooRealVar* mass,
		   TString &sample,
		   TString &mode,
		   bool        debug = false);

  //===========================================================================
  // Create RooKeysPdf for dataSetMC with observable massMC.
  // Sample and mode are used to create the name of RooKeysPdf.
  //==========================================================================
  RooKeysPdf* CreatePDFMC(RooDataSet* dataSetMC,
			  RooRealVar* massMC, 
			  TString &sample,
			  TString &mode,
			  Bool_t mistag,
			  bool        debug = false);
  
  RooHistPdf* CreateHistPDF(RooDataSet* dataSet,
                            RooRealVar* obs,
                            TString &name,
                            Int_t bin,
                            bool debug = false);

  RooAbsPdf* CreateBinnedPDF(RooDataSet* dataSet,
                             RooRealVar* obs,
                             TString &name,
                             Int_t bin,
                             bool debug = false);

  //===========================================================================
  // Get observable ( obs ) from workspace (work)
  //==========================================================================
  RooRealVar* GetObservable(RooWorkspace* work, TString &obs, bool        debug = false);

  //===========================================================================
  // Get observable ( obs ) from workspace (work)
  //==========================================================================
  RooArgSet* GetRooArgSet(RooWorkspace* work, TString &obs, bool        debug = false);

  //===========================================================================
  // Get category observable ( obs ) from workspace (work)
  //==========================================================================
  RooCategory* GetCategory(RooWorkspace* work, TString &obs, bool        debug = false);


  //===========================================================================
  // Get data set ( dat ) from workspace (work)
  //==========================================================================
  RooDataSet* GetDataSet(RooWorkspace* work, TString &obs, bool        debug = false);

  //===========================================================================
  // Get data histogram ( dat ) from workspace (work)
  //==========================================================================
  RooDataHist* GetDataHist(RooWorkspace* work, TString &obs, bool        debug = false);

  //===========================================================================
  // Save workspace in the ROOT file
  //==========================================================================
  void SaveWorkspace(RooWorkspace* work, TString &name, bool        debug = false);

  //===========================================================================
  // Load workspace from the ROOT file
  //==========================================================================
  RooWorkspace* LoadWorkspace(TString &fileName, TString& workName, bool        debug = false);

  //===========================================================================
  // Check polarity (down,up) from check 
  //==========================================================================
  TString CheckPolarity(std::string& check, bool debug);
  TString CheckPolarity(TString& check, bool debug);

  //===========================================================================
  // Check D/Ds final state (kkpi,kpipi,pipipi) from check
  //==========================================================================
  TString CheckDMode(std::string& check, bool debug);
  TString CheckDMode(TString& check, bool debug);

  TString CheckKKPiMode(std::string& check, bool debug);
  TString CheckKKPiMode(TString& check, bool debug);

  TString GetLabel(TString& mode, bool debug);
  TString CheckBDTGBin(TString& check, bool debug);
} // end of namespace

//=============================================================================

#endif  // B2DXFITTERS_GENERALUTILS_H
