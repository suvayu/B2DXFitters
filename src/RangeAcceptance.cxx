/***************************************************************************** 
 * Project: RooFit                                                           * 
 *                                                                           * 
 * This code was autogenerated by RooClassFactory                            * 
 *****************************************************************************/ 

// Your description goes here... 

#include "B2DXFitters/RangeAcceptance.h" 
#include "RooAbsReal.h" 

RangeAcceptance::RangeAcceptance(const char *name, const char *title, 
	RooAbsReal& _x, double _xmin, double _xmax) :
    RooAbsReal(name,title), 
    x("x","x",this,_x),
    xmin(_xmin), xmax(_xmax)
{ 
} 


RangeAcceptance::RangeAcceptance(const RangeAcceptance& other, const char* name) :  
    RooAbsReal(other,name), 
    x("x",this,other.x),
    xmin(other.xmin), xmax(other.xmax)
{ 
} 

RangeAcceptance::~RangeAcceptance() { }


Double_t RangeAcceptance::evaluate() const 
{ 
    const double xx = double(x);
    return (xmin <= xx && xx <= xmax) ? 1.0 : 0.0;
} 



