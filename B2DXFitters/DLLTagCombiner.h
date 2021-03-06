/*****************************************************************************
 * Project: RooFit                                                           *
 *                                                                           *
  * This code was autogenerated by RooClassFactory                            * 
 *****************************************************************************/

#ifndef DLLTAGCOMBINER_H
#define DLLTAGCOMBINER_H

#include "RooAbsReal.h"
#include "RooArgList.h"
#include "RooListProxy.h"

#include "TagCombiner.h"

class DLLTagCombiner : public RooAbsReal
{
    public:
	enum { NMAX = 5 };

	DLLTagCombiner() {} ; 
	DLLTagCombiner(const char *name, const char *title,
		const RooArgList& _tagdecisions,
		const RooArgList& _tagomegas);
	DLLTagCombiner(const DLLTagCombiner& other, const char* name=0) ;
	virtual TObject* clone(const char* newname) const { return new DLLTagCombiner(*this,newname); }
	virtual ~DLLTagCombiner();

    protected:
	RooListProxy tagdecisions;
	RooListProxy tagomegas;

	mutable TagTools::TagCombiner<NMAX> combiner; //! transient member

	Double_t evaluate() const;

    private:
	ClassDef(DLLTagCombiner, 1);
};
 
#endif
