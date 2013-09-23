/** @file TaggingCat.h
 *
 * @author Chiara Farinelli
 * @date ca. Aug 2012
 *
 */
#ifndef TAGGINGCAT
#define TAGGINGCAT

#include "RooAbsReal.h"
#include "RooListProxy.h"
#include "RooCategoryProxy.h"
#include "RooRealProxy.h"
#include "RooAbsReal.h"
#include "RooAbsCategory.h"
 
/** @brief "multiplex" the different per-category mistags into one variable according to tagging category
 *
 * @author Chiara Farinelli
 * @date ca. Aug 2012
 *
 * @author Manuel Schiller
 * @date 2013-09-2012
 * 	also add the possibility to multiplex tagging efficiencies in the
 * 	same way
 */
class TaggingCat : public RooAbsReal {
public:
  TaggingCat() {} ; 
  /** @brief constructor
   *
   * @param _name	name of variable
   * @param _title	title of variable
   * @param _qt		tagged Bbar (-1), untagged (0), tagged B (+1)
   * @param _cat	tagging category (0, 1, ..., N)
   * @param _vars	list of per-category mistags
   * @param _isTagEff	use to _vars as tagging efficiencies
   *
   * if _isTagEff is true, this class returns 1-sum_i _vars[i]->getVal()
   * when 0 == _qt
   */
  TaggingCat(const char *name, const char *title,
	     RooAbsCategory& _qt,
             RooAbsCategory& _cat,
             RooArgList& _vars,
	     bool _isTagEff = false);
  
  TaggingCat(const TaggingCat& other, const char* name=0) ;
  virtual TObject* clone(const char* newname) const { return new TaggingCat(*this,newname); }
  virtual ~TaggingCat();

protected:

  RooCategoryProxy qt;
  RooCategoryProxy cat;
  RooListProxy catlist;
  RooRealProxy untaggedVal;

  Double_t evaluate() const;

private:
  ClassDef(TaggingCat, 2);
};
 
#endif
