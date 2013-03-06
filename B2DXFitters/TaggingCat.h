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
#include "RooAbsReal.h"
#include "RooAbsCategory.h"
 
/** @brief "multiplex" the different per-category mistags into one variable according to tagging category
 *
 * @author Chiara Farinelli
 * @date ca. Aug 2012
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
   */
  TaggingCat(const char *name, const char *title,
	     RooAbsCategory& _qt,
             RooAbsCategory& _cat,
             RooArgList& _vars);
  
  TaggingCat(const TaggingCat& other, const char* name=0) ;
  virtual TObject* clone(const char* newname) const { return new TaggingCat(*this,newname); }
  virtual ~TaggingCat();

protected:

  RooCategoryProxy qt;
  RooCategoryProxy cat;

  RooListProxy catlist;

  Double_t evaluate() const;

private:
  ClassDef(TaggingCat, 1);
};
 
#endif
