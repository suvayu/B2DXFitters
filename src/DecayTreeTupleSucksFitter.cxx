/**
 * @file DecayTreeTupleSucksFitter.cxx
 *
 * fit four-momenta from DecayTreeTuple (saved in float precision), imposing
 * constraints on the known masses and four-momentum conservation to regain
 * some of the lost precision
 *
 * @author Manuel Schiller <manuel.schiller@nikhef.nl>
 * @date 2012-07-17
 */

#include <cmath>
#include <cstdio>
#include <limits>
#include <vector>
#include <cassert>
#include <algorithm>

#include "B2DXFitters/QRDecomposition.h"
#include "B2DXFitters/DecayTreeTupleSucksFitter.h"

DecayTreeTupleSucksFitter::DecayTreeTupleSucksFitter(
	double motherMass, double daughter1Mass, double daughter2Mass,
	double starredMass, double missingMass,
	double sigmaMotherMass, double sigmaDaughter1Mass,
	double sigmaDaughter2Mass, double sigmaStarMass, double sigmaMissMass) :
    m_motherM(motherMass),
    m_daughter1M(daughter1Mass), m_daughter2M(daughter2Mass),
    m_starM(starredMass), m_missM(missingMass),
    m_sigmaMotherM(sigmaMotherMass),
    m_sigmaDaughter1M(sigmaDaughter1Mass),
    m_sigmaDaughter2M(sigmaDaughter2Mass),
    m_sigmaStarM(sigmaStarMass),
    m_sigmaMissM(sigmaMissMass)
{
    const double m[5] = { m_motherM, m_daughter1M, m_daughter2M,
	m_starM, m_missM };
    double mhi = m[0];
    // find biggest non-zero mass - usually it's the mother...
    for (unsigned i = 0; i < 5; ++i) {
	if (m[i] > 0. && m[i] > mhi)
	    mhi = m[i];
    }
    // put mass scale to mhi
    const double mscale = mhi;
    // assign mass errors based on mass scale
    if (m_sigmaMotherM < -0. && m_motherM >= 0.)
	m_sigmaMotherM = std::numeric_limits<float>::epsilon() * mscale;
    if (m_sigmaDaughter1M < -0. && m_daughter1M >= 0.)
	m_sigmaDaughter1M = std::numeric_limits<float>::epsilon() * mscale;
    if (m_sigmaDaughter2M < -0. && m_daughter2M >= 0.)
	m_sigmaDaughter2M = std::numeric_limits<float>::epsilon() * mscale;
    if (m_sigmaStarM < -0. && m_starM >= 0.)
	m_sigmaStarM = std::numeric_limits<float>::epsilon() * mscale;
    if (m_sigmaMissM < -0. && m_missM >= 0.)
	m_sigmaMissM = std::numeric_limits<float>::epsilon() * mscale;
}

bool DecayTreeTupleSucksFitter::doFit(
	double *pMo, double* pDa1, double* pDa2, double *pMi) const
{
    const unsigned maxiter = 1024;
    // figure out dimensionality of problem
    const unsigned dim = (pMi ? 16 : 12);
    // verify that all quantities are given
    assert(pMo);
    assert(pDa1);
    assert(pDa2);
    assert((m_starM < -0. && m_sigmaStarM < -0.) ||
	    (m_starM >= -0. && m_sigmaStarM > 0. && pMi));
    assert((m_missM < -0. && m_sigmaMissM < -0.) ||
	    (m_missM >= -0. && m_sigmaMissM > 0.));

    // current best guess of 4-momenta
    double qMo[4], qDa1[4], qDa2[4], qMi[4];
    // convenience arrays
    const double *p[4] = { pMo, pDa1, pDa2, pMi };
    double *q[4] = { qMo, qDa1, qDa2, qMi };
    const double m[5] = {
	m_motherM, m_daughter1M, m_daughter2M, m_missM, m_starM
    };
    const double sm[5] = {
	m_sigmaMotherM, m_sigmaDaughter1M,
	m_sigmaDaughter2M, m_sigmaMissM, m_sigmaStarM
    };
    // right hand side/correction to 4-momenta
    // order is qMo, qDa1, qDa2 (, qMi)
    std::vector<double> dq(dim, 0.);
    // matrix
    std::vector<std::vector<double> > mat(dim, std::vector<double>(dim, 0.));

    if (pMi) {
	// supply initial guess for missing particle
	for (unsigned i = 0; i < 4; ++i) {
	    pMi[i] = pMo[i] - pDa1[i] - pDa2[i];
	}
    }
    // starting values are "measured" momenta
    std::copy(pMo, pMo + 4, qMo);
    std::copy(pDa1, pDa1 + 4, qDa1);
    std::copy(pDa2, pDa2 + 4, qDa2);
    if (pMi) std::copy(pMi, pMi + 4, qMi);

    unsigned dst = -1;
    if (m_starM >= -0. && m_sigmaStarM > 0.) {
	// autodetect the daughter of the starred particle among the
	// daughters; we chose such that the starred is heavier than the
	// unstarred particle, and the two have the smallest mass difference
	for (unsigned dd = 1; dd < 3; ++dd) {
	    // skip if starred particle is lighter than unstarred
	    if (m[4] < m[dd])
		continue;
	    // skip if starred particle is further away in mass from unstarred
	    // than the current best guess
	    if (unsigned(-1) != dst &&
		    std::abs(m[4] - m[dst]) < std::abs(m[4] - m[dd]))
		continue;
	    dst = dd;
	}
	assert(dst != unsigned(-1));
    }

    // iterate (linearised) fit
    unsigned niter;
    for (niter = 0; niter < maxiter; ++niter) {
	// zero matrix, right hand side
	std::fill(dq.begin(), dq.end(), 0.);
	for (unsigned i = 0; i < dim; ++i) {
	    std::fill(mat[i].begin(), mat[i].end(), 0.);
	}
	// fill matrix, right hand side
	for (unsigned d = 0; d < dim / 4; ++d) {
	    for (unsigned i = 0; i < 4; ++i) {
		// constrain q to measured momenta p withing float precision
		if (d < 3) {
		    const double s2 = p[d][i] * p[d][i] *
			std::numeric_limits<float>::epsilon() *
			std::numeric_limits<float>::epsilon();
		    dq[4 * d + i] += (q[d][i] - p[d][i]) / s2;
		    mat[4 * d + i][4 * d + i] += 1. / s2;
		}

		// impose 4-vector conservation
		{
		    double s2 = 0.;
		    for (unsigned j = 0; j < 3; ++j) {
			s2 += 65536. * p[j][i] * p[j][i] *
			    std::numeric_limits<double>::epsilon() *
			    std::numeric_limits<double>::epsilon();
		    }
		    double tmp = 0.;
		    for (unsigned j = 0; j < dim / 4; ++j) {
			if (j) tmp -= q[j][i];
			else tmp += q[j][i];
		    }
		    dq[4 * d + i] += tmp / s2 * (d ? -1. : 1.);
		    for (unsigned j = 0; j < dim / 4; ++j) {
			mat[4 * d + i][4 * j + i] +=
			    double((d ? -1 : 1) * (j ? -1 : +1)) / s2;
		    }
		}

		// only apply mass constraint on missing mass if we're
		// instructed to do so
		if (3 == d && (m_missM < -0. || m_sigmaMissM < -0.))
		    continue;
		// mass constraints
		{
		    // protect mass error transformation from zero mass
		    const double m2 = std::max(m[d] * m[d], 1.);
		    const double tmp = (i ? -0.5 : 0.5) /
			(sm[d] * sm[d] * m2) *
			(M2(q[d]) - m[d] * m[d]);
		    dq[4 * d + i] += tmp * q[d][i];
		    mat[4 * d + i][4 * d + i] += tmp;
		    for (unsigned j = 0; j < 4; ++j) {
			mat[4 * d + i][4 * d + j] +=
			    double((i ? -1 : 1) * (j ? -1 : 1)) *
			    q[d][i] * q[d][j] / 
			    (sm[d] * sm[d] * m2);
		    }
		}
	    }
	}
	// if needed, apply constraint on starred particle mass
	if (unsigned(-1) != dst) {
	    const unsigned idx[2] = { dst, 3 };
	    // get 4-momentum of starred particle
	    const double qst[4] = {
		q[dst][0] + q[3][0], q[dst][1] + q[3][1],
		q[dst][2] + q[3][2], q[dst][3] + q[3][3]
	    };
	    // update right hand side and matrix
	    for (unsigned j = 0; j < 2; ++j) {
		const unsigned d = idx[j];
		for (unsigned i = 0; i < 4; ++i) {
		    // protect mass error transformation from zero mass
		    const double m2 = std::max(m[4] * m[4], 1.);
		    const double tmp = (i ? -0.5 : 0.5) /
			(4. * sm[4] * sm[4] * m2) *
			(M2(qst) - m[4] * m[4]);
		    dq[4 * d + i] += tmp * qst[i];
		    mat[4 * d + i][4 * dst + i] += tmp;
		    mat[4 * d + i][4 * 3 + i] += tmp;
		    for (unsigned k = 0; k < 4; ++k) {
			const double tmp2 =
			    double((i ? -1 : 1) * (k ? -1 : 1)) *
			    qst[i] * qst[k] / 
			    (sm[4] * sm[4] * m2);
			mat[4 * d + i][4 * dst + k] += tmp2;
			mat[4 * d + i][4 * 3 + k] += tmp2;
		    }
		}
	    }
	}

	// decompose matrix
	QRDecomposition<long double> decomp(dim, mat);
	if (!decomp.ok()) {
	    std::printf("%s, in %s line %u: Status of QR decomposition: %d\n",
		    __func__, __FILE__, __LINE__, decomp.ok());
	    return false;
	}
	decomp.solve(dim, dq);

	// apply shifts
	for (unsigned d = 0; d < dim / 4; ++d) {
	    for (unsigned i = 0; i < 4; ++i) {
		q[d][i] -= dq[4 * d + i];
	    }
	}
	// check for convergence
	bool converged = true;
	for (unsigned d = 0; d < dim / 4 && converged; ++d) {
	    for (unsigned i = 0; i < 4; ++i) {
		// consider converged if only lowest 16/53 bits in mantissa
		// change
		const double eps = 65536. *
		    std::numeric_limits<double>::epsilon();
		if (std::abs(dq[d * 4 + i]) > eps &&
			std::abs(dq[d * 4 + i] / q[d][i]) > eps) {
		    converged = false;
		    break;
		}
	    }
	    // also protect against nonphysical values
	    if (dq[d * 4] < -1. || M2(&dq[d * 4]) < -1.) {
		converged = false;
		break;
	    }
	}
	if (unsigned(-1) != dst) {
	    // also protect against nonphysical values
	    // get 4-momentum of starred particle
	    const double qst[4] = {
		q[dst][0] + q[3][0], q[dst][1] + q[3][1],
		q[dst][2] + q[3][2], q[dst][3] + q[3][3]
	    };
	    if (qst[0] < -1. || M2(qst) < -1.) {
		converged = false;
	    }
	}
	if (converged) break;
    }
    // check for no convergence
    if (maxiter == niter) {
	std::printf("%s, in %s line %u: No convergence!\n",
		__func__, __FILE__, __LINE__);
	return false;
    }

    // copy back resulting momenta
    std::copy(qMo, qMo + 4, pMo);
    std::copy(qDa1, qDa1 + 4, pDa1);
    std::copy(qDa2, qDa2 + 4, pDa2);
    if (pMi) std::copy(qMi, qMi + 4, pMi);

    return true;
}

#ifdef TESTMANUEL
// include a little test program for running standalone
int main(int argc, char** argv)
{
    double pB[4] = { 229392.062500, -5512.819824, -1341.069946, 229259.093750 };
    double pD[4] = { 182871.156250, -3216.939941, -2438.939941, 182815.984375 };
    double ph[4] = {  36441.722656, -2003.869995,  1146.180054,  36368.261719 };
    double pm[4];
    double pDst[4];
    for (unsigned i = 0; i < 4; ++i) {
	pm[i] = pB[i] - pD[i] - ph[i];
	pDst[i] = pm[i] + pD[i];
    }

    const double *p[5] = { pB, pD, ph, pm, pDst };
    const char *n[5] = { "pB", "pD", "ph", "pm", "p*" };

    std::printf("BEFORE FIT:\n");
    for (unsigned i = 0; i < 5; ++i) {
	std::printf("%2s = (%12.6g, %12.6g, %12.6g, %12.6g), m2 = %12.6g, m = %12.6g\n",
		n[i], p[i][0], p[i][1], p[i][2], p[i][3],
		p[i][0] * p[i][0] - 
		    (p[i][1] * p[i][1] + p[i][2] * p[i][2] + p[i][3] * p[i][3]),
		std::sqrt(p[i][0] * p[i][0] - 
		    (p[i][1] * p[i][1] + p[i][2] * p[i][2] + p[i][3] * p[i][3])));
    }

    DecayTreeTupleSucksFitter fitter(
	    5366.3, 1968.49, 139.57018, 2112.34, 0.);
    std::printf("\nFIT STATUS %d\n\n", fitter.fit(pB, pD, ph, pm));
    for (unsigned i = 0; i < 4; ++i) {
	pDst[i] = pm[i] + pD[i];
    }

    std::printf("AFTER FIT:\n");
    for (unsigned i = 0; i < 5; ++i) {
	std::printf("%2s = (%12.6g, %12.6g, %12.6g, %12.6g), m2 = %12.6g, m = %12.6g\n",
		n[i], p[i][0], p[i][1], p[i][2], p[i][3],
		p[i][0] * p[i][0] - 
		    (p[i][1] * p[i][1] + p[i][2] * p[i][2] + p[i][3] * p[i][3]),
		std::sqrt(p[i][0] * p[i][0] - 
		    (p[i][1] * p[i][1] + p[i][2] * p[i][2] + p[i][3] * p[i][3])));
    }

    return 0;
}
#endif

// vim: tw=78:sw=4:ft=cpp
