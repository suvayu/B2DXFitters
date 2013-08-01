#include <RooResolutionModel.h>
#include "B2DXFitters/RooAbsEffResModel.h"

//_____________________________________________________________________________
RooAbsEffResModel::RooAbsEffResModel(const char *name, const char *title, RooRealVar& __convVar) 
   : RooResolutionModel(name, title, __convVar)
{ }

//_____________________________________________________________________________
RooAbsEffResModel::RooAbsEffResModel(const RooAbsEffResModel& other, const char* name) 
  : RooResolutionModel(other, name)
{ }

RooAbsEffResModel::~RooAbsEffResModel()
{ }
