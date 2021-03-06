/*****************************************************************************
 * Project: RooFit                                                           *
 *                                                                           *
  * This code was autogenerated by RooClassFactory                            * 
 *****************************************************************************/

#ifndef TAGDLLTOTAGETA_H
#define TAGDLLTOTAGETA_H

#include "RooAbsReal.h"
#include "RooRealProxy.h"
 
class TagDLLToTagEta : public RooAbsReal {
public:
  TagDLLToTagEta() {} ; 
  TagDLLToTagEta(const char *name, const char *title,
	      RooAbsReal& _dll);
  TagDLLToTagEta(const TagDLLToTagEta& other, const char* name=0) ;
  virtual TObject* clone(const char* newname) const { return new TagDLLToTagEta(*this,newname); }
  virtual ~TagDLLToTagEta();

protected:

  RooRealProxy dll;
  
  Double_t evaluate() const;

private:
  ClassDef(TagDLLToTagEta, 1);
};
 
#endif
