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
RooConstVar NonOscTaggingPdf::s_one("one", "1.0", 1.0);

NonOscTaggingPdf::NonOscTaggingPdf(const char* name, const char* title,
	RooAbsCategory& qf, RooAbsCategory& qt,
	RooAbsRealLValue& etaobs, RooAbsPdf& etapdf,
	RooAbsReal& epsilon, RooAbsReal& adet,
	RooAbsReal& atageff_f, RooAbsReal& atageff_t) :
    RooAbsPdf(name, title),
    m_qf("qf", "qf", this, qf), m_qts("qts", "qts", this),
    m_etaobs("etaobs", "etaobs", this, etaobs),
    m_etapdfs("etapdfs", "etapdfs", this),
    m_etapdfutinstance(
	    (std::string(GetName()) + "_untagged").c_str(),
	    (std::string(GetName()) + "_untagged").c_str(),
	    RooArgSet(etaobs)),
    m_epsilons("epsilons", "epsilons", this),
    m_adet("adet", "adet", this, adet),
    m_atageffs_f("atageffs_f", "atageffs_f", this),
    m_atageffs_t("atageffs_t", "atageffs_t", this),
    m_cacheMgr(this)
{
    assert(checkDepsForConsistency(
		RooArgSet(qf, qt, etaobs),
		RooArgSet(etapdf, epsilon, adet, atageff_f, atageff_t),
		&etaobs, RooArgSet(etapdf)));
    m_qts.add(qt);
    initListProxies(RooArgList(epsilon),
	    RooArgList(atageff_f), RooArgList(atageff_t), RooArgList(etapdf));
}

NonOscTaggingPdf::NonOscTaggingPdf(const char* name, const char* title,
	RooAbsCategory& qf, RooAbsCategory& qt,
	RooAbsReal& epsilon, RooAbsReal& adet,
	RooAbsReal& atageff_f, RooAbsReal& atageff_t) :
    RooAbsPdf(name, title),
    m_qf("qf", "qf", this, qf), m_qts("qts", "qts", this),
    m_epsilons("epsilons", "epsilons", this),
    m_adet("adet", "adet", this, adet),
    m_atageffs_f("atageffs_f", "atageffs_f", this),
    m_atageffs_t("atageffs_t", "atageffs_t", this),
    m_cacheMgr(this)
{
    assert(checkDepsForConsistency(
		RooArgSet(qf, qt),
		RooArgSet(epsilon, adet, atageff_f, atageff_t)));
    m_qts.add(qt);
    initListProxies(RooArgList(epsilon),
	    RooArgList(atageff_f), RooArgList(atageff_t));
}

NonOscTaggingPdf::NonOscTaggingPdf(const char* name, const char* title,
	RooAbsCategory& qf, RooAbsCategory& qt,
	RooAbsRealLValue& etaobs, RooArgList& etapdfs,
	RooArgList& epsilons, RooAbsReal& adet,
	RooArgList& atageffs_f, RooArgList& atageffs_t) :
    RooAbsPdf(name, title),
    m_qf("qf", "qf", this, qf), m_qts("qts", "qts", this),
    m_etaobs("etaobs", "etaobs", this, etaobs),
    m_etapdfs("etapdfs", "etapdfs", this),
    m_etapdfutinstance(
	    (std::string(GetName()) + "_untagged").c_str(),
	    (std::string(GetName()) + "_untagged").c_str(),
	    RooArgSet(etaobs)),
    m_epsilons("epsilons", "epsilons", this),
    m_adet("adet", "adet", this, adet),
    m_atageffs_f("atageffs_f", "atageffs_f", this),
    m_atageffs_t("atageffs_t", "atageffs_t", this),
    m_cacheMgr(this)
{
    RooArgSet params(adet);
    params.add(etapdfs);
    params.add(epsilons);
    params.add(atageffs_f);
    params.add(atageffs_t);
    assert(checkDepsForConsistency(
		RooArgSet(qf, qt, etaobs), params, &etaobs, etapdfs));
    m_qts.add(qt);
    initListProxies(epsilons, atageffs_f, atageffs_t, etapdfs);
}

NonOscTaggingPdf::NonOscTaggingPdf(const char* name, const char* title,
	RooAbsCategory& qf, RooAbsCategory& qt,
	RooArgList& epsilons, RooAbsReal& adet,
	RooArgList& atageffs_f, RooArgList& atageffs_t) :
    RooAbsPdf(name, title),
    m_qf("qf", "qf", this, qf), m_qts("qts", "qts", this),
    m_epsilons("epsilons", "epsilons", this),
    m_adet("adet", "adet", this, adet),
    m_atageffs_f("atageffs_f", "atageffs_f", this),
    m_atageffs_t("atageffs_t", "atageffs_t", this),
    m_cacheMgr(this)
{
    RooArgSet params(adet);
    params.add(epsilons);
    params.add(atageffs_f);
    params.add(atageffs_t);
    assert(checkDepsForConsistency(RooArgSet(qf, qt), params));
    m_qts.add(qt);
    initListProxies(epsilons, atageffs_f, atageffs_t);
}

NonOscTaggingPdf::NonOscTaggingPdf(
	const NonOscTaggingPdf& other, const char* name) :
    RooAbsPdf(other, name),
    m_qf("qf", this, other.m_qf), m_qts("qts", this, other.m_qts),
    m_etaobs("etaobs", this, other.m_etaobs),
    m_etapdfs("etapdfs", "etapdfs", this),
    m_etapdfutinstance(other.m_etapdfutinstance),
    m_epsilons("epsilons", this, other.m_epsilons),
    m_adet("adet", this, other.m_adet),
    m_atageffs_f("atageffs_f", this, other.m_atageffs_f),
    m_atageffs_t("atageffs_t", this, other.m_atageffs_t),
    m_cacheMgr(other.m_cacheMgr, this)
{
    // no need to verify constraints as in other constructors - we make a copy
    // of something that has already been verified
    if (m_etaobs.absArg()) {
	RooFIter it = other.m_etapdfs.fwdIterator();
	// skip other.m_etapdfutinstance;
	it.next();
	m_etapdfs.add(m_etapdfutinstance);
	for (RooAbsArg* arg = it.next(); arg; arg = it.next())
	    m_etapdfs.add(*arg);
    }
}

NonOscTaggingPdf::~NonOscTaggingPdf() { }

TObject* NonOscTaggingPdf::clone(const char* newname) const
{ return new NonOscTaggingPdf(*this, newname); }

bool NonOscTaggingPdf::checkDepsForConsistency(
	const RooArgSet& obs, const RooArgSet& params,
	const RooAbsArg* etaobs, const RooArgSet& etas) const
{
    // observables must not overlap with one another, or be constant
    RooFIter it = obs.fwdIterator();
    for (RooAbsArg* o1 = it.next(); o1; o1 = it.next()) {
	if (o1->isConstant()) continue;
	RooFIter jt = it;
	for (RooAbsArg* o2 = jt.next(); o2; o2 = jt.next()) {
	    if (o1->overlaps(*o2) && !o2->isConstant()) return false;
	}
    }

    // paramers must not overlap with observables, be constant or inherit from
    // TaggingCat
    it = params.fwdIterator();
    for (RooAbsArg* o1 = it.next(); o1; o1 = it.next()) {
	if (o1->isConstant()) continue;
	if (o1->InheritsFrom("TaggingCat")) continue;
	const bool isMistag = (0 != etas.find(*o1));
	// check out overlap with observables
	RooFIter jt = obs.fwdIterator();
	for (RooAbsArg* o2 = jt.next(); o2; o2 = jt.next()) {
	    if (isMistag && o2 == etaobs) continue;
	    if (o1->overlaps(*o2) && !o2->isConstant()) return false;
	}
    }

    return true;
}

unsigned NonOscTaggingPdf::getMaxQt() const
{
    assert(1 == m_qts.getSize());
    TIterator *it =
	dynamic_cast<const RooAbsCategory&>(*m_qts.at(0)).typeIterator();
    unsigned maxqt = 0u;
    for (RooCatType* cat = dynamic_cast<RooCatType*>(it->Next()); cat;
	    cat = dynamic_cast<RooCatType*>(it->Next())) {
	const unsigned idx = std::abs(cat->getVal());
	if (idx > maxqt) maxqt = idx;
    }
    delete it;
    return maxqt;
}

void NonOscTaggingPdf::fillListProxy(RooListProxy& proxy,
	const RooArgList& list, const RooArgList& listbar,
	const RooAbsArg& zeroelem) const
{
    const unsigned idxend = 1u + (2u * getMaxQt());
    for (unsigned idx = 0; idx < idxend; ++idx) {
	const int qt = qtFromIdx(idx);
	const int absqt = std::abs(qt);
	if (!qt) {
	    proxy.add(zeroelem);
	} else if (qt < 0) {
	    const int listidx = std::min(absqt - 1, listbar.getSize() - 1);
	    proxy.add(*listbar.at(listidx));
	} else {
	    const int listidx = std::min(absqt - 1, list.getSize() - 1);
	    proxy.add(*list.at(listidx));
	}
    }
}

void NonOscTaggingPdf::initListProxies(
	const RooArgList& tageffs,
	const RooArgList& atageffs_f,
	const RooArgList& atageffs_t,
	const RooArgList& etapdfs)
{
   // nothing in slot for (qt = 0), so put dummy value there
   fillListProxy(m_epsilons, tageffs, tageffs, s_one);
   // last one is dummy (tagging efficiency asymmetry makes no sense for
   // qt = 0)
   fillListProxy(m_atageffs_f, atageffs_f, atageffs_f, s_one);
   fillListProxy(m_atageffs_t, atageffs_t, atageffs_t, s_one);
   if (etapdfs.getSize()) {
       fillListProxy(m_etapdfs, etapdfs, etapdfs, m_etapdfutinstance);
   }
}

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
    assert(1 == m_qts.getSize());
    if (&dep == m_qf.absArg()) return kTRUE;
    if (&dep == m_qts.at(0)) return kTRUE;
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
    assert(1 == m_qts.getSize());
    // we know how to integrate over etaobs, qf, qt
    if (m_etaobs.absArg()) {
	matchArgs(allVars, anaIntVars, m_etaobs);
    }
    matchArgs(allVars, anaIntVars, m_qf);
    matchArgs(allVars, anaIntVars, *m_qts.at(0));
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
    m_parent(parent), m_etapdfint(1u + 2u * parent.getMaxQt(), 0),
    m_rangeName(rangeName ? rangeName->GetName() : 0),
    m_qtmax(parent.getMaxQt()), m_flags(None)
{
    assert(1 == parent.m_qts.getSize());
    // set flag for qf/qt integration
    if (iset.find(parent.m_qf.arg()))
        m_flags = static_cast<Flags>(m_flags | IntQf);
    if (iset.find(*parent.m_qts.at(0)))
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
	for (int qt = -m_qtmax; qt <= int(m_qtmax); ++qt) {
	    const unsigned idx = NonOscTaggingPdf::idxFromQt(qt);
	    RooAbsPdf* etapdf = dynamic_cast<RooAbsPdf*>(
		    parent.m_etapdfs.at(idx));
	    if (m_flags & IntEta) {
		// we really integrate over eta
		RooArgSet etaiset(parent.m_etaobs.arg());
		RooArgSet* etanset = nset ? &m_nset : 0;
		m_etapdfint[idx] = etapdf->createIntegral(
			etaiset, etanset, 0, m_rangeName);
	    } else {
		m_etapdfint[idx] = etapdf;
	    }
	}
    }
}

NonOscTaggingPdf::CacheElem::~CacheElem()
{
    if (m_flags & IntEta) {
	for (unsigned i = 0; i < m_etapdfint.size(); ++i)
	    delete m_etapdfint[i];
    }
}

RooArgList NonOscTaggingPdf::CacheElem::containedArgs(Action)
{
    assert(1 == m_parent.m_qts.getSize());
    RooArgList retVal;
    if (!(m_flags & IntQf)) retVal.add(m_parent.m_qf.arg());
    if (!(m_flags & IntQt)) retVal.add(*m_parent.m_qts.at(0));
    for (unsigned i = 0; i < m_etapdfint.size(); ++i) {
	if (!m_etapdfint[i]) continue;
	if (retVal.find(*m_etapdfint[i])) continue;
	retVal.add(*m_etapdfint[i]);
    }
    if (!(m_flags & IntEta)) {
	if (m_parent.m_etaobs.absArg()) {
	    retVal.add(m_parent.m_etaobs.arg());
	    RooFIter it = m_parent.m_etapdfs.fwdIterator();
	    for (RooAbsArg *obj = it.next(); obj; obj = it.next()) {
		if (retVal.find(*obj)) continue;
		retVal.add(*obj);
	    }
	}
    }
    retVal.add(m_parent.m_adet.arg());
    RooFIter it = m_parent.m_epsilons.fwdIterator();
    for (RooAbsArg *obj = it.next(); obj; obj = it.next()) {
	if (retVal.find(*obj)) continue;
	retVal.add(*obj);
    }
    it = m_parent.m_atageffs_f.fwdIterator();
    for (RooAbsArg *obj = it.next(); obj; obj = it.next()) {
	if (retVal.find(*obj)) continue;
	retVal.add(*obj);
    }
    it = m_parent.m_atageffs_t.fwdIterator();
    for (RooAbsArg *obj = it.next(); obj; obj = it.next()) {
	if (retVal.find(*obj)) continue;
	retVal.add(*obj);
    }
    return retVal;
}

double NonOscTaggingPdf::CacheElem::etapdfint(const int qt) const
{
    const unsigned idx = NonOscTaggingPdf::idxFromQt(qt);
    return (m_etapdfint.empty() || !m_etapdfint[idx]) ? 1. :
	m_etapdfint[idx]->getVal((m_flags & NormEta) ? &m_nset : 0);
}

double NonOscTaggingPdf::CacheElem::qfpdf(const int qf) const
{
    assert(1 == std::abs(qf));
    return .5 * (1. + double(qf) * double(m_parent.m_adet));
}

double NonOscTaggingPdf::CacheElem::qtetapdf(const int qf, const int qt) const
{
    assert(1 == std::abs(qf));
    assert(unsigned(std::abs(qt)) <= m_qtmax);
    if (qt) {
	const unsigned idx = NonOscTaggingPdf::idxFromQt(qt);
	const double atf(((RooAbsReal*) m_parent.m_atageffs_f.at(idx))->getVal());
	const double att(((RooAbsReal*) m_parent.m_atageffs_t.at(idx))->getVal());
	const double eps(((RooAbsReal*) m_parent.m_epsilons.at(idx))->getVal());
	const int sqt = (qt < 0) ? -1 : 1;
	return 0.25 * etapdfint(qt) * eps *
	    (1. + double(qf) * atf) * (1. + double(sqt) * att);
    } else {
	// sum up the contribution of tagged events for both qf = -1 and qf =
	// 1; what's left is the efficiency of qt = 0 events, and half of it
	// goes to qf = -1 and half to qf = 1. (that way, asymmetries in
	// detection are handled completely by the detection asymmetry)
	double eps = 1.;
	for (unsigned iqt = 1; iqt <= m_qtmax; ++iqt) {
	    const unsigned idx = NonOscTaggingPdf::idxFromQt(iqt);
	    const double e(((RooAbsReal*)
			m_parent.m_epsilons.at(idx))->getVal());
	    eps -= e;
	}
	return 0.5 * etapdfint(qt) * eps;
    }
    // must never get here
    assert(1 == 0);
    return std::numeric_limits<double>::quiet_NaN();
}

double NonOscTaggingPdf::CacheElem::eval(const int qf, const int qt) const
{ return qfpdf(qf) * qtetapdf(qf, qt); }

double NonOscTaggingPdf::CacheElem::eval() const
{
    assert(1 == m_parent.m_qts.getSize());
    if (!(m_flags & (IntQf | IntQt))) {
	const int iqt(dynamic_cast<RooAbsCategory&>(
		    *m_parent.m_qts.at(0)).getIndex());
	// no qf or qt integration
	return eval(int(m_parent.m_qf), iqt);
    } else if ((m_flags & IntQf) && !(m_flags & IntQt)) {
	// integrate over qf
	const int iqt(dynamic_cast<RooAbsCategory&>(
		    *m_parent.m_qts.at(0)).getIndex());
	const double atf = (!iqt) ? 0. :
	    dynamic_cast<RooAbsReal&>(*m_parent.m_atageffs_f.at(
			NonOscTaggingPdf::idxFromQt(iqt))).getVal();
	if (0. == std::abs(atf)) {
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
	    return qfint * qtetapdf(1, iqt);
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
		retVal += eval(qfty->getVal(), iqt);
	    }
	    return retVal;
	}
    } else if (!(m_flags & IntQf) && (m_flags & IntQt)) {
	// loop over qt states
        const RooCategory& qt(
                dynamic_cast<const RooCategory&>(*m_parent.m_qts.at(0)));
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
	// check if we can optimise by factorising the integrals
	bool factorises = true;
	for (int qt = -m_qtmax; qt <= int(m_qtmax); ++qt) {
	    if (!qt) continue;
	    const unsigned idx = NonOscTaggingPdf::idxFromQt(qt);
	    const double att(((RooAbsReal*)
			m_parent.m_atageffs_t.at(idx))->getVal());
	    const double atf(((RooAbsReal*)
			m_parent.m_atageffs_f.at(idx))->getVal());
	    if (0. != std::abs(att) || 0. != std::abs(atf)) {
		factorises = false;
		break;
	    }
	}
	if (factorises) {
	    double qfint = 0., qtint = 0.;
	    // loop over qf states in range
	    const RooCategory& qf(
		    dynamic_cast<const RooCategory&>(m_parent.m_qf.arg()));
	    std::auto_ptr<TIterator> qfit(qf.typeIterator());
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
	    // loop over qt states in range
	    const RooCategory& qt(
		    dynamic_cast<const RooCategory&>(*m_parent.m_qts.at(0)));
	    std::auto_ptr<TIterator> qtit(qt.typeIterator());
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
			dynamic_cast<const RooCategory&>(*m_parent.m_qts.at(0)));
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
