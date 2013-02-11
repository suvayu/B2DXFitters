/**
 * @file FinalStateChargePdf.cxx
 *
 * pdf to describe final state charge distribution (in terms of an asymmetry)
 *
 * @author Manuel Schiller <manuel.schiller@nikhef.nl>
 * @date 2012-10-16
 */

#include <memory>
#include <cassert>
#include <algorithm>
 
#include <RooCategory.h>

#include "B2DXFitters/FinalStateChargePdf.h"

FinalStateChargePdf::FinalStateChargePdf(const char *name, const char *title,
	RooAbsCategory& qf, RooAbsReal& asymm) :
    RooAbsPdf(name, title), 
    m_qf("qf", "qf", this, qf), m_asymm("asymm", "asymm", this, asymm)
{ } 

FinalStateChargePdf::FinalStateChargePdf(
	const FinalStateChargePdf& other, const char* name) : 
    RooAbsPdf(other, name), 
    m_qf("qf", this, other.m_qf), m_asymm("asymm", this, other.m_asymm)
{ } 

FinalStateChargePdf::~FinalStateChargePdf() { }

TObject* FinalStateChargePdf::clone(const char* newname) const
{ return new FinalStateChargePdf(*this, newname); }

Double_t FinalStateChargePdf::evaluate() const 
{ 
    const int qf(m_qf);
    assert(std::abs(qf) == 1);
    return eval(qf);
}

Double_t FinalStateChargePdf::eval(const int qf) const
{ return 1. + double(qf) * double(m_asymm); } 

Int_t FinalStateChargePdf::getAnalyticalIntegral(
	RooArgSet& allVars, RooArgSet& anaIntVars,
	const char* /* rangeName */) const
{
    int code = 0;
    // check for integration over qt/qf
    if (dynamic_cast<const RooCategory*>(m_qf.absArg()) && 
	    matchArgs(allVars, anaIntVars, m_qf)) code |= 1;
    return code;
}

Double_t FinalStateChargePdf::analyticalIntegral(
	Int_t code, const char* rangeName) const
{
    assert(code == 1);
    // sum over categories
    double retVal = 0.;
    const RooCategory& qf(dynamic_cast<const RooCategory&>(m_qf.arg()));
    std::auto_ptr<TIterator> qfit(qf.typeIterator());
    while (RooCatType* qfty = reinterpret_cast<RooCatType*>(qfit->Next())) {
	if (code & 1) {
	    // sum over qf states in range
	    if (qf.hasRange(rangeName) &&
		    !qf.isStateInRange(rangeName, qfty->GetName()))
		continue;
	} else {
	    // no qf integral requested, just use the current qf value
	    if (qfty->getVal() != qf.getIndex())
		continue;
	}
	assert(std::abs(qfty->getVal()) == 1);
	retVal += eval(qfty->getVal());
    }
    return retVal;
}

// vim: sw=4:tw=78:ft=cpp
