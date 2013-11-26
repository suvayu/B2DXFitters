/**
 * @file MistagCalibration.cxx
 *
 * Mistag calibration with polynomial
 *
 * @author Vladimir Gligorov <vladimir.gligorov@cern.ch>
 * @date 2012-09-11
 * 	initial version
 *
 * @author Manuel Schiller <manuel.schiller@nikhef.nl>
 * @date 2012-10-09
 * 	subsequent cleanups, functionality for calibration polynomials,
 * 	integrals over mistag
 */
#include <cstdio>
#include <RooRealVar.h>
#include <RooConstVar.h>

#include "B2DXFitters/MistagCalibration.h" 

MistagCalibration::MistagCalibration(const char *name, const char *title, 
	RooAbsReal& eta, RooArgList& calibcoeffs, RooAbsReal& etaavg) :
    RooAbsReal(name, title), 
    m_eta("eta", "eta", this, eta),
    m_calibcoeffs("calibcoeffs", "calibcoeffs", this),
    m_etaavg("etaavg", "etaavg", this, etaavg)
{
    /// mistag and avgmistag have to be either RooConstVars or RooRealVars
    assert(0 != dynamic_cast<RooRealVar*>(&eta) ||
	    0 != dynamic_cast<RooConstVar*>(&eta));
    assert(0 != dynamic_cast<RooRealVar*>(&etaavg) ||
	    0 != dynamic_cast<RooConstVar*>(&etaavg));
    init(calibcoeffs, eta);
}
void MistagCalibration::init(const RooArgList& calibcoeffs, RooAbsReal& eta)
{
    RooFIter it = calibcoeffs.fwdIterator();
    while (RooAbsArg* obj = it.next()) {
	// fail if there's something in there that does not inherit from
	// RooAbsReal
	RooAbsReal& var = dynamic_cast<RooAbsReal&>(*obj);
	// also fail if the coefficients contain the mistag itself (we want to
	// provide analytical integrals, and that only works if the
	// coefficients are sane)
	assert(!var.overlaps(eta));
	// accept calibration coefficient
	m_calibcoeffs.add(var);
    }
}

MistagCalibration::MistagCalibration(const char *name, const char *title, 
	RooAbsReal& eta, RooAbsReal& p0, RooAbsReal& p1) :
    RooAbsReal(name, title), 
    m_eta("eta", "eta", this, eta),
    m_calibcoeffs("calibcoeffs", "calibcoeffs", this),
    m_etaavg("etaavg", "etaavg", this, 0)
{
    /// mistag has to be either RooConstVars or RooRealVars
    assert(0 != dynamic_cast<RooRealVar*>(&eta) ||
	    0 != dynamic_cast<RooConstVar*>(&eta));
    init(RooArgList(p0, p1), eta);
}

MistagCalibration::MistagCalibration(const char *name, const char *title, 
	RooAbsReal& eta, RooAbsReal& p0, RooAbsReal& p1, RooAbsReal& etaavg) :
    RooAbsReal(name, title), 
    m_eta("eta", "eta", this, eta),
    m_calibcoeffs("calibcoeffs", "calibcoeffs", this),
    m_etaavg("etaavg", "etaavg", this, etaavg)
{
    /// mistag and avgmistag have to be either RooConstVars or RooRealVars
    assert(0 != dynamic_cast<RooRealVar*>(&eta) ||
	    0 != dynamic_cast<RooConstVar*>(&eta));
    assert(0 != dynamic_cast<RooRealVar*>(&etaavg) ||
	    0 != dynamic_cast<RooConstVar*>(&etaavg));
    init(RooArgList(p0, p1), eta);
} 

MistagCalibration::MistagCalibration(const MistagCalibration& other, const char* name) :  
    RooAbsReal(other, name), 
    m_eta("eta", this, other.m_eta),
    m_calibcoeffs("calibcoeffs", this, other.m_calibcoeffs),
    m_etaavg("etaavg", this, other.m_etaavg)
{ } 

TObject* MistagCalibration::clone(const char* newname) const
{ return new MistagCalibration(*this,newname); }

MistagCalibration::~MistagCalibration() { }

Double_t MistagCalibration::evaluate() const 
{
    const double eta(m_eta);
    // calibrate the mistag
    const double dm = eta - (m_etaavg.absArg() ? double(m_etaavg) : 0.);
    double m = 1.;
    double sum = 0.;
    unsigned k = 0;
    RooFIter it = m_calibcoeffs.fwdIterator();
    while (const RooAbsReal* c = static_cast<const RooAbsReal*>(it.next())) {
	const double cc = c->getVal();
	sum += m * cc;
	m *= dm;
	++k;
    }
    // check if we accumulated something, if so use calibrated mistag
    if (k) return sum;
    else return eta;
}

Int_t MistagCalibration::getAnalyticalIntegral(
	RooArgSet& allVars, RooArgSet& anaIntVars,
	const char* /* rangeName */) const
{
    if (matchArgs(allVars, anaIntVars, m_eta)) return 1;
    return 0;
}

Double_t MistagCalibration::evalIntEta(
	const double etalo, const double etahi) const
{
    // mistag integral with calibration (if needed)
    const double etaavg(m_etaavg.absArg() ? double(m_etaavg) : 0.);
    const double detalo = etalo - etaavg;
    const double detahi = etahi - etaavg;
    double petalo = 1., petahi = 1., isum = 0.;
    unsigned k = 0;
    RooFIter it = m_calibcoeffs.fwdIterator();
    while (const RooAbsReal* c = static_cast<const RooAbsReal*>(it.next())) {
	petalo *= detalo;
	petahi *= detahi;
	++k;
	isum += (petahi - petalo) * c->getVal() / double(k);
    }
    // check if we accumulated something, if so use calibrated mistag
    if (k) return isum;
    else return 0.5 * (etahi * etahi - etalo * etalo);
}

Double_t MistagCalibration::analyticalIntegral(
	Int_t code, const char* rangeName) const
{
    assert(1 == code);
    // integrate over mistag
    const double retVal = evalIntEta(m_eta.min(rangeName), m_eta.max(rangeName));
    return retVal;
}

// vim: ft=cpp:sw=4:tw=78
