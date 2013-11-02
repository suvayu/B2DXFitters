/*****************************************************************************
 * Project: RooFit                                                           *
 * Package: RooFitModels                                                     *
 *    File: $Id: RooGaussModel.h,v 1.21 2007/05/11 09:13:07 verkerke Exp $
 * Authors:                                                                  *
 *
 * Redistribution and use in source and binary forms,                        *
 * with or without modification, are permitted according to the terms        *
 * listed in LICENSE (http://roofit.sourceforge.net/license.txt)             *
 *****************************************************************************/
#ifndef ROO_ABS_EFF_RES_MODEL
#define ROO_ABS_EFF_RES_MODEL

#include "RooArgSet.h"
class RooAbsReal;

class RooAbsEffResModel {
public:
   // Constructors, assignment etc
   virtual ~RooAbsEffResModel();
  
   /** 
    * Get a RooArgSet of all observables
    * (pointer because genreflex dictionaries can't handle value)
    * @return RooArgSet of observables
    */
   virtual RooArgSet* observables() const = 0;

   virtual const RooAbsReal* efficiency() const = 0;

};

#endif
