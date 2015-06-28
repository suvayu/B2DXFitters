/*****************************************************************************
 * Project: RooFit                                                           *
 *                                                                           *
  * This code was autogenerated by RooClassFactory                            * 
 *****************************************************************************/

#ifndef TAGDLLTOTAGDEC_H
#define TAGDLLTOTAGDEC_H

#include "RooAbsCategory.h"
#include "RooRealProxy.h"
#include "RooListProxy.h"
class RooAbsReal;
class RooArgList;
 
class TagDLLToTagDec : public RooAbsCategory {
public:
  TagDLLToTagDec() {} ; 
  TagDLLToTagDec(const char *name, const char *title,
	      RooAbsReal& _dll);
  TagDLLToTagDec(const char *name, const char *title,
	      RooAbsReal& _dll, RooArgList& _indecisions);
  TagDLLToTagDec(const TagDLLToTagDec& other, const char* name=0) ;
  virtual TObject* clone(const char* newname) const { return new TagDLLToTagDec(*this,newname); }
  virtual ~TagDLLToTagDec();

protected:

  RooRealProxy dll;
  RooListProxy indecisions;
  
  RooCatType evaluate() const;

private:
  ClassDef(TagDLLToTagDec, 1);
};
 
#endif
