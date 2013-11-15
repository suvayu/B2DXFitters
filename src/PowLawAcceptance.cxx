/**
 * @file   PowLawAcceptance.cxx
 * @author Suvayu Ali <Suvayu.Ali@cern.ch>
 * @date   Thu May 17 21:46:42 2012
 *
 * @brief  This class implements a power law acceptance function.
 *
 */


#include <RooAbsReal.h>
#include <RooAbsCategory.h>
#include <cmath>

#include "B2DXFitters/PowLawAcceptance.h"


/**
 * Static data member for acceptance with no correction
 *
 */
RooConstVar PowLawAcceptance::_one(
    "PowLawAcceptance::_one", "PowLawAcceptance::_one", 1.0);


/**
 * Default constructor, used during ROOT I/O.  Ensures objects are
 * consistent when reading instances of older version of the class.
 *
 */
PowLawAcceptance::PowLawAcceptance()
{
}


PowLawAcceptance::PowLawAcceptance(const char *name, const char *title,
				   RooAbsReal& turnon, RooAbsReal& time,
				   RooAbsReal& __offset, RooAbsReal& exponent,
				   RooAbsReal& beta, RooAbsReal* correction) :
  RooAbsReal(name, title),
  _turnon("turnon", "turnon", this, turnon),
  _time("time", "time", this, time),
  _offset("offset", "offset", this, __offset),
  _exponent("exponent", "exponent", this, exponent),
  _beta("beta", "beta", this, beta),
  _correction("correction", "correction", this,
	      correction ? *correction : _one)
{
}


PowLawAcceptance::PowLawAcceptance(const PowLawAcceptance& other,
				   const char* name) :
  RooAbsReal(other, name),
  _turnon("turnon", this, other._turnon),
  _time("time", this, other._time),
  _offset("offset", this, other._offset),
  _exponent("exponent", this, other._exponent),
  _beta("beta", this, other._beta),
  _correction("correction", this, other._correction)
{
}


/**
 * This version of the copy constructor allows you to change the
 * acceptance correction to something new or back to unity.
 *
 * @param other PowLawAcceptance instance copied from
 * @param name New name
 * @param correction New correction factor
 */
PowLawAcceptance::PowLawAcceptance(const PowLawAcceptance& other,
				   const char* name,
				   RooAbsReal* correction) :
  RooAbsReal(other, name),
  _turnon("turnon", this, other._turnon),
  _time("time", this, other._time),
  _offset("offset", this, other._offset),
  _exponent("exponent", this, other._exponent),
  _beta("beta", this, other._beta),
  _correction("correction", "correction", this,
	      correction ? *correction : _one)
{
}


PowLawAcceptance::~PowLawAcceptance() {}


TObject* PowLawAcceptance::clone(const char* newname) const
{
  return new PowLawAcceptance(*this, newname);
}


PowLawAcceptance& PowLawAcceptance::operator=(const PowLawAcceptance& other)
{
  if (&other == this)
    return *this;

  RooAbsReal::operator=(other);
  _turnon = RooRealProxy("turnon", this, other._turnon);
  _time = RooRealProxy("time", this, other._time);
  _offset = RooRealProxy("offset", this, other._offset);
  _exponent = RooRealProxy("exponent", this, other._exponent);
  _beta = RooRealProxy("beta", this, other._beta);
  _correction = RooRealProxy("correction", this, other._correction);

  return *this;
}


Double_t PowLawAcceptance::evaluate() const
{
  Double_t turnon((Double_t)_turnon), time((Double_t)_time),
    __offset((Double_t)_offset), exponent((Double_t)_exponent),
    beta((Double_t)_beta), ratio(1.0);

  // check if underlying data type is valid
  if (_correction.absArg()) ratio = (Double_t)_correction;

  if (time < _time.min()) return 0.;
  if (time > _time.max()) return 0.;
  if (beta < -0.0){ return 0.0; } //std::cout<<"Case beta <0"<<std::endl; return 0.0;}
  if (beta*time > 1.0) { return 0.0; } //std::cout<<"Case beta*time > 1.0"<<std::endl; return 0.0; }
  Double_t expnoff = std::pow(turnon*time, exponent) - __offset;

  if (expnoff <= 0.0) {
    //std::cout<<"Case exponff < 0 "<<std::endl; 
    return 0.0;
  } else {
    Double_t denominator(1.0 + expnoff);
    return (ratio * (1.0 - 1.0/denominator) * (1.0 - beta*time));
  }
}
