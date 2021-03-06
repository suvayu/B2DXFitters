/*****************************************************************************
 * Project: RooFit                                                           *
 *                                                                           *
 * This code was autogenerated by RooClassFactory                            *
 *****************************************************************************/

// Your description goes here...

#include <cmath>
#include <cstdio>
#include <cassert>
#include <algorithm>

#include "RooAbsReal.h"
#include "B2DXFitters/MistagDistribution.h"

MistagDistribution::MistagDistribution(const char *name, const char *title,
	RooAbsReal& _w, RooAbsReal& _w0, RooAbsReal& _wa,
	RooAbsReal& _f) : RooAbsPdf(name,title),
    w("w","w",this,_w), w0("w0","w0",this,_w0), wa("wa","wa",this,_wa),
    f("f","f",this,_f),
    lastw0(0.), lastwa(0.), lastf(0.), lastwc(0.)
{ }


MistagDistribution::MistagDistribution(const MistagDistribution& other, const char* name) :
    RooAbsPdf(other,name),
    w("w",this,other.w), w0("w0",this,other.w0), wa("wa",this,other.wa),
    f("f",this,other.f),
    lastw0(0.), lastwa(0.), lastf(0.), lastwc(0.)
{ }

MistagDistribution::~MistagDistribution() { }


double MistagDistribution::getWc() const
{
    const double _w0 = w0;
    const double _wa = wa;
    const double _f = f;
    // quickly validate input variables
    if (_w0 < 0.0 || _w0 > 0.5 || _wa <= 0.0 ||
	    _wa >= 0.5 || _f < 0.0 || _f > 1.0)
	return 0.0;
    if (0. != lastwc && lastw0 == _w0 && lastwa == _wa && lastf == _f) {
	return lastwc;
    } else {
	// calculate e_f_fective wc
	const double i1 =
	    (36. * _f*_f + 24. * _f + 4.) * _wa * _wa +
	    ((8. * _f + 8.) * _w0 - 36. * _f*_f - 28. * _f - 8.) * _wa -
	    8. * _f * _w0*_w0 + (4. * _f - 4.) * _w0 + 9. * _f*_f + 6. * _f + 3.;
	// expression under square root negative, no solution _for wc
	if (i1 < 0.0) return 0.;
	const double i2 = (6. * _f + 2.) * _wa - 2. * _w0 - _f + 1.;
	const double wc1 = 0.25 * (i2 + std::sqrt(i1)) / (_f + 0.5);
	const double wc2 = 0.25 * (i2 - std::sqrt(i1)) / (_f + 0.5);
	// check _for wc solution in allowed range
	const double wc = (0.0 <= wc1 && wc1 <= 0.5) ? wc1 : wc2;
	if (!(0.0 <= wc && wc <= 0.5)) return (lastwc = 0.0);
	lastwc = wc;
	lastw0 = _w0;
	lastwa = _wa;
	lastf = _f;
	return wc;
    }
    return 0.;
}

Double_t MistagDistribution::evaluate() const
{
    const double _w = w;
    const double _w0 = w0;
    const double _wa = wa;
    const double _f = f;
    // quickly validate input variables
    if (_w < 0.0 || _w > 0.5 || _w0 < 0.0 || _w0 > 0.5 || _wa <= 0.0 ||
	    _wa >= 0.5 || _f < 0.0 || _f > 1.0)
	return 0.0;
    // we we're below the lower turnon, we're done as well
    if (_w < _w0) return 0.0;

    const double wc = getWc();
    if (!(0.0 <= wc && wc <= 0.5)) return 0.0;
    // ok, evaluate pdf
    if (_w < wc) {
	const double x = (_w - _w0) / (wc - _w0);
	return x * x;
    } else {
	return 1. - (1. - _f) * (_w - wc) / (0.5 - wc);
    }
    // should never arrive here...
    return 0.0;
}

Int_t MistagDistribution::getAnalyticalIntegral(RooArgSet& integ, RooArgSet& anaIntSet, const char*) const
{
    if (matchArgs(integ, anaIntSet, w)) return 1;
    return 0;
}

Double_t MistagDistribution::analyticalIntegral(Int_t code, const char *rangeName) const
{
    switch(code) {
	default:
	    assert(1 == 0);
	    break;
	case 1:
	    {
		const double _w0 = w0;
		const double _wa = wa;
		const double _f = f;
		// quickly validate input variables
		if (_w0 < 0.0 || _w0 > 0.5 || _wa <= 0.0 ||
			_wa >= 0.5 || _f < 0.0 || _f > 1.0)
		    return 0.0;
		const double wc = getWc();
		if (!(0.0 <= wc && wc <= 0.5)) return 0.0;
		// set up integration ranges
		bool minus = false;
		double wmin = this->w.min(rangeName);
		double wmax = this->w.max(rangeName);
		if (wmax < wmin) {
		    std::swap(wmin, wmax);
		    minus = true;
		}
		// clip integration range
		//
		// from -infinity to w0, pdf is zero
		if (wmin < _w0) wmin = _w0;
		// from 0.5 to +infinity, pdf is zero
		if (wmax > 0.5) wmax = 0.5;
		// get integration "midpoint" - if wc is in the integration
		// range, wmid is set to wc, otherwise, we set it to the
		// relevant end point of the integration
		const double wmid = std::max(wmin, std::min(wc, wmax));
		double sum = 0.;
		if (wmin >= _w0 && wmid > wmin) { 
		    const double tmp = 1. / (wc - _w0) / (wc - _w0);
		    sum += (wmid - wmin) * _w0 * _w0 * tmp;
		    sum -= (wmid * wmid - wmin * wmin) * _w0 * tmp;
		    sum += (wmid * wmid * wmid - wmin * wmin * wmin) * tmp / 3.;
		}
		if (wmid >= wc && wmax > wmid) {
		    const double tmp = (1. - _f) / (0.5 - wc);
		    sum += (wmax - wmid) * (1. + wc * tmp);
		    sum += -0.5 * tmp * (wmax * wmax - wmid * wmid);
		}
		if (minus) return -sum;
		else return sum;
	    }
	    break;
    }
    return 0.;
}
