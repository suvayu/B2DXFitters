/** @file TaggingCat.cxx
 *
 * @author Chiara Farinelli
 * @date ca. Aug 2012
 */
#include "Riostream.h" 

#include "B2DXFitters/TaggingCat.h" 
#include "RooAbsReal.h" 
#include "RooAbsCategory.h" 
#include "RooConstVar.h"
#include "RooAddition.h"
#include <cmath>
#include <cassert> 

TaggingCat::TaggingCat(const char *name, const char *title,
                       RooAbsCategory& _qt,
                       RooAbsCategory& _cat,
                       RooArgList& _vars,
		       bool _isTagEff) :
  
  RooAbsReal(name, title),
  qt("qt", "qt", this, _qt),
  cat("cat", "cat", this, _cat),
  catlist("catlist", "catlist", this),
  untaggedVal("untaggedVal", "untaggedVal", this)
{ 
  RooAbsReal* obj = 0;

  for (TIterator* it = _vars.createIterator();
       0 != (obj = dynamic_cast<RooAbsReal*>(it->Next())); ) {
    catlist.add(*obj);
  }
  if (_isTagEff) {
      // if this is used as a tagging efficiency, we return 1 sum of tagging
      // efficiencies of the different categories listed in _vars
      std::string tmpnam = name;
      tmpnam += "_sum";
      RooAddition* sum = new RooAddition(tmpnam.c_str(), "sum", _vars);
      untaggedVal.setArg(*sum);
      addOwnedComponents(*sum);
  }
} 


TaggingCat::TaggingCat(const TaggingCat& other, const char* name) :  
    RooAbsReal(other, name), 
    qt("qt", this, other.qt),
    cat("cat", this, other.cat),
    catlist("catlist", this, other.catlist),
    untaggedVal("untaggedVal", this, other.untaggedVal)
{
    if (untaggedVal.absArg()) {
	std::string tmpnam = GetName();
	tmpnam += "_sum";
	RooAbsReal* newarg = new RooAddition(tmpnam.c_str(), "sum", catlist);
	untaggedVal.setArg(*newarg);
	addOwnedComponents(*newarg);
    }
}

TaggingCat::~TaggingCat()
{ }

Double_t TaggingCat::evaluate() const 
{ 
    if (0 == int(qt)) {
	// fallback from the old days
	if (!untaggedVal.absArg()) return 0.5;
	else return 1. - Double_t(untaggedVal);
    }
    const int c = (int) cat;
    assert(c >= 0);
    assert(c < catlist.getSize());
    return static_cast<RooAbsReal*>(catlist.at(c))->getVal();
} 



