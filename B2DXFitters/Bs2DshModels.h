//---------------------------------------------------------------------------//
//                                                                           //
//  RooFit models for Bs -> Ds h                                             //
//                                                                           //
//  Header file                                                              //
//                                                                           //
//  Authors: Eduardo Rodrigues                                               //
//  Date   : 24 / 05 / 2011                                                  //
//                                                                           //
//---------------------------------------------------------------------------//

#ifndef BS2DSHMODELS_H
#define BS2DSHMODELS_H 1

// STL includes

// ROOT and RooFit includes
#include "RooRealVar.h"
#include "RooStringVar.h"
#include "RooAbsPdf.h"


namespace Bs2DshModels {

  //===========================================================================
  // Extended PDF background models for Bs -> Ds pi as defined in the
  // Delta m_s analysis
  // - combinatorial backgroud
  // - physical backgrounds
  //===========================================================================
  RooAbsPdf* buildBsBackgroundEPDFInMass( RooAbsReal& m_obs_mass,
                                          RooStringVar& filesDir,
                                          RooRealVar& nCombBkgEvts,
                                          RooRealVar& nBd2DPiEvts,
                                          RooRealVar& nBs2DsRhoEvts,
                                          RooRealVar& nBs2DsstPiEvts,
                                          RooRealVar& nBs2DsXEvts,
                                          RooRealVar& nLb2LcPiEvts,
                                          bool debug = false
                                          );
  
} // end of namespace

//=============================================================================

#endif  // BS2DSHMODELS_H
