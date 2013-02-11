//---------------------------------------------------------------------------//
//                                                                           //
//  General RooFit models                                                    //
//                                                                           //
//  Header file                                                              //
//                                                                           //
//  Authors: Eduardo Rodrigues                                               //
//  Date   : 19 / 05 / 2011                                                  //
//                                                                           //
//---------------------------------------------------------------------------//

#ifndef GENERALMODELS_H
#define GENERALMODELS_H 1

// STL includes

// ROOT and RooFit includes
#include "RooRealVar.h"
#include "RooAbsPdf.h"
#include "RooKeysPdf.h"
#include "RooResolutionModel.h"
#include "RooDataSet.h"

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
                               const char* prefix = "Sig",
                               const char* bName = "B_{d}",
                               bool debug = false
                               );
  
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
                                const char* prefix = "Sig",
                                const char* bName = "B_{d}",
                                bool debug = false
                                );
  
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
                               const char* prefix = "Sig",
                               const char* bName = "B_{d}",
                               bool debug = false
                               );
  
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
                                const char* prefix = "Sig",
                                const char* bName = "B_{d}",
                                bool debug = false
                                );

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
                                const char* prefix = "Sig",
                                const char* bName = "B_{d}",
                                bool debug = false
                                );
  
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
                                         const char* prefix = "Sig",
                                         const char* bName = "B_{d}",
                                         bool debug = false
                                         );
  
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
                                 const char* prefix = "Sig",
                                 const char* bName = "B_{d}",
                                 bool debug = false
                                 );
  
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
                               const char* prefix = "Sig",
                               const char* bName = "B_{d}",
                               bool debug = false
                               );
  
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
                                const char* prefix = "Sig",
                                const char* bName = "B_{d}",
                                bool debug = false
                                );

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
                                         const char* prefix = "Sig",
                                         const char* bName = "B_{d}",
                                         bool debug = false
                                         );

  //===========================================================================
  // Build a RooKeysPdf PDF named "mpdf<prefix>"
  // (assumes this PDF is always in mass, therefore the "mpdf" ;-))
  // "mirror" and "rho" are RooKeysPdf's parameters, see class documentation
  // "prefix" uniquely identifies the decay mode, e.g. "Bs2DsPi"
  // "bName" identifies the B-meson name
  //===========================================================================
  RooAbsPdf* buildKeysPDF( RooAbsReal& obs,
                           RooDataSet& dataset,
                           RooKeysPdf::Mirror mirror = RooKeysPdf::MirrorBoth,
                           double rho = 1.,
                           const char* prefix = "Sig",
                           const char* bName = "B_{d}",
                           bool debug = false
                           );
  
} // end of namespace

//=============================================================================

#endif  // GENERALMODELS_H
