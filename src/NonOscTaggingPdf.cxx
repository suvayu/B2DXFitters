/** @file NonOscTaggingPdf.cxx
 *
 * tagging behaviour and asymmetries for non-oscillating backgrounds
 */
#include <cmath>
#include <memory>
#include <limits>
#include <algorithm>

#include <RooCategory.h>

#include "B2DXFitters/NonOscTaggingPdf.h"

RooArgSet NonOscTaggingPdf::s_emptyset;

NonOscTaggingPdf::NonOscTaggingPdf(const char* name, const char* title,
	RooAbsCategory& qf, RooAbsCategory& qt,
	RooAbsRealLValue& etaobs, RooAbsPdf& etapdf,
	RooAbsReal& epsilon, RooAbsReal& adet,
	RooAbsReal& atageff_f, RooAbsReal& atageff_t) :
    RooAbsPdf(name, title),
    m_qf("qf", "qf", this, qf), m_qt("qt", "qt", this, qt),
    m_etaobs("etaobs", "etaobs", this, etaobs),
    m_etapdf("etapdf", "etapdf", this, etapdf),
    m_etapdfutinstance(
	    (std::string(GetName()) + "_untagged").c_str(),
	    (std::string(GetName()) + "_untagged").c_str(),
	    RooArgSet(etaobs)),
    m_etapdfut("etapdfut", "etapdfut", this, m_etapdfutinstance),
    m_epsilon("epsilon", "epsilon", this, epsilon),
    m_adet("adet", "adet", this, adet),
    m_atageff_f("atageff_f", "atageff_f", this, atageff_f),
    m_atageff_t("atageff_t", "atageff_t", this, atageff_t),
    m_cacheMgr(this)
{
    if (!qf.isConstant()) {
	assert(!qf.overlaps(qt) || qt.isConstant());
	assert(!qf.overlaps(etaobs) || etaobs.isConstant());
	assert(!qf.overlaps(etapdf) || etapdf.isConstant());
	assert(!qf.overlaps(epsilon) || epsilon.isConstant());
	assert(!qf.overlaps(adet) || adet.isConstant());
	assert(!qf.overlaps(atageff_f) || atageff_f.isConstant());
	assert(!qf.overlaps(atageff_t) || atageff_t.isConstant());
    }
    if (!qt.isConstant()) {
	assert(!qt.overlaps(qf) || qf.isConstant());
	assert(!qt.overlaps(etaobs) || etaobs.isConstant());
	assert(!qt.overlaps(etapdf) || etapdf.isConstant());
	assert(!qt.overlaps(epsilon) || epsilon.isConstant());
	assert(!qt.overlaps(adet) || adet.isConstant());
	assert(!qt.overlaps(atageff_f) || atageff_f.isConstant());
	assert(!qt.overlaps(atageff_t) || atageff_t.isConstant());
    }
    if (!etaobs.isConstant()) {
	assert(!etaobs.overlaps(qf) || qf.isConstant());
	assert(!etaobs.overlaps(qt) || qt.isConstant());
	assert(etaobs.overlaps(etapdf));
	assert(!etaobs.overlaps(epsilon) || epsilon.isConstant());
	assert(!etaobs.overlaps(adet) || adet.isConstant());
	assert(!etaobs.overlaps(atageff_f) || atageff_f.isConstant());
	assert(!etaobs.overlaps(atageff_t) || atageff_t.isConstant());
    }
    if (!etapdf.isConstant()) {
	assert(!etapdf.overlaps(qf) || qf.isConstant());
	assert(!etapdf.overlaps(qt) || qt.isConstant());
	assert(etapdf.overlaps(etaobs));
	assert(!etapdf.overlaps(epsilon) || epsilon.isConstant());
	assert(!etapdf.overlaps(adet) || adet.isConstant());
	assert(!etapdf.overlaps(atageff_f) || atageff_f.isConstant());
	assert(!etapdf.overlaps(atageff_t) || atageff_t.isConstant());
    }
    if (!epsilon.isConstant()) {
	assert(!epsilon.overlaps(qf) || qf.isConstant());
	assert(!epsilon.overlaps(qt) || qt.isConstant());
	assert(!epsilon.overlaps(etaobs) || etaobs.isConstant());
	assert(!epsilon.overlaps(etapdf) || etapdf.isConstant());
	assert(!epsilon.overlaps(adet) || adet.isConstant());
	assert(!epsilon.overlaps(atageff_f) || atageff_f.isConstant());
	assert(!epsilon.overlaps(atageff_t) || atageff_t.isConstant());
    }
    if (!adet.isConstant()) {
	assert(!adet.overlaps(qf) || qf.isConstant());
	assert(!adet.overlaps(qt) || qt.isConstant());
	assert(!adet.overlaps(etaobs) || etaobs.isConstant());
	assert(!adet.overlaps(etapdf) || etapdf.isConstant());
	assert(!adet.overlaps(epsilon) || epsilon.isConstant());
	assert(!adet.overlaps(atageff_f) || atageff_f.isConstant());
	assert(!adet.overlaps(atageff_t) || atageff_t.isConstant());
    }
    if (!atageff_f.isConstant()) {
	assert(!atageff_f.overlaps(qf) || qf.isConstant());
	assert(!atageff_f.overlaps(qt) || qt.isConstant());
	assert(!atageff_f.overlaps(etaobs) || etaobs.isConstant());
	assert(!atageff_f.overlaps(etapdf) || etapdf.isConstant());
	assert(!atageff_f.overlaps(epsilon) || epsilon.isConstant());
	assert(!atageff_f.overlaps(adet) || adet.isConstant());
	assert(!atageff_f.overlaps(atageff_t) || atageff_t.isConstant());
    }
    if (!atageff_t.isConstant()) {
	assert(!atageff_t.overlaps(qf) || qf.isConstant());
	assert(!atageff_t.overlaps(qt) || qt.isConstant());
	assert(!atageff_t.overlaps(etaobs) || etaobs.isConstant());
	assert(!atageff_t.overlaps(etapdf) || etapdf.isConstant());
	assert(!atageff_t.overlaps(epsilon) || epsilon.isConstant());
	assert(!atageff_t.overlaps(adet) || adet.isConstant());
	assert(!atageff_t.overlaps(atageff_f) || atageff_f.isConstant());
    }
}

NonOscTaggingPdf::NonOscTaggingPdf(const char* name, const char* title,
	RooAbsCategory& qf, RooAbsCategory& qt,
	RooAbsReal& epsilon, RooAbsReal& adet,
	RooAbsReal& atageff_f, RooAbsReal& atageff_t) :
    RooAbsPdf(name, title),
    m_qf("qf", "qf", this, qf), m_qt("qt", "qt", this, qt),
    m_epsilon("epsilon", "epsilon", this, epsilon),
    m_adet("adet", "adet", this, adet),
    m_atageff_f("atageff_f", "atageff_f", this, atageff_f),
    m_atageff_t("atageff_t", "atageff_t", this, atageff_t),
    m_cacheMgr(this)
{
    if (!qf.isConstant()) {
	assert(!qf.overlaps(qt) || qt.isConstant());
	assert(!qf.overlaps(epsilon) || epsilon.isConstant());
	assert(!qf.overlaps(adet) || adet.isConstant());
	assert(!qf.overlaps(atageff_f) || atageff_f.isConstant());
	assert(!qf.overlaps(atageff_t) || atageff_t.isConstant());
    }
    if (!qt.isConstant()) {
	assert(!qt.overlaps(qf) || qf.isConstant());
	assert(!qt.overlaps(epsilon) || epsilon.isConstant());
	assert(!qt.overlaps(adet) || adet.isConstant());
	assert(!qt.overlaps(atageff_f) || atageff_f.isConstant());
	assert(!qt.overlaps(atageff_t) || atageff_t.isConstant());
    }
    if (!epsilon.isConstant()) {
	assert(!epsilon.overlaps(qf) || qf.isConstant());
	assert(!epsilon.overlaps(qt) || qt.isConstant());
	assert(!epsilon.overlaps(adet) || adet.isConstant());
	assert(!epsilon.overlaps(atageff_f) || atageff_f.isConstant());
	assert(!epsilon.overlaps(atageff_t) || atageff_t.isConstant());
    }
    if (!adet.isConstant()) {
	assert(!adet.overlaps(qf) || qf.isConstant());
	assert(!adet.overlaps(qt) || qt.isConstant());
	assert(!adet.overlaps(epsilon) || epsilon.isConstant());
	assert(!adet.overlaps(atageff_f) || atageff_f.isConstant());
	assert(!adet.overlaps(atageff_t) || atageff_t.isConstant());
    }
    if (!atageff_f.isConstant()) {
	assert(!atageff_f.overlaps(qf) || qf.isConstant());
	assert(!atageff_f.overlaps(qt) || qt.isConstant());
	assert(!atageff_f.overlaps(epsilon) || epsilon.isConstant());
	assert(!atageff_f.overlaps(adet) || adet.isConstant());
	assert(!atageff_f.overlaps(atageff_t) || atageff_t.isConstant());
    }
    if (!atageff_t.isConstant()) {
	assert(!atageff_t.overlaps(qf) || qf.isConstant());
	assert(!atageff_t.overlaps(qt) || qt.isConstant());
	assert(!atageff_t.overlaps(epsilon) || epsilon.isConstant());
	assert(!atageff_t.overlaps(adet) || adet.isConstant());
	assert(!atageff_t.overlaps(atageff_f) || atageff_f.isConstant());
    }
}

NonOscTaggingPdf::NonOscTaggingPdf(
	const NonOscTaggingPdf& other, const char* name) :
    RooAbsPdf(other, name),
    m_qf("qf", this, other.m_qf), m_qt("qt", this, other.m_qt),
    m_etaobs("etaobs", this, other.m_etaobs),
    m_etapdf("etapdf", this, other.m_etapdf),
    m_etapdfutinstance(other.m_etapdfutinstance),
    m_etapdfut("etapdfut", this, other.m_etapdfut),
    m_epsilon("epsilon", this, other.m_epsilon),
    m_adet("adet", this, other.m_adet),
    m_atageff_f("atageff_f", this, other.m_atageff_f),
    m_atageff_t("atageff_t", this, other.m_atageff_t),
    m_cacheMgr(other.m_cacheMgr, this)
{
    if (m_etaobs.absArg()) {
	m_etapdfut.setArg(m_etapdfutinstance);
    }
}

NonOscTaggingPdf::~NonOscTaggingPdf() { }

TObject* NonOscTaggingPdf::clone(const char* newname) const
{ return new NonOscTaggingPdf(*this, newname); }

Bool_t NonOscTaggingPdf::selfNormalized() const
{ return kTRUE; }

Double_t NonOscTaggingPdf::evaluate() const
{
    // get value
    const double val = getCache(
	    s_emptyset, _normSet, RooNameReg::ptr(0)).first->eval();
    if (!_normSet) {
	return val;
    }
    // normalise if we have to
    const char *nrange = (_normRangeOverride.Length() ?
	    _normRangeOverride.Data() :
	    ((_normRange.Length()) ? _normRange.Data() : 0));
    const double norm = getCache(*_normSet, _normSet,
	    RooNameReg::ptr(nrange)).first->eval();
    return val / norm;
}

Bool_t NonOscTaggingPdf::forceAnalyticalInt(const RooAbsArg& dep) const
{
    if (&dep == m_qf.absArg()) return kTRUE;
    if (&dep == m_qt.absArg()) return kTRUE;
    if (&dep == m_etaobs.absArg()) return kTRUE;
    return kFALSE;
}

Int_t NonOscTaggingPdf::getAnalyticalIntegral(
	RooArgSet& allVars, RooArgSet& anaIntVars,
	const char* rangeName) const
{ return getAnalyticalIntegralWN(allVars, anaIntVars, _normSet, rangeName); }

Double_t NonOscTaggingPdf::analyticalIntegral(
	Int_t code, const char* rangeName) const
{ return analyticalIntegralWN(code, _normSet, rangeName); }

Int_t NonOscTaggingPdf::getAnalyticalIntegralWN(
	RooArgSet& allVars, RooArgSet& anaIntVars,
	const RooArgSet* nset, const char* rangeName) const
{
    // perform analytical integrals
    // we know how to integrate over etaobs, qf, qt
    if (m_etaobs.absArg()) {
	matchArgs(allVars, anaIntVars, m_etaobs);
    }
    matchArgs(allVars, anaIntVars, m_qf);
    matchArgs(allVars, anaIntVars, m_qt);
    // create the integral object
    unsigned icode = 1 + getCache(
	    anaIntVars, nset, RooNameReg::ptr(rangeName)).second;
    assert(icode < 32767);
    unsigned ncode = 0;
    // create normalisation object (if needed)
    if (nset) {
	const char *nrange = (_normRangeOverride.Length() ?
		_normRangeOverride.Data() :
		((_normRange.Length()) ? _normRange.Data() : 0));
	ncode = 1 + getCache(
		*nset, nset, RooNameReg::ptr(nrange)).second;
	assert(ncode < 32767);
    }
    return (ncode << 15) | icode;
}

Double_t NonOscTaggingPdf::analyticalIntegralWN(
        Int_t code, const RooArgSet* nset, const char* /* rangeName */) const
{
    if (!code) return getValV(nset);
    assert(code > 0);
    const unsigned icode(unsigned(code) & 32767);
    const unsigned ncode((unsigned(code) >> 15) & 32767);
    assert(Int_t(icode | (ncode << 15)) == code);

    CacheElem* ic =
        static_cast<CacheElem*>(m_cacheMgr.getObjByIndex(icode - 1));
    const double ival = ic->eval();
    if (ncode) {
        CacheElem* nc =
            static_cast<CacheElem*>(m_cacheMgr.getObjByIndex(ncode - 1));
        const double nval = nc->eval();
        return ival / nval;
    } else {
        return ival;
    }
}

NonOscTaggingPdf::CacheElemPair NonOscTaggingPdf::getCache(
	const RooArgSet& iset, const RooArgSet* nset,
	const TNamed* rangeName) const
{
    Int_t idx = -1;
    CacheElem* cache = reinterpret_cast<CacheElem*>(
	    m_cacheMgr.getObj(nset, &iset, &idx, rangeName));
    if (cache) {
	idx = m_cacheMgr.lastIndex();
	assert(idx >= 0);
	return CacheElemPair(cache, idx);
    }
    // ok, integral not in cache yet
    cache = new CacheElem(*this, iset, nset, rangeName);
    assert(cache);
    // put it in cache
    idx = m_cacheMgr.setObj(nset, &iset, cache, rangeName);
    assert(idx >= 0);
    return CacheElemPair(cache, idx);
}

NonOscTaggingPdf::CacheElem::CacheElem(const NonOscTaggingPdf& parent,
	const RooArgSet& iset, const RooArgSet* nset,
	const TNamed* rangeName) :
    m_parent(parent), m_etapdfint(0), m_etapdfintut(0),
    m_rangeName(rangeName ? rangeName->GetName() : 0), m_flags(None)
{
    // set flag for qf/qt integration
    if (iset.find(parent.m_qf.arg()))
        m_flags = static_cast<Flags>(m_flags | IntQf);
    if (iset.find(parent.m_qt.arg()))
        m_flags = static_cast<Flags>(m_flags | IntQt);

    if (parent.m_etaobs.absArg()) {
	// massage integration set (if needed)
	if (iset.find(parent.m_etaobs.arg())) {
	    m_flags = static_cast<Flags>(m_flags | IntEta);
	}
	// massage normalisation set as well (if present)
	if (nset && nset->find(m_parent.m_etaobs.arg())) {
	    m_nset.add(m_parent.m_etaobs.arg());
	    m_flags = static_cast<Flags>(m_flags | NormEta);
	}
	if (m_flags & IntEta) {
	    // we really integrate over eta
	    RooArgSet etaiset(parent.m_etaobs.arg());
	    RooArgSet* etanset = nset ? &m_nset : 0;
	    m_etapdfint = parent.m_etapdf.arg().createIntegral(
		    etaiset, etanset, 0, m_rangeName);
	    m_etapdfintut = parent.m_etapdfut.arg().createIntegral(
		    etaiset, etanset, 0, m_rangeName);
	} else {
	    // do not integrate over eta
	    m_etapdfint = const_cast<RooAbsReal*>(&parent.m_etapdf.arg());
	    m_etapdfintut = const_cast<RooAbsReal*>(&parent.m_etapdfut.arg());
	}
    }
}

NonOscTaggingPdf::CacheElem::~CacheElem()
{
    if (m_flags & IntEta) {
	delete m_etapdfint;
	delete m_etapdfintut;
    }
}

RooArgList NonOscTaggingPdf::CacheElem::containedArgs(Action)
{
    RooArgList retVal;
    if (m_etapdfint) retVal.add(*m_etapdfint);
    if (m_etapdfintut) retVal.add(*m_etapdfintut);
    if (!(m_flags & IntQf)) retVal.add(m_parent.m_qf.arg());
    if (!(m_flags & IntQt)) retVal.add(m_parent.m_qt.arg());
    if (!(m_flags & IntEta)) {
	if (m_parent.m_etaobs.absArg()) retVal.add(m_parent.m_etaobs.arg());
	if (m_parent.m_etapdf.absArg()) retVal.add(m_parent.m_etapdf.arg());
	if (m_parent.m_etapdfut.absArg()) retVal.add(m_parent.m_etapdfut.arg());
    }
    retVal.add(m_parent.m_epsilon.arg());
    retVal.add(m_parent.m_adet.arg());
    retVal.add(m_parent.m_atageff_f.arg());
    retVal.add(m_parent.m_atageff_t.arg());
    return retVal;
}
double NonOscTaggingPdf::CacheElem::etapdfint() const
{
    return !m_etapdfint ? 1. :
	m_etapdfint->getVal((m_flags & NormEta) ? &m_nset : 0);
}

double NonOscTaggingPdf::CacheElem::etapdfintut() const
{
    return !m_etapdfintut ? 1. :
	m_etapdfintut->getVal((m_flags & NormEta) ? &m_nset : 0);
}

double NonOscTaggingPdf::CacheElem::qfpdf(const int qf) const
{ return .5 * (1. + double(qf) * double(m_parent.m_adet)); }

double NonOscTaggingPdf::CacheElem::qtetapdf(const int qf, const int qt) const
{
    if (qt) {
	return 0.25 * etapdfint() * double(m_parent.m_epsilon) *
	    (1. + double(qf) * double(m_parent.m_atageff_f)) *
	    (1. + double(qt) * double(m_parent.m_atageff_t));
    } else {
	return 0.5 * etapdfintut() * (1. - double(m_parent.m_epsilon)) *
	    (1. + double(qf) * double(m_parent.m_atageff_f));
    }
    // must never get here
    assert(1 == 0);
    return std::numeric_limits<double>::quiet_NaN();
}

double NonOscTaggingPdf::CacheElem::eval(const int qf, const int qt) const
{
    assert(std::abs(qf) == 1);
    assert(std::abs(qt) <= 1);
    return qfpdf(qf) * qtetapdf(qf, qt);
}

double NonOscTaggingPdf::CacheElem::eval() const
{
    if (!(m_flags & (IntQf | IntQt))) {
	// no qf or qt integration
	return eval(int(m_parent.m_qf), int(m_parent.m_qt));
    } else if ((m_flags & IntQf) && !(m_flags & IntQt)) {
	// integrate over qf
	if (0. == std::abs(double(m_parent.m_atageff_f))) {
	    // optimisation: integral factorises in this case
	    // loop over qf states
	    const RooCategory& qf(
		    dynamic_cast<const RooCategory&>(m_parent.m_qf.arg()));
	    std::auto_ptr<TIterator> qfit(qf.typeIterator());
	    double qfint = 0.;
	    while (RooCatType* qfty =
		    reinterpret_cast<RooCatType*>(qfit->Next())) {
		// skip qf states not in range if the category has a range of that
		// name (if there's no range of rangeName in qf, we use all qf
		// states)
		if (qf.hasRange(m_rangeName) &&
			!qf.isStateInRange(m_rangeName, qfty->GetName()))
		    continue;
		qfint += qfpdf(qfty->getVal());
	    }
	    return qfint * qtetapdf(1, int(m_parent.m_qt));
	} else {
	    // loop over qf states
	    const RooCategory& qf(
		    dynamic_cast<const RooCategory&>(m_parent.m_qf.arg()));
	    std::auto_ptr<TIterator> qfit(qf.typeIterator());
	    const int iqt(m_parent.m_qt);
	    double retVal = 0.;
	    while (RooCatType* qfty =
		    reinterpret_cast<RooCatType*>(qfit->Next())) {
		// skip qf states not in range if the category has a range of that
		// name (if there's no range of rangeName in qf, we use all qf
		// states)
		if (qf.hasRange(m_rangeName) &&
			!qf.isStateInRange(m_rangeName, qfty->GetName()))
		    continue;
		retVal += eval(qfty->getVal(), iqt);
	    }
	    return retVal;
	}
    } else if (!(m_flags & IntQf) && (m_flags & IntQt)) {
	// loop over qt states
        const RooCategory& qt(
                dynamic_cast<const RooCategory&>(m_parent.m_qt.arg()));
        std::auto_ptr<TIterator> qtit(qt.typeIterator());
	const int iqf(m_parent.m_qf);
	double retVal = 0.;
        while (RooCatType* qtty =
                reinterpret_cast<RooCatType*>(qtit->Next())) {
            // skip qt states not in range if the category has a range of that
            // name (if there's no range of rangeName in qt, we use all qt
            // states)
            if (qt.hasRange(m_rangeName) &&
                    !qt.isStateInRange(m_rangeName, qtty->GetName()))
                continue;
	    retVal += qtetapdf(iqf, qtty->getVal());
	}
	return qfpdf(iqf) * retVal;
    } else if ((m_flags & IntQf) && (m_flags & IntQt)) {
	if (0. == std::abs(double(m_parent.m_atageff_f))) {
	    // optimisation: integral factorises in this case
	    // loop over qf states
	    const RooCategory& qf(
		    dynamic_cast<const RooCategory&>(m_parent.m_qf.arg()));
	    std::auto_ptr<TIterator> qfit(qf.typeIterator());
	    double qfint = 0.;
	    while (RooCatType* qfty =
		    reinterpret_cast<RooCatType*>(qfit->Next())) {
		// skip qf states not in range if the category has a range of that
		// name (if there's no range of rangeName in qf, we use all qf
		// states)
		if (qf.hasRange(m_rangeName) &&
			!qf.isStateInRange(m_rangeName, qfty->GetName()))
		    continue;
		qfint += qfpdf(qfty->getVal());
	    }
	    // loop over qt states
	    const RooCategory& qt(
		    dynamic_cast<const RooCategory&>(m_parent.m_qt.arg()));
	    std::auto_ptr<TIterator> qtit(qt.typeIterator());
	    double qtint = 0.;
	    while (RooCatType* qtty =
		    reinterpret_cast<RooCatType*>(qtit->Next())) {
		// skip qt states not in range if the category has a range of that
		// name (if there's no range of rangeName in qt, we use all qt
		// states)
		if (qt.hasRange(m_rangeName) &&
			!qt.isStateInRange(m_rangeName, qtty->GetName()))
		    continue;
		qtint += qtetapdf(1, qtty->getVal());
	    }
	    return qfint * qtint;
	} else {
	    // loop over qf states
	    const RooCategory& qf(
		    dynamic_cast<const RooCategory&>(m_parent.m_qf.arg()));
	    std::auto_ptr<TIterator> qfit(qf.typeIterator());
	    double retVal = 0.;
	    while (RooCatType* qfty =
		    reinterpret_cast<RooCatType*>(qfit->Next())) {
		// skip qf states not in range if the category has a range of that
		// name (if there's no range of rangeName in qf, we use all qf
		// states)
		if (qf.hasRange(m_rangeName) &&
			!qf.isStateInRange(m_rangeName, qfty->GetName()))
		    continue;
		const int iqf = qfty->getVal();
		// loop over qt states
		const RooCategory& qt(
			dynamic_cast<const RooCategory&>(m_parent.m_qt.arg()));
		std::auto_ptr<TIterator> qtit(qt.typeIterator());
		while (RooCatType* qtty =
			reinterpret_cast<RooCatType*>(qtit->Next())) {
		    // skip qt states not in range if the category has a range of that
		    // name (if there's no range of rangeName in qt, we use all qt
		    // states)
		    if (qt.hasRange(m_rangeName) &&
			    !qt.isStateInRange(m_rangeName, qtty->GetName()))
			continue;
		    retVal += eval(iqf, qtty->getVal());
		}
	    }
	    return retVal;
	}
    }
    // must not arrive here
    assert(1 == 0);
    return std::numeric_limits<double>::quiet_NaN();
}

// vim: sw=4:tw=78:ft=cpp
