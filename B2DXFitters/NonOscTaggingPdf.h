/** @file NonOscTaggingPdf.h
 *
 * tagging behaviour and asymmetries for non-oscillating backgrounds
 */
#ifndef NONOSCTAGGINGPDF
#define NONOSCTAGGINGPDF

#include <cmath>
#include <cassert>
#include <vector>

#include <RooAbsPdf.h>
#include <RooAbsReal.h>
#include <RooUniform.h>
#include <RooRealProxy.h>
#include <RooConstVar.h>
#include <RooListProxy.h>
#include <RooAbsCategory.h>
#include <RooCategoryProxy.h>

/** @brief tagging behaviour and asymmetries for non-oscillating backgrounds
 *
 * @author Manuel Schiller <manuel.schiller@nikhef.nl>
 * @date 2012-11-15
 * * initial release
 *
 * @author Manuel Schiller <manuel.schiller@nikhef.nl>
 * @date 2013-11-17
 * * major code refactoring to allow to switch between different taggers
 *   depending on the value of qt
 * * the new version of the class is source compatible with the old version -
 *   existing code need to be changed to get the old functionality
 * * however, the persistent form of the class is incompatible with the old
 *   version, so that old RooFit workspaces which contain DecRateCoeff
 *   instances can no longer be read
 * * put in the necessary ground work to extend the functionality of the class
 *   to do the combination of taggers inside the DecRateCoeff class at some
 *   point in the future without breaking persistency again
 *
 * This class provides the tagging behaviour and asymmetries for
 * non-oscillating backgrounds. For a single tagger, the pdf can be written as
 * @f$P(q_f)\cdot P(q_t|q_f)\cdot P(\eta|q_t)@f$ with:
 *
 * @f[P(q_f) \sim (1+q_f\cdot a_{det})/2@f]
 * @f[P(q_t|q_f) \sim \left\{\begin{array}{l l}
 * \left(1-\sum_{q_f,q_t\ne 0}\epsilon\cdot(1+q_f\cdot a^f_{tageff})
 * \cdot(1+q_t\cdot a^t_{tageff})/4\right)/2 & \textrm{if $q_t=0$} \\
 * \epsilon\cdot(1+q_f\cdot a^f_{tageff})\cdot(1+q_t\cdot a^t_{tageff})/4 &
 * \textrm{if $|q_t|=1$} \\
 * \end{array}\right. @f]
 * @f[P(\eta|q_t) \sim \left\{\begin{array}{l l}
 * U(\eta) & \textrm{if $q_t = 0$} \\
 * P(\eta) & \textrm{if $|q_t| = 1$} \\
 * \end{array}\right. @f]
 *
 * This class can also handle several mutually exclusive taggers. To this end,
 * the meaning of the tagging decision @f$q_t@f$ is generalised: @f$q_t=0@f$
 * means the event is untagged, @f$|q_t| = k@f$ means the event was tagged by
 * tagger @f$k@f$, and the sign of @f$q_t@f$ inicates if the event was tagged
 * as a B (positive) or B bar (negative). Each tagger has its own tagging
 * efficiency, tagging efficiency asymmetries @f$a^t_{tageff}@f$ and
 * @f$a^f_{tageff}@f$ and mistag distribution, if applicable.
 *
 * This construction also allows to treat uncorrelated taggers. By using the
 * convention @f$|q_t|=\sum_{k=1}^N |d_k|\cdot 2^k@f$ where @f$d_k@f$ is the
 * decision of the k-th tagger, we get mutually exclusive "tagging categories"
 * which allow the formalism described in the last paragraph to work. For
 * example, for two independent taggers OS (k=1) and SSK (k =2), we would get
 * @f$|q_t| = 0@f$ for untagged events, @f$|q_t|=1@f$ for events tagged only by
 * OS and not by SSK, @f$|q_t|=2@f$ for events tagged only by SSK and not by
 * OS, and @f$|q_t|=3@f$ for events tagged only by both OS and SSK.
 */
class NonOscTaggingPdf : public RooAbsPdf
{
    private:
	class CacheElem; // forward declaration
	friend class CacheElem;
	/// pair of cache element and corresponding slot number in cache
	typedef std::pair<NonOscTaggingPdf::CacheElem*, Int_t> CacheElemPair;

    public:
	/// constructor for ROOT I/O
	inline NonOscTaggingPdf() {}

	/** @brief constructor for use with per-event mistag
	 *
	 * @param name		name of pdf
	 * @param title		title of pdf
	 * @param qf		final state charge (+/-1)
	 * @param qt		tagging decision (0,+/-1)
	 * @param etaobs	per-event mistag observable
	 * @param etapdf	eta pdf for tagged events
	 * @param epsilon	tagging efficiency
	 * @param adet		detection (charge) asymmetry
	 * @param atageff_f	tagging efficiency asymmetry (qf dependence)
	 * @param atageff_t	tagging efficiency asymmetry (qt dependence)
	 */
	NonOscTaggingPdf(const char* name, const char* title,
		RooAbsCategory& qf, RooAbsCategory& qt,
		RooAbsRealLValue& etaobs, RooAbsPdf& etapdf,
		RooAbsReal& epsilon, RooAbsReal& adet,
		RooAbsReal& atageff_f, RooAbsReal& atageff_t);

	/** @brief constructor for use with average mistag
	 *
	 * @param name		name of pdf
	 * @param title		title of pdf
	 * @param qf		final state charge (+/-1)
	 * @param qt		tagging decision (0,+/-1)
	 * @param epsilon	tagging efficiency
	 * @param adet		detection (charge) asymmetry
	 * @param atageff_f	tagging efficiency asymmetry (qf dependence)
	 * @param atageff_t	tagging efficiency asymmetry (qt dependence)
	 */
	NonOscTaggingPdf(const char* name, const char* title,
		RooAbsCategory& qf, RooAbsCategory& qt,
		RooAbsReal& epsilon, RooAbsReal& adet,
		RooAbsReal& atageff_f, RooAbsReal& atageff_t);

	/** @brief constructor for use with per-event mistag
	 *
	 * @param name		name of pdf
	 * @param title		title of pdf
	 * @param qf		final state charge (+/-1)
	 * @param qt		tagging decision (-N, ..., -1, 0, 1, ..., N)
	 * @param etaobs	per-event mistag observable
	 * @param etapdfs	eta pdfs for tagged events
	 * @param epsilons	tagging efficiencies
	 * @param adet		detection (charge) asymmetry
	 * @param atageffs_f	tagging efficiency asymmetries (qf dependence)
	 * @param atageffs_t	tagging efficiency asymmetries (qt dependence)
	 */
	NonOscTaggingPdf(const char* name, const char* title,
		RooAbsCategory& qf, RooAbsCategory& qt,
		RooAbsRealLValue& etaobs, RooArgList& etapdfs,
		RooArgList& epsilons, RooAbsReal& adet,
		RooArgList& atageffs_f, RooArgList& atageffs_t);

	/** @brief constructor for use with average mistag
	 *
	 * @param name		name of pdf
	 * @param title		title of pdf
	 * @param qf		final state charge (+/-1)
	 * @param qt		tagging decision (-N, ..., -1, 0, 1, ..., N)
	 * @param epsilons	tagging efficiencies
	 * @param adet		detection (charge) asymmetry
	 * @param atageffs_f	tagging efficiency asymmetries (qf dependence)
	 * @param atageffs_t	tagging efficiency asymmetries (qt dependence)
	 */
	NonOscTaggingPdf(const char* name, const char* title,
		RooAbsCategory& qf, RooAbsCategory& qt,
		RooArgList& epsilons, RooAbsReal& adet,
		RooArgList& atageffs_f, RooArgList& atageffs_t);

	/** @brief copy constructor
	 *
	 * @param other	pdf to copy
	 * @param name	name the copy should get
	 */
	NonOscTaggingPdf(const NonOscTaggingPdf& other, const char* name = 0);

	/** @brief clone pdf
	 *
	 * @param newname	name of the clone
	 * @returns		pointer to clone
	 */
	virtual TObject* clone(const char* newname) const;
	
	/// destructor
	virtual ~NonOscTaggingPdf();
	
	/// announce our intention to normalise ourselves
	virtual Bool_t selfNormalized() const;

	/// force use of analytical integrals
	virtual Bool_t forceAnalyticalInt(const RooAbsArg& dep) const;

	/// announce analytical integrals
	virtual Int_t getAnalyticalIntegral(
		RooArgSet& allVars, RooArgSet& anaIntVars,
		const char* rangeName = 0) const;

	/// provide analytical integrals
	virtual Double_t analyticalIntegral(
		Int_t code, const char* rangeName = 0) const;

	/// announce analytical integrals
	virtual Int_t getAnalyticalIntegralWN(
		RooArgSet& allVars, RooArgSet& anaIntVars,
		const RooArgSet* nset, const char* rangeName) const;

	/// provide analytical integrals
	virtual Double_t analyticalIntegralWN(Int_t code,
		const RooArgSet* nset, const char* rangeName) const;

    protected:
	/// return (unnormalised) value of pdf
	virtual Double_t evaluate() const;

	/// return (integral) cache element
	CacheElemPair getCache(
		const RooArgSet& iset, const RooArgSet* nset = 0,
		const TNamed* irangeName = 0) const;

		/** @brief consistency check to be used in constructor
	 *
	 * @param obs		set of observables
	 * @param params	set of other parameters
	 * @param etaobs	mistag observable (if set)
	 * @param etas		calibrated mistags (if non-empty)
	 *
	 * @returns true if sets valid input for construction of DecRateCoeff
	 *
	 * observables must not overlap with one another, and parameters must
	 * not overlap with observables, be constant or inherit from
	 * TaggingCat.
	 *
	 * tagging calibrations may (obviously) depend on the mistag
	 * observables.
	 */
	bool checkDepsForConsistency(
		const RooArgSet& obs, const RooArgSet& params,
		const RooAbsArg* etaobs = 0,
		const RooArgSet& etas = RooArgSet()) const;

	/// get maximial value of the index in qt
	unsigned getMaxQt() const;

	/// convert qt = -N, -N + 1, ..., -1, 0, 1, ..., N - 1, N to index
	static inline unsigned idxFromQt(int qt)
	{ return (qt < 0) ? (2u * (-qt) - 1u) : (2u * qt); }

	/// convert index to qt
	static inline int qtFromIdx(unsigned idx)
	{
	    const unsigned absqt = (1u + idx) / 2u;
	    return (idx & 1) ? -absqt : absqt;
	}

	/** @brief fill ListProxies, respecting conventions
	 *
	 * @param proxy		set proxy to fill
	 * @param list		what to fill with (qt > 0)
	 * @param listbar	what to fill with (qt < 0)
	 * @param zeroelem	what to fill with (qt == 0)
	 */
	void fillListProxy(RooListProxy& proxy,
		const RooArgList& list, const RooArgList& listbar,
		const RooAbsArg& zeroelem) const;

	/** @brief initialise our member list proxies with the RIGHT STUFF
	 *
	 * this routine factors out common functionality needed in the
	 * constructors
	 *
	 * @param tageffs	tagging efficiencies (|qt| = 1, ...)
	 * @param atageffs_f	tagging efficiency asymmetries (final state)
	 * @param atageffs_t	tagging efficiency asymmetries (tag. dec.)
	 * @param etapdfs	mistag distributions
	 */
	void initListProxies(
		const RooArgList& tageffs,
		const RooArgList& atageffs_f,
		const RooArgList& atageffs_t,
		const RooArgList& etapdfs = RooArgList());

    private:
	static RooArgSet s_emptyset;	///< empty set
	static RooConstVar s_one;	///< +1 (constant)

	RooCategoryProxy m_qf;		///< final state charge
	RooListProxy m_qts;		///< tagging decision(s)

	RooRealProxy m_etaobs;		///< eta observable
	RooListProxy m_etapdfs;		///< eta pdfs
	RooUniform m_etapdfutinstance;	///< inst. of eta pdf (untagged events)

	RooListProxy m_epsilons;	///< tagging efficiencies
	RooRealProxy m_adet;		///< detection (charge) asymmetry
	RooListProxy m_atageffs_f;	///< tagging efficiency asymmetries (qf)
	RooListProxy m_atageffs_t;	///< tagging efficiency asymmetries (qt)

	mutable RooObjCacheManager m_cacheMgr;	///< integral cache

	/// hold integral objects
	class CacheElem : public RooAbsCacheElement
        {
	    public:
		/// constructor
		CacheElem(const NonOscTaggingPdf& parent,
			const RooArgSet& iset, const RooArgSet* nset = 0,
			const TNamed* rangeName = 0);

		/// destructor
		virtual ~CacheElem();

		/// return list of contained RooFit variables
		virtual RooArgList containedArgs(Action);

		/// evaluate the cache element
		double eval() const;

	    protected:
		/// return eta pdf (integral)
		double etapdfint(const int qt) const;

		/// return P(qt)
		double qfpdf(const int qf) const;

		/// return P(qt, eta|qf)
		double qtetapdf(const int qf, const int qt) const;

		/// evaluate for given values of qf, qt
		double eval(const int qf, const int qt) const;

	    private:
		const NonOscTaggingPdf& m_parent; 	///< parent pdf
		std::vector<RooAbsReal*> m_etapdfint;	///< eta pdf (integral)
		RooArgSet m_nset;		  	///< normalisation set
		const char* m_rangeName;	  	///< name of int. range
		unsigned m_qtmax;			///< max. abs(qt)
		enum Flags {
		    None = 0,			  ///< no flags set
		    IntQf = 1,			  ///< integrate over qf
		    IntQt = 2,			  ///< integrate over qt
		    IntEta = 4,			  ///< integrate over eta
		    NormEta = 8			  ///< normalise over eta
		} m_flags;			  ///< flags
        };

	ClassDef(NonOscTaggingPdf, 3);
};

#endif

// vim: sw=4:tw=78:ft=cpp
