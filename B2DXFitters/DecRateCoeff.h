/**
 * @file DecRateCoeff.h
 *
 * cosh/sinh/cos/sin coefficients in decay rate equations
 *
 * @author Manuel Schiller <manuel.schiller@nikhef.nl>
 * @date 2012-10-24
 */
#ifndef DECRATECOEFF
#define DECRATECOEFF

#include <map>
#include <string>
#include <vector>
#include <utility>

#include <RooAbsReal.h>
#include <RooAbsPdf.h>
#include <RooUniform.h>
#include <RooCategory.h>
#include <RooRealProxy.h>
#include <RooCategoryProxy.h>

/** @brief cosh/sinh/cos/sin coefficients in decay rate equations
 *
 * This class calculates the coefficients which go in front of the
 * cosh/sinh/cos/sin terms in the decay rate equations (RooBDecay). By forming
 * a suitable sum over the true initial state flavour inside the class
 * implementation, it is possible to treat production, detection and tagging
 * efficiency asymmetries from first principles. A constant mistag asymmetry
 * has also been implemented.
 *
 * The coefficient can be either CP even or CP odd (the latter has the
 * property that, with perfect tagging, it changes sign under CP), and it can
 * be different depending on final state charge (@f$C_f@f$ for @f$q_f=+1@f$,
 * @f$C_{\bar{f}}@f$ for @f$q_f=-1@f$).
 *
 * These "coefficients" are hermaphrodites in the sense that they are not
 * proper PDFs as such, but have to be normalised in a similar manner to
 * proper PDFs: If it were not for the coefficients which we need to put into
 * the decay rate equations, we would write down a PDF @f$P(q_f)\cdot
 * P(q_t,\eta)@f$, and this is the expression that needs to be used to
 * normalise the coefficients correctly. However, to be usable in the decay
 * rate equations, the proper prefactors have to be included which adds four
 * parameters @f$\alpha(q_i,q_f)@f$, so that the total PDF is @f$P(q_f)\cdot
 * P(q_t,\eta;\alpha(+1,q_f),\alpha(-1,q_f))@f$. The component PDFs are
 * written down below:
 *
 * @f[P(q_f)=1+q_f\cdot a_{det}@f]
 * @f[P(q_t,\eta;\alpha(+1,q_f),\alpha(-1,q_f))=
 * \left\{\begin{array}{l l}
 * (1+a_{prod}) \cdot \left(1-\epsilon (1+a_{tageff})\right) \cdot
 * U(\eta) \cdot \alpha(+1, q_f) +
 * (1-a_{prod}) \cdot \left(1-\epsilon (1-a_{tageff})\right) \cdot
 * U(\eta) \cdot \alpha(-1, q_f) &
 * \textrm{if $qt=0$} \\
 *
 * (1+a_{prod}) \cdot \epsilon \cdot (1+a_{tageff}) \cdot P(\eta)
 * \cdot \left(1-\eta_c(\eta)\cdot(1+a_{mistag})\right) \cdot
 * \alpha(+1, q_f) +
 * (1-a_{prod}) \cdot \epsilon \cdot (1-a_{tageff}) \cdot P(\eta)
 * \cdot \eta_c(\eta)\cdot(1-a_{mistag}) \cdot
 * \alpha(-1, q_f) &
 * \textrm{if $qt=+1$} \\
 *
 * (1+a_{prod}) \cdot \epsilon \cdot (1+a_{tageff}) \cdot P(\eta)
 * \cdot \eta_c(\eta)\cdot(1+a_{mistag}) \cdot
 * \alpha(+1, q_f) +
 * (1-a_{prod}) \cdot \epsilon \cdot (1-a_{tageff}) \cdot P(\eta)
 * \cdot \left(1 - \eta_c(\eta)\cdot(1-a_{mistag})\right) \cdot
 * \alpha(-1, q_f) &
 * \textrm{if $qt=-1$} \\
 * \end{array}\right.@f]
 *
 * The asymmetries given above (@f$a_{prod}@f$, @f$a_{det}@f$,
 * @f$a_{mistag}@f$, @f$a_{mistag}@f$) are assumed to be independent of any
 * observables (at least for the time being).
 *
 * The coefficients @f$\alpha(q_i, q_f)@f$ are put to 1 to calculate the
 * normalisation of the coefficients, their unnormalised values are calculated
 * as follows:
 *
 * For CP-even coefficients, we have
 * @f[ \alpha(q_i, q_f) = \left\{\begin{array}{l l}
 * C_f & \textrm{for $q_f = +1$} \\
 * C_{\bar{f}} & \textrm{for $q_f = -1$} \\
 * \end{array}\right. @f]
 *
 * For CP-odd coefficients, we have
 * @f[ \alpha(q_i, q_f) = q_i \cdot q_f \cdot \left\{\begin{array}{l l}
 * C_f & \textrm{for $q_f = +1$} \\
 * C_{\bar{f}} & \textrm{for $q_f = -1$} \\
 * \end{array}\right. @f]
 *
 * Moreover, an overall minus sign can be prepended in the definition of the
 * @f$\alpha(q_i,q_f)@f$.
 *
 * Instead of using @f$C_f@f$ and @f$C_{\bar{f}}@f$ directly, it is also
 * possible to use the average @f$\langle C\rangle=(C_f+C_{\bar{f}})/2@f$
 * difference @f$\Delta C=(C_f-C_{\bar{f}})/2@f$ of @f$C_f@f$ and
 * @f$C_{\bar{f}}@f$. The advantage to fitting for @f$\langle C\rangle@f$ and
 * @f$\Delta C@f$ are smaller correlations in the typical case, see e.g.
 *
 * http://de.arxiv.org/abs/1208.6463
 *
 * for details.
 *
 * @author Manuel Schiller <manuel.schiller@nikhef.nl>
 * @date 2012-10-24
 */
class DecRateCoeff : public RooAbsReal
{
    private:
	class CacheElem; // forward decl.
	friend class CacheElem;
	/// pair of cache element and corresponding slot number in cache
	typedef std::pair<DecRateCoeff::CacheElem*, Int_t> CacheElemPair;

    public:
	/// flags
	typedef enum {
	    CPEven = 0,	  ///< nothing set for CP even coefficients
	    CPOdd = 1,	  ///< bit 0 set for CP odd coefficient
	    Minus = 2,	  ///< bit 1 set to apply an overall minus sign
	    AvgDelta = 4, ///< bit 2 set if Cf/Cfbar refer to average and Delta C
	} Flags;

	/// default constructor for ROOT I/O
	DecRateCoeff() : m_nsethash(0) { }

	/** @brief constructor
	 *
	 * initialise pdf to average over initial flavour when using per-event
	 * mistag
	 *
	 * @param name		name of the pdf
	 * @param title		title of the pdf
	 * @param flags		flags
	 * @param qf		final state charge (-1, +1)
	 * @param qt		tagging decision (-1, 0, 1)
	 * @param Cf		coefficient for qf = +1
	 * @param Cfbar		coefficient for qf = -1
	 * @param etaobs	mistag observable
	 * @param etapdf	per-event-mistag distribution for tagged events
	 * @param tageff	tagging efficiency
	 * @param eta		(calibrated) per-event mistag
	 * @param aprod		production asymmetry
	 * @param adet		detection asymmetry
	 * @param atageff	tagging efficiency asymmetry (as function of qi)
	 * @param amistag	per-event mistag asymmetry
	 *
	 * If flags has AvgDelta set, we interpret the parameter Cf to be the
	 * average C, @f$\langle C\rangle=(C_f+C_{\bar{f}})/2@f$, and Cfbar to
	 * be the difference in C, @f$\Delta C=(C_f-C_{\bar{f}})/2@f$. The
	 * advantage to fitting for @f$\langle C\rangle@f$ and @f$\Delta C@f$
	 * are smaller correlations in the typical case, see e.g.
	 *
	 * http://de.arxiv.org/abs/1208.6463
	 *
	 * for details.
	 */
	DecRateCoeff(const char* name, const char* title, Flags flags,
		RooAbsCategory& qf, RooAbsCategory& qt,
		RooAbsReal& Cf, RooAbsReal& Cfbar,
		RooAbsRealLValue& etaobs, RooAbsPdf& etapdf,
		RooAbsReal& tageff, RooAbsReal& eta,
		RooAbsReal& aprod, RooAbsReal& adet,
		RooAbsReal& atageff, RooAbsReal& amistag);

	/** @brief constructor
	 *
	 * initialise pdf to average over initial flavour when using an
	 * average mistag
	 *
	 * @param name		name of the pdf
	 * @param title		title of the pdf
	 * @param flags		flags
	 * @param qf		final state charge (-1, +1)
	 * @param qt		tagging decision (-1, 0, 1)
	 * @param Cf		coefficient for qf = +1
	 * @param Cfbar		coefficient for qf = -1
	 * @param tageff	tagging efficiency
	 * @param eta		average mistag
	 * @param aprod		production asymmetry
	 * @param adet		detection asymmetry
	 * @param atageff	tagging efficiency asymmetry (as function of qi)
	 * @param amistag	per-event mistag asymmetry
	 *
	 * If flags has AvgDelta set, we interpret the parameter Cf to be the
	 * average C, @f$\langle C\rangle=(C_f+C_{\bar{f}})/2@f$, and Cfbar to
	 * be the difference in C, @f$\Delta C=(C_f-C_{\bar{f}})/2@f$. The
	 * advantage to fitting for @f$\langle C\rangle@f$ and @f$\Delta C@f$
	 * are smaller correlations in the typical case, see e.g.
	 *
	 * http://de.arxiv.org/abs/1208.6463
	 *
	 * for details.
	 */
	DecRateCoeff(const char* name, const char* title, Flags flags,
		RooAbsCategory& qf, RooAbsCategory& qt,
		RooAbsReal& Cf, RooAbsReal& Cfbar,
		RooAbsReal& tageff, RooAbsReal& eta,
		RooAbsReal& aprod, RooAbsReal& adet,
		RooAbsReal& atageff, RooAbsReal& amistag);

	/** @brief copy constructor
	 *
	 * @param other	pdf to copy
	 * @param name	name for the copy of other
	 */
	DecRateCoeff(
		const DecRateCoeff& other, const char* name = 0);

	/** @brief clone
	 *
	 * @param newname	name for the copy of other
	 * @returns		pointer to copy of this object
	 */
	virtual TObject* clone(const char* newname) const;

	/// destructor
	virtual ~DecRateCoeff();

	/// get value of function
	virtual Double_t getValV(const RooArgSet* nset) const;

	/// force all integrals to be treated analytically
	virtual Bool_t forceAnalyticalInt(const RooAbsArg& dep) const;

	/** @brief anounce analytical integrals
	 *
	 * @param allVars	variables over which integration is desired
	 * @param anaIntVars	variables for which we can perform analytical integral
	 * @param rangeName	range over which to integrate
	 * @returns		code for that particular integration
	 *
	 * Note: since this is not a proper PDF, it uses the default range to
	 * normalise the coefficient. The coefficient is normalised over the
	 * current normalisation set.
	 */
	virtual Int_t getAnalyticalIntegral(
		RooArgSet& allVars, RooArgSet& anaIntVars,
		const char* rangeName = 0) const;

	/** @brief perform analytical integrals
	 *
	 * @param code		code for integral to be performed
	 * @param rangeName	range over which to integrate
	 * @returns		value of the integral
	 *
	 * Note: since this is not a proper PDF, it uses the default range to
	 * normalise the coefficient. The coefficient is normalised over the
	 * current normalisation set.
	 */
	virtual Double_t analyticalIntegral(
		Int_t code, const char* rangeName = 0) const;

	/** @brief anounce analytical integrals
	 *
	 * @param allVars	variables over which integration is desired
	 * @param anaIntVars	variables for which we can perform analytical integral
	 * @param nset		normalisation set
	 * @param rangeName	range over which to integrate
	 * @returns		code for that particular integration
	 *
	 * Note: since this is not a proper PDF, it uses the default range to
	 * normalise the coefficient.
	 */
	virtual Int_t getAnalyticalIntegralWN(
		RooArgSet& allVars, RooArgSet& anaIntVars,
		const RooArgSet* nset = 0, const char* rangeName = 0) const;
	
	/** @brief perform analytical integrals
	 *
	 * @param code		code for integral to be performed
	 * @param nset		normalisation set
	 * @param rangeName	range over which to integrate
	 * @returns		value of the integral
	 *
	 * Note: since this is not a proper PDF, it uses the default range to
	 * normalise the coefficient.
	 */
	virtual Double_t analyticalIntegralWN(
		Int_t code, const RooArgSet* nset = 0,
		const char* rangeName = 0) const;

    protected:
	/// return value of coefficient
	Double_t evaluate() const;
	
	/// return (integral) cache element
	CacheElemPair getCache(
		const RooArgSet& iset, const RooArgSet* nset = 0,
		const TNamed* irangeName = 0) const;

	/// hash the contents of a RooArgSet
	UInt_t hash(const RooArgSet& s) const;

    private:
	static RooArgSet s_emptyset;	///< empty RooArgSet
	RooCategoryProxy m_qf;		///< final state charge
	RooCategoryProxy m_qt;		///< tagging decision
	RooRealProxy m_Cf;		///< coefficient for qf = +1
	RooRealProxy m_Cfbar;		///< coefficient for qf = -1
	RooRealProxy m_etaobs;		///< mistag observable
	RooRealProxy m_etapdf;		///< per-event mistag pdf
	/// instance of per-event mistag pdf for untagged events (flat)
	RooUniform m_etapdfutinstance;
	/// per-event mistag pdf for untagged events (flat)
	RooRealProxy m_etapdfut;
	RooRealProxy m_tageff;		///< tagging efficiency
	RooRealProxy m_eta;		///< per-event/average mistag
	RooRealProxy m_aprod;		///< production asymmetry
	RooRealProxy m_adet;		///< detection asymmetry
	RooRealProxy m_atageff;		///< tagging efficiency asymmetry
	RooRealProxy m_amistag;		///< asymmetry in predicted mistag
	/// integral cache
	mutable RooObjCacheManager m_cacheMgr; //! transient member
	/// place to keep normalisation sets
	mutable std::map<UInt_t, RooArgSet> m_nsets; //! transient member
	/// current normalisation set
	mutable const RooArgSet* m_nset; //! transient member
	/// hash of current normalisation set
	mutable UInt_t m_nsethash; //! transient member
        Flags m_flags;			///< flags

	/** @brief hold cached integrals
	 *
	 * technically, this may not integrate at all, depending on the
	 * integration set you supply at construction
	 *
	 * @author Manuel Schiller <manuel.schiller@nikhef.nl>
	 * @date 2012-11-08
	 */
	class CacheElem : public RooAbsCacheElement
        {
	    public:
		/// constructor
		CacheElem(const DecRateCoeff& parent,
			const RooArgSet& iset, const RooArgSet* nset = 0,
			const TNamed* rangeName = 0);

		/// destructor
		virtual ~CacheElem();
		
		/// return list of contained RooFit variables
		virtual RooArgList containedArgs(Action);
		
		/// return value of cache element
		double eval(const double alphapp, const double alphapm,
			const double alphamp, const double alphamm) const;
	
	    protected:
		/// set up binned evaluation of integral of eta product
		void setupBinnedProdctIntegral();

		/// return integral over mistag pdf (tagged events)
		inline double etaintpdftagged() const
		{
		    return m_etaintpdftagged ?
			m_etaintpdftagged->getValV(
				(m_flags & NormEta) ? &m_nset : 0) : 1.0;
		}

		/// return integral over mistag pdf times mistag (tagged events)
		double etaintprodpdfmistagtagged() const;
		
		/// retun integral over mistag pdf (untagged events)
		inline double etaintpdfuntagged() const
		{
		    return m_etaintpdfuntagged ? 
			m_etaintpdfuntagged->getValV(
				(m_flags & NormEta) ? &m_nset : 0) : 1.0;
		}
		
		/// return value of qf pdf
		double qfpdf(const int qf) const;
		
		/// return value of (q_t, eta) pdf
		double qtetapdf(const int qf, const int qt,
			const double alphapp, const double alphapm,
			const double alphamp, const double alphamm) const;

	    private:
		/// integral over mistag pdf (tagged events)
		RooAbsReal *m_etaintpdftagged;
		/// integral over mistag pdf times mistag (tagged events)
		RooAbsReal *m_etaintprodpdfmistagtagged;
		/// integral over mistag pdf (untagged events)
		RooAbsReal *m_etaintpdfuntagged;
		/// normalisation set to use for mistag pdfs
		RooArgSet m_nset;
		/// integration range
		const char* m_rangeName;
		/// parent
		const DecRateCoeff& m_parent;

		// for binned eta pdfs, we sum up our P(eta) * eta_c(eta)
		// product integrals ourselves; we need a couple of extra
		// members for that
		
		/// name of the working range
		std::string m_workRangeName;
		/// two RooRealProxyVars so we can move the range over eta
		std::pair<RooRealVar*, RooRealVar*> m_workRange;
		/// a vector of eta bin boundaries
		std::vector<double> m_etabins;
		/// cached value of product integral
		mutable double m_prodcachedval; //! transient data member
		
		/// flags
		enum Flags {
		    None = 0,
		    IntQf = 1,		/// integrate over qf
		    IntQt = 2,		/// integrate over qt
		    IntEta = 4,		/// integrate over eta
		    NormEta = 8,	/// eta is in normalisation set
		    ProdIntBinned = 16	/// binned product: m_etapdf and m_eta
		} m_flags;
	};

	ClassDef(DecRateCoeff, 1);
};

#endif // DECRATECOEFF

// vim: sw=4:tw=78:ft=cpp
