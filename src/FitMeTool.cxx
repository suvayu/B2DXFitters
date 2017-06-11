//---------------------------------------------------------------------------//
//                                                                           //
//  Fitter toolkit base class based on RooFit                                //
//                                                                           //
//  Source file                                                              //
//                                                                           //
//  Author: Eduardo Rodrigues                                                //
//  Date  : 12 / 11 / 2010                                                   //
//                                                                           //
//---------------------------------------------------------------------------//

// STL includes
#include <limits>
#include <utility>
#include <map>
#include <iterator>

// ROOT and RooFit includes
#include "TTree.h"
#include "TChain.h"
#include "TIterator.h"
#include "RooDataSet.h"
#include "RooExtendPdf.h"
#include "RooStats/SPlot.h"
#include "RooMsgService.h"

// B2DXFitters includes
#include "B2DXFitters/FitMeTool.h"


//=============================================================================
// Class constructor (public)
//=============================================================================
FitMeTool::FitMeTool( bool debug )
{
  if ( debug )
    printf( "==> FitMeTool::FitMeTool()\n" );
  
  setDebug( debug );
  initialiseDataMembers();
}

//=============================================================================
// Class constructor (public)
//=============================================================================
FitMeTool::FitMeTool( int toyNumber, bool debug )
{
  if ( debug )
    printf( "==> FitMeTool::FitMeTool( toy # %d, debug=%s )\n",
            toyNumber, debug ? "true" : "false" );
  
  setDebug( debug ); 
  initialiseDataMembers();
  
  m_config_toyNumber = toyNumber;
}

//=============================================================================
// Initialise the class data members (protected)
//=============================================================================
void FitMeTool::initialiseDataMembers() 
{  
  // Set and store some configuration variables
  m_config_toyNumber          = -1;
  m_config_seed               = -1;
  m_config_seedSet            = false;
  m_config_saveFitResult2File = false;
  
  // Initialise relevant variables
  m_observables = NULL;
  m_conditionalObservables = 0;
  m_externalConstraints = 0;
  
  m_modelPDF = NULL;
  
  m_data = NULL;
  
  m_fitResult  = NULL;
  m_outputFile = NULL;
  
  // Create the fitter workspace
  m_workSpace = new RooWorkspace( "FitMeToolWS" );
}

//=============================================================================
// Get the random seed last generated/set and stored (public)
//=============================================================================
int FitMeTool::getSeed() 
{  
  if ( m_config_debug )
    printf( "==> FitMeTool::getSeed()\n" );
  
  if ( ! m_config_seedSet )
	 printf( "[WARNING] random seed not set. Returning default value!\n" );

  return m_config_seed;
}

//=============================================================================
// Set the random seed for toy MC event generation (public)
//=============================================================================
void FitMeTool::setSeed( int seed ) 
{  
  if ( m_config_debug )
    printf( "==> FitMeTool::setSeed( %d )\n", seed );
  
  // protect against seed 0 which makes bad things happen with most
  // generators
  if (0 == seed) seed = 1;
  RooRandom::randomGenerator() -> SetSeed( seed );
  
  m_config_seed    = seed;
  m_config_seedSet = true;
}

//=============================================================================
// Generate and store a new random seed (protected)
//=============================================================================
void FitMeTool::generateSeed() 
{  
  if ( m_config_debug )
    printf( "==> FitMeTool::generateSeed()\n" );
  
  TRandom3 rndm = TRandom3( m_config_toyNumber + 1 );
  
  setSeed( unsigned( rndm.Uniform( 1, std::numeric_limits<unsigned>::max() ) ) );
}

//=============================================================================
// Generate a toy MC sample (public)
//=============================================================================
void FitMeTool::generate( long int nevents,
                     const RooCmdArg& arg1,
                     const RooCmdArg& arg2,
                     const RooCmdArg& arg3,
                     const RooCmdArg& arg4 )
{
  if ( m_config_debug ) printf( "==> FitMeTool::generate()\n" );
  
  // Does it make sense to generate events in the first place!?
  // ----------------------------------------------------------
  if ( m_config_toyNumber < 0 ) {
    printf( "[ERROR] An input ntuple has been/is to be read in, so why would you also generate events !?\n" );
    exit( -1 );
  }
  
  // The generation of events requires the observables to be defined!
  // ----------------------------------------------------------------
  const RooArgSet* observables = getObservables();
  if ( observables == NULL ) {
    printf( "[ERROR] Impossible to generate events since model observables not yet defined!\n" );
    exit( -1 );
  }  
  
  if ( m_modelPDF -> canBeExtended() )
    printf( "    # of events to generate: %f\n",
            m_modelPDF -> expectedEvents( observables ) );
  else
    printf( "    # of events to generate: %ld\n", nevents );
  
  // Generate a random seed if none already set
  // ==========================================
  if ( m_config_debug ) printf( "    Get or generate & set a random seed ...\n" );
  if ( ! m_config_seedSet ) generateSeed();
  
  // Generate the events
  // ===================
  if ( m_config_debug ) printf( "    Generating the events ...\n" );
  RooDataSet* dataset = NULL;
  if ( m_modelPDF -> canBeExtended() )
    dataset = m_modelPDF -> generate( *observables, RooFit::Verbose(kTRUE),
	    arg1, arg2, arg3, arg4 );
  else
    dataset = m_modelPDF -> generate( *observables, nevents, RooFit::Verbose(kTRUE),
	    arg1, arg2, arg3, arg4 );
  if ( m_config_debug ) printf( "    ... done.\n" );
  setData( dataset );
  
  printf( "    # generated events = %d\n", dataset -> numEntries() );
}

//=============================================================================
// Fit and optionally save the result to a file (public)
//=============================================================================
void FitMeTool::fit( bool save2file,
                     const RooCmdArg& arg1,
                     const RooCmdArg& arg2,
                     const RooCmdArg& arg3,
                     const RooCmdArg& arg4,
                     const RooCmdArg& arg5,
                     const RooCmdArg& arg6,
                     const RooCmdArg& arg7
                     )
{
  if ( m_config_debug )
    printf( "==> FitMeTool::fit()\n" );
  
  m_config_saveFitResult2File = save2file;
  
  // Is there any data to fit to, in the first place ;-)?
  // ----------------------------------------------------
  if ( ! m_data )
  {
    printf( "[ERROR] Please generate or read in a dataset before trying to fit to it !\n" );
    exit( -1 );
  }  
  
  // Fit the model PDF to the dataset and store the fit result if requested
  // ----------------------------------------------------------------------
  RooLinkedList cmdArgs;
  RooCmdArg tmp[3];
  tmp[0] = RooFit::Save();
  cmdArgs.Add(&tmp[0]);
  if (m_conditionalObservables) {
      tmp[1] = RooFit::ConditionalObservables(*m_conditionalObservables);
      cmdArgs.Add(&tmp[1]);
  }
  if (m_externalConstraints) {
      tmp[2] = RooFit::ExternalConstraints(*m_externalConstraints);
      cmdArgs.Add(&tmp[2]);
  }
  cmdArgs.Add(const_cast<RooCmdArg*>(&arg1));
  cmdArgs.Add(const_cast<RooCmdArg*>(&arg2));
  cmdArgs.Add(const_cast<RooCmdArg*>(&arg3));
  cmdArgs.Add(const_cast<RooCmdArg*>(&arg4));
  cmdArgs.Add(const_cast<RooCmdArg*>(&arg5));
  cmdArgs.Add(const_cast<RooCmdArg*>(&arg6));
  cmdArgs.Add(const_cast<RooCmdArg*>(&arg7));
  m_fitResult = m_modelPDF -> fitTo(*m_data, cmdArgs);
  //if ( m_fitResult ) m_fitResult -> Print( "v" );
  //std::cout << "FIT ERRORS!" << std::endl;
  //std::cout << m_modelPDF->find("deltaMs_ub")->getVal() << " +- " << m_modelPDF->find("deltaMs_ub")->getError() << std::endl;
  //std::cout << "FIT ERRORS!" << std::endl; 
  if ( m_config_saveFitResult2File ) {
    createOutputFile();
    m_fitResult -> Clone() -> Write(); 
    m_workSpace -> import(*m_fitResult); 
    if ( m_config_debug ) printf( "    RooFitResult object stored to output ROOT file.\n" ); 
  }
}

//=============================================================================
// Get the fit result (public)
//=============================================================================
RooFitResult* FitMeTool::getFitResult()
{
  if ( m_config_debug )
    printf( "==> FitMeTool::getFitResult()\n" );
  
  if ( ! m_fitResult ) {
    printf( "[ERROR] \"Fit result variable\" = NULL!\n" );
    printf( "[ERROR] --> Are you sure the fit was run asking for the result to be stored ;-)?\n" );
  }  
  
  return m_fitResult;
}

//=============================================================================
// Set debugging mode on/off (public)
//=============================================================================
void FitMeTool::setDebug( bool yesNo )
{
  m_config_debug = yesNo;
  
  if ( m_config_debug )
    std::cout << "==> FitMeTool: debugging ON" << std::endl;
  else
    std::cout << "==> FitMeTool: debugging OFF" << std::endl;
}

//=============================================================================
// Set the fit observables (public)
//=============================================================================
void FitMeTool::setObservables( RooArgSet* observables )
{
  if ( m_config_debug )
    printf( "==> FitMeTool::setObservables( %p )\n", observables );
  
  // Just checking for NULL pointers ;-)
  if ( ! observables )
  {
    printf( "[ERROR] The input set of observables is NULL! Nothing done.\n" );
    exit( -1 );
  }
  else {
    if ( m_observables )
      printf( "[WARNING] Set of observables overriden.\n" );

    // Always import new objects to the FitMeTool workspace !
    Bool_t error = m_workSpace -> import( *( observables ) );
    if ( error ) {
      printf( "[ERROR] Failed to import the observables to the workspace!\n" );
      exit( -1 );
    }
    // Give a name to the set so as to be able to refer to it in the workspace
    error = m_workSpace -> defineSet( "observables", *( observables ) );
    
    // Keep a direct pointer to the set of observables
    m_observables = const_cast<RooArgSet*>( m_workSpace -> set( "observables" ) );
  }
}

void FitMeTool::setConditionalObservables(RooArgSet* condObs)
{
    // all conditional observables are observables and must therefore already
    // have counterparts with the same name in the workspace
    if (!condObs) {
	m_conditionalObservables = 0;
	return;
    }
    m_conditionalObservables = new RooArgSet();
    TIterator *it = condObs->createIterator();
    RooAbsArg* arg;
    while ((arg = reinterpret_cast<RooAbsArg*>(it->Next()))) {
	RooAbsArg* wsarg = reinterpret_cast<RooAbsArg*>(m_workSpace->obj(arg->GetName()));
	if (!wsarg) {
	    printf("[ERROR]: %s line %d: conditional observable must already be in workspace!\n",
		    __func__, __LINE__);
	    exit(-1);
	}
	m_conditionalObservables->add(*wsarg);
    }
    delete it;
    m_workSpace->defineSet("conditionalObservables", *m_conditionalObservables);
    delete m_conditionalObservables;
    m_conditionalObservables = const_cast<RooArgSet*>(m_workSpace->set("conditionalObservables"));
}

void FitMeTool::setExternalConstraints(RooArgSet* extConstraints)
{
    // external constraints are not part of the pdf or the observables, so they
    // need to be imported
    if (!extConstraints) {
	m_externalConstraints = 0;
	return;
    }
    // Always import new objects to the FitMeTool workspace !
    if (m_workSpace->import(*extConstraints)) {
      printf( "[ERROR] Failed to import the external constraints to the workspace!\n" );
      exit( -1 );
    }
    // Give a name to the set so as to be able to refer to it in the workspace
    m_workSpace->defineSet("externalConstraints", *extConstraints);
    
    // Keep a direct pointer to the set of externalConstraints
    m_externalConstraints = const_cast<RooArgSet*>(m_workSpace->set("externalConstraints"));
}

//=============================================================================
// Get the fit observables (public)
//=============================================================================
const RooArgSet* FitMeTool::getObservables() const
{
  if ( m_config_debug )
    printf( "==> FitMeTool::getObservables()\n" );
  
  RooArgSet* observables = NULL;
  if ( m_data )
    // Extract the observables directly from the model if a dataset has been defined
    observables = m_modelPDF -> getObservables( m_data );
  else
    // Otherwise return whatever has been specified by the user, if at all!
    observables = m_observables;
  
  if ( m_config_debug && observables ) {
    printf( "    Set of observables:\n" );
    observables -> Print( "v" );
  }
  
  return observables;
}

const RooArgSet* FitMeTool::getConditionalObservables() const
{ return m_conditionalObservables; }

const RooArgSet* FitMeTool::getExternalConstraints() const
{ return m_externalConstraints; }

//=============================================================================
// Set the model PDF and the data (public)
//=============================================================================
void FitMeTool::setModelPDFandData( RooWorkspace* ws      ,
                                    const char* modelName ,
                                    const char* dataName
                                    )
{
  if ( m_config_debug )
    printf( "==> FitMeTool::setModelPDFandDataSet( WS=%s, model=%s, data=%s )\n",
            ws -> GetName(), modelName, dataName );
  
  // Just checking for NULL pointers ;-)
  if ( ! ws )
  {
    printf( "[ERROR] The input RooWorkspace is NULL ! Nothing done.\n" );
    exit( -1 );
  }
  
  // Set the model PDF
  setModelPDF( ws, modelName );
  
  // Set the dataset
  setData( ws, dataName );
  
  // Extract the observables directly from the model if a dataset has been defined
  setObservables( m_modelPDF -> getObservables( m_data ) );
}

//=============================================================================
// Set the model PDF (public)
//=============================================================================
void FitMeTool::setModelPDF( RooAbsPdf* modelPDF )
{
  if ( m_config_debug )
    printf( "==> FitMeTool::setModelPDF( model=%s )\n", modelPDF -> GetName() );
  
  // Just checking for NULL pointers ;-)
  if ( ! modelPDF )
  {
    printf( "[ERROR] The input model PDF is NULL! Nothing done.\n" );
    exit( -1 );
  }
  else {
    if ( m_modelPDF )
      printf( "[WARNING] Model PDF overriden.\n" );
    
    // Always import new objects to the FitMeTool workspace !
    Bool_t error = m_workSpace -> import( *( modelPDF ) );
    
    if ( error ) {
      printf( "[ERROR] Failed to import the observables to the workspace!\n" );
      exit( -1 );
    }
    
    // Keep a direct pointer to the model PDF
    m_modelPDF = m_workSpace -> pdf( modelPDF -> GetName() );
  }
}

//=============================================================================
// Set the model PDF (public)
//=============================================================================
void FitMeTool::setModelPDF( RooWorkspace* ws, const char* modelName )
{
  if ( m_config_debug )
    printf( "==> FitMeTool::setModelPDF( WS=%s, model=%s )\n",
            ws -> GetName(), modelName );
  
  // Just checking for NULL pointers ;-)
  if ( ! ws )
  {
    printf( "[ERROR] The input RooWorkspace is NULL ! Nothing done.\n" );
    exit( -1 );
  }
  
  RooAbsPdf* pdf = (RooAbsPdf*) ws -> pdf( modelName );
  if ( ! pdf ) {
    printf( "[ERROR] Model PDF \"%s\" not found in workspace \"%s\"! Nothing done.\n",
            modelName, ws -> GetName() );
    exit( -1 );
  }
  
  setModelPDF( pdf );
}

//=============================================================================
// Set the model PDF (public)
//=============================================================================
void FitMeTool::setModelPDF( const char* fileName,
                             const char* wsName,
                             const char* modelName
                             )
{
  if ( m_config_debug )
    printf( "==> FitMeTool::setModelPDF( file=%s, WS=%s, model=%s )\n", fileName, wsName, modelName );
  
  TFile* file = TFile::Open( fileName );
  if ( file == NULL ) {
    printf( "[ERROR] The workspace file \"%s\" does not exist! Nothing done.\n",
            fileName );
    exit( -1 );
  }
  
  RooWorkspace* ws = (RooWorkspace*) file -> Get( wsName );
  if ( ! ws ) {
    printf( "[ERROR] Workspace \"%s\" not found on file \"%s\"!\n", wsName, fileName );
    exit( -1 );
  }
  
  setModelPDF( ws, modelName );
}

//=============================================================================
// Get the model PDF (public)
//=============================================================================
RooAbsPdf* FitMeTool::getModelPDF()
{
  if ( m_config_debug )
    printf( "==> FitMeTool::getModelPDF()\n" );
  
  // First things first: has the model PDF been built already!?
  if ( ! m_modelPDF )
  {
    printf( "[ERROR] Impossible to return the model PDF since it hasn't been built yet!\n" );
    exit( -1 );
  }
  else
    return m_modelPDF;
}

//=============================================================================
// Save the model PDF on to a ROOT file (public)
//=============================================================================
void FitMeTool::saveModelPDF( const char* workspaceFileName )
{
  if ( m_config_debug )
    printf( "==> FitMeTool::saveModelPDF( workspaceFileName=\"%s\" )\n", workspaceFileName );
  
  char rootFileName[100];
  sprintf( rootFileName, "%s", workspaceFileName );
  Bool_t error = m_workSpace -> writeToFile( rootFileName );
  if ( error ) {
    printf( "[ERROR] Failed to write out the model PDF to a workspace on file \"%s\"!\n",
            rootFileName );
    exit( -1 );
  }
  else
    printf( "Workspace \"%s\" with model PDF successfully written out to file \"%s\"!\n",
            m_workSpace -> GetName(), rootFileName );
}

//=============================================================================
// Save the data on to a ROOT file (public)
//=============================================================================
void FitMeTool::saveData( const char* workspaceFileName )
{
  if ( m_config_debug )
    printf( "==> FitMeTool::saveData( workspaceFileName=\"%s\" )\n", workspaceFileName );
  
  char rootFileName[100];
  sprintf( rootFileName, "%s", workspaceFileName );
  Bool_t error = m_workSpace -> writeToFile( rootFileName );
  if ( error ) {
    printf( "[ERROR] Failed to write out the data to a workspace on file \"%s\"!\n",
            rootFileName );
    exit( -1 );
  }
  else
    printf( "Workspace \"%s\" with data successfully written out to file \"%s\"!\n",
            m_workSpace -> GetName(), rootFileName ); 
}

//=============================================================================
// Set the generated/read data (public)
//=============================================================================
void FitMeTool::setData( RooAbsData* data )
{
  if ( m_config_debug )
    printf( "==> FitMeTool::setData( %s )\n",
            data == NULL ? "NULL" : data -> GetName() );
  
  // Just checking for NULL pointers ;-)
  if ( ! data )
  {
    printf( "[ERROR] The input data is NULL ! Nothing done.\n" );
    exit( -1 );
  }
  else {
    if ( m_data )
      printf( "[WARNING] Data overriden.\n" );
    
    // Always import new objects to the FitMeTool workspace !
    Bool_t error = m_workSpace -> import( *( data ) );
    
    if ( error ) {
      printf( "[ERROR] Failed to import the data to the workspace!\n" );
      exit( -1 );
    }
    
    // Keep a direct pointer to the data
    m_data = m_workSpace -> data( data -> GetName() );
  }
}

//=============================================================================
// Set the generated/read data (public)
//=============================================================================
void FitMeTool::setData( const char* fileName,
                         const char* wsName,
                         const char* dataName
                         )
{
  if ( m_config_debug )
    printf( "==> FitMeTool::setData( file=%s, WS=%s, data=%s )\n", fileName, wsName, dataName );
  
  TFile* file = TFile::Open( fileName );
  if ( file == NULL ) {
    printf( "[ERROR] The workspace file \"%s\" does not exist! Nothing done.\n",
            fileName );
    exit( -1 );
  }
  
  RooWorkspace* ws = (RooWorkspace*) file -> Get( wsName );
  if ( ! ws ) {
    printf( "[ERROR] Workspace \"%s\" not found on file \"%s\"!\n", wsName, fileName );
    exit( -1 );
  }
  
  setData( ws, dataName );
}

//=============================================================================
// Set the generated/read data (public)
//=============================================================================
void FitMeTool::setData( RooWorkspace* ws, const char* dataName )
{
  if ( m_config_debug )
    printf( "==> FitMeTool::setData( WS=%s, data=%s )\n",
            ws -> GetName(), dataName );
  
  // Just checking for NULL pointers ;-)
  if ( ! ws )
  {
    printf( "[ERROR] The input RooWorkspace is NULL ! Nothing done.\n" );
    exit( -1 );
  }
  
  RooAbsData* data = (RooAbsData*) ws -> data( dataName );
  if ( ! data ) {
    printf( "[ERROR] Data \"%s\" not found in workspace \"%s\"! Nothing done.\n",
            dataName, ws -> GetName() );
    exit( -1 );
  }
  
  setData( data );
}

//=============================================================================
// Set the generated/read dataset (public)
//=============================================================================
void FitMeTool::setDataSet( const char* fileName,
                            const char* treeName,
                            const char* subDir,
                            const char* cuts
                            )
{
  if ( m_config_debug )
    printf( "==> FitMeTool::setDataSet( file=%s, tree=%s, subdir=%s, cuts=%s )\n",
            fileName, treeName, subDir, cuts );
  
  // Does it make sense to read in data in the first place!?
  if ( m_config_toyNumber >= 0 ) {
    printf( "[ERROR] A toy number %d has been specified, so why would you also read in events !?\n", m_config_toyNumber );
    exit( -1 );
  }
  
  TFile* file =  TFile::Open( fileName, "READ" );
  if ( file == NULL ) {
    printf( "[ERROR] The ntuple data file \"%s\" does not exist! Nothing done.\n",
            fileName );
    exit( -1 );
  }

  char chainName[500];
  sprintf( chainName, "%s%s%s",
           ( subDir == NULL ? "" : subDir ), ( subDir == NULL ? "" : "/" ), treeName );
  TTree* tree = (TTree*) file -> Get( chainName );
  if ( tree == NULL ) {
    printf( "[ERROR] Unable to find TTree '%s' in input data file '%s'! Nothing done.\n",
            chainName, fileName );
    exit( -1 );
  }
  if ( m_config_debug )
    printf( "    TTree '%s': %d entries\n", chainName, (int) tree -> GetEntries() );
  
  if ( m_observables != NULL ) {
    RooAbsData* dataset = new RooDataSet( "data", "data", *m_observables,
                                          RooFit::Import( *tree ),
                                          RooFit::Cut( cuts )  );
    setData( dataset );
  }
  else {
    printf( "[ERROR] Impossible to define the RooDataSet since model observables not yet defined!\n" );
    exit( -1 );
  }
  
  if ( m_config_debug && m_data ) m_data -> Print( "v" );
}

//=============================================================================
// Set the generated/read dataset (public)
//=============================================================================
void FitMeTool::setDataSet( std::vector<std::string> filesList,
                            const char* treeName,
                            const char* subDir,
                            const char* cuts
                            )
{
  // Make a string with the comma-separated list of input files (can be improved)
  std::ostringstream s;
  std::copy( filesList.begin(), filesList.end(),
             std::ostream_iterator<std::string>( s, "," ) );
  char filesListStream[10000];
  sprintf( filesListStream,  "[%s]", s.str().c_str() );
  if ( m_config_debug )
    printf( "==> FitMeTool::setDataSet( filesList=%s, tree=%s, subdir=%s, cuts=%s )\n",
            filesListStream, treeName, subDir, cuts );
  
  // Does it make sense to read in data in the first place!?
  if ( m_config_toyNumber >= 0 ) {
    printf( "[ERROR] A toy number %d has been specified, so why would you also read in events !?\n", m_config_toyNumber );
    exit( -1 );
  }
  
  for ( unsigned int iFile = 0; iFile < filesList.size(); ++iFile ) {
    const char* fileName = filesList[ iFile ].c_str();
    TFile* file =  TFile::Open( fileName, "READ" );
    if ( file == NULL ) {
      printf( "[ERROR] The ntuple data file \"%s\" in the list does not exist! Nothing done.\n",
              fileName );
      exit( -1 );
    }
  }
  
  char chainName[100];
  sprintf( chainName, "%s%s%s", subDir,
           ( subDir == NULL ? "" : "/" ),
           treeName );             // "NAME" or "DIR/NAME"
  TChain* chain = new TChain( chainName, "" );
  
  for ( unsigned int iFile = 0; iFile < filesList.size(); ++iFile ) {
    const char* fileName = filesList[ iFile ].c_str();
    chain -> Add( fileName );
    printf( "  File '%s' added to the chain\n", fileName );
  }
  
  TTree* tree = chain;
  
  if ( m_config_debug )
    printf( "    TChain '%s': %d entries\n", chainName, (int) tree -> GetEntries() );
  
  if ( m_observables != NULL ) {
    RooAbsData* dataset = new RooDataSet( "data", "data", *m_observables,
                                          RooFit::Import( *tree ),
                                          RooFit::Cut( cuts )  );
    setData( dataset );
  }
  else {
    printf( "[ERROR] Impossible to define the RooDataSet since model observables not yet defined!\n" );
    exit( -1 );
  }
  
  if ( m_config_debug && m_data ) m_data -> Print( "v" );
}

//=============================================================================
// Get the generated/read data (public)
//=============================================================================
RooAbsData* FitMeTool::getData()
{
  if ( m_config_debug )
    printf( "==> FitMeTool::getData()\n" );
  
  // Just checking: has the data been defined (generated or read in) already!?
  if ( ! m_data )
  {
    printf( "[ERROR] Impossible to return the dataset since it hasn't been defined yet!\n" );
    exit( -1 );
  }
  else
    return m_data;
}

//=============================================================================
// Create an output file to store the fit results (RooFitResult object)
// File name format: "fitresult_<toyNumber>.root" for toys and
//                    "fitresult_ntuple.root" when reading data from an ntuple
// (protected)
//=============================================================================
void FitMeTool::createOutputFile()
{
  if ( m_config_debug )
    printf( "==> FitMeTool::createOutputFile()\n" );
  
  char rootfilename[100];
  if ( m_config_toyNumber < 0 )
    sprintf( rootfilename, "fitresult_ntuple.root" );
  else
    sprintf( rootfilename, "fitresult_%04d.root", m_config_toyNumber );
  
  if ( m_config_debug )
    printf( "    Creating output ROOT file \"%s\" ...", rootfilename ); 
  delete m_outputFile;
  m_outputFile = new TFile( rootfilename, "RECREATE" );
  if ( m_config_debug )
    printf( " done.\n" ); 
}

//=============================================================================
// Print the PDF model structure including variables, observables, parameters
// (public)
//=============================================================================
void FitMeTool::printModelStructure()
{
  if ( m_config_debug )
    printf( "==> FitMeTool::printModelStructure()\n" );
  
  RooAbsPdf* modelPDF = getModelPDF() ;
  
  if ( ! modelPDF ) {
    printf( "[ERROR] Impossible to print model structure since PDF not yet defined !?\n" );
    return;
  }
  
  // Model structure
  printf( "Model PDF name / title: \"%s\" / \"%s\"\n",
          modelPDF -> GetName(), modelPDF -> GetTitle() );
  modelPDF -> Print( "t" );
	
  // Model variables
  printf( "Model PDF variables:\n" );
  RooArgSet* vars = modelPDF -> getVariables();
  vars -> Print( "v" );
	
  // Model observables
  if ( m_observables ) {
    printf( "Model PDF observables:\n" );
    m_observables -> Print( "v" );
	}
  
  // Model parameters
  if ( m_data ) {
    printf( "Model PDF parameters:\n" );
    RooArgSet* params = modelPDF -> getParameters( m_data );
    params -> Print( "v" );
  }
}

//=============================================================================
// Produce a graphical representation of the model PDF with the dot tool
// (public)
//=============================================================================
void FitMeTool::produceGraphicalModelStructure( const char* fileName )
{
  if ( m_config_debug )
    printf( "==> FitMeTool::produceGraphicalModelStructure()\n" );
 
  // First check that the GraphViz dot tool exists on the system ;-)

  getModelPDF() -> graphVizTree( "model.dot" );

  // Finally, produce the GIF file
  char cmd[200];
  sprintf( cmd, "dot -Tgif -o %s model.dot", fileName );
  system( cmd );

  printf( "    Graphical representation of the structure of the model produced: model.gif.\n" );
}


void FitMeTool::printTotalYields(const char* wildcard)
{

  if ( m_config_debug )
    printf( "==> FitMeTool::printTotalYields()\n");

  // Get all model PDF variables matching a wildcard                                                                                                                                             
  // -----------------------------------------------                                                                                                                                             
  RooArgSet* vars = getMatchingVariableNames( "*Evts*", false );
  if ( vars && vars -> getSize() == 0 ) {
    printf( "[WARNING] Found no variable matching the wildcard '%s' ! Please check.\n",
            wildcard);
    return;
  }

  TIterator* it = vars -> createIterator();
  TObject* obj  = NULL;
  std::vector<TString> usedNames; 

  while ( ( obj = it -> Next() ) ) 
    {
      RooAbsReal* nVar = dynamic_cast<RooAbsReal*>( obj );
      if ( ! nVar ) continue;
      TString name = nVar->GetName(); 
      Ssiz_t first = name.First("_");
      Ssiz_t lenght = name.Length();
      name.Remove(first,lenght);
      Bool_t notUsed = false; 
      for (unsigned int i = 0; i < usedNames.size(); i++ )
	{
	  if ( usedNames[i] == name ) { notUsed = true; }
	}
      if ( notUsed == false)  { usedNames.push_back(name); } 
    }

  std::cout<<"##################################################################"<<std::endl;
  std::cout<<"                  Total number of yields                          "<<std::endl; 
  std::cout<<"##################################################################"<<std::endl; 

  Double_t sigVal(0.0), sigErr(0.0);
  Double_t bkgVal(0.0), bkgErr(0.0); 

  for(unsigned int i = 0; i < usedNames.size(); i++ )
    {
      TString name = usedNames[i]+"*Evts*"; 
      RooArgSet* varsType = getMatchingVariableNames( name.Data(), false );
      TIterator* itType = varsType -> createIterator();
      TObject* objType  = NULL;
      Double_t val = 0.0;
      Double_t err = 0.0; 
      while ( ( objType = itType -> Next() ) )
	{
	  RooRealVar* nVar = dynamic_cast<RooRealVar*>( objType );
	  if ( ! nVar ) continue;
	  Double_t valC = nVar->getValV();
	  Double_t errC = nVar->getError(); 
	  val = val + valC;
	  err = err + errC*errC;
	  if ( usedNames[i] != "nSig" ) { bkgVal = bkgVal +valC; bkgErr = bkgErr+ errC*errC; }
	  else {  sigVal = sigVal +valC; sigErr = sigErr+ errC*errC; } 
	}
      err = std::sqrt(err); 
      printf( "%25s:  %10.2f +/- %5.2f \n", usedNames[i].Data(), val, err );
    }
  bkgErr = std::sqrt(bkgErr);
  sigErr = std::sqrt(sigErr); 

  std::cout<<"------------------------------------------------------------------"<<std::endl;
  printf( "%25s:  %10.2f +/- %5.2f \n", "Background", bkgVal, bkgErr );
  printf( "%25s:  %10.2f +/- %5.2f \n", "Signal", sigVal, sigErr );

  Double_t SB = sigVal/bkgVal; 
  Double_t SS = sigVal/std::sqrt(sigVal + bkgVal); 
  std::cout<<"------------------------------------------------------------------"<<std::endl;
  printf( "##################################################################\n" );
  std::cout<<"------------------------------------------------------------------"<<std::endl;
  std::cout<<"                Performance in full range                         "<<std::endl;
  std::cout<<"------------------------------------------------------------------"<<std::endl;
  printf( "%25s:  %10.2f  \n", "S/B", SB);
  printf( "%25s:  %10.2f  \n", "S/sqrt(S+B)",SS);
  std::cout<<"##################################################################"<<std::endl;


}
//=============================================================================
// Calculate yields in a defined observable range given an input wildcard
// for matching "yield variables" (public)
//=============================================================================
void FitMeTool::printYieldsInRange( const char* wildcard,
                                    const char* observableName,
                                    double low, double high,
                                    const char* rangeName,
				    const char* observableName2,
				    double low2, double high2,
				    const char* observableName3,
				    double low3, double high3
                                    )
{
  if ( m_config_debug )
    printf( "==> FitMeTool::printYieldsInRange( obs=%s, range=[%6.2f,%6.2f], rangeName=%s )\n",
            observableName, low, high, rangeName );
  
  // Set the range for the input observable, if necessary
  // ----------------------------------------------------
  const RooArgSet* observables = getObservables();
  if ( ! observables ) {
    printf( "[ERROR] Observables still undefined !\n" );
    return;
  }
  
  RooArgSet* set = new RooArgSet();

  RooRealVar* obs = (RooRealVar*) observables -> find( observableName );
  if ( ! obs ) {
    printf( "[ERROR] Cannot find the observable '%s' among the defined set of observables !\n",
            observableName );
    return;
  }
 
  
  if ( ! obs -> hasRange( rangeName ) ) obs -> setRange( rangeName, low, high );
  set->add(*obs); 

  RooRealVar* obs2 = NULL;
  if ( observableName2 != NULL )
    {
      obs2 = (RooRealVar*) observables -> find( observableName2 );
      if ( ! obs2 ) {
        printf( "[ERROR] Cannot find the observable '%s' among the defined set of observables !\n",
                observableName2 );
	return;
      }

      if ( ! obs2 -> hasRange( rangeName ) ) obs2 -> setRange( rangeName, low2, high2 );
      set->add(*obs2);
    }

  RooRealVar* obs3 = NULL;
  if ( observableName3 != NULL )
    {
      obs3 = (RooRealVar*) observables -> find( observableName3 );
      if ( ! obs3 ) {
        printf( "[ERROR] Cannot find the observable '%s' among the defined set of observables !\n",
                observableName3 );
        return;
      }

      if ( ! obs3 -> hasRange( rangeName ) ) obs3 -> setRange( rangeName, low3, high3 );
      set->add(*obs3);
    }


  // Get all model PDF variables matching a wildcard
  // -----------------------------------------------
  RooArgSet* vars = getMatchingVariableNames( "*Evts*", true );
  if ( vars && vars -> getSize() == 0 ) {
    printf( "[WARNING] Found no variable matching the wildcard '%s' ! Please check.\n",
            wildcard );
    return;
  }
  
  // Get all RooExtendPdf PDFs in the fit model PDF
  // ----------------------------------------------
  RooArgSet* epdfs = getEPDFComponents();
  if ( epdfs && epdfs -> getSize() == 0 ) {
    printf( "[ERROR] Found no EPDFs in the fit model ! Please check.\n" );
    return;
  }  
  
  // Loop over all yield variables -> calculate and print the yields
  // ---------------------------------------------------------------
  std::map< const char*, std::pair<double,double> > yieldsMap;

  TIterator* it = vars -> createIterator();
  TObject* obj  = NULL;
  std::vector<TString> usedNames;
  while ( ( obj = it -> Next() ) ) {
    RooAbsReal* nVar = dynamic_cast<RooAbsReal*>( obj );
    if ( ! nVar ) continue;
    TString name = nVar->GetName();
    Ssiz_t first = name.First("_");
    Ssiz_t lenght = name.Length();
    name.Remove(first,lenght);
    Bool_t notUsed = false;
    for (unsigned int i = 0; i < usedNames.size(); i++ )
      {
	if ( usedNames[i] == name ) { notUsed = true; }
      }
    if ( notUsed == false)  { usedNames.push_back(name); }

    RooAbsPdf* epdf = getMatchingEPDFComponent( nVar -> GetName(), epdfs );
    if ( ! epdf ) {
      printf( "[ERROR] Cannot find an EPDF matching the yield variable '%s'. Yield variable skipped !\n",
              nVar -> GetName() );
      continue;
    }
    RooAbsReal* fracVar = epdf -> createIntegral( *set,
                                                  RooFit::NormSet( *set ),
                                                  RooFit::Range( rangeName )
                                                  );
    const double n = nVar    -> getVal();
    const double f = fracVar -> getVal();
    yieldsMap[ nVar -> GetName() ] = std::make_pair( n, f );    
  }

  // At last print all calculated yields
  // -----------------------------------
  printf( "\n##################################################################\n" );
  printf( "Yields in range [%6.2f,%6.2f] for variable %s named '%s' :\n", low, high, obs->GetName(), rangeName );
  if ( observableName2 != NULL ) { printf( "Yields in range [%6.2f,%6.2f] for variable %s named '%s' :\n", low2, high2, obs2->GetName(), rangeName );}
  if ( observableName3 != NULL ) { printf( "Yields in range [%6.2f,%6.2f] for variable %s named '%s' :\n", low3, high3, obs3->GetName(), rangeName );}
  for ( std::map< const char*, std::pair<double,double > >::const_iterator iter = yieldsMap.begin();
        iter != yieldsMap.end(); ++iter ) {
    const double n = ( iter -> second ).first;
    const double f = iter -> second.second;
    printf( "%25s: %10.2f    ( %5.3f * %8.2f )\n",
            iter -> first, n * f, f, n );
  }

  std::cout<<"------------------------------------------------------------------"<<std::endl;
  Double_t sigVal(0.0), sigValTot(0.0);
  Double_t bkgVal(0.0), bkgValTot(0.0); 

  for(unsigned int i = 0; i < usedNames.size(); i++ )
    {
      Double_t val = 0.0;
      Double_t valTot = 0.0; 
      for ( std::map< const char*, std::pair<double,double > >::const_iterator iter = yieldsMap.begin();
	    iter != yieldsMap.end(); ++iter ) 
	{
	  TString name = iter->first;
	  if ( name.Contains(usedNames[i]) == true )
	    {
	      const double n = ( iter -> second ).first;
	      const double f = iter -> second.second;
	      val = val + n*f;
	      valTot = valTot +n; 
	      if ( usedNames[i] != "nSig" ) { bkgVal = bkgVal +n*f; bkgValTot = bkgValTot + n; }
	      else {  sigVal = sigVal + n*f; sigValTot = sigValTot +n;}
	    }
	}
      printf( "%25s:  %10.2f ( total: %10.2f )\n", usedNames[i].Data(), val, valTot );
    }

  std::cout<<"------------------------------------------------------------------"<<std::endl;
  printf( "%25s:  %10.2f ( total: %10.2f )\n", "Background", bkgVal, bkgValTot );
  printf( "%25s:  %10.2f ( total: %10.2f )\n", "Signal", sigVal, sigValTot );
  std::cout<<"------------------------------------------------------------------"<<std::endl;
  
  Double_t SB = sigVal/bkgVal;
  Double_t SS = sigVal/std::sqrt(sigVal + bkgVal);

  Double_t SBTot = sigValTot/bkgValTot;
  Double_t SSTot = sigValTot/std::sqrt(sigValTot + bkgValTot);
  printf( "##################################################################\n" );
  std::cout<<"------------------------------------------------------------------"<<std::endl;
  std::cout<<"                Performance in signal range                         "<<std::endl;
  std::cout<<"------------------------------------------------------------------"<<std::endl;
  printf( "%25s:  %10.2f ( total: %10.2f ) \n",   "S/B", SB, SBTot);
  printf( "%25s:  %10.2f ( total: %10.2f )  \n", "S/sqrt(S+B)",SS, SSTot);

  printf( "##################################################################\n" );


}

//=============================================================================
// Calculate input variable yield in a defined observable range (public)
//=============================================================================
void FitMeTool::printYieldInRange( const char* yieldVarName,
                                   const char* observableName,
                                   double low, double high,
                                   const char* rangeName,
				   const char* observableName2,
                                   double low2, double high2,
				   const char* observableName3,
                                   double low3, double high3
                                   )
{
  if ( m_config_debug )
    printf( "==> FitMeTool::printYieldInRange( yieldVarName=%s, obs=%s, range=[%6.2f,%6.2f], rangeName=%s )\n",
            yieldVarName, observableName, low, high, rangeName );
  
  // Set the range for the input observable, if necessary
  // ----------------------------------------------------
  const RooArgSet* observables = getObservables();
  if ( ! observables ) {
    printf( "[ERROR] Observables still undefined !\n" );
    return;
  }
  
  RooRealVar* obs = (RooRealVar*) observables -> find( observableName );
  RooArgSet* set = new RooArgSet(); 
  if ( ! obs ) {
    printf( "[ERROR] Cannot find the observable '%s' among the defined set of observables !\n",
            observableName );
    return;
  }
  
  if ( ! obs -> hasRange( rangeName ) ) obs -> setRange( rangeName, low, high );
  set->add(*obs);

  RooRealVar* obs2 = NULL;
  if ( observableName2 != NULL )
    {
      obs2 = (RooRealVar*) observables -> find( observableName2 );
      if ( ! obs2 ) {
	printf( "[ERROR] Cannot find the observable '%s' among the defined set of observables !\n",
		observableName2 );
	return;
      }

      if ( ! obs2 -> hasRange( rangeName ) ) obs2 -> setRange( rangeName, low2, high2 );
      set->add(*obs2);
    }

  RooRealVar* obs3 = NULL;
  if ( observableName3 != NULL )
    {
      obs3 = (RooRealVar*) observables -> find( observableName3 );
      if ( ! obs3 ) {
        printf( "[ERROR] Cannot find the observable '%s' among the defined set of observables !\n",
                observableName3 );
        return;
      }

      if ( ! obs3 -> hasRange( rangeName ) ) obs3 -> setRange( rangeName, low3, high3 );
      set->add(*obs3); 
    }


  // Get the model EPDF yield variable matching the input name
  // ---------------------------------------------------------
  RooArgSet* vars = getMatchingVariableNames( yieldVarName, true );
  if ( ! vars ) {
    printf( "[ERROR] Found no variable matching the input name '%s' ! Please check.\n",
            yieldVarName );
    return;    
  }
  const RooAbsReal* nVar = dynamic_cast<const RooAbsReal*>( vars -> first() );
  
  // Get the RooExtendPdf PDF relating to the input (yield) variable
  // ---------------------------------------------------------------
  RooAbsPdf* epdf = getMatchingEPDFComponent( yieldVarName );
  if ( ! epdf ) {
    printf( "[ERROR] Cannot find an EPDF matching the yield variable '%s'. No yield calculated !\n",
            yieldVarName );
    return;
  }
  
  // At last perform the calculation and print it
  // --------------------------------------------
  RooAbsReal* fracVar = epdf -> createIntegral( *set,
                                                RooFit::NormSet( *set ),
                                                RooFit::Range( rangeName )
                                                );
  double n = nVar    -> getVal();
  double f = fracVar -> getVal();
  
  printf( "\n#################################################################\n" );
  printf( "Yields in range [%6.2f,%6.2f] for variable %s named '%s' :\n", low, high, obs->GetName(), rangeName );
  if ( observableName2 != NULL ) { printf( "Yields in range [%6.2f,%6.2f] for variable %s named '%s' :\n", low2, high2, obs2->GetName(), rangeName );}
  if ( observableName3 != NULL ) { printf( "Yields in range [%6.2f,%6.2f] for variable %s named '%s' :\n", low3, high3, obs3->GetName(), rangeName );}

  printf( "%25s: %10.2f    ( %5.3f * %8.2f )\n\n",
          nVar -> GetName(), n * f, f, n );
  printf( "#################################################################\n" );
}



//=============================================================================
// Get all RooExtendPdf PDFs in the fit model PDF, if any
//=============================================================================
RooArgSet* FitMeTool::getEPDFComponents()
{
  if ( m_config_debug )
    printf( "==> FitMeTool::getEPDFComponents()\n" );
  
  RooArgSet* epdfs = new RooArgSet( "ModelEPDFComponents" );
  
  TIterator* it = m_modelPDF -> getComponents() -> createIterator();
  
  TObject* obj = NULL;
  while ( ( obj = it -> Next() ) ) {
    if ( ! dynamic_cast<RooExtendPdf*>( obj ) ) continue;
    epdfs -> add( *( RooExtendPdf* ) obj ); 
  }
  
  if ( m_config_debug ) epdfs -> Print();
  
  return epdfs;
}

//=============================================================================
// Get the RooExtendPdf PDF relating to the input (yield) variable (protected)
//=============================================================================
RooAbsPdf* FitMeTool::getMatchingEPDFComponent( const char* yieldVarName,
                                                RooArgSet* epdfs )
{
  if ( m_config_debug )
    printf( "==> FitMeTool::getMatchingEPDFComponent( yieldVarName=%s )\n",
            yieldVarName );
  
  if ( ! epdfs ) epdfs = getEPDFComponents();
  
  TIterator* it = epdfs -> createIterator();
  
  TObject* obj = NULL;
  while ( ( obj = it -> Next() ) ) {
    RooAbsPdf* pdf = dynamic_cast<RooAbsPdf*>( obj );
    if ( pdf && pdf -> getVariables() -> find( yieldVarName ) )
      return pdf;
  }
  
  return NULL;
}

//=============================================================================
// Get all model PDF variables matching a wildcard (protected)
//=============================================================================
RooArgSet* FitMeTool::getMatchingVariableNames( const char* wildcard, bool debug )
{
  if ( debug )
    printf( "==> FitMeTool::getMatchingVariableNames( wildcard='%s' )\n",
            wildcard );  
  
  RooArgSet* vars = new RooArgSet( "MatchingVariableNames" );
  
  RooAbsCollection* coll = m_modelPDF -> getVariables() -> selectByName( wildcard );
  
  TIterator* it = coll -> createIterator();
  
  TObject* obj = NULL;
  while ( ( obj = it -> Next() ) ) {
    RooAbsReal* var = dynamic_cast<RooAbsReal*>( obj );
    if ( ! var ) continue;
    vars -> add( *var ); 
  }
  
  if ( debug ) vars -> Print( "v" );

  return vars;
}

//=============================================================================
// Prepare and save sWeights
//=============================================================================
void FitMeTool::savesWeights(const char* observableName, 
                             RooDataSet* data, 
                             TString& mode,
                             bool save2file,
                             const RooCmdArg& arg1,
                             const RooCmdArg& arg2,
                             const RooCmdArg& arg3,
                             const RooCmdArg& arg4,
                             const RooCmdArg& arg5,
                             const RooCmdArg& arg6,
                             const RooCmdArg& arg7)
{
  if ( m_config_debug )
    printf( "==> FitMeTool::savesWeights( obs=%s, data=%s, mode=%s )\n",
            observableName, data == NULL ? "NULL" : data -> GetName(), mode.Data() );
  
  // Sanity checks
  // -------------
  if ( ! data ) {
    printf( "[ERROR] The input data is NULL ! Nothing done.\n" );
    return;
  }
  if ( ! m_modelPDF ) {
    printf( "[ERROR] Impossible to return the model PDF since it hasn't been built yet!\n" );
    return;
  }
  
  const RooArgSet* observables = getObservables();
  if ( ! observables ) {
    printf( "[ERROR] Observables still undefined ! No sWeights saved.\n" );
    return;
  }
  
  // Find the input observable in the set of model observables
  // ---------------------------------------------------------
  RooRealVar* obs = (RooRealVar*) observables -> find( observableName );
  if ( ! obs ) {
    printf( "[ERROR] Cannot find the input observable '%s' among the defined set of observables !\n",
            observableName );
    printf( "[ERROR] No sWeights saved.\n" );
    return;
  }
  
  // Get all model PDF yield variables - assuming they match the wildcard "*Evts*"
  // ----------------------------------------------------------------------------
  RooArgSet* vars2 = getMatchingVariableNames( "*Evts*" );
  RooArgList* vars = new RooArgList( *vars2 );
  if ( vars && vars -> getSize() == 0 ) {
    printf( "[WARNING] Found no yield variable matching the wildcard \"*Evts*\" ! Please check.\n");
    return;
  }  

  /*RooArgList* vars = new RooArgList( "MatchingVariableNames" );
  RooAbsCollection* coll = m_modelPDF -> getVariables() -> selectByName("*Evts");
  
  TIterator* it2 = coll -> createIterator();
  TObject* obj2 = NULL;
  while ( ( obj2 = it2 -> Next() ) ) {
  RooAbsReal* var = dynamic_cast<RooAbsReal*>( obj2 );
  if ( ! var ) continue;
      vars -> add( *var );
  }
  if ( m_config_debug ) vars -> Print();
  if ( vars && vars -> getSize() == 0 ) {
       printf( "[WARNING] Found no variable matching the wildcard ! Please check.\n");
       return;
     }
  */

  // Check for non-const model parameters and set them to constant
  // This is absolutely necessary for the sPlots technique to work !
  // ---------------------------------------------------------------
  RooArgSet* params = m_modelPDF -> getParameters( data );  
  TIterator* it = params -> createIterator();
  TObject* obj  = NULL;
  while ( ( obj = it -> Next() ) ) {
    //RooAbsRealLValue* param = dynamic_cast<RooAbsRealLValue*>( obj );
    RooRealVar* param = dynamic_cast<RooRealVar*>( obj );
    if ( param &&
         ( ! vars -> contains( *param ) ) &&
         ( ! param -> isConstant() ) ) {
      printf( "[WARNING] Variable \"%s\" set to constant (%lf) - sPlot technique requirement.\n",
              param -> GetName(), param -> getVal() );
      param -> setConstant();
    }
    /*
    TString name = param->GetName();
    if ( name.Contains("Evts") == true && param->isConstant() == true)
      {
	Double_t val = param->getValV();
	if (val == 0.0 )
	  {
	    param->setRange(-1.0, 1.0);
	  }
	else
	  {
	    param->setRange(0.95*val, 1.05*val);
	  }
	param->clearValueAndShapeDirty(); 
	param->setConstant(false); 
	printf( "[WARNING] Variable \"%s\" set to be floated - sPlot technique requirement.\n",
		param -> GetName() );
      }
    */
    //if (vars -> contains( *param )) {
    //  param -> setConstant(kFALSE);
    //}
  }
  fit(save2file,
      arg1,
      arg2,
      arg3,
      arg4,
      arg5,
      arg6,
      arg7);
  // Produce the new dataset with the sWeights for the yield variable
  // ----------------------------------------------------------------
  RooStats::SPlot* splot = NULL;
  TString splotname = "sPlot_"+mode;
  TString dupa = "data_sweight";
  RooArgSet set;

  
  RooMsgService::instance().deleteStream(RooFit::Eval);

  splot = new RooStats::SPlot(splotname.Data(), splotname.Data(), *data, m_modelPDF,*vars,set,true,true, dupa.Data());
  if (splot != NULL ) { printf("SPlot is created\n"); } else { printf("[ERROR] Cannot create sPlot\n"); return; }
  
  RooMsgService::instance().reset();

  // Check that the weights seem reasonable
  // --------------------------------------
  printf( "Cross-check on sWeights:\n" );
  for ( int i = 0; i < vars -> getSize(); ++i ) {
    RooAbsArg* iarg = vars -> at( i );
    RooAbsRealLValue* ivar = dynamic_cast<RooAbsRealLValue*>( iarg );
    if ( ivar ) printf( "Yield of %40s is %15f. From sWeights it is %15f\n",
                        ivar -> GetName(), ivar -> getVal(),
                        splot -> GetYieldFromSWeight( ivar -> GetName() ) );
  }
  
  // Finally, store the sWeights on a ROOT file
  // ------------------------------------------
  TString name = mode;
  TString name2 = "dataSetBsDsK_up_pipipi";
  //data->Print("v");
 
  std::cout << "About to write the sWeights to " << name.Data() << std::endl;
 
  TFile* out = new TFile( name.Data(), "RECREATE" );
  out->cd();
  splot->GetSDataSet()->tree()->Write();
  out->Close();
  delete out;
}

//=============================================================================
// 
//=============================================================================
RooUnblindOffset* FitMeTool::blindValue( RooRealVar& varToBeblinded,
                                         RooCategory& category,
                                         const std::string prefix
                                         )
{
  // NOTE: CODE TO BE FINALISED !!!  
  double scale = 0.2;
  std::string name  = prefix + varToBeblinded.GetName();
  std::string title = prefix + varToBeblinded.GetTitle();
  std::cout << "Blinding " << varToBeblinded.GetName()
       << ", val = " <<   varToBeblinded.getVal() << std::endl;
  RooUnblindOffset* blindedVar = new RooUnblindOffset( name.c_str(),
                                                       title.c_str(),
                                                       "chocolateKKK",
                                                       scale,
                                                       varToBeblinded,
                                                       category
                                                       );
  
  return blindedVar;
}

//=============================================================================
// Class destructor (public)
//=============================================================================
FitMeTool::~FitMeTool()
{
  if ( m_config_debug )
    printf( "==> FitMeTool::~FitMeTool()\n" );
  
  if ( m_config_saveFitResult2File ) {
    m_outputFile -> Close();
    
    if ( m_config_debug )
      printf( "    Output ROOT file (with fit results) closed.\n" );
    delete m_outputFile;
    m_outputFile = 0;
  }
  delete m_workSpace;
}

//=============================================================================
