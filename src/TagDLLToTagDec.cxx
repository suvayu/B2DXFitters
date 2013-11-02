/***************************************************************************** 
 * Project: RooFit                                                           * 
 *                                                                           * 
 * This code was autogenerated by RooClassFactory                            * 
 *****************************************************************************/ 

// Your description goes here... 

#include "Riostream.h" 

#include "B2DXFitters/TagDLLToTagDec.h" 
#include "RooAbsReal.h" 

#include "B2DXFitters/TagCombiner.h"

TagDLLToTagDec::TagDLLToTagDec(const char *name, const char *title, 
	RooAbsReal& _dll) :
    RooAbsCategory(name,title), 
    dll("dll","dll",this,_dll)
{ 
    defineType("B", +1);
    defineType("Bbar", -1);
    defineType("Untagged", 0);
} 


TagDLLToTagDec::TagDLLToTagDec(const TagDLLToTagDec& other, const char* name) :  
    RooAbsCategory(other,name), 
    dll("dll",this,other.dll)
{ 
} 

TagDLLToTagDec::~TagDLLToTagDec() { }


RooCatType TagDLLToTagDec::evaluate() const 
{
    return *lookupType(int(TagTools::tagDec(double(dll))));
}
