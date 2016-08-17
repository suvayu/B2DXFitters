/*****************************************************************************
 * Project: RooFit                                                           *
 * Package: RooFitModels                                                     *
 * @(#)root/roofit:$Id: RooBSpline.cxx 45780 2012-08-31 15:45:27Z moneta $
 * Authors:                                                                  *
 *   Manuel Schiller
 *                                                                           *
 *****************************************************************************/

//////////////////////////////////////////////////////////////////////////////
//
// BEGIN_HTML
// Swimming Acceptance (series of turning points), suitable for use in
// RooGaussEfficiencyModel as efficiency
// END_HTML
//
// STD & STL
#include <algorithm>
#include <cmath>
#include <complex>
#include <numeric>
#include <limits>

// ROOT
#include "TH1.h"
#include "TMath.h"

// RooFit
#include "Riostream.h"
#include "RooAbsCategory.h"
#include "RooAbsReal.h"
#include "RooArgList.h"
#include "RooConstVar.h"
#include "RooFit.h"
#include "RooMath.h"
#include "RooMsgService.h"
#include "RooRealVar.h"

// B2DXFitters
#include "B2DXFitters/RooSwimmingAcceptance.h"

bool RooSwimmingAcceptance::updateTPs(double min, double max) const
{
    //assert(min <= max);
    m_tps.clear();
    bool retVal = !m_initialTPState;
    RooFIter fit = m_tpList.fwdIterator();
    const RooAbsReal *ptp = nullptr;
    double tp = -std::numeric_limits<double>::infinity();
    unsigned n = m_nTp;
    // start by skipping the turning points < min, keep track of state of
    // acceptance (on/off) in retVal
    while (n-- && (retVal = !retVal,
                ptp = static_cast<const RooAbsReal*>(fit.next())) &&
            (tp = ptp->getVal()) < min) {}
    // add the first TP to m_tps restricted to the range [min, max], keep track
    // if it's turning the acceptance on or off
    if (min < tp && tp < max) m_tps.push_back(min), retVal = !retVal;
    if (tp < max) m_tps.push_back(tp);
    // add the remaining TP < max
    while (n-- && (ptp = static_cast<const RooAbsReal*>(fit.next())) &&
            (tp = ptp->getVal()) < max) {
        m_tps.push_back(tp);
    }
    // and end with max
    m_tps.push_back(max);
    //assert(m_tps.size() >= 2);
    //assert(std::is_sorted(m_tps.begin(), m_tps.end()));
    return retVal;
}

RooSwimmingAcceptance::RooSwimmingAcceptance()
{}

RooSwimmingAcceptance::RooSwimmingAcceptance(const char* name, const char* title,
    RooRealVar& x, RooAbsCategory& nTurningPoints, const RooArgList& turningPoints,
    InitialTurningPointState initialTurningPoint)
    : RooAbsGaussModelEfficiency(name, title)
    , m_initialTPState(On == initialTurningPoint)
    , m_x("x", "Dependent", this, x)
    , m_nTp("nTp", "number of turning points", this, nTurningPoints)
    , m_tpList("tpList", "List of turning points", (RooAbsArg*)this)
{
    m_tpList.add(turningPoints);
    m_tps.reserve(m_tpList.getSize() + 2);
    m_M.reserve(m_tpList.getSize() + 2);
}

RooSwimmingAcceptance::RooSwimmingAcceptance(const RooSwimmingAcceptance& other, const char* name)
    : RooAbsGaussModelEfficiency(other, name)
    , m_initialTPState(other.m_initialTPState)
    , m_x("x", this, other.m_x)
    , m_nTp("nTp", this, other.m_nTp)
    , m_tpList("tpList", this, other.m_tpList)
{
    m_tps.reserve(m_tpList.getSize() + 2);
    m_M.reserve(m_tpList.getSize() + 2);
}

RooSwimmingAcceptance::~RooSwimmingAcceptance()
{}

Double_t RooSwimmingAcceptance::evaluate() const
{
    bool state = !updateTPs();
    const double x = m_x;
    auto it = std::upper_bound(m_tps.begin(), m_tps.end(), x);
    if (m_tps.begin() != it && x == *(it - 1)) --it;
    state ^= std::distance(m_tps.begin(), it) & 1;
    return state;
}

Int_t RooSwimmingAcceptance::getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars,
    const char* /* rangeName */) const
{
    if (matchArgs(allVars, analVars, m_x))
        return 1;
    return 0;
}

Double_t RooSwimmingAcceptance::analyticalIntegral(Int_t code, const char* rangeName) const
{
    if (code != 1) {
        coutE(InputArguments) << "RooSwimmingAcceptance::analyticalIntegral(" << GetName()
                              << "): argument \"code\" can only have value 1" << std::endl;
        assert(code == 1);
    }
    const RooAbsRealLValue& xa = static_cast<const RooAbsRealLValue&>(m_x.arg());
    bool state = updateTPs(xa.getMin(rangeName), xa.getMax(rangeName));
    m_tps.erase(
        std::adjacent_difference(m_tps.begin() + !state, m_tps.end(),
                                  m_tps.begin()),
        m_tps.end());
    int i = 0;
    m_tps.erase(std::remove_if(m_tps.begin(), m_tps.end(), [&i] (double)
        { return (++i) & 1; }), m_tps.end());
    return std::accumulate(m_tps.begin(), m_tps.end(), 0.);
}

std::complex<double> RooSwimmingAcceptance::productAnalyticalIntegral(
    Double_t umin, Double_t umax, Double_t scale, Double_t _offset,
    const std::complex<double>& z) const
{
    const double lo = scale * umin + _offset;
    const double hi = scale * umax + _offset;
    bool accState = updateTPs(lo, hi);
    //assert(m_tps.size() >= 2);
    typedef typename decltype(m_M)::value_type M_n;
    m_M.clear();
    std::transform(m_tps.begin(), m_tps.end(), std::back_inserter(m_M),
        [z, _offset, scale] (double x)
        { return M_n((x - _offset) / scale, z); });
    //TODO: verify we remain within [lo,hi]
    //assert(std::abs(lo - m_tps.front()) <= 1e-7 * std::abs(lo + m_tps.front()));
    //assert(std::abs(hi - m_tps.back()) <= 1e-7 * std::abs(hi + m_tps.back()));
    const RooGaussModelAcceptance::K_n K(z);
    const std::complex<double> Kval = K(0);
    // FIXME:TODO: we currently assume that m_tps(0),m_tps(knotSize()-1)] fully contained in [lo,hi]
    // take M[i] if lo<=m_tps(i) else M_n(lo) ; take M[i+1] if m_tps(i+1)<=hi else M_n(hi)
    std::adjacent_difference(m_M.begin(), m_M.end(), m_M.begin());
    return std::accumulate(m_M.begin() + 1, m_M.end(), std::complex<double>(0, 0),
        [&Kval, &accState] (std::complex<double> sum, const M_n& dM)
        { accState = !accState; return sum + dM(0) * Kval * double(!accState); });
}

Int_t RooSwimmingAcceptance::getMaxVal(const RooArgSet& vars) const
{
    // check that vars only contains _x...
    return (vars.getSize() == 1 && vars.contains(m_x.arg())) ? 1 : 0;
}

Double_t RooSwimmingAcceptance::maxVal(Int_t code) const
{
    if (code != 1) {
        coutE(InputArguments) << "RooSwimmingAcceptance::maxVal(" << GetName()
                              << "): argument \"code\" can only have value 1" << std::endl;
        assert(code == 1);
    }
    return 1;
}

std::list<Double_t>* RooSwimmingAcceptance::binBoundaries(RooAbsRealLValue& obs,
    Double_t xlo, Double_t xhi) const
{
    // Check that we have observable, if not no binning is returned
    if (m_x.arg().GetName() != obs.GetName()) return 0;
    updateTPs(xlo, xhi);
    std::list<Double_t>* bounds = new std::list<Double_t>;
    std::copy(m_tps.begin(), m_tps.end(), std::back_inserter(*bounds));
    return bounds;
}
