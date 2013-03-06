/** @file TaggingCat.cxx
 *
 * @author Chiara Farinelli
 * @date ca. Aug 2012
 */
#include "Riostream.h" 

#include "B2DXFitters/TaggingCat.h" 
#include "RooAbsReal.h" 
#include "RooAbsCategory.h" 
#include <cmath>
#include <cassert> 

TaggingCat::TaggingCat(const char *name, const char *title,
                       RooAbsCategory& _qt,
                       RooAbsCategory& _cat,
                       RooArgList& _vars) :
  
  RooAbsReal(name, title),
  qt("qt", "qt", this, _qt),
  cat("cat", "cat", this, _cat),
  catlist("catlist", "catlist", this)
{ 
  RooAbsReal* obj = 0;

  for (TIterator* it = _vars.createIterator();
       0 != (obj = dynamic_cast<RooAbsReal*>(it->Next())); ) {
    catlist.add(*obj);
  }
} 


TaggingCat::TaggingCat(const TaggingCat& other, const char* name) :  
    RooAbsReal(other, name), 
    qt("qt", this, other.qt),
    cat("cat", this, other.cat),
    catlist("catlist", this, other.catlist)
{ }

TaggingCat::~TaggingCat()
{ }

Double_t TaggingCat::evaluate() const 
{ 
    if (0 == int(qt)) return 0.5;
    const int c = (int) cat;
    assert(c >= 0);
    assert(c < catlist.getSize());
    return static_cast<RooAbsReal*>(catlist.at(c))->getVal();
} 



