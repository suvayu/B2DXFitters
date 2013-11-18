/**
 * @file   RooSimultaneousResModel.cxx
 * @author Manuel Schiller <manuel.schiller@nikhef.nl>
 * @date   Mon Nov 19 2013
 *
 * @brief  Implementation file for RooSimultaneousResModel.
 *
 */

//////////////////////////////////////////////////////////////////////////////
//
// BEGIN_HTML
// Class RooSimultaneousResModel implements a RooResolutionModel that switches
// between different resolution models depending on the index state of a
// category.
// END_HTML
//

#include <cstring>
#include <cmath>
#include <string>
#include <memory>
#include <limits>
#include <cassert>
#include <sstream>

#include "RooProduct.h"
#include "RooCustomizer.h"
#include "RooFormulaVar.h"
#include "RooNameSet.h"
#include "B2DXFitters/RooSimultaneousResModel.h"
#include "RooHistPdf.h"
#include "RooRealVar.h"
#include "RooCachedReal.h"
#include "RooCategory.h"

#include "TPad.h"
#include "RooPlot.h"

RooArgSet RooSimultaneousResModel::s_emptyset;

RooSimultaneousResModel::CacheElem::CacheElem(
	const RooSimultaneousResModel& parent,
	const RooArgSet& iset, const char* rangeName) :
    m_parent(parent), m_flags(None)
{
    const RooAbsCategory& cat = dynamic_cast<const RooAbsCategory&>(
	    parent.m_cat.arg());
    RooArgSet myiset(iset);
    if (!iset.find(cat)) {
	// do not integrate over cat, so just copy the resmodels from parent
	m_resmodels.reserve(parent.m_resmodels.getSize());
	RooFIter it = parent.m_resmodels.fwdIterator();
	for (RooAbsReal* obj = static_cast<RooAbsReal*>(it.next()); obj;
		obj = static_cast<RooAbsReal*>(it.next())) {
	    m_resmodels.push_back(obj);
	}
    } else {
	// integrate over cat - this is more work
	myiset.remove(cat);
	m_flags = static_cast<Flags>(m_flags | IntCat);
	// loop over parent resmodels, and customise them with a constant
	// category
	m_resmodels.reserve(parent.m_resmodels.getSize());
	RooFIter it = parent.m_resmodels.fwdIterator();
	unsigned idx = 0;
	for (RooAbsReal* obj = static_cast<RooAbsReal*>(it.next()); obj;
		obj = static_cast<RooAbsReal*>(it.next()), ++idx) {
	    // build a (hopefully unique) suffix for objects we have to clone/modify
	    std::ostringstream sfx;
	    sfx << parent.GetName() << "_CacheElem_" << RooNameSet(iset).content();
	    if (rangeName && std::strlen(rangeName)) sfx << "_" << rangeName;
	    sfx << "_IDX_" << idx;
	    // create a clone of our category
	    const std::string catname(sfx.str());
	    RooCategory *newcat = new RooCategory(
		    catname.c_str(), catname.c_str());
	    // loop over states of cat, duplicate them
	    std::auto_ptr<TIterator> tyit(cat.typeIterator());
	    while (RooCatType* type =
		    reinterpret_cast<RooCatType*>(tyit->Next())) {
		newcat->defineType(type->GetName(), type->getVal());
	    }
	    // set current index
	    newcat->setIndex(idx);
	    newcat->setConstant(true);
	    m_cats.push_back(newcat);
	    sfx << "_custobj";
	    const std::string objname(sfx.str());
	    RooCustomizer c(*obj, objname.c_str());
	    c.replaceArg(cat, *newcat);
	    obj = dynamic_cast<RooAbsReal*>(c.build());
	    assert(obj);
	    m_resmodels.push_back(obj);
	}
    }
    // do we need to integrate anything other than (potentially) cat?
    if (myiset.getSize()) {
	// yes, create those integrals
	for (std::vector<RooAbsReal*>::iterator it = m_resmodels.begin();
		m_resmodels.end() != it; ++it) {
	    RooAbsReal* rm = *it;
	    *it = rm->createIntegral(myiset, rangeName);
	    (*it)->addOwnedComponents(RooArgSet(*rm));
	}
    }
}

RooSimultaneousResModel::CacheElem::~CacheElem()
{
    if (dynamic_cast<RooAbsReal*>(m_parent.m_resmodels.at(0)) !=
	    m_resmodels.front()) {
	for (std::vector<RooAbsReal*>::const_iterator it = m_resmodels.begin();
		m_resmodels.end() != it; ++it) delete *it;
    }
    if (m_flags & IntCat) {
	for (std::vector<RooCategory*>::const_iterator it = m_cats.begin();
		m_cats.end() != it; ++it) delete *it;
    }
}

RooArgList RooSimultaneousResModel::CacheElem::containedArgs(RooAbsCacheElement::Action)
{
    RooArgList retVal;
    for (std::vector<RooAbsReal*>::const_iterator it = m_resmodels.begin();
	    m_resmodels.end() != it; ++it) retVal.add(**it);
    if (m_flags & IntCat) {
	for (std::vector<RooCategory*>::const_iterator it = m_cats.begin();
		m_cats.end() != it; ++it) retVal.add(**it);
    } else {
	retVal.add(m_parent.m_cat.arg());
    }
    return retVal;
}

double RooSimultaneousResModel::CacheElem::getVal(const RooArgSet* nset) const
{
    if (m_flags & IntCat) {
	double sum = 0.;
	for (std::vector<RooAbsReal*>::const_iterator it = m_resmodels.begin();
		m_resmodels.end() != it; ++it) {
	    sum += (*it)->getVal(nset);
	}
	return sum;
    } else {
	unsigned cat = Int_t(m_parent.m_cat);
	assert(cat < m_resmodels.size());
	return m_resmodels[cat]->getVal(nset);
    }
    // must not reach this point
    assert(false);
    return std::numeric_limits<double>::quiet_NaN();
}

RooSimultaneousResModel::RooSimultaneousResModel(const char *name, const char *title,
	RooAbsCategory& cat, RooArgList& resmodels) :
    RooResolutionModel(name, title,
	    dynamic_cast<RooResolutionModel&>(*resmodels.at(0)).convVar()),
    m_cat("cat", "cat", this, cat),
    m_resmodels("resmodels", "resmodels", this),
    _cacheMgr(this)
{
    // add the other resolution models to the RooListProxy
    m_resmodels.add(resmodels);
    // make sure they all have the same convolution variable
    RooFIter it = resmodels.fwdIterator();
    for (RooAbsArg* obj = it.next(); obj; obj = it.next()) {
	RooResolutionModel& resmodel =
	    dynamic_cast<RooResolutionModel&>(*obj);
	assert(&convVar() == &resmodel.convVar());
    }
}

RooSimultaneousResModel::RooSimultaneousResModel(const RooSimultaneousResModel& other, const char* name) :
    RooResolutionModel(other, name),
    m_cat("cat", this, other.m_cat),
    m_resmodels("resmodels", this, other.m_resmodels),
    _cacheMgr(other._cacheMgr, this)
{
}

RooSimultaneousResModel::~RooSimultaneousResModel()
{ 
}

TObject* RooSimultaneousResModel::clone(const char* newname) const
{ return new RooSimultaneousResModel(*this, newname); }

Int_t RooSimultaneousResModel::basisCode(const char* name) const
{
    // return basis function code for underlying resolution models,
    // make sure that codes agree
    bool filled = false;
    Int_t code = 0;
    RooFIter it = m_resmodels.fwdIterator();
    for (RooAbsArg* obj = it.next(); obj; obj = it.next()) {
	RooResolutionModel& resmodel =
	    dynamic_cast<RooResolutionModel&>(*obj);
	Int_t tmpcode = resmodel.basisCode(name);
	if (!filled) {
	    code = tmpcode, filled = true;
	} else if (code != tmpcode) {
	    assert(code != tmpcode);
	}
    }
    assert(filled);
    return code;
}

Double_t RooSimultaneousResModel::evaluate() const
{
    CacheElem *cache = getCache(&s_emptyset, 0);
    assert(cache);
    return cache->getVal();
}

RooSimultaneousResModel* RooSimultaneousResModel::convolution(RooFormulaVar* inBasis,
	RooAbsArg* owner) const
{
    // Instantiate a clone of this resolution model representing a
    // convolution with given basis function. The owners object name
    // is incorporated in the clones name to avoid multiple
    // convolution objects with the same name in complex PDF
    // structures.
    //
    // Note: The 'inBasis' formula expression must be a RooFormulaVar
    // that encodes the formula in the title of the object and this
    // expression must be an exact match against the implemented basis
    // function strings (see derived class implementation of method
    // basisCode() for those strings

    // Check that primary variable of basis functions is our convolution variable
    if (inBasis->getParameter(0) != x.absArg()) {
	coutE(InputArguments) << "RooSimultaneousResModel::convolution("
	    << GetName() << "," << this
	    << ") convolution parameter of basis function and PDF don't match"
	    << std::endl << "basis->findServer(0) = "
	    << inBasis->findServer(0) << std::endl
	    << "x.absArg()           = "
	    << x.absArg() << std::endl;
	return 0;
    }

    if (basisCode(inBasis->GetTitle())==0) {
	coutE(InputArguments) << "RooSimultaneousResModel::convolution("
	    << GetName() << "," << this
	    << ") basis function '"
	    << inBasis->GetTitle()
	    << "' is not supported." << std::endl;
	return 0;
    }

    std::string newName(GetName());
    newName += "_conv_";
    newName += inBasis->GetName();
    newName += "_[";
    newName += owner->GetName();
    newName += "]";

    RooArgList convs;
    RooFIter it = m_resmodels.fwdIterator();
    for (RooAbsArg* obj = it.next(); obj; obj = it.next()) {
	RooResolutionModel& resmodel =
	    dynamic_cast<RooResolutionModel&>(*obj);
	RooResolutionModel *conv = resmodel.convolution(inBasis, owner);

	std::string newTitle(conv->GetTitle());
	newTitle += " convoluted with basis function ";
	newTitle += inBasis->GetName();
	conv->SetTitle(newTitle.c_str());
	convs.add(*conv);
    }

    std::string newTitle(GetTitle());
    newTitle += " convoluted with basis function ";
    newTitle += inBasis->GetName();
    RooSimultaneousResModel *myclone =
	new RooSimultaneousResModel(newName.c_str(), newTitle.c_str(),
		const_cast<RooAbsCategory&>(
		    static_cast<const RooAbsCategory&>(m_cat.arg())), convs);
    myclone->addOwnedComponents(convs);
    myclone->changeBasis(inBasis);

    // interpolation
    const char* cacheParamsStr = getStringAttribute("CACHEPARAMINT");
    if (cacheParamsStr && std::strlen(cacheParamsStr)) {
	myclone->setStringAttribute("CACHEPARAMINT", cacheParamsStr);
    }

    return myclone;
}

Int_t RooSimultaneousResModel::getAnalyticalIntegral(RooArgSet& allVars,
	RooArgSet& analVars,
	const char* rangeName) const
{
    if (_forceNumInt) return 0;
    analVars.add(allVars);
    getCache(&allVars, RooNameReg::ptr(rangeName));
    return 1 + _cacheMgr.lastIndex();
}

Double_t RooSimultaneousResModel::analyticalIntegral(Int_t code,
	const char* rangeName) const
{
    assert(code > 0);
    CacheElem* cache =
	static_cast<CacheElem*>(_cacheMgr.getObjByIndex(code - 1));
    if (!cache) {
	std::auto_ptr<RooArgSet> vars(getParameters(RooArgSet()));
	std::auto_ptr<RooArgSet>
	    iset(_cacheMgr.nameSet2ByIndex(code - 1)->select(*vars));
	cache = getCache(iset.get(), RooNameReg::ptr(rangeName));
	assert(cache);
    }
    return cache->getVal();
}

Bool_t RooSimultaneousResModel::forceAnalyticalInt(const RooAbsArg& /*dep*/) const
{ return true; }

RooSimultaneousResModel::CacheElem* RooSimultaneousResModel::getCache(const RooArgSet *iset,
	const TNamed *rangeName) const
{
    int sterileIndex(-1);
    CacheElem* cache = static_cast<CacheElem*>
	(_cacheMgr.getObj(0, iset, &sterileIndex, rangeName));
    // if we have the CacheElem in the cache manager, we return
    if (cache) return cache;
    // if not, we create it...
    cache = new CacheElem(*this, *iset,
	    RooNameReg::str(rangeName));
    assert(cache);
    _cacheMgr.setObj(0, iset, cache, rangeName);
    // and then we call getCache again so that _cacheMgr.lastIndex() returns
    // the right index...
    return getCache(iset, rangeName);
}

// vim: sw=4:ft=cpp:tw=78
