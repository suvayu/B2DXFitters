/***************************************************************************** 
 * Project: RooFit                                                           * 
 *                                                                           * 
 * This code was autogenerated by RooClassFactory                            * 
 *****************************************************************************/ 

// Your description goes here... 
#include <cassert>
#include "Riostream.h" 

#include "B2DXFitters/DLLTagCombiner.h" 
#include "RooAbsReal.h" 
#include "RooAbsCategory.h" 

DLLTagCombiner::DLLTagCombiner(const char *name, const char *title, 
		const RooArgList& _tagdecisions,
		const RooArgList& _tagomegas) :
    RooAbsReal(name,title), 
    tagdecisions("tagdecisions", "tagdecisions", this),
    tagomegas("tagomegas", "tagomegas", this)
{ 
    assert(_tagdecisions.getSize() == _tagomegas.getSize());
    assert(_tagdecisions.getSize() <= NMAX);
    RooFIter it = _tagdecisions.fwdIterator();
    for (RooAbsArg* obj = it.next(); obj; obj = it.next())
	tagdecisions.add(*obj);
    it = _tagomegas.fwdIterator();
    for (RooAbsArg* obj = it.next(); obj; obj = it.next())
	tagomegas.add(*obj);
} 


DLLTagCombiner::DLLTagCombiner(const DLLTagCombiner& other, const char* name) :  
    RooAbsReal(other,name), 
    tagdecisions("tagdecisions", this, other.tagdecisions),
    tagomegas("tagomegas", this, other.tagomegas),
    combiner(other.combiner)
{ 
    assert(tagdecisions.getSize() == tagomegas.getSize());
    assert(tagdecisions.getSize() <= NMAX);
} 

DLLTagCombiner::~DLLTagCombiner() { }


Double_t DLLTagCombiner::evaluate() const 
{
    TagTools::TagCombiner<NMAX>::DLLVector dllvect;
    for (unsigned i = 0; i < unsigned(tagdecisions.getSize()); ++i) {
	const int dec = int(dynamic_cast<RooAbsCategory&>(
		    *tagdecisions.at(i)).getIndex());
	const double omega = double(dynamic_cast<RooAbsReal&>(
		    *tagomegas.at(i)).getVal());
	dllvect[i] = TagTools::tagDLL(
		static_cast<TagTools::TagDec>(
		    (dec > 0) ? 1 : ((dec < 0) ? -1 : 0)), omega);
    }
    return combiner.combine(dllvect);
}
