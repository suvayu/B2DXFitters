/** @file NonOscTaggingPdf.h
 *
 * tagging behaviour and asymmetries for non-oscillating backgrounds
 */
#ifndef NONOSCTAGGINGPDF
#define NONOSCTAGGINGPDF

#include <cmath>
#include <cassert>

#include <RooAbsPdf.h>
#include <RooAbsReal.h>
#include <RooUniform.h>
#include <RooRealProxy.h>
#include <RooAbsCategory.h>
#include <RooCategoryProxy.h>
 
/** @brief tagging behaviour and asymmetries for non-oscillating backgrounds
 *
 * @author Manuel Schiller <manuel.schiller@nikhef.nl>
 * @date 2012-11-15
 *
 * this class provides the tagging behaviour and asymmetries for
 * non-oscillating backgrounds, specifically, the pdf can be written as
 * @f$P(q_f)\cdot P(q_t|q_f)\cdot P(\eta|q_t)@f$ with:
 *
 * @f[P(q_f) \sim (1+q_f\cdot a_{det})/2@f]
 * @f[P(q_t|q_f) \sim \left\{\begin{array}{l l}
 * (1-\epsilon)\cdot(1+q_f\cdot a^f_{tageff})/2 & \textrm{if $q_t=0$} \\
 * \epsilon\cdot(1+q_f\cdot a^f_{tageff})\cdot(1+q_t\cdot a^t_{tageff})/4 &
 * \textrm{if $|q_t|=1$} \\
 * \end{array}\right. @f]
 * @f[P(\eta|q_t) \sim \left\{\begin{array}{l l}
 * U(\eta) & \textrm{if $q_t = 0$} \\
 * P(\eta) & \textrm{if $|q_t| = 1$} \\
 * \end{array}\right. @f]
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
	
	/// announce our intention to normalise ourselved
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

    private:
	static RooArgSet s_emptyset;	///< empty set

	RooCategoryProxy m_qf;		///< final state charge
	RooCategoryProxy m_qt;		///< tagging decision

	RooRealProxy m_etaobs;		///< eta observable
	RooRealProxy m_etapdf;		///< eta pdf (tagged events)
	RooUniform m_etapdfutinstance;	///< inst. of eta pdf (untagged events)
	RooRealProxy m_etapdfut;	///< eta pdf (untagged events)

	RooRealProxy m_epsilon;		///< tagging efficiency
	RooRealProxy m_adet;		///< detection (charge) asymmetry
	RooRealProxy m_atageff_f;	///< tagging efficiency asymmetry (qf)
	RooRealProxy m_atageff_t;	///< tagging efficiency asymmetry (qt)

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
		double etapdfint() const;

		/// return untagged eta pdf (integral)
		double etapdfintut() const;
	
		/// return P(qt)
		double qfpdf(const int qf) const;

		/// return P(qt, eta|qf)
		double qtetapdf(const int qf, const int qt) const;

		/// evaluate for given values of qf, qt
		double eval(const int qf, const int qt) const;

	    private:
		const NonOscTaggingPdf& m_parent; ///< parent pdf
		RooAbsReal* m_etapdfint;	  ///< eta pdf (integral)
		RooAbsReal* m_etapdfintut;	  ///< (untagged) eta pdf (int.)
		RooArgSet m_nset;		  ///< normalisation set
		const char* m_rangeName;	  ///< name of integration range
		enum Flags {
		    None = 0,			  ///< no flags set
		    IntQf = 1,			  ///< integrate over qf
		    IntQt = 2,			  ///< integrate over qt
		    IntEta = 4,			  ///< integrate over eta
		    NormEta = 8			  ///< normalise over eta
		} m_flags;			  ///< flags
        };

	ClassDef(NonOscTaggingPdf, 2);
};

#endif

// vim: sw=4:tw=78:ft=cpp
