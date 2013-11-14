/**
 * @file TagCombiner.h
 *
 * utilities and classes to combine uncorrelated taggers
 *
 * @author Manuel Schiller <manuel.schiller@nikhef.nl>
 * @date 2013-10-26
 */
#ifndef TAGCOMBINER_H
#define TAGCOMBINER_H

#include <cmath>
#include <cassert>
#include <limits>
#include <iostream>
#include <numeric>

#include "Math/SVector.h"

/// tools for tagging combinations
namespace TagTools {
    /// tagging decision
    typedef enum { Bbar = -1, Untagged = 0, B = 1 } TagDec;

    /// convert pair (tagging decision, mistag eta) to tagging DLL
    static inline double tagDLL(TagDec dec, double eta)
    {
	assert(Bbar == dec || Untagged == dec || B == dec);
	/// regularise eta and dec
	if (Untagged == dec) {
	    eta = 0.5;
	} else {
	    if (eta <= 0.) {
		eta = std::numeric_limits<double>::min();
	    } else if (eta >= 0.5) {
		eta = 0.5;
		dec = Untagged;
	    }
	}
	const double tmp = (Untagged == dec) ? 0. :
	    (double(int(dec)) * (0.5 - eta));
        const double pb = 0.5 + tmp, pbar = 0.5 - tmp;
	assert(0. <= pb && pb <= 1.);
	assert(0. <= pbar && pbar <= 1.);
        // dll = log(pb) - log(bbar)
        return std::log(pb) - std::log(pbar);
    }

    /// convert tagging DLL to tagging decision
    static inline TagDec tagDec(double dll)
    { return (dll > 0.) ? B : ((dll < 0.) ? Bbar : Untagged); }

    /// convert tagging DLL to mistag eta
    static inline double tagEta(double dll)
    { return 1. / (1. + std::exp(std::abs(dll))); }

    /// efficient and numerically stable evaluation of polynomials
    namespace PolyEvalHelpers {
	/// recursive evaluation in the Horner scheme
	template<unsigned NC, unsigned NR> struct PolyEval
	{
	    double operator()(const double coeff[], double x) const
	    { return PolyEval<NC + 1, NR - 1>()(coeff, x) * x + coeff[NC]; }
	};

	/// template specialisation to terminate recursive evaluation
	template<unsigned NC> struct PolyEval<NC, 0u>
	{
	    double operator()(const double coeff[], double /* x */) const
	    { return coeff[NC]; }
	};
    }

    /** @brief evaluate tagging calibration polynomial
     *
     * @author Manuel Schiller <manuel.schiller@nikhef.nl>
     * @date 2013-10-26
     *
     * @tparam N	degree of calibration polynomial
     * @param eta	(uncalibrated) mistag @f$\eta@f$
     * @param aveta	average mistag @f$\langle\eta\rangle@f$
     * @param p		calibration parameters @f$ p_0, p_1, \ldots , p_N @f$
     *
     * @returns calibrated mistag @f$\eta_c@f$
     *
     * The calibrated mistag is calculated according to:
     *
     * @f[ \eta_c = \sum_{k=0}^N p_k \cdot (\eta-\langle\eta\rangle)^k @f]
     */
    template<unsigned N> static inline double evalCalibPoly(
	    double eta, double aveta, const double p[N + 1u])
    {
	const double deta = eta - aveta;
	return PolyEvalHelpers::PolyEval<0, N>()(p, deta);
    }

    /** @brief class to combine (uncorrelated) taggers
     *
     * @author Manuel Schiller <manuel.schiller@nikhef.nl>
     * @date 2013-10-26
     *
     * @tparam N		 number of taggers to combine
     *
     * Combination of (uncorrelated) taggers is most easily
     * achieved by transforming the output of each tagger into a so-called
     * Tagging DLL. If the @f$k@f$-th tagger produces a decision @f$d_k@f$ and
     * a mistag prediction @f$\eta_k@f$, this is best converted to a
     * probablility for the event to contain a @f$b@f$ (@f$\overline{b}@f$)
     * quark, @f$P_b^{(k)}@f$ (@f$P_{\overline{b}}^{(k)}@f$). The Tagging DLL
     * for that tagger is defined through the likelihood ratio:
     *
     * @f[ DLL_k = \log\left(\frac{P_b^{(k)}}{P_{\overline{b}}^{(k)}}\right)
     * @f]
     *
     * The combination of uncorrelated taggers can then be written as sum over
     * the contributing DLLs of the individual taggers:
     *
     * @f[ DLL_{\mathrm{comb}} = \sum_{k=1}^N DLL_k @f]
     *
     * Using the combiner is remarkably easy:
     *
     * @code
     * // combine five taggers
     * enum { N = 5 };
     * // tag combiner (assuming uncorrelated taggers)
     * TagTools::TagCombiner<N> combiner();
     *
     * // loop over candidates
     * for (unsigned iCand = 0; iCand < nCands; ++iCand) {
     *     // tagging decisions and predicted mistags
     *     TagTools::TagCombiner<N>::DLLVector dlls;
     *     for (unsigned i = 0; i < N; ++i) {
     *         TagTools::TagDec dec;
     *         double eta;
     *         // get tagging decision dec and predicted mistag eta for tagger
     *         // i, (re-)calibrate if necessary
     *
     *         // when all is done, compute tagging DLL
     *         dlls[i] = TagTools::tagDLL(dec, eta);
     *     }
     *     double combDLL = combiner.combine(dlls);
     *     TagTools::TagDec dec = tagDec(combDLL);
     *     double eta = tagEta(combDLL);
     *     // save combined tagging decision dec and mistag prediction etas
     *     // somewhere
     * }
     * @endcode
     */
    template<unsigned N>
    class TagCombiner
    {
	public:
	    /// vector of tagging DLLs
	    typedef ROOT::Math::SVector<double, N> DLLVector;

	    /** @brief constructor
	     * 
	     * combine a number of uncorrelated taggers
	     */
	    TagCombiner() { }

	    /// combine a set of taggers
	    double combine(const DLLVector& dllvect)
	    {
		// sum up decorrelated DLL contributions to combine the taggers
		const double dll = std::accumulate(
			dllvect.begin(), dllvect.end(), 0.);
		return dll;
	    }

	    /// combine a set of taggers
	    double combine(const double dlls[N])
	    { return combine(DLLVector(&dlls[0], &dlls[N])); }

	    /// combine a set of taggers
	    double combine(const TagDec decs[N], const double etas[N])
	    {
		DLLVector dlls;
		for (unsigned i = 0; i < N; ++i) dlls[i] = tagDLL(decs[i], etas[i]);
		return combine(dlls);
	    }

	private:
    };
}

#endif // TAGCOMBINER_H

// vim: sw=4:tw=78:ft=cpp
