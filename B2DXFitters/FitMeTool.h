//---------------------------------------------------------------------------//
//                                                                           //
//                                                                           //
//  Mass and propertime fitter base class based on RooFit                    //
//                                                                           //
//  Header file                                                              //
//                                                                           //
//  Conventions:                                                             //
//  - m_config_xxx  : fitter configuration variables                         //
//  - m_observables : fitter observables                                     //
//  - m_modelPDF    : model PDF                                              //
//  - m_fitResult   : RooFitResult fit result object                         //
//  - m_outputFile  : output file where fit results get saved                //
//  - m_workSpace   : fitter RooWorkspace                                    //
//                                                                           //
//  Authors: Eduardo Rodrigues                                               //
//  Date   : 12 / 10 / 2010                                                  //
//                                                                           //
//---------------------------------------------------------------------------//

#ifndef FITMETOOL_H
#define FITMETOOL_H 1

// STL includes
#include <iostream>
#include <sstream>
#include <string>
#include <algorithm>
#include <vector>

// ROOT and RooFit includes
#include "TFile.h"
#include "TRandom3.h"
#include "RooRandom.h"
#include "RooCmdArg.h"
#include "RooArgSet.h"
#include "RooRealVar.h"
#include "RooFormulaVar.h"
#include "RooCategory.h"
#include "RooAbsPdf.h"
#include "RooAbsData.h"
#include "RooMinuit.h"
#include "RooFitResult.h"
#include "RooWorkspace.h"
#include "RooUnblindOffset.h"
#include "RooSimultaneous.h"

//=============================================================================
// FitMeTool class declaration
//=============================================================================
class FitMeTool {
  
public :
  // Class constructors
  FitMeTool( bool debug = false );
  FitMeTool( int toyNumber, bool debug = false );
  
  // Class destructor
  virtual ~FitMeTool();
  
  // Generate a toy MC sample
  virtual void generate( long int nevents = 0,
            const RooCmdArg& arg1 = RooCmdArg::none(),
            const RooCmdArg& arg2 = RooCmdArg::none(),
            const RooCmdArg& arg3 = RooCmdArg::none(),
            const RooCmdArg& arg4 = RooCmdArg::none() );
  
public:
  // Fit and optionally save the result to a file
  void fit( bool save2file = true,
            const RooCmdArg& arg1 = RooCmdArg::none(),
            const RooCmdArg& arg2 = RooCmdArg::none(),
            const RooCmdArg& arg3 = RooCmdArg::none(),
            const RooCmdArg& arg4 = RooCmdArg::none(),
            const RooCmdArg& arg5 = RooCmdArg::none(),
            const RooCmdArg& arg6 = RooCmdArg::none(),
            const RooCmdArg& arg7 = RooCmdArg::none()
            );
  
  // Get the fit result (RooFitResult object)
  RooFitResult* getFitResult();
  
  // Set the random seed for toy MC event generation
  void setSeed( int seed );
  // Get the random seed last generated/set and stored
  int  getSeed();
  
  //Set debugging mode on/off
  void setDebug( bool yesNo );
  
  // Set the fit observables
  void       setObservables( RooArgSet* observables = NULL );
  void       setConditionalObservables(RooArgSet* condObs = 0);
  void       setExternalConstraints(RooArgSet* extConstraints = 0);

  // Get the fit observables
  const RooArgSet* getObservables() const;
  // get the conditional observables
  const RooArgSet* getConditionalObservables() const;
  // get external constraints
  const RooArgSet* getExternalConstraints() const;
  
  // Set the model PDF and the data
  void      setModelPDFandData( RooWorkspace* ws                        ,
                                const char* modelName = "UNSPECIFIED" ,
                                const char* dataName  = "UNSPECIFIED"
                                );
  // Set the model PDF
  void       setModelPDF( RooAbsPdf* modelPDF = NULL );
  //void       setModelPDF( RooSimultaneous* modelPDF = NULL );
  void       setModelPDF( const char* fileName,
                          const char* wsName    = "UNSPECIFIED",
                          const char* modelName = "UNSPECIFIED"
                          );
  void       setModelPDF( RooWorkspace* ws,
                          const char* modelName = "UNSPECIFIED"
                          );
  // Get the model PDF
  RooAbsPdf* getModelPDF();
  
  // Set the generated/read data
  void        setData( RooAbsData* data = NULL );
  void        setData( const char* fileName,
                       const char* wsName   = "UNSPECIFIED",
                       const char* dataName = "UNSPECIFIED"
                       );
  void        setData( RooWorkspace* ws,
                       const char* dataName = "UNSPECIFIED"
                       );
  void        setDataSet( const char* fileName,
                          const char* treeName,
                          const char* subDir = NULL,
                          const char* cuts = ""
                          );
  void        setDataSet( std::vector<std::string> filesList,
                          const char* treeName,
                          const char* subDir = NULL,
                          const char* cuts = ""
                          );
  
  // Get the generated/read data
  RooAbsData* getData();
  
  // Save the model PDF on to a ROOT file
  void       saveModelPDF( const char* workspaceFileName = "FitMeTool" );
  // Save the data on to a ROOT file
  void       saveData ( const char* workspaceFileName = "FitMeTool" );
  
  // Print the PDF model structure including variables, observables, parameters
  void printModelStructure();
  
  // Produce a graphical representation of the model PDF with the dot tool
  void produceGraphicalModelStructure( const char* fileName = "model.gif" );
  
  // Calculate yields in a defined observable range given an input wildcard
  // for matching "yield variables"
  void printYieldsInRange( const char* wildcard,
                           const char* observableName,
                           double low, double high, const char* rangeName = "SignalRegion"
                           );
  void printYieldInRange( const char* yieldVarName,
                          const char* observableName,
                          double low, double high, const char* rangeName = "SignalRegion"
                          );
  
  RooUnblindOffset* blindValue( RooRealVar& varToBeBlinded,
                                RooCategory& category,
                                const std::string prefix = "blinded"
                                );
 
  //Set sWeights
  void savesWeights(const char* observableName, RooDataSet* data, TString &mode);
 
  
protected:
  // Initialise the class data members
  void initialiseDataMembers();
  
  // Generate and store a new random seed
  void generateSeed();
  
  // Create an output file to store the fit results (RooFitResult object)
  // File name format: "fitresult_<toyNumber>.root" for toys and
  //                    "fitresult_ntuple.root" when reading data from an ntuple
  void createOutputFile();  
  
  // Get all RooExtendPdf PDFs in the fit model PDF, if any
  RooArgSet* getEPDFComponents();
  
  // Get the RooExtendPdf PDF relating to the input (yield) variable
  RooAbsPdf* getMatchingEPDFComponent( const char* yieldVarName,
                                       RooArgSet* epdfs = NULL );
  
  // Get all model PDF variables matching a wildcard
  RooArgSet* getMatchingVariableNames( const char* wildcard = "*Evts" );  
  
 

  protected:  // Data members
  // Fit observables
  RooArgSet* m_observables;
  RooArgSet* m_conditionalObservables;
  RooArgSet* m_externalConstraints;

  // Configuration data members
  bool m_config_debug;
  int  m_config_toyNumber;
  int  m_config_seed;
  bool m_config_seedSet;
  bool m_config_saveFitResult2File;
  
  // Model PDF
  RooAbsPdf* m_modelPDF;
  //RooSimultaneous* m_modelPDF;

  // Dataset variable
  RooAbsData* m_data;
  
  // Variable storing the fit results
  RooFitResult* m_fitResult;

  // Extra data members
  TFile* m_outputFile;

  // Fitter workspace
  RooWorkspace* m_workSpace;
  
protected:
  ClassDef( FitMeTool, 1 )

};

//=============================================================================

#endif  // FITMETOOL_H
