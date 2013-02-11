/**
 * @file   KinHack.h
 * @date   Thu Jul 26 10:18:49 2012
 *
 * @brief  This file defines the TwoBodyDecay class
 *
 *         This is a kinematics hack for missing MC samples
 *
 */

#ifndef __KINHACK_H
#define __KINHACK_H

#include <TLorentzVector.h>

class TwoBodyDecay {
  public:
    TwoBodyDecay(TLorentzVector& pown,
	TwoBodyDecay *dau1=NULL,
	TwoBodyDecay *dau2=NULL) :
      _plv(pown),
      _dirn((1.0 / pown.P()) * pown.BoostVector()),
      _pmag_parent(pown.P()), _oldmass(pown.M()),
      _dau1(dau1), _dau2(dau2)
  { assert((_dau2 == NULL and _dau1 == NULL) or (_dau2 and _dau1)); }

    void toRestFrame();
    void toParentFrame();
    void setMass(double mass)
    { _plv.SetVectM(_plv.Vect(), mass); }
    void update_momenta();

    void Print(unsigned level = 0) const;

  private:
    TLorentzVector &_plv;	// 4-momentum in current frame
    TVector3 _dirn;		// boost direction to parent frame
    double _pmag_parent;	// boost momentum in parent frame
    double _oldmass;
    TwoBodyDecay *_dau1;
    TwoBodyDecay *_dau2;

    void boostToFrame(const TVector3& direction, double magnitude, unsigned level = 0);
    void boostFromFrame(const TVector3& direction, double magnitude, unsigned level = 0)
    { boostToFrame(direction, -magnitude, level); }
    double RelFourMomCons() const;
};

#endif	// __KINHACK_H
