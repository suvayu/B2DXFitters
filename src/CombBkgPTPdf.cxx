/***************************************************************************** 
 * Project: RooFit                                                           * 
 *                                                                           * 
 * This code was autogenerated by RooClassFactory                            * 
 *****************************************************************************/ 

// Your description goes here... 

#include "Riostream.h" 

#include "RooAbsReal.h" 
#include "RooAbsCategory.h" 
#include <cmath> 
#include <cassert>
#include <algorithm>

// B2DXFitters includes
#include "B2DXFitters/CombBkgPTPdf.h"

// ClassImp(CombBkgPTPdf) 

CombBkgPTPdf::CombBkgPTPdf(const char *name, const char *title, 
	RooAbsReal& _t, RooAbsReal& _a, RooAbsReal& _f, RooAbsReal& _alpha,
	RooAbsReal& _beta) :
    RooAbsPdf(name,title), 
    t("t","t",this,_t),
    a("a","a",this,_a),
    f("f","f",this,_f),
    alpha("alpha","alpha",this,_alpha),
    beta("beta","beta",this,_beta)
{ } 

CombBkgPTPdf::CombBkgPTPdf(const CombBkgPTPdf& other, const char* name) :  
    RooAbsPdf(other,name), 
    t("t",this,other.t),
    a("a",this,other.a),
    f("f",this,other.f),
    alpha("alpha",this,other.alpha),
    beta("beta",this,other.beta)
{ } 

Double_t CombBkgPTPdf::evaluate() const 
{ 
    if (t < a) return 0.;
    return ((t - a) * (t - a) *
	    (f * std::exp(-alpha * t) + (1. - f) * std::exp(-beta * t)));
}

Int_t CombBkgPTPdf::getAnalyticalIntegral(
	RooArgSet& allVars, RooArgSet& integVars, const char*) const
{
    // we know how to do the time integral analytically
    if (matchArgs(allVars, integVars, t)) return 1;
    return 0;
}

double CombBkgPTPdf::monoInt(double t, double a, double alpha)
{
    const double alphat = alpha * t;
    const double oneplusalphat = 1. + alphat;
    return -std::exp(-alphat) / alpha * (
	    a * a +
	    (-2. * a * oneplusalphat +
	    (oneplusalphat * oneplusalphat + 1.) / alpha) / alpha);
}

Double_t CombBkgPTPdf::analyticalIntegral(Int_t code, const char*) const
{
    switch (code) {
	case 1:
	    {
		double tmin = t.min(), tmax = t.max();
		bool minus = false;
		if (tmin > tmax) {
		    std::swap(tmin, tmax);
		    minus = true;
		}
		if (tmin < a) tmin = a;
		if (tmax < a) tmax = a;
		if (tmin == tmax) return 0.;
		const double ialpha = 
		    monoInt(tmax, a, alpha) - monoInt(tmin, a, alpha);
		const double ibeta = 
		    monoInt(tmax, a, beta) - monoInt(tmin, a, beta);
		const double retVal = f * ialpha + (1. - f) * ibeta;
		if (minus) return -retVal;
		else return retVal;
	    }
	    break;
	default:
	    assert(1 == 0);
	    break;
    }
    return 0.;
}
