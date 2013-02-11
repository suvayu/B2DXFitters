/**
 * @file   KinHack.cxx
 * @date   Thu Jul 26 10:16:33 2012
 *
 * @brief  This file implements the TwoBodyDecay class
 *
 *         This is a kinematics hack for missing MC samples
 *
 */

#include <cstring>
#include <cstdio>
#include <cmath>
#include <cassert>
#include <stdexcept>

#include "B2DXFitters/KinHack.h"


double TwoBodyDecay::RelFourMomCons() const
{
  if (!_dau1 || !_dau2) return 0.;
  double retVal = _dau1->RelFourMomCons() + _dau2->RelFourMomCons();
  retVal += (_plv.Px() - _dau1->_plv.Px() - _dau2->_plv.Px()) /
    (std::abs(_plv.Px()) + std::numeric_limits<double>::epsilon());
  retVal += (_plv.Py() - _dau1->_plv.Py() - _dau2->_plv.Py()) /
    (std::abs(_plv.Py()) + std::numeric_limits<double>::epsilon());
  retVal += (_plv.Pz() - _dau1->_plv.Pz() - _dau2->_plv.Pz()) /
    (std::abs(_plv.Pz()) + std::numeric_limits<double>::epsilon());
  retVal += (_plv.E() - _dau1->_plv.E() - _dau2->_plv.E()) /
    (std::abs(_plv.E()) + std::numeric_limits<double>::epsilon());
  return retVal;
}

void TwoBodyDecay::boostToFrame(const TVector3& direction, double magnitude, unsigned level)
{
  _plv.Boost(-magnitude * direction);
  if (level) {
    _dirn = (1.0 / _plv.P()) * _plv.BoostVector();
    _pmag_parent = _plv.P();
  } else if (magnitude > 0.) {
    _plv.SetVectM(TVector3(0., 0., 0.), _plv.M());
  }

  if (_dau1) _dau1->boostToFrame(direction, magnitude, level + 1);
  if (_dau2) _dau2->boostToFrame(direction, magnitude, level + 1);
}


void TwoBodyDecay::toRestFrame()
{
  boostToFrame(_dirn, _pmag_parent);

  if (_dau1) _dau1->toRestFrame();
  if (_dau2) _dau2->toRestFrame();
}


void TwoBodyDecay::toParentFrame()
{
  if (_dau1) _dau1->toParentFrame();
  if (_dau2) _dau2->toParentFrame();

  boostFromFrame(_dirn, _pmag_parent);
}


void TwoBodyDecay::update_momenta()
{
  if (_dau1 && _dau2) {
    const double M = _plv.M();
    const double m1 = _dau1->_plv.M();
    const double m2 = _dau2->_plv.M();

    const double r1 = m1 / M, r2 = m2 / M;

    const double t1 = 0.5 * (1. - (r1 * r1 + r2 * r2)), t2 = r1 * r2;
    const double pmag = M * std::sqrt((t1 + t2) * (t1 - t2));

    const double oEn1 = std::sqrt(_dau1->_oldmass * _dau1->_oldmass +
	_dau1->_pmag_parent * _dau1->_pmag_parent);
    const double nEn1 = std::sqrt(m1 * m1 + pmag * pmag);
    _dau1->_dirn *= oEn1 / nEn1;
    _dau1->_pmag_parent = pmag;

    const double oEn2 = std::sqrt(_dau2->_oldmass * _dau2->_oldmass +
	_dau2->_pmag_parent * _dau2->_pmag_parent);
    const double nEn2 = std::sqrt(m2 * m2 + pmag * pmag);
    _dau2->_dirn *= oEn2 / nEn2;
    _dau2->_pmag_parent = pmag;
  }

  _oldmass = _plv.M();

  if (_dau1) _dau1->update_momenta();
  if (_dau2) _dau2->update_momenta();
}


void TwoBodyDecay::Print(unsigned level) const
{
  const std::string indent(4 * level, ' ');

  std::printf("SA-DEBUG: %s_plv: E = %12.6g, Px = %12.6g, Py = %12.6g, Pz = %12.6g M = %12.6g\n",
      indent.c_str(), _plv.E(), _plv.Px(), _plv.Py(), _plv.Pz(), _plv.M());
  std::printf("SA-DEBUG: %s_dirn, _pmag_parent: Px = %12.6g, Py = %12.6g, Pz = %12.6g, E = %12.6g\n",
      indent.c_str(), _dirn.X(), _dirn.Y(), _dirn.Z(), _pmag_parent);
  std::printf("SA-DEBUG: %sRelative 4-Momentum conservation: %12.6g\n",
      indent.c_str(), RelFourMomCons());

  if (_dau1) _dau1->Print(level + 1);
  if (_dau2) _dau2->Print(level + 1);
}
