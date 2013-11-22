/**
 * @file RooSimultaneousResModel.h
 *
 * @author Manuel Schiller <manuelsr@nikhef.nl>
 * @date Mon Nov 19 2013
 *
 * @brief header for RooSimultaneousResModel class
 */

#ifndef ROOSIMULTANEOUSMODEL_H
#define ROOSIMULTANEOUSMODEL_H

#include <map>
#include <vector>
#include <string>

#include "RooListProxy.h"
#include "RooCategoryProxy.h"
#include "RooResolutionModel.h"
#include "RooAbsCacheElement.h"

class RooArgSet;

/** @brief simultaneous resolution model
 *
 * This class allows to switch between different resolution models depending on
 * the value of a category variable.
 *
 * @author Manuel Schiller <manuelsr@nikhef.nl>
 * @date   Mon Nov 18 2013
 */
class RooSimultaneousResModel : public RooResolutionModel
{
    public:
	/** @brief constructor
	 *
	 * @param name		name
	 * @param title		title
	 * @param cat		category
	 * @param map		map: index -> resolution models to switch between
	 */
	RooSimultaneousResModel(const char *name, const char *title,
		RooAbsCategoryLValue& cat,
		const std::map<Int_t, RooResolutionModel*>& map);

	/** @brief constructor
	 *
	 * @param name		name
	 * @param title		title
	 * @param cat		category
	 * @param map		map: label -> resolution models to switch between
	 */
	RooSimultaneousResModel(const char *name, const char *title,
		RooAbsCategoryLValue& cat,
		const std::map<std::string, RooResolutionModel*>& map);

	/** @brief constructor
	 *
	 * @param name		name
	 * @param title		title
	 * @param cat		category
	 * @param resmodels	resolution models to switch between
	 *
	 * resolution models in resmodels must appear in the same order as the
	 * states in the type iterator of cat
	 */
	RooSimultaneousResModel(const char *name, const char *title,
		RooAbsCategoryLValue& cat, const RooArgList& resmodels);
	
	/** @brief copy constructor
	 *
	 * @param other	instance to copy
	 * @param name	name of the new instance
	 */
	RooSimultaneousResModel(const RooSimultaneousResModel& other, const char* name=0);
	
	/// destructor
	virtual ~RooSimultaneousResModel();

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

	// virtual Int_t getGenerator(const RooArgSet& directVars,
	// 			     RooArgSet &generateVars,
	// 			     Bool_t staticInitOK = kTRUE) const;
	// virtual void initGenerator(Int_t code);
	// virtual void generateEvent(Int_t code);

	// virtual RooAbsGenContext* modelGenContext(const RooAbsAnaConvPdf& convPdf,
	// 					    const RooArgSet &vars,
	// 					    const RooDataSet *prototype = 0,
	// 					    const RooArgSet* auxProto = 0,
	// 					    Bool_t verbose= kFALSE) const;

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
	virtual RooSimultaneousResModel* convolution(RooFormulaVar* inBasis,
		RooAbsArg* owner) const;

    private:
	/** @brief class to do all the actual (hard) work
	 *
	 * @author Manuel Schiller <manuelsr@nikhef.nl>
	 * @date   Mon Nov 18 2013
	 *
	 * This class creates the necessary customisations of the underlying
	 * resolutions models, integrates them (if needed), and performs the
	 * sum over the category used to switch between resolution models (if
	 * applicable).
	 */
	class CacheElem : public RooAbsCacheElement {
	    public:
		/** @brief constructor
		 *
		 * @param parent	parent object (RooSimultaneousResModel instance)
		 * @param iset		variables to integrate over (if any)
		 * @param rangeName	integration range (if any)
		 */
		CacheElem(const RooSimultaneousResModel& parent,
			const RooArgSet& iset, const char* rangeName);

		/// destructor
		virtual ~CacheElem();

		/** @brief return contained objects
		 *
		 * @returns contained objects, so RooFit can invalidate the
		 * caches when shape changes occur (e.g RooCustomizer is used
		 * on a RooSimultaneousResModel)
		 */
		virtual RooArgList containedArgs(RooAbsCacheElement::Action);

		/** @brief return value
		 *
		 * @param nset	variables over which to normalise
		 * @returns value, k-factor smeared
		 */
		double getVal(const RooArgSet* nset = 0) const;

	    private:
		/// parent object
		const RooSimultaneousResModel& m_parent;
		/// resolution models (or their integrals)
		std::vector<RooAbsReal*> m_resmodels;
		/// mapping category index to index in m_resmodels
		std::map<Int_t, unsigned> m_idxmap;
	};

	friend class RooSimultaneousResModel::CacheElem;

	/** @brief get or create CacheElem object associated with iset and
	 * rangeName.
	 *
	 * @param iset		variables over which to integrate (if any)
	 * @param rangeName	integration range
	 *
	 * @returns corresponding CacheElem object, owned by _cacheMgr
	 */
	CacheElem* getCache(const RooArgSet* iset, const TNamed* rangeName = 0) const;

	/** @brief fill resolution models and corresponding category indices
	 *
	 * @param map mapping index -> resolution model
	 */
	void fillResModelsAndIndices(
		const std::map<Int_t, RooResolutionModel*>& map);

	/// category
	RooCategoryProxy m_cat;	
	/// resolution models
	RooListProxy m_resmodels;
	/// cache manager
	mutable RooObjCacheManager _cacheMgr;	//! transient object

	static RooArgSet s_emptyset; ///< empty RooArgSet

	ClassDef(RooSimultaneousResModel, 1) // Resolution model with k-factor
};

#endif	// ROOSIMULTANEOUSMODEL_H

// vim: sw=4:ft=cpp:tw=78
