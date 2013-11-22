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
    m_parent(parent)
{
    //printf("DEBUG: In %s (%s, line %u)\n", __func__, __FILE__, __LINE__);
    const RooAbsCategoryLValue& cat =
	dynamic_cast<const RooAbsCategoryLValue&>(parent.m_cat.arg());
    m_resmodels.reserve(parent.m_resmodels.getSize());
    // loop over parent resmodels, and keep those which are in range
    {
    RooFIter it = parent.m_resmodels.fwdIterator();
    unsigned i = 0;
    std::auto_ptr<TIterator> tyit(cat.typeIterator());
    for (RooAbsReal* obj = static_cast<RooAbsReal*>(it.next()); obj;
	    obj = static_cast<RooAbsReal*>(it.next()), ++i) {
	RooCatType* type = reinterpret_cast<RooCatType*>(tyit->Next());
	m_resmodels.push_back(obj);
	m_idxmap[type->getVal()] = i;
	//printf("DEBUG: In %s (%s, line %u): obj %s\n", __func__, __FILE__, __LINE__, obj->GetName());
    }
    }
    // do we need to integrate anything other than (potentially) cat?
    if (iset.getSize()) {
	// yes, create those integrals
	for (std::vector<RooAbsReal*>::iterator it = m_resmodels.begin();
		m_resmodels.end() != it; ++it) {
	    RooAbsReal* rm = *it;
	    *it = rm->createIntegral(iset, rangeName);
	    (*it)->addOwnedComponents(RooArgSet(*rm));
	    //printf("DEBUG: In %s (%s, line %u): iobj %s\n", __func__, __FILE__, __LINE__, (*it)->GetName());
	}
    }
    //printf("DEBUG: In %s (%s, line %u)\n", __func__, __FILE__, __LINE__);
}

RooSimultaneousResModel::CacheElem::~CacheElem()
{
    if (!m_parent.m_resmodels.find(*m_resmodels.front())) {
	for (std::vector<RooAbsReal*>::const_iterator it = m_resmodels.begin();
		m_resmodels.end() != it; ++it) delete *it;
    }
}

RooArgList RooSimultaneousResModel::CacheElem::containedArgs(RooAbsCacheElement::Action)
{
    RooArgList retVal;
    for (std::vector<RooAbsReal*>::const_iterator it = m_resmodels.begin();
	    m_resmodels.end() != it; ++it) {
	retVal.add(**it);
	//(*it)->treeNodeServerList(&retVal);
    }
    retVal.add(m_parent.m_cat.arg());
    return retVal;
}

double RooSimultaneousResModel::CacheElem::getVal(const RooArgSet* nset) const
{
    const Int_t catidx = Int_t(m_parent.m_cat);
    return m_resmodels[const_cast<std::map<Int_t, unsigned>&>(m_idxmap)[catidx]]->getVal(nset);
}

void RooSimultaneousResModel::fillResModelsAndIndices(
	const std::map<Int_t, RooResolutionModel*>& map)
{
    for (std::map<Int_t, RooResolutionModel*>::const_iterator it =
	    map.begin(); map.end() != it; ++it) {
	// make sure all resolution models have same convolution variable
	assert(&convVar() == &(it->second->convVar()));
	assert(!it->second->overlaps(m_cat.arg()));
	m_resmodels.add(*(it->second));
    }
    const RooAbsCategoryLValue& cat(
	    dynamic_cast<const RooAbsCategoryLValue&>(m_cat.arg()));
    assert(m_resmodels.getSize() == cat.numTypes());
}

RooSimultaneousResModel::RooSimultaneousResModel(
	const char *name, const char *title, RooAbsCategoryLValue& cat,
	const std::map<Int_t, RooResolutionModel*>& map) :
    RooResolutionModel(name, title, map.begin()->second->convVar()),
    m_cat("cat", "cat", this, cat),
    m_resmodels("resmodels", "resmodels", this),
    _cacheMgr(this)
{
    fillResModelsAndIndices(map);
}

RooSimultaneousResModel::RooSimultaneousResModel(
	const char *name, const char *title, RooAbsCategoryLValue& cat,
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
	const char *name, const char *title, RooAbsCategoryLValue& cat,
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

    RooArgList convlist;
    RooFIter it = m_resmodels.fwdIterator();
    for (RooAbsArg* obj = it.next(); obj; obj = it.next()) {
	RooResolutionModel& resmodel =
	    dynamic_cast<RooResolutionModel&>(*obj);
	RooResolutionModel *conv = resmodel.convolution(inBasis, owner);

	std::string newTitle(conv->GetTitle());
	newTitle += " convoluted with basis function ";
	newTitle += inBasis->GetName();
	conv->SetTitle(newTitle.c_str());
	convlist.add(*conv);
    // interpolation
    const char* cacheParamsStr = getStringAttribute("CACHEPARAMINT");
    if (cacheParamsStr && std::strlen(cacheParamsStr)) {
	conv->setStringAttribute("CACHEPARAMINT", cacheParamsStr);
    }

    }

    std::string newTitle(GetTitle());
    newTitle += " convoluted with basis function ";
    newTitle += inBasis->GetName();
    RooSimultaneousResModel *myclone =
	new RooSimultaneousResModel(newName.c_str(), newTitle.c_str(),
		const_cast<RooAbsCategoryLValue&>(
		    static_cast<const RooAbsCategoryLValue&>(m_cat.arg())), convlist);
    myclone->addOwnedComponents(convlist);
    myclone->changeBasis(inBasis);

    return myclone;
}

Int_t RooSimultaneousResModel::getAnalyticalIntegral(RooArgSet& allVars,
	RooArgSet& analVars, const char* rangeName) const
{
    if (_forceNumInt) return 0;
    analVars.add(allVars);
    if (analVars.find(m_cat.arg())) analVars.remove(m_cat.arg());
    getCache(&analVars, RooNameReg::ptr(rangeName));
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
