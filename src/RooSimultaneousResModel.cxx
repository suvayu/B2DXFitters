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
	unsigned i = 0;
	for (RooAbsReal* obj = static_cast<RooAbsReal*>(it.next()); obj;
		obj = static_cast<RooAbsReal*>(it.next()), ++i) {
	    // build a (hopefully unique) suffix for objects we have to clone/modify
	    std::ostringstream sfx;
	    sfx << parent.GetName() << "_CacheElem_" << RooNameSet(iset).content();
	    if (rangeName && std::strlen(rangeName)) sfx << "_" << rangeName;
	    sfx << "_IDX_" << parent.m_indices[i];
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
	    newcat->setIndex(parent.m_indices[i]);
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
	const RooAbsCategory& cat = dynamic_cast<const RooAbsCategory&>(
		m_parent.m_cat.arg());
	double sum = 0.;
	std::auto_ptr<TIterator> tyit(cat.typeIterator());
	while (RooCatType* type =
		reinterpret_cast<RooCatType*>(tyit->Next())) {
	    // TODO: check if this is in integration range
	    std::vector<Int_t>::const_iterator it =
		std::lower_bound(m_parent.m_indices.begin(),
			m_parent.m_indices.end(), type->getVal());
	    // we must find the correct element here by construction
	    assert(m_parent.m_indices.end() != it && type->getVal() == *it);
	    const unsigned idx = it - m_parent.m_indices.begin();
	    assert(unsigned(idx) < m_resmodels.size());
	    sum += m_resmodels[idx]->getVal(nset);
	}
	return sum;
    } else {
	const Int_t catidx = Int_t(m_parent.m_cat);
	std::vector<Int_t>::const_iterator it =
	    std::lower_bound(m_parent.m_indices.begin(),
		    m_parent.m_indices.end(), catidx);
	// we must find the correct element here by construction
	assert(m_parent.m_indices.end() != it && catidx == *it);
	const unsigned idx = it - m_parent.m_indices.begin();
	assert(idx < m_resmodels.size());
	return m_resmodels[idx]->getVal(nset);
    }
    // must not reach this point
    assert(false);
    return std::numeric_limits<double>::quiet_NaN();
}

void RooSimultaneousResModel::fillResModelsAndIndices(
	const std::map<Int_t, RooResolutionModel*>& map)
{
    m_indices.reserve(map.size());
    for (std::map<Int_t, RooResolutionModel*>::const_iterator it =
	    map.begin(); map.end() != it; ++it) {
	// make sure all resolution models have same convolution variable
	assert(&convVar() == &(it->second->convVar()));
	m_indices.push_back(it->first);
	m_resmodels.add(*(it->second));
	// map should be sorted by key - make sure that is the case (we will
	// make use of that assumption elsewhere in the code)
	assert(m_indices.size() <= 1 ||
		(*(m_indices.rbegin() + 1)) < (m_indices.back()));
    }
    const RooAbsCategory& cat(
	    dynamic_cast<const RooAbsCategory&>(m_cat.arg()));
    assert(m_resmodels.getSize() == cat.numTypes());
    assert(m_indices.size() == unsigned(cat.numTypes()));
}

RooSimultaneousResModel::RooSimultaneousResModel(
	const char *name, const char *title, RooAbsCategory& cat,
	const std::map<Int_t, RooResolutionModel*>& map) :
    RooResolutionModel(name, title, map.begin()->second->convVar()),
    m_cat("cat", "cat", this, cat),
    m_resmodels("resmodels", "resmodels", this),
    _cacheMgr(this)
{
    fillResModelsAndIndices(map);
}

RooSimultaneousResModel::RooSimultaneousResModel(
	const char *name, const char *title, RooAbsCategory& cat,
	const std::map<std::string, RooResolutionModel*>& map) :
    RooResolutionModel(name, title, map.begin()->second->convVar()),
    m_cat("cat", "cat", this, cat),
    m_resmodels("resmodels", "resmodels", this),
    _cacheMgr(this)
{
    std::map<Int_t, RooResolutionModel*> imap;
    std::auto_ptr<TIterator> tyit(cat.typeIterator());
    while (RooCatType* type =
	    reinterpret_cast<RooCatType*>(tyit->Next())) {
	const std::map<std::string, RooResolutionModel*>::const_iterator
	    it = map.find(std::string(type->GetName()));
	assert(map.end() != it);
	assert(it->second);
	imap.insert(std::make_pair(type->getVal(), it->second));
    }
    fillResModelsAndIndices(imap);
}

RooSimultaneousResModel::RooSimultaneousResModel(
	const char *name, const char *title, RooAbsCategory& cat,
	const RooArgList& resmodels) :
    RooResolutionModel(name, title,
	    dynamic_cast<RooResolutionModel&>(*resmodels.at(0)).convVar()),
    m_cat("cat", "cat", this, cat),
    m_resmodels("resmodels", "resmodels", this),
    _cacheMgr(this)
{
    std::map<Int_t, RooResolutionModel*> map;
    std::auto_ptr<TIterator> tyit(cat.typeIterator());
    RooFIter it = resmodels.fwdIterator();
    while (RooCatType* type =
	    reinterpret_cast<RooCatType*>(tyit->Next())) {
	RooResolutionModel* obj = dynamic_cast<RooResolutionModel*>(it.next());
	assert(obj);
	map.insert(std::make_pair(type->getVal(), obj));
    }
    fillResModelsAndIndices(map);
}

RooSimultaneousResModel::RooSimultaneousResModel(const RooSimultaneousResModel& other, const char* name) :
    RooResolutionModel(other, name),
    m_cat("cat", this, other.m_cat),
    m_resmodels("resmodels", this, other.m_resmodels),
    m_indices(other.m_indices),
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

    std::map<Int_t, RooResolutionModel*> convs;
    RooArgList convlist;
    RooFIter it = m_resmodels.fwdIterator();
    unsigned i = 0;
    for (RooAbsArg* obj = it.next(); obj; obj = it.next(), ++i) {
	RooResolutionModel& resmodel =
	    dynamic_cast<RooResolutionModel&>(*obj);
	RooResolutionModel *conv = resmodel.convolution(inBasis, owner);

	std::string newTitle(conv->GetTitle());
	newTitle += " convoluted with basis function ";
	newTitle += inBasis->GetName();
	conv->SetTitle(newTitle.c_str());
	convs.insert(std::make_pair(m_indices[i], conv));
	convlist.add(*conv);
    }

    std::string newTitle(GetTitle());
    newTitle += " convoluted with basis function ";
    newTitle += inBasis->GetName();
    RooSimultaneousResModel *myclone =
	new RooSimultaneousResModel(newName.c_str(), newTitle.c_str(),
		const_cast<RooAbsCategory&>(
		    static_cast<const RooAbsCategory&>(m_cat.arg())), convs);
    myclone->addOwnedComponents(convlist);
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
