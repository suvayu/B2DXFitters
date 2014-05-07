/**
 * @file eps.e
 *
 * @author Manuel Schiller <manuel.schiller@nikhef.nl>
 * @date 2014-04-30
 *
 * @brief calculate tagging eff.s/asym.s after split into OS only, SSK only,
 * OS+SSK events
 *
 * assumes independent taggers
 */
#include <stdio.h>
#include <math.h>

/** @brief combine tagging efficiencies assuming no correlation
 *
 * @param out	output (eps_OSonly, eps_SSKonly, eps_OS+SSK, a_OSonly, ...
 * @param eps	input: tagging efficiencies (eps_OS, eps_SSK)
 * @param deps	input: (Delta eps_OS, Delta eps_SSK)
 */
static void combineEps(double out[6], const double eps[2], const double deps[2])
{
    double oeps[6];
    unsigned mask, i;
    int flav;
    for (mask = 1; mask < 4; ++mask) {
	for (flav = -1; flav <= 1; flav += 2) {
	    double e1 = eps[0] + 0.5 * flav * deps[0];
	    double e2 = eps[1] + 0.5 * flav * deps[1];
	    if (!(mask & 1)) e1 = 1. - e1;
	    if (!(mask & 2)) e2 = 1. - e2;
	    oeps[3 * ((1 - flav) / 2) + mask - 1] = e1 * e2;
	}
    }
    for (i = 0; i < 3; ++i) {
	out[i] = 0.5 * (oeps[i] + oeps[3 + i]);
	out[3 + i] = 0.5 * (oeps[i] - oeps[3 + i]) / out[i];
    }
}

int main(int argc, char* argv[])
{
    const double     eps[2] = {  0.387,  0.477 };
    const double  epserr[2] = {  0.003,  0.003 };
    const double    deps[2] = { -0.00197, 0.00022 };
    const double depserr[2] = {  0.00126, 0.00004 };
    const char* label[3] = { " OS only", "SSK only", "  OS+SSK" };
    double onom[6]; ///< nominal combined efficiencies/asymmetries
    double cov[6 * 7 / 2]; ///< covariance, packed (save only lower half)
    unsigned i;
    printf("Combining tagging efficiencies (signal):\n"
	    " OS: eps = %f+/-%f Delta eps = % f+/-%f\n"
	    "SSK: eps = %f+/-%f Delta eps = % f+/-%f\n\n",
	    eps[0], epserr[0], deps[0], depserr[0],
	    eps[1], epserr[1], deps[1], depserr[1]);
    combineEps(onom, eps, deps);
    // zero cov
    for (i = 0; i < 6 * 7 / 2; ++i) cov[i] = 0.;
    // up-/down-variation
    for (i = 0; i < 4; ++i) {
	const double epsd[2] = {
	    eps[0] - epserr[0] * (i == 0), eps[1] - epserr[1] * (i == 1)
	};
	const double epsu[2] = {
	    eps[0] + epserr[0] * (i == 0), eps[1] + epserr[1] * (i == 1)
	};
	const double depsd[2] = {
	    deps[0] - depserr[0] * (i == 2), deps[1] - depserr[1] * (i == 3)
	};
	const double depsu[2] = {
	    deps[0] + depserr[0] * (i == 2), deps[1] + depserr[1] * (i == 3)
	};
	double od[6], ou[6];
	unsigned j;
	combineEps(od, epsd, depsd);
	combineEps(ou, epsu, depsu);
	// form approx. 2 * df/ddelta * delta in ou
	for (j = 0; j < 6; ++j) ou[j] -= od[j];
	// update covariance matrix
	for (j = 0; j < 6; ++j) {
	    unsigned k;
	    for (k = 0; k <= j; ++k) {
		cov[(j * (j + 1)) / 2 + k] += 0.25 * ou[j] * ou[k];
	    }
	}

    }
    for (i = 0; i < 3; ++i) {
	const unsigned idx1 = (i * (i + 1)) / 2 + i;
	const unsigned idx2 = ((3 + i) * (i + 4)) / 2 + i + 3;
	printf("%s: eps=%f+/-%f a=% f+/-%f\n", label[i],
		onom[i], sqrt(cov[idx1]), onom[3 + i], sqrt(cov[idx2]));
    }
    printf("\nCorrelation:\n");
    for (i = 0; i < 6; ++i) {
	const double cii = cov[(i * (i + 1)) / 2 + i];
	unsigned j;
	for (j = 0; j < 6; ++j) {
	    const double cjj = cov[(j * (j + 1)) / 2 + j];
	    const double cij = (i >= j) ?
		cov[(i * (i + 1)) / 2 + j] : cov[(j * (j + 1)) / 2 + i];
	    printf(" % 24.16e", cij / sqrt(cii * cjj));
	}
	printf("\n");
    }

    return 0;
}

