//---------------------------------------------------------------------------//
//                                                                           //
//  Propertime resolution models for Bx -> Dx h                              //
//                                                                           //
//  Source file                                                              //
//                                                                           //
//  Authors: Eduardo Rodrigues                                               //
//  Date   : 19 / 05 / 2011                                                  //
//                                                                           //
//---------------------------------------------------------------------------//

// STL includes


// ROOT and RooFit includes
#include "RooAddModel.h"
#include "RooGaussModel.h"
#include "RooWorkspace.h"

// B2DXFitters includes
#include "B2DXFitters/PropertimeResolutionModels.h"


namespace PTResModels {
  
  //=============================================================================
  // Helper function returning a resolution model by name
  // Implemented models:
  //   "truth"          --> RooTruthModel
  //   "Gaussian"       --> RooGaussModel
  //   "DoubleGaussian" --> RooAddModel of 2 RooGaussModel
  //=============================================================================
  RooResolutionModel* getPTResolutionModel( const char* modelName,
                                            RooRealVar& time,
                                            const char* prefix,
                                            bool debug,
                                            double scalingfactor,
                                            double biasonmean
                                            )
  {
    if ( debug )
      printf( "==> PTResModels::getPTResolutionModel( %s, %s )\n",
              modelName, prefix );
    
    // Create a local workspace
    RooWorkspace* workSpace = new RooWorkspace( "PTResModelsWS", kTRUE );
    
    Bool_t error = workSpace -> import( time );
    if ( error ) {
      printf( "[ERROR] Time observable failed to be imported to the local workspace!\n" );
      exit( -1 );
    }

    if      ( strcmp( modelName, "truth" ) == 0 ) {
      printf( "    Using a \"RooTruthModel\" for the '%s' propertime resolution.\n", prefix );
      workSpace -> factory( Form( "TruthModel::%sTruthPTRM(%s)",
                                  prefix, time.GetName() ) );
      return dynamic_cast<RooResolutionModel*>( &(workSpace -> allResolutionModels()[ Form( "%sTruthPTRM", prefix ) ] ) );
    }
    else if ( strcmp( modelName, "Gaussian" ) == 0 ) {
      printf( "    Using a \"RooGaussModel\" for the '%s' propertime resolution.\n", prefix );
      RooRealVar* singlegausmean  = new RooRealVar("MeanSingleGaus","MeanSingleGaus",0.0+biasonmean);
      RooRealVar* singlegauswidth = new RooRealVar("WidthSingleGaus","WidthSingleGaus",0.050*scalingfactor);  
      RooGaussModel* singlegausmodel = new RooGaussModel("PTRMGaussian_signal","PTRMGaussian_signal",time, *singlegausmean, *singlegauswidth);
      return singlegausmodel;
      //workSpace -> factory( Form( "GaussModel::%sGaussianPTRM(%s,%sGaussianPTRM_mean[0],%sGaussianPTRM_sigma[0.050])",
      //                            prefix, time.GetName(), prefix, prefix ) );
      //return dynamic_cast<RooResolutionModel*>( &( workSpace -> allResolutionModels()[ Form( "%sGaussianPTRM", prefix ) ] ) );
    }
    else if ( strcmp( modelName, "DoubleGaussian" ) == 0 ) {
      printf( "    Using a double Gaussian model with fixed parameters.\n" );
      workSpace ->
        factory( Form( "AddModel::%sDoubleGaussianPTRM("
                       "{GaussModel(%s,%sDoubleGaussianPTRM_bias[0],%sDoubleGaussianPTRM_sigma1[0.0311]),"
                       "GaussModel(%s,%sDoubleGaussianPTRM_bias[0],%sDoubleGaussianPTRM_sigma2[0.0592])},"
                       "%sDoubleGaussianPTRM_frac1[0.442])",
                       prefix, time.GetName(), prefix, prefix, time.GetName(), prefix, prefix, prefix ) );
      return
        dynamic_cast<RooResolutionModel*>( &( workSpace -> allResolutionModels()[ Form( "%sDoubleGaussianPTRM", prefix ) ] ) );
    }
    else if ( strcmp( modelName, "TripleGaussian") == 0 ) {
      printf( "    Using a triple Gaussian model with fixed parameters.\n" );
      return tripleGausResolutionModel(time,true,true,true,false,scalingfactor,biasonmean); 
    }
    else {
      printf( "[ERROR] The specified PT resolution model \"%s\" is not recognised!\n",
              modelName );
      return NULL;
    }
  }
  
  //=============================================================================
  // 
  //=============================================================================
  RooResolutionModel* tripleGausResolutionModel( RooRealVar& time,
                                                 bool fixparameters,
                                                 bool fixfractions,
                                                 bool extended,
                                                 bool debug,
                                                 double scalingfactor,  
                                                 double biasonmean
                                                 )
  {
    if ( debug )
      printf( "==> PTResModels::tripleGausResolutionModel( .)\n" );

    RooRealVar  *bias;
    RooRealVar *FractionGaus1;
    RooRealVar *FractionGaus2;
    RooRealVar *FractionGaus3;
    RooRealVar *WidthGaus1;
    RooRealVar *WidthGaus2;
    RooRealVar *WidthGaus3;
    // values come from the proper time calibration
    
    if(!fixfractions){
      FractionGaus1= new RooRealVar("FractionGaus1",   "FractionGaus1",  0.325  ,     0.1,     0.9);
      FractionGaus2= new RooRealVar("FractionGaus2",   "FractionGaus2",  0.664  ,     0.1,     0.9);
      FractionGaus3= new RooRealVar("FractionGaus3",   "FractionGaus3",  1-0.989,    0.01,    0.10);
    }
    else{
      FractionGaus1= new RooRealVar("FractionGaus1",   "FractionGaus1",  0.595   );
      FractionGaus2= new RooRealVar("FractionGaus2",   "FractionGaus2",  0.386);
      FractionGaus3= new RooRealVar("FractionGaus3",   "FractionGaus3",  0.02 );
    }
    if(!fixparameters){
      bias      = new RooRealVar(      "bias",            "bias",     0.0,   -0.01,    0.01);
      WidthGaus1= new RooRealVar("WidthGaus1",      "WidthGaus1",  0.0257,    0.01,    0.04);
      WidthGaus2= new RooRealVar("WidthGaus2",      "WidthGaus2",  0.0684,    0.04,    0.10);
      WidthGaus3= new RooRealVar("WidthGaus3",      "WidthGaus3",   0.273,    0.10,    0.40);
    }
    else{
      bias      = new RooRealVar(      "bias",            "bias",    -0.00149+biasonmean);
      WidthGaus1= new RooRealVar("WidthGaus1",      "WidthGaus1",  0.029*scalingfactor);
      WidthGaus2= new RooRealVar("WidthGaus2",      "WidthGaus2",  0.059*scalingfactor);
      WidthGaus3= new RooRealVar("WidthGaus3",      "WidthGaus3",   0.182*scalingfactor);
    }
    RooGaussModel *timeGausModel1 = new RooGaussModel("timeGausModel1","timeGausModel1",time,*bias,*WidthGaus1);
    RooGaussModel *timeGausModel2 = new RooGaussModel("timeGausModel2","timeGausModel2",time,*bias,*WidthGaus2);
    RooGaussModel *timeGausModel3 = new RooGaussModel("timeGausModel3","timeGausModel3",time,*bias,*WidthGaus3);
    
    RooAddModel * tripleGausModelResolution;
    if(extended){
      tripleGausModelResolution = new RooAddModel("tripleGausModelResolution","tripleGausModelResolution",
                                                  RooArgList(*timeGausModel1 , *timeGausModel2, *timeGausModel3),
                                                  RooArgList(*FractionGaus1, *FractionGaus2, *FractionGaus3)
                                                  );
    }
    else {
      tripleGausModelResolution = new RooAddModel("tripleGausModelResolution","tripleGausModelResolution",
                                                  RooArgList(*timeGausModel1 , *timeGausModel2, *timeGausModel3),
                                                  RooArgList(*FractionGaus1, *FractionGaus2)
                                                  );
    }
    return tripleGausModelResolution;
  }
  
}

//=============================================================================
