/**
 * @file DecayTreeTupleSucksFitter.h
 *
 * fit four-momenta from DecayTreeTuple (saved in float precision), imposing
 * constraints on the known masses and four-momentum conservation to regain
 * some of the lost precision
 *
 * @author Manuel Schiller <manuel.schiller@nikhef.nl>
 * @date 2012-07-17
 */

#ifndef DECAYTREEFITTERSUCKS_H
#define DECAYTREEFITTERSUCKS_H 1

/** @class DecayTreeTupleSucksFitter
 *
 * @author Manuel Schiller <manuel.schiller@nikhef.nl>
 * @date 2012-07-17
 *
 * This class allows to refit MC truth particle momenta read from a
 * DecayTreeTuple, constraining masses of particle to their know masses and
 * imposing 4-momentum conservation. The reason this is needed lies in the
 * fact that the precision used to save momenta in the DecayTreeTuple (float
 * precision) is not sufficient to guarantee these properties.
 *
 * For example: The mass of a pion from a B decay as calculated from the MC
 * truth 4-vector may deviate by as much as 4 MeV from the mass at which it
 * was generated due to the precision loss incurred by saving the 4-momentum
 * as float...
 *
 * Note: The order for the four-vectors is (E, px, py, pz)!
 */
class DecayTreeTupleSucksFitter
{
    public:
	/** @brief initialise fitter with given masses
	 *
	 * @param motherMass	mass of mother particle
	 * @param daughter1Mass	mass of first daughter
	 * @param daughter2Mass	mass of second daughter
	 * @param starredMass	if >= 0: constrain mass of starred particle
	 * @param missingMass	if >= 0: constrain mass of missing particle
	 * @param sigmaMotherMass	strength of mother mass constraint
	 * @param sigmaDaughter1Mass	strength of 1st daughter mass constraint
	 * @param sigmaDaughter2Mass	strength of 2nd daughter mass constraint
	 * @param sigmaStarMass		strength of starred mass constraint
	 * @param sigmaMissMass		strength of missing mass constraint
	 *
	 * default is to not constrain the mass of the missing particle; the
	 * sigma* parameters allow to loosen the mass constraint - instead of
	 * pinning the mass of a fitted 4-momentum vector to the mass given,
	 * you can loosen this to be compatible with the natural width of the
	 * particle (if it has an appreciable natural width)
	 *
	 * Note: constraining to a 0 mass particle should work, but there's no
	 * guarantee that you end up on the positive side for the resulting
	 * mass (but you will be close to zero mass).
	 */
	DecayTreeTupleSucksFitter(
		double motherMass, double daughter1Mass, double daughter2Mass,
		double starredMass = -1., double missingMass = -1.,
		double sigmaMotherMass = -1., double sigmaDaughter1Mass = -1.,
		double sigmaDaughter2Mass = -1., double sigmaStarMass = -1.,
		double sigmaMissMass = -1.);

	/// fit momenta subject to constraints specified in constructor
	inline bool fit(double (&pMother)[4],
		double (&pDaughter1)[4], double (&pDaughter2)[4]) const
	{ return doFit(&pMother[0], &pDaughter1[0], &pDaughter2[0], 0); }
	/// fit momenta subject to constraints specified in constructor
	inline bool fit(double (&pMother)[4], double (&pDaughter1)[4],
		double (&pDaughter2)[4], double (&pMiss)[4]) const
	{ return doFit(&pMother[0], &pDaughter1[0], &pDaughter2[0], &pMiss[0]); }

    private:
	double m_motherM;
	double m_daughter1M;
	double m_daughter2M;
	double m_starM;
	double m_missM;
	double m_sigmaMotherM;
	double m_sigmaDaughter1M;
	double m_sigmaDaughter2M;
	double m_sigmaStarM;
	double m_sigmaMissM;

	bool doFit(double *pMo, double* pDa1, double* pDa2, double* pMi) const;

	inline double M2(const double* p) const
	{ return p[0] * p[0] - (p[1] * p[1] + p[2] * p[2] + p[3] * p[3]); }
};

#endif // DECAYTREEFITTERSUCKS_H

// vim: tw=78:sw=4:ft=cpp
