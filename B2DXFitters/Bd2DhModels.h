//---------------------------------------------------------------------------//
//                                                                           //
//  RooFit models for Bd -> D h                                              //
//                                                                           //
//  Header file                                                              //
//                                                                           //
//  Authors: Eduardo Rodrigues                                               //
//  Date   : 18 / 05 / 2011                                                  //
//                                                                           //
//---------------------------------------------------------------------------//

#ifndef BD2DHMODELS_H
#define BD2DHMODELS_H 1

// STL includes

// ROOT and RooFit includes
#include "RooRealVar.h"
#include "RooStringVar.h"
#include "RooAbsPdf.h"
#include "RooResolutionModel.h"


namespace Bd2DhModels {

  //=============================================================================
  // PDF background models for Bd -> D pi as defined in the
  // Delta m_d analysis
  // - combinatorial backgroud
  // - physical backgrounds
  //=============================================================================
  RooAbsPdf* buildBdBackgroundPDFInMass( RooAbsReal& m_obs_mass,
                                         RooStringVar& filesDir,
                                         const long fracCombBkgEvts,
                                         const long fracBd2DKEvts,
                                         const long fracBd2DstPiEvts,
                                         const long fracBd2DXEvts,
                                         bool debug = false
                                         );

  //=============================================================================
  // Extended PDF background models for Bd -> D pi as defined in the
  // Delta m_d analysis
  // - combinatorial backgroud
  // - physical backgrounds
  //=============================================================================  
  RooAbsPdf* buildBdBackgroundEPDFInMass( RooAbsReal& m_obs_mass,
                                          RooStringVar& filesDir,
                                          RooRealVar& nCombBkgEvts,
                                          RooRealVar& nBd2DKEvts,
                                          RooRealVar& nBd2DRhoEvts,
                                          RooRealVar& nBd2DstPiEvts,
                                          RooRealVar& nBd2DXEvts,
                                          bool debug = false
                                          );

  //===========================================================================
  // Extended PDF background models in time for Bd -> D pi as defined in the
  // Delta m_d analysis, when no tagging information is used
  // - combinatorial backgroud
  // - Bd -> D K physical background
  //===========================================================================
  RooAbsPdf* buildBdBackgroundNoTagEPDFInTime( RooAbsReal& time,
                                               RooRealVar& Gamma,
                                               RooRealVar& nCombBkgEvts,
                                               RooRealVar& CombBkgPTPdf_a,
                                               RooRealVar& CombBkgPTPdf_f,
                                               RooRealVar& CombBkgPTPdf_alpha,
                                               RooRealVar& CombBkgPTPdf_beta,
                                               RooRealVar& nBd2DKEvts,
                                               RooResolutionModel* resModel,
                                               RooAbsReal* acceptance,
                                               bool debug = false
                                               );
  
} // end of namespace

//=============================================================================

#endif  // BD2DHMODELS_H
 
