//---------------------------------------------------------------------------//
//                                                                           //
//  General RooFit models                                                    //
//                                                                           //
//  Source file                                                              //
//                                                                           //
//  Authors: Eduardo Rodrigues                                               //
//  Date   : 19 / 05 / 2011                                                  //
//                                                                           //
//---------------------------------------------------------------------------//

// STL includes
#include <cassert>


// ROOT and RooFit includes
#include "RooGlobalFunc.h"
#include "RooArgSet.h"
#include "RooAddPdf.h"
#include "RooProdPdf.h"
#include "RooExtendPdf.h"
#include "RooEffProd.h"
#include "RooGaussian.h"
#include "RooDecay.h"
#include "RooBDecay.h"
#include "RooCBShape.h"
#include "RooWorkspace.h"

// B2DXFitters includes
#include "B2DXFitters/GeneralModels.h"
#include "B2DXFitters/Inverse.h"


namespace GeneralModels {

  //===========================================================================
  // Build a Gaussian PDF named "mpdf<prefix>"
  // (assumes this PDF is always in mass, therefore the "mpdf" ;-))
  // "prefix" uniquely identifies the decay mode, e.g. "Bs2DsPi"
  // "bName" identifies the B-meson name
  //===========================================================================
  RooAbsPdf* buildGaussianPDF( RooAbsReal& obs,
                               double mean,
                               double sigma,
                               const char* prefix,
                               const char* bName,
                               bool debug
                               )
  {
    if ( debug )
      printf( "==> GeneralModels::buildGaussianPDF( ... )\n" );
    
    RooRealVar* meanVar = new RooRealVar( Form( "mpdf%s_mean", prefix ),
                                          Form( "'%s' %s Gaussian PDF in %s - mean",
                                                prefix, bName, obs.GetName() ),
                                          mean, 5000., 5600., "MeV/c^{2}"
                                          );
    
    RooRealVar* sigmaVar = new RooRealVar( Form( "mpdf%s_sigma", prefix ),
                                           Form( "'%s' %s Gaussian PDF in %s - sigma",
                                                 prefix, bName, obs.GetName() ),
                                           sigma, 0., 50, "MeV/c^{2}"
                                           );
    
    RooGaussian* pdf = new RooGaussian( Form( "mpdf%s", prefix ),
                                        Form( "'%s' %s Gaussian PDF in %s",
                                              prefix, bName, obs.GetName() ),
                                        obs, *meanVar, *sigmaVar
                                        );
    
    return pdf;
  }

  //===========================================================================
  // Build a Gaussian extended PDF named "mepdf<prefix>"
  // (assumes this PDF is always in mass, therefore the "mepdf" ;-))
  // "prefix" uniquely identifies the decay mode, e.g. "Bs2DsPi"
  // "bName" identifies the B-meson name
  //===========================================================================
  RooAbsPdf* buildGaussianEPDF( RooAbsReal& obs,
                                double mean,
                                double sigma,
                                RooRealVar& nEvents,
                                const char* prefix,
                                const char* bName,
                                bool debug
                                )
  {
    if ( debug )
      printf( "==> GeneralModels::buildGaussianEPDF( ... )\n" );

    RooAbsPdf* pdf = buildGaussianPDF( obs, mean, sigma,
                                       prefix, bName,
                                       debug
                                       );

    RooExtendPdf* epdf = new RooExtendPdf( Form( "mepdf%s", prefix ),
                                           Form( "'%s' %s Gaussian EPDF in %s",
                                                 prefix, bName, obs.GetName() ),
                                           *pdf, nEvents
                                           );

    return epdf;
  }

  //===========================================================================
  // Build a RooDecay PDF named "tpdf<prefix>"
  // (assumes this PDF is always in time, therefore the "tpdf" ;-))
  // "prefix" uniquely identifies the decay mode, e.g. "Bs2DsPi"
  // "bName" identifies the B-meson name
  //===========================================================================
  RooAbsPdf* buildRooDecayPDF( RooAbsReal& time,
                               RooRealVar& Gamma,
                               RooResolutionModel* resModel,
                               RooAbsReal* acceptance,
                               const char* prefix,
                               const char* bName,
                               bool debug
                               )
  {
    if ( debug )
      printf( "==> GeneralModels::buildRooDecayPDF( ... )\n" );

    if ( ! resModel ) {
      printf( "[ERROR] No propertime resolution model set!\n" );
      exit( -1 );
    }

    // Create a local workspace
    RooWorkspace* workSpace = new RooWorkspace( "LocalRDWS", kTRUE );

    bool error_t  = workSpace -> import( time      );
    bool error_rm = workSpace -> import( *resModel );
    if ( error_t || error_rm ) {
      printf( "[ERROR] Time observable or resolution model failed to be imported to the local workspace!\n" );
      exit( -1 );
    }

    RooRealVar* new_time = workSpace -> var( time.GetName() );
    RooResolutionModel* new_resModel =
      dynamic_cast<RooResolutionModel*>( &( workSpace -> allResolutionModels()[ resModel -> GetName() ] ) );

    Inverse tau( Form( "tpdf%s_tau", prefix ), Form( "tpdf%s_tau", prefix ), Gamma );
    RooAbsPdf* pdf_noAcc =
      new RooDecay( Form( "tpdf%s_noAcc", prefix ),
                    Form( "'%s' %s PDF in %s (without acc.)",
                          prefix, bName, time.GetName() ),
                    *new_time,
                    tau,
                    *new_resModel,
                    RooDecay::SingleSided
                    );

    // Include the acceptance function if non NULL:
    // PDF -> PDF * acceptance
    if ( acceptance ) {
      RooAbsPdf* pdf_acc = new RooEffProd( Form( "tpdf%s", prefix ),
                                           Form( "'%s' %s PDF in %s (with acc.)",
                                                 prefix, bName, time.GetName() ),
                                           *pdf_noAcc, *acceptance
                                           );
      bool error = workSpace -> import( *pdf_acc );
      if ( error ) {
        printf( "[ERROR] PDF with acc. failed to be imported to the local workspace!\n" );
        exit( -1 );
      }
      return workSpace -> pdf( Form( "tpdf%s", prefix ) );
    }
    else {
      bool error = workSpace -> import( *pdf_noAcc );
      if ( error ) {
        printf( "[ERROR] PDF without acc. failed to be imported to the local workspace!\n" );
        exit( -1 );
      }
      return workSpace -> pdf( Form( "tpdf%s_noAcc", prefix ) );
    }
  }

  //===========================================================================
  // Build a RooDecay extended PDF named "tepdf<prefix>"
  // (assumes this PDF is always in time, therefore the "tepdf" ;-))
  // "prefix" uniquely identifies the decay mode, e.g. "Bs2DsPi"
  // "bName" identifies the B-meson name
  //===========================================================================
  RooAbsPdf* buildRooDecayEPDF( RooAbsReal& time,
                                RooRealVar& Gamma,
                                RooResolutionModel* resModel,
                                RooAbsReal* acceptance,
                                RooRealVar& nEvents,
                                const char* prefix,
                                const char* bName,
                                bool debug
                                )
  {
    if ( debug )
      printf( "==> GeneralModels::buildRooDecayEPDF( ... )\n" );

    RooAbsPdf* pdf = buildRooDecayPDF( time, Gamma,
                                       resModel, acceptance,
                                       prefix, bName,
                                       debug
                                       );

    RooExtendPdf* epdf = new RooExtendPdf( Form( "tepdf%s", prefix ),
                                           Form( "'%s' %s EPDF in %s (%s acc.)",
                                                 prefix, bName, time.GetName(),
                                                 acceptance == NULL ? "without" : "with" ),
                                           *pdf, nEvents
                                           );
    return epdf;
  }

  //===========================================================================
  // Build a RooBDecay PDF named "tpdf<prefix>" with a resolution model with
  // per-event decay time errors
  // (assumes this PDF is always in time, therefore the "tpdf" ;-))
  // "prefix" uniquely identifies the decay mode, e.g. "Bs2DsPi"
  // "bName" identifies the B-meson name
  //===========================================================================
  RooAbsPdf* buildRooBDecayPDFWithPEDTE( RooAbsReal& time,
                                         RooAbsReal* timeerr,
                                         RooAbsReal& Gamma,
                                         RooAbsReal& deltaGamma,
                                         RooAbsReal& deltaM,
                                         RooAbsReal& cosh,
                                         RooAbsReal& sinh,
                                         RooAbsReal& cos,
                                         RooAbsReal& sin,
                                         RooAbsPdf*  timeerrPdf,
                                         RooResolutionModel* resModel,
                                         RooAbsReal* acceptance,
                                         const char* prefix,
                                         const char* bName,
                                         bool debug
                                         )
  {
    if ( debug )
      printf( "==> GeneralModels::buildRooBDecayPDFWithPEDTE( ... )\n" );

    if ( ! resModel ) {
      printf( "[ERROR] No decay time resolution model set!\n" );
      exit( -1 );
    }
    
    if ((timeerr && !timeerrPdf) || (!timeerr && timeerrPdf)) {
      printf( "[ERROR] timeerr and timeerrPdf must either be both NULL or both non-NULL!\n" );
      exit( -1 );
    }

    // Create a local workspace
    RooWorkspace* workSpace = new RooWorkspace( "LocalRBDWSWithPEDTE" );

    bool error_rm    = workSpace -> import( *resModel   );
    bool error_tepdf = !timeerrPdf ? false : workSpace -> import( *timeerrPdf );
    if ( error_rm || error_tepdf ) {
      printf( "[ERROR] Time/time error obs. or res. model or time error PDF failed to be imported to the local workspace!\n" );
      exit( -1 );
    }

    RooRealVar* new_time = workSpace -> var( time.GetName() );
    assert(*new_time == time);
    RooResolutionModel* new_resModel =
      dynamic_cast<RooResolutionModel*>( &( workSpace -> allResolutionModels()[ resModel -> GetName() ] ) );
    assert(new_resModel == resModel);
    RooAbsPdf* new_timeerrPdf = !timeerrPdf ? timeerrPdf :
      dynamic_cast<RooAbsPdf*>( &( workSpace -> allPdfs()[ timeerrPdf -> GetName() ] ) );
    assert(new_timeerrPdf == timeerrPdf);

    Inverse tau( Form( "tpdf%s_tau", prefix ), Form( "tpdf%s_tau", prefix ), Gamma );

    RooBDecay* pdf_bdecay =
      new RooBDecay( Form( "tpdf%s_bdecay", prefix ),
                     Form( "'%s' %s PDF in %s (B-decay part)",
                           prefix, bName, time.GetName() ),
                     *new_time,
                     tau, deltaGamma,
                     cosh, sinh,
                     cos, sin,
                     deltaM,
                     *new_resModel,
                     RooBDecay::SingleSided
                     );

    RooAbsPdf* pdf_noAcc = !timeerrPdf ? dynamic_cast<RooAbsPdf*>(pdf_bdecay) :
      dynamic_cast<RooAbsPdf*>(
	      new RooProdPdf( Form( "tpdf%s_noAcc", prefix ),
                      Form( "'%s' %s PDF in %s (without acc.)",
                            prefix, bName, time.GetName() ),
                      RooArgSet(*new_timeerrPdf),
                      RooFit::Conditional( RooArgSet(*pdf_bdecay),
                                           RooArgSet(*new_time)
                                           )
                      ));

    // Include the acceptance function if non NULL:
    // PDF -> PDF * acceptance
    if ( acceptance ) {
      RooAbsPdf* pdf_acc = new RooEffProd( Form( "tpdf%s", prefix ),
                                           Form( "'%s' %s PDF in %s (with acc.)",
                                                 prefix, bName, time.GetName() ),
                                           *pdf_noAcc, *acceptance
                                           );
      bool error = workSpace -> import( *pdf_acc );
      if ( error ) {
        printf( "[ERROR] PDF with acc. failed to be imported to the local workspace!\n" );
        exit( -1 );
      }
      return workSpace -> pdf( pdf_acc->GetName() );
    } else {
      bool error = workSpace -> import( *pdf_noAcc );
      if ( error ) {
        printf( "[ERROR] PDF without acc. failed to be imported to the local workspace!\n" );
        exit( -1 );
      }
      return workSpace -> pdf( pdf_noAcc->GetName() );
    }
  }

  //===========================================================================
  // Build a RooBDecay PDF named "tpdf<prefix>" with a resolution model with
  // per-event decay time errors
  // (assumes this PDF is always in time, therefore the "tpdf" ;-))
  // "prefix" uniquely identifies the decay mode, e.g. "Bs2DsPi"
  // "bName" identifies the B-meson name
  //===========================================================================
  RooAbsPdf* buildRooBDecayPDFWithPEDTE( RooAbsReal& time,
                                         RooAbsReal& timeerr,
                                         RooAbsReal& Gamma,
                                         RooAbsReal& deltaGamma,
                                         RooAbsReal& deltaM,
                                         RooAbsReal& cosh,
                                         RooAbsReal& sinh,
                                         RooAbsReal& cos,
                                         RooAbsReal& sin,
                                         RooAbsPdf*  timeerrPdf,
                                         RooResolutionModel* resModel,
                                         RooAbsReal* acceptance,
                                         const char* prefix,
                                         const char* bName,
                                         bool debug
	  )
  {
      if ( ! timeerrPdf ) {
	  printf( "[ERROR] No decay time error PDF set!\n" );
	  exit( -1 );
      }
      return buildRooBDecayPDFWithPEDTE( time, &timeerr, Gamma, deltaGamma,
	      deltaM, cosh, sinh, cos, sin, timeerrPdf, resModel, acceptance,
	      prefix, bName, debug);
  }

  //===========================================================================
  // Build a RooBDecay PDF named "tpdf<prefix>"
  // (assumes this PDF is always in time, therefore the "tpdf" ;-))
  // "prefix" uniquely identifies the decay mode, e.g. "Bs2DsPi"
  // "bName" identifies the B-meson name
  //===========================================================================
  RooAbsPdf* buildRooBDecayPDF( RooAbsReal& time,
                                RooAbsReal& Gamma,
                                RooAbsReal& deltaGamma,
                                RooAbsReal& deltaM,
                                RooAbsReal& cosh,
                                RooAbsReal& sinh,
                                RooAbsReal& cos,
                                RooAbsReal& sin,
                                RooResolutionModel* resModel,
                                RooAbsReal* acceptance,
                                const char* prefix,
                                const char* bName,
                                bool debug
                                )
  {
    return buildRooBDecayPDFWithPEDTE(time, (RooAbsReal*)0, Gamma, deltaGamma,
	    deltaM, cosh, sinh, cos, sin, 0, resModel, acceptance, prefix,
	    bName, debug);
  }

  //===========================================================================
  // Build a RooBDecay extended PDF named "tepdf<prefix>"
  // (assumes this PDF is always in time, therefore the "tepdf" ;-))
  // "prefix" uniquely identifies the decay mode, e.g. "Bs2DsPi"
  // "bName" identifies the B-meson name
  //===========================================================================
  RooAbsPdf* buildRooBDecayEPDF( RooAbsReal& time,
                                 RooAbsReal& Gamma,
                                 RooAbsReal& deltaGamma,
                                 RooAbsReal& deltaM,
                                 RooAbsReal& cosh,
                                 RooAbsReal& sinh,
                                 RooAbsReal& cos,
                                 RooAbsReal& sin,
                                 RooResolutionModel* resModel,
                                 RooAbsReal* acceptance,
                                 RooAbsReal& nEvents,
                                 const char* prefix,
                                 const char* bName,
                                 bool debug
                                 )
  {
    if ( debug )
      printf( "==> GeneralModels::buildRooBDecayEPDF( ... )\n" );

    RooAbsPdf* pdf = buildRooBDecayPDF( time, Gamma, deltaGamma, deltaM,
                                        cosh, sinh, cos, sin,
                                        resModel, acceptance,
                                        prefix, bName,
                                        debug
                                        );

    RooExtendPdf* epdf = new RooExtendPdf( Form( "tepdf%s", prefix ),
                                           Form( "'%s' %s EPDF in %s (%s acc.)",
                                                 prefix, bName, time.GetName(),
                                                 acceptance == NULL ? "without" : "with" ),
                                           *pdf, nEvents
                                           );
    return epdf;
  }

  //===========================================================================
  // Build a Double Crystal Ball PDF named "mpdf<prefix>"
  // (assumes this PDF is always in mass, therefore the "mpdf" ;-))
  // "prefix" uniquely identifies the decay mode, e.g. "Bs2DsPi"
  // "bName" identifies the B-meson name
  //===========================================================================
  RooAbsPdf* buildDoubleCBPDF( RooAbsReal& obs,
                               double mean,
                               double sigma1,
                               double alpha1,
                               double n1,
                               double sigma2,
                               double alpha2,
                               double n2,
                               double frac,
                               const char* prefix,
                               const char* bName,
                               bool debug
                               )
  {
    if ( debug )
      printf( "==> GeneralModels::buildDoubleCBPDF( ... )\n" );

    RooRealVar* meanVar = new RooRealVar( Form( "mpdf%s_mean", prefix ),
                                          Form( "'%s' %s DbleCB PDF in %s - mean",
                                                prefix, bName, obs.GetName() ),
                                          mean, 5000., 5600., "MeV/c^{2}"
                                          );

    RooRealVar* sigma1Var = new RooRealVar( Form( "mpdf%s_sigma1", prefix ),
                                            Form( "'%s' %s DblCB PDF in %s - sigma1",
                                                  prefix, bName, obs.GetName() ),
                                            sigma1, 0., 50., "MeV/c^{2}"
                                            );

    RooRealVar* sigma2Var = new RooRealVar( Form( "mpdf%s_sigma2", prefix ),
                                            Form( "'%s' %s DblCB PDF in %s - sigma2",
                                                  prefix, bName, obs.GetName() ),
                                            sigma2, 0., 50., "MeV/c^{2}"
                                            );

    RooRealVar* alpha1Var = new RooRealVar( Form( "mpdf%s_alpha1", prefix ),
                                            Form( "'%s' %s DblCB PDF in %s - alpha1",
                                                  prefix, bName, obs.GetName() ),
                                            alpha1, 0., 5.
                                            );

    RooRealVar* alpha2Var = new RooRealVar( Form( "mpdf%s_alpha2", prefix ),
                                            Form( "'%s' %s DblCB PDF in %s - alpha2",
                                                  prefix, bName, obs.GetName() ),
                                            alpha2, -5., 0.
                                            );

    RooRealVar* n1Var = new RooRealVar( Form( "mpdf%s_n1", prefix ),
                                        Form( "'%s' %s DblCB PDF in %s - n1",
                                              prefix, bName, obs.GetName() ),
                                        n1, 0., 5.
                                        );

    RooRealVar* n2Var = new RooRealVar( Form( "mpdf%s_n2", prefix ),
                                        Form( "'%s' %s DblCB PDF in %s - n2",
                                              prefix, bName, obs.GetName() ),
                                        n2, 0., 5.
                                        );

    RooRealVar* fracVar = new RooRealVar( Form( "mpdf%s_frac", prefix ),
                                          Form( "'%s' %s DblCB PDF in %s - frac",
                                                prefix, bName, obs.GetName() ),
                                          frac, 0., 1.
                                          );

    RooCBShape* pdf1 = new RooCBShape( Form( "mpdf%s_CB1", prefix ),
                                       Form( "'%s' %s CB1 PDF in %s",
                                             prefix, bName, obs.GetName() ),
                                       obs,
                                       *meanVar, *sigma1Var, *alpha1Var, *n1Var
                                       );

    RooCBShape* pdf2 = new RooCBShape( Form( "mpdf%s_CB2", prefix ),
                                       Form( "'%s' %s CB2 PDF in %s",
                                             prefix, bName, obs.GetName() ),
                                       obs,
                                       *meanVar, *sigma2Var, *alpha2Var, *n2Var
                                       );

    RooAddPdf* pdf = new RooAddPdf( Form( "mpdf%s", prefix ),
                                    Form( "'%s' %s DbleCB PDF in %s",
                                          prefix, bName, obs.GetName() ),
                                    *pdf1, *pdf2, *fracVar
                                    );

    return pdf;
  }

  //===========================================================================
  // Build a Double Crystal Ball extended PDF named "mepdf<prefix>"
  // (assumes this PDF is always in mass, therefore the "mepdf" ;-))
  // "prefix" uniquely identifies the decay mode, e.g. "Bs2DsPi"
  // "bName" identifies the B-meson name
  //===========================================================================
  RooAbsPdf* buildDoubleCBEPDF( RooAbsReal& obs,
                                double mean,
                                double sigma1,
                                double alpha1,
                                double n1,
                                double sigma2,
                                double alpha2,
                                double n2,
                                double frac,
                                RooRealVar& nEvents,
                                const char* prefix,
                                const char* bName,
                                bool debug
                                )
  {
    if ( debug )
      printf( "==> GeneralModels::buildDoubleCBEPDF( ... )\n" );

    RooAbsPdf* pdf = buildDoubleCBPDF( obs,
                                       mean,
                                       sigma1,
                                       alpha1,
                                       n1,
                                       sigma2,
                                       alpha2,
                                       n2,
                                       frac,
                                       prefix,
                                       bName,
                                       debug
                                       );

    RooExtendPdf* epdf = new RooExtendPdf( Form( "mepdf%s", prefix ),
                                           Form( "'%s' %s DbleCB EPDF in %s",
                                                 prefix, bName, obs.GetName() ),
                                           *pdf, nEvents
                                           );

    return epdf;
  }

  //===========================================================================
  // Build a RooKeysPdf PDF named "mpdf<prefix>"
  // (assumes this PDF is always in mass, therefore the "mpdf" ;-))
  // "mirror" and "rho" are RooKeysPdf's parameters, see class documentation
  // "prefix" uniquely identifies the decay mode, e.g. "Bs2DsPi"
  // "bName" identifies the B-meson name
  //===========================================================================
  RooAbsPdf* buildKeysPDF( RooAbsReal& obs,
                           RooDataSet& dataset,
                           RooKeysPdf::Mirror mirror,
                           double rho,
                           const char* prefix,
                           const char* bName,
                           bool debug
                           )
  {
    if ( debug )
      printf( "==> GeneralModels::buildKeysPDF( obs=%s, dataset=%s )\n",
              obs.GetName(), dataset.GetName() );
    
    return new RooKeysPdf( Form( "mpdf%s", prefix ),
                           Form( "'%s' %s Keys PDF in %s",
                                 prefix, bName, obs.GetName() ),
                           obs, dataset,
                           mirror, rho
                           );
  }
  
} // end of namespace

//=============================================================================
