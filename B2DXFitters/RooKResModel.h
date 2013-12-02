/**
 * @file   RooKResModel.h
 * @author Suvayu Ali <Suvayu.Ali@cern.ch>
 * @date   Fri Aug 30 15:18:23 2013
 * @author Manuel Schiller <manuelsr@nikhef.nl>
 * @date   Tue Oct 22 2013
 *
 * @brief  RooKResModel definition.
 *         Started from a copy of RooEffResModel.
 *
 */

#ifndef ROO_KRES_MODEL
#define ROO_KRES_MODEL

#include "RooRealProxy.h"
#include "RooSetProxy.h"
#include "RooAbsCacheElement.h"

#define RooConvGenContext RooConvGenContext; friend class RooKResModel
#include "RooResolutionModel.h"
#undef RooConvGenContext

class RooHistPdf;
class RooRealVar;
class RooArgSet;

/** @brief resolution model to apply a k-factor smearing
 *
 * This class performs a substitution q_i -> k * q_i for a given set of
 * quantities q_i in an underlying resolution model R(x); given a distribution
 * P(k) of k, the class proceeds to calculate a "smeared" resolution model
 * R'(x):
 *
 * @f[ R'(x, q_1, \ldots) = \int dk P(k) R(x, k * q_1, \ldots) k @f]
 *
 * The factor @f$k@f$ in the formula above undoes the effect k has on the
 * normalisation of the resulting pdf, effectively yielding a class that
 * integrates out a (conditional) per-event observable.
 *
 * @author Suvayu Ali <Suvayu.Ali@cern.ch>
 * @date   Fri Aug 30 15:18:23 2013
 * 	- initial implementation, debugging and testing
 *
 * @author Manuel Schiller <manuelsr@nikhef.nl>
 * @date   Tue Oct 22 2013
 * 	- speedups in evaluate() through caching / interpolation to avoid a
 * 	  timing behaviour that scales linearly with the number of bins in k
 * 	  (can be up to O(10) times speed increase)
 * 	- better numerical robustness (avoid division by zero etc)
 * 	- const correctness
 *	- more documentation
 */
class RooKResModel : public RooResolutionModel
{
    public:
	/// constructor for ROOT I/O
	RooKResModel();

	/** @brief constructor
	 *
	 * @param name		name
	 * @param title		title
	 * @param res_model	underlying resolution model
	 * @param kfactor_pdf	k-factor distribution
	 * @param kfactor_var	k-factor variable
	 * @param substTargets	quantities q_i that need substituting k * q_i
	 * @param evalInterpVars
	 * 			if non-empty, variables in which to
	 * 			interpolate evaluation
	 */
	RooKResModel(const char *name, const char *title,
		RooResolutionModel& res_model,
		RooHistPdf& kfactor_pdf,
		RooAbsRealLValue& kfactor_var,
		const RooArgSet& substTargets,
		const RooArgSet& evalInterpVars = RooArgSet());
	
	/** @brief copy constructor
	 *
	 * @param other	instance to copy
	 * @param name	name of the new instance
	 */
	RooKResModel(const RooKResModel& other, const char* name=0);
	
	/// destructor
	virtual ~RooKResModel();

	/** @brief clone object
	 *
	 * @param newname	name of the clone
	 *
	 * @returns cloned object
	 */
	virtual TObject* clone(const char* newname) const;
	
	/** @brief return basis code associated to string
	 *
	 * @param name	string describing which basis to returns
	 *
	 * @returns basis code (0 if unsuccessful)
	 */
	virtual Int_t basisCode(const char* name) const;

	/** @brief check for availability of analytical integral
	 *
	 * @param allVars	set of variables over which to integrate
	 * @param analVars	(on return) set of variables over which
	 * 			the class can integrate analytically
	 * @param rangeName	range over which to integrate
	 *
	 * @returns code for analytical integration (0 if unsupported)
	 */
	virtual Int_t getAnalyticalIntegral(RooArgSet& allVars,
		RooArgSet& analVars,
		const char* rangeName=0) const;
	/** @brief perform analytical integral
	 *
	 * @param code		integration code returned by
	 * 			getAnalyticalIntegral
	 * @param rangeName	name of the integration range
	 *
	 * @returns value of integral
	 */
	virtual Double_t analyticalIntegral(Int_t code,
		const char* rangeName) const;

	/** @brief inform RooFit which variables must be integrated analytically
	 *
	 * @param dep	variables to test
	 *
	 * @returns true if integration must be done analytically
	 */
	virtual Bool_t forceAnalyticalInt(const RooAbsArg& dep) const;

	/** @brief create generator context
	 *
	 * @param convPdf	pdf which should be smeared with a k-factor
	 * 			distribution
	 * @param vars		which variables to generate
	 * @param prototype	prototype dataset
	 * @param auxProto	auxiliary prototype data
	 * @param verbose	be verbose
	 *
	 * @returns generator context
	 */
	virtual RooAbsGenContext* modelGenContext(
		const RooAbsAnaConvPdf& convPdf, const RooArgSet &vars,
		const RooDataSet *prototype = 0,
		const RooArgSet* auxProto = 0, Bool_t verbose= kFALSE) const;
	/** @brief check if direct generation is safe
	 *
	 * @param arg	variable to generate
	 *
	 * @returns true if arg is safe to generate directly
	 */
	virtual Bool_t isDirectGenSafe(const RooAbsArg& arg) const;

	/** @brief announce capability to generate directly
	 *
	 * @param directVars	desired generation variables
	 * @param generateVars	variables which this class can generate
	 * @param staticInitOK  ?
	 *
	 * @returns code > 0 if direct generation is supported over a
	 *          subset of variables
	 */
	virtual Int_t getGenerator(const RooArgSet& directVars,
		RooArgSet &generateVars, Bool_t staticInitOK) const;

	/** @brief direct generation of a single event
	 *
	 * @param code	generation code returned by getGenerator
	 *
	 * due to the way RooAbsAnaConvPdf works, this is a dummy
	 * implementation which should never get called (and will abort the
	 * program); RooAbsAnaConvPdf will prefer modelGenContext
	 */
	virtual void generateEvent(Int_t code);

	/// return underlying resolution model
	const RooResolutionModel& resmodel() const;
	/// return k-factor distribution
	const RooHistPdf& kpdf() const;
	/// return k-factor variable
	const RooAbsRealLValue& kvar() const;

    protected:
	/** @brief evaluate the resolution model
	 *
	 * @returns current value
	 */
	virtual Double_t evaluate() const;

	/** @brief return object which convolves a basis function with the
	 * resolution model.
	 *
	 * @param inBasis	basis function to convolve with
	 * @param owner		caller of this routine
	 *
	 * @returns object which can be used to evaluate the convolution
	 */
	virtual RooKResModel* convolution(RooFormulaVar* inBasis,
		RooAbsArg* owner) const;

    private:
	/** @brief class to do all the actual (hard) work
	 *
	 * This class does the calculation needed when applying a k-factor.
	 * Since the k-factor smearing process is virtually identical for
	 * evaluating the resolution mode and for evaluating its integrals, the
	 * code and methods can be shared.
	 *
	 * The class creates the integral object for the underlying resolution
	 * model (if needed), performs the desired substitutions of quantities
	 * q_i -> k * q_i, and keeps the resulting objects around for
	 * evaluation. With the underlying resolution model (or its integral)
	 * denoted @f$F(x, k)@f$ (x stands generically for all the other
	 * variables the expression depends on) and the k-factor distribution
	 * @f$P(k)@f$, the class computes:
	 *
	 * @f[ \sum_{i=1}^N P(\frac{k_{i-1} + k{i}}{2}) \cdot (k_{i}-k_{i-1})
	 * \cdot F(x, k) \cdot \frac{k_{i-1} + k{i}}{2} @f]
	 *
	 * This is essentially a sum over the bins of the k-factor
	 * distribution, with the last term applying a normalisation correction
	 * needed to undo the partial normalisation that occurs in the
	 * underlying resolution model. (RooKResModel itself will normalise
	 * correctly.)
	 */
	class DeceptiveCache : public RooAbsCacheElement {
	    public:
		/** @brief constructor
		 *
		 * @param parent	parent object (RooKResModel instance)
		 * @param iset		variables to integrate over (if any)
		 * @param rangeName	integration range (if any)
		 *
		 * evaluate
		 */
		DeceptiveCache(const RooKResModel& parent, const RooArgSet& iset,
			const char* rangeName);

		/** @brief constructor
		 *
		 * @param parent	parent object (RooKResModel instance)
		 *
		 * create and store interpolation object
		 */
		DeceptiveCache(const RooKResModel& parent);

		/// destructor
		virtual ~DeceptiveCache();

		/** @brief return contained objects
		 *
		 * @returns contained objects, so RooFit can invalidate the
		 * caches when shape changes occur (e.g RooCustomizer is used
		 * on a RooKResModel)
		 */
		virtual RooArgList containedArgs(RooAbsCacheElement::Action);
		/** @brief return value
		 *
		 * @param nset	variables over which to normalise
		 * @returns value, k-factor smeared
		 */
		double getVal(const RooArgSet* nset = 0) const;

	    private:
		mutable double _cval;	/**< cached value */
		RooRealVar* _kvar;	/**< k-factor variable */
		RooHistPdf* _kpdf;	/**< k-factor pdf */
		RooAbsReal* _val;       /**< value */
		/// reference to parent for logging
		const RooKResModel& _parent;
		/// normalisation set with only _kvar
		RooArgSet _knset;
		/// k-factor bin boundaries
		std::vector<double> _kbins;
	};

	friend class RooKResModel::DeceptiveCache;

	/** @brief get or create DeceptiveCache object associated with iset and
	 * rangeName.
	 *
	 * @brief iset		variables over which to integrate (if any)
	 * @brief rangeName	integration range
	 * @brief interp	create interpolating cache element
	 *
	 * if interp is true, create an interpolating cache element to speed
	 * evaluation - this will only work if nothing is integrated over
	 *
	 * @returns corresponding DeceptiveCache object, owned by _cacheMgr
	 */
	DeceptiveCache* getCache(const RooArgSet* iset,
		const TNamed* rangeName = 0, bool interp = false) const;

	RooRealProxy _resmodel;    /**< resolution model (RooResolutionModel) */
	RooRealProxy _kfactor_pdf; /**< k-factor distribution (RooHistPdf) */
	RooRealProxy _kfactor_var; /**< k-factor variable (RooRealVar) */
	RooSetProxy _substTargets; ///< substitution targets
	RooSetProxy _evalInterpVars; ///< variables in which to interpolate in evaluate()
	/// cache manager
	mutable RooObjCacheManager _cacheMgr;	//! transient object

	static RooArgSet s_emptyset; ///< empty RooArgSet

	ClassDef(RooKResModel, 1) // Resolution model with k-factor
};

#endif	// ROO_KRES_MODEL
