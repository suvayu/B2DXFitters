/** @file QRDecomposition.h
 *
 * QR decomposition of square matrices
 *
 * @author Manuel Tobias Schiller
 * @date Aug 20 2008
 */

#ifndef _QRDECOMPOSITION_H
#define _QRDECOMPOSITION_H

#include <cmath>
#include <limits>
#include <complex>
#include <algorithm>

namespace ROOT {
    namespace Math {
	/// forward declaration
	template<class F,unsigned int D1,unsigned int D2,class R> class SMatrix;
	/// forward declaration
	template <class T,unsigned int D> class SVector;
    }
}

/// namespace to hold helper functions/structs for QRDecomposition
namespace QRDecompositionTools {
    /// return eps for a certain floating point type
    /**
     *  eps is the smallest positive number that, when added to 1, yields a
     *  number greater than one
     */
    template<class T> inline T eps(const T&)
    {
	static T eps = -1;
	if (eps > T(0)) return eps;
	// a straightforward implementation - we only play a few games
	// with a volatile variable tmp below to make sure the compiler
	// does not compare in floating point registers which may have a
	// greater precision than the type we want to check
	volatile T tmp = T(3) / T(2);
	for (eps = 1; tmp > T(1); eps /= T(2)) tmp = T(1) + eps / T(4);
	return eps;
    }
    /// overload for known floating point types (float)
    inline float eps(const float&)
    { return std::numeric_limits<float>::epsilon(); }
    /// overload for known floating point types (double)
    inline double eps(const double&)
    { return std::numeric_limits<double>::epsilon(); }
    /// overload for known floating point types (long double)
    inline long double eps(const long double&)
    { return std::numeric_limits<long double>::epsilon(); }

    /// struct to typedef floating point base type
    template<class T>
	struct ComplexBaseType { typedef T type; };
    /// struct to typedef floating point base type, specialised for std::complex
    template<class T>
	struct ComplexBaseType<std::complex<T> > { typedef T type; };

    /// proxy struct to avoid ROOT SVector/SMatrix indexing nightmares
    template<class V, bool forMatrix = false> struct VectorIndexingProxy
    {
	typedef typename V::value_type F;
	V& v;
	VectorIndexingProxy(V& b) : v(b) { }
	inline F& operator[](unsigned i) { return v(i); }
	inline const F& operator[](unsigned i) const { return v(i); }
    };

    /// proxy struct to avoid ROOT SVector/SMatrix indexing nightmares
    template<class V> struct VectorIndexingProxy<V, true>
    {
	typedef typename V::value_type F;
	V& v;
	unsigned i;
	VectorIndexingProxy(V& b, unsigned row) : v(b), i(row) { }
	inline F& operator[](unsigned j) { return v(i, j); }
	inline const F& operator[](unsigned j) const { return v(i, j); }
    };

    /// proxy struct to avoid ROOT SVector/SMatrix indexing nightmares
    template<class V> struct MatrixIndexingProxy
    {
	V& v;
	MatrixIndexingProxy(V& b) : v(b) { }
	inline VectorIndexingProxy<V, false>&
	    operator[](unsigned i)
	    { return VectorIndexingProxy<V, false>(v, i); }
	inline const VectorIndexingProxy<V, false>&
	    operator[](unsigned i) const 
	    { return VectorIndexingProxy<V, false>(v, i); }
    };

    /// proxy struct to present a matrix column as (row-)vector
    template <class M, class F> struct TransposingProxy {
	M& m_m;
	unsigned m_col;
	TransposingProxy(M& m, unsigned col) : m_m(m), m_col(col) { }
	inline F& operator[](unsigned i) { return m_m[i][m_col]; }
	inline F operator[](unsigned i) const { return m_m[i][m_col]; }
    };
}

/// do a QR decomposition of a square matrix
/** @class QRDecomposition QRDecomposition.h 
 *
 * template parameter F specifies the floating point type to be used
 * internally for calculations (can also be complex)
 *
 * This implementation is not optimized for speed but for reliability.
 * When presented with a singular matrix, it will attempt to solve the
 * system of linear equations for the non-singular portion of the system.
 * When this behaviour is undesired, one should test if the matrix is
 * singular with one of the methods of this class.
 *
 * If you need to solve a system of linear equations, please note that the
 * solve method is more accurate than a call to invert and a matrix
 * multiplication. invert should only be used when you really need the
 * inverse of a matrix.
 *
 * @author Manuel Tobias Schiller
 *
 * @date Jul 30 2006	initial implementation
 * @date Aug 05 2006	implemented version with pivoting
 * @date Aug 14 2008	rewrite as templated class
 * @date Aug 19 2008	make it work for complex matrices
 * @date Sep 26 2013	change pivoting for better stability
 */
template <class F = double>
class QRDecomposition
{
    /// convenience typedef for floating point base type
    typedef typename QRDecompositionTools::ComplexBaseType<F>::type FBASE;

    public:
    /// constructor from something that behaves like a C style array
    /**
     * @param nn dimension of the matrix
     * @param m matrix itself
     * @param eps consider element to be zero if below eps * max(abs(m[i][j]))
     */
    template <class M>
	QRDecomposition(unsigned nn, const M& m, FBASE eps = -1) :
	    nnn(nn), a(new F[nn * (nn + 1)]), c(new F[nn]), d(a + nn * nn),
	    pc(new unsigned[2 * nn]), pr(pc + nn), nsing(0)
    {
	// copy m to working area a
	for (unsigned i = 0; i < nn; ++i) {
	    for (unsigned j = 0; j < nn; ++j) {
		a[i * nn + j] = m[i][j];
	    }
	}
	// make sure that eps has a reasonable size
	// if the user specifies a positive value, we use it (the user usually
	// knows best), otherwise, we just use eps() for our base floating
	// point type
	if (eps < FBASE(0))
	    eps = QRDecompositionTools::eps(eps);
	// decompose the beast
	decompose(eps);
    }

    /// constructor from ROOT's SMatrix
    /**
     * @param m matrix itself
     * @param eps consider element to be zero if below eps * max(abs(m[i][j]))
     */
    template <unsigned nn, class R>
	QRDecomposition(const ROOT::Math::SMatrix<F, nn, nn, R>& m, FBASE eps = -1) :
	    nnn(nn), a(new F[nn * (nn + 1)]), c(new F[nn]), d(a + nn * nn),
	    pc(new unsigned[2 * nn]), pr(pc + nn), nsing(0)
    {
	// copy m to working area a
	for (unsigned i = 0; i < nn; ++i) {
	    for (unsigned j = 0; j < nn; ++j) {
		a[i * nn + j] = m(i, j);
	    }
	}
	// make sure that eps has a reasonable size
	// if the user specifies a positive value, we use it (the user usually
	// knows best), otherwise, we just use eps() for our base floating
	// point type
	if (eps < FBASE(0))
	    eps = QRDecompositionTools::eps(eps);
	// decompose the beast
	decompose(eps);
    }

    /** @brief copy constructor
     *
     * @param other	matrix to copy from
     */
    QRDecomposition(const QRDecomposition<F>& other) :
	    nnn(other.nnn), a(new F[nnn * (nnn + 1)]), c(new F[nnn]), d(a + nnn * nnn),
	    pc(new unsigned[2 * nnn]), pr(pc + nnn), nsing(other.nsing)
    {
	for (unsigned i = 0; i < nnn * (nnn + 1); ++i) a[i] = other.a[i];
	for (unsigned i = 0; i < nnn; ++i) c[i] = other.c[i];
	for (unsigned i = 0; i < 2 * nnn; ++i) pc[i] = other.pc[i];
    }

    /** @brief assignment operator
     *
     * @param other	matrix to assign to this matrix
     * @returns		this matrix
     */
    QRDecomposition<F>& operator=(const QRDecomposition<F>& other)
    {
	if (&other == this) return *this;
	delete[] a;
	delete[] c;
	delete[] pc;
	nnn = other.nnn;
	a = new F[nnn * (nnn + 1)];
	c = new F[nnn];
	d = a + nnn * nnn;
	pc = new unsigned[2 * nnn];
	pr = pc + nnn;
	nsing = other.nsing;
	return *this;
    }

    /// destructor
    virtual ~QRDecomposition()
    {
	delete[] a;
	delete[] c;
	delete[] pc;
    }

    /// return number of singularities encoutered
    inline unsigned nSing() const { return nsing; }
    /// return dimensionality of the matrix
    inline unsigned n() const { return nnn; }
    /// return rank of the matrix
    inline unsigned rank() const { return n() - nSing(); }
    /// return true if decomposition was successful
    inline bool ok() const { return 0 == nsing; }

    /// solve system of linear equations (e.g. M x = b)
    /**
     * @param nn dimension of b
     * @param b right hand side vector in M x = b
     * @returns number of singularities encountered, solution x in b
     */
    template<class V> inline unsigned solve(unsigned nn, V& b) const
    {
	if (n() != nn) throw;

	// apply pivoting
	//F* tmp = new F[nn];
	F tmpa[nn];
	F* tmp = tmpa;
	for (unsigned i = nn; i--; tmp[i] = b[pr[i] / nn]);
	// solve
	doSolve(nn, tmp);
	// copy back to user supplied vector
	for (unsigned i = nn; i--; b[pc[i]] = tmp[i]);
	//delete[] tmp;

	return nSing();
    }

    /// solve system of linear equations (version for ROOT's SVectors)
    /**
     * @param b right hand side vector in M x = b
     * @returns number of singularities encountered, solution x in b
     */
    template <unsigned nn>
    inline unsigned solve(ROOT::Math::SVector<F,nn>& b) const
    { return solve(nn, QRDecompositionTools::VectorIndexingProxy<
	    ROOT::Math::SVector<F,nn>, false>(b)); }

    /// form inverse of matrix using calculated QR decomposition
    /**
     * @param nn size of matrix
     * @param m destination of inverse
     * @returns number of singularities in original matrix
     */
    template <class M> inline unsigned invert(unsigned nn, M& m) const
    {
	if (n() != nn) throw;

	// zero output matrix
	for (unsigned i = 0; i < nn; ++i)
	    for (unsigned j = 0; j < nn; ++j) m[i][j] = 0;

	// ok, solve for each unit vector along one of the coordinate
	// axes
	for (unsigned i = 0; i < nn; ++i) {
	    m[i][i] = 1;
	    QRDecompositionTools::TransposingProxy<M, F> proxy(m, i);
	    solve(nn, proxy);
	}

	return nSing();
    }

    /// form inverse of matrix using calculated QR decomposition
    /**
     * @param m destination of inverse
     * @returns number of singularities in original matrix
     */
    template <unsigned nn, class R> inline unsigned invert(
	    ROOT::Math::SMatrix<F, nn, nn, R>& m) const
    { return invert(nn, QRDecompositionTools::MatrixIndexingProxy<
	    ROOT::Math::SMatrix<F,nn,nn,R> >(m)); }

    protected:
    /** A few words on the storage format of the decomposed matrix:
     *
     * a contains the householder vectors below and including the diagonal.
     * c contains scaling factors by which the tensor product of a
     * householder vector with itself must be divided.
     *
     * Above the diagonal, a contains the entries of R; the diagonal of R is
     * in d.
     *
     * p contains the permutation of rows applied to the original matrix. It
     * is applied to a in the code, while c and d are filled in the order of
     * the permuted rows.
     */
    unsigned nnn;	///< size of matrix
    F* a;		///< decomposed matrix
    FBASE* c;		///< scaling for householder matrices
    F* d;		///< diagonale of R
    unsigned* pc;	///< permutation for column pivoting
    unsigned* pr;	///< permutation for row pivoting
    unsigned nsing;	///< number of singularities

    /// squared distance from zero for real number
    inline FBASE norm(const FBASE& x) const { return x * x; }
    /// squared distance from zero for complex number
    inline FBASE norm(const std::complex<FBASE>& x) const
    { return std::norm(x); }

    /// complex conjugate of real number (is identity)
    inline FBASE conj(const FBASE& x) const { return x; }
    /// complex conjugate for complex numbers
    inline std::complex<FBASE> conj(const std::complex<FBASE>& x) const
    { return std::conj(x); }

    /// method to chose correct sign/phase when decomposing matrix
    inline FBASE choosePhase(const FBASE& x, const FBASE& y) const
    { return (y < FBASE(0)) ? -x : x; }
    /// method to chose correct sign/phase when decomposing matrix
    inline std::complex<FBASE> choosePhase(
	    const FBASE& x, const std::complex<FBASE>& y) const
    { return (x / abs(y)) * y; }

    /// method that does the actual decomposition
    inline void decompose(const FBASE& eps)
    {
	using std::sqrt;
	using std::abs;
	const unsigned nn = n();

	// set up the identity row and column permutations for pivoting
	for (unsigned i = nn; i--; pc[i] = i, pr[i] = nn * i);
	// find greatest absolute value of all elements in the matrix
	// we need this to tell if a value is close to singular or not
	// (1e-16 may be a large value if the maximum in the matrix is
	// 1e-15, if the maximum is 3.1415 however, it's small, of course)
	FBASE max = 0;
	for (unsigned i = 0; i < nn; ++i) {
	    for (unsigned j = 0; j < nn; ++j)
		if (abs(a[pr[i] + j]) > max)
		    max = abs(a[pr[i] + j]);
	}
	if (FBASE(0) == max) max = 1;

	// ok, here comes the main decomposition loop
	for (unsigned i = 0; i < (nn - 1); ++i) {
	    // get column with largest column norm for column pivoting
	    FBASE best = 0;
	    unsigned q = i;
	    for (unsigned j = i; j < nn; ++j) {
		FBASE tmp = 0;
		for (unsigned k = i; k < nn; ++k)
		    tmp += norm(a[pr[k] + pc[j]]);
		if (tmp <= best) continue;
		q = j;
		best = tmp;
	    }
	    FBASE colnorm = best;
	    std::swap(pc[i], pc[q]);

	    FBASE scale = 0;
	    // determine scale
	    for (unsigned j = i; j < nn; ++j)
		if (abs(a[pr[j] + pc[i]]) > scale)
		    scale = abs(a[pr[j] + pc[i]]);
	    // we have to handle singularity - decomposition is attempted
	    // anyway (i.e. decompose the non-singular part of the matrix)
	    if (std::max(scale, abs(a[pr[i] + pc[i]])) <= eps * max) {
		++nsing;
		d[i] = c[i] = 0;
		continue;
	    }
	    // select a pivot element (i.e. next row to work on)
	    // we use the one with the largest non-zero element on the
	    // diagonal
	    best = abs(a[pr[i] + pc[i]]);
	    q = i;
	    for (unsigned j = i + 1; j < nn; ++j) {
		FBASE goodness = abs(a[pr[j] + pc[i]]);
		if (goodness <= best) continue;
		// better than previous best pivot choice, save it
		best = goodness;
		q = j;
	    }
	    // ok, modify the permutation in such a way that the pivot
	    // element's row "bubbles up" to the diagonale
	    std::swap(pr[i], pr[q]);
	    // we scale the entries of our matrix (to avoid wildly differing
	    // orders of magnitude)
	    // scale the i-th column vector and calculate its length
	    // scale still contains the scale factor we need (see above), and
	    // colnorm can be adjusted
	    for (unsigned j = i; j < nn; ++j)
		a[pr[j] + pc[i]] /= scale;
	    colnorm = sqrt(colnorm) / scale;

	    // the orthogonal matrix Q for this step is 1 in that part of our
	    // matrix which has already been decomposed to upper triangular
	    // form anyway, so we consider the rest only in the description
	    // below
	    // calculate vector v such that Q = 1 - 2 v * v^T is the
	    // orthogonal transform we are looking for
	    // ( complex case: Q = 1 - 2 v * conj(v^T) )
	    // this works like that: x = i-th column vector of a,
	    // u = x - sqrt(x^T*x)*(1,0,...)^T,
	    // v = u / sqrt(u^T*u)
	    // Q as defined above will then reflect u onto the i-th axis
	    // we also have to make sure that x[0] and sqrt(x^T*x) have
	    // opposite signs to avoid loss in precision (complex case:
	    // u[0] and sqrt(x^T*x) should have the same argument)
	    // things get slightly complicated by the compact storage format
	    // and the scaling stuff needed
	    F sigma = choosePhase(colnorm, a[pr[i] + pc[i]]);
	    a[pr[i] + pc[i]] += sigma; // v in a[pr[i]][pc[i]]...a[pr[n]][pc[i]]
	    c[i] = colnorm * abs(a[pr[i] + pc[i]]); // 1/2 * |v|^2
	    d[i] = -scale * sigma;
	    // apply Q to rest of a
	    for (unsigned j = i + 1; j < nn; ++j) {
		F tmp = 0;
		for (unsigned k = i; k < nn; ++k)
		    tmp += conj(a[pr[k] + pc[i]]) * a[pr[k] + pc[j]];
		tmp /= c[i];
		for (unsigned k = i; k < nn; ++k)
		    a[pr[k] + pc[j]] -= tmp * a[pr[k] + pc[i]];
	    }
	}
	// write d entry for last column and check one last time for
	// singularity
	if (abs(d[nn - 1] = a[pr[nn - 1] + pc[nn - 1]]) <= eps * max) {
	    d[nn - 1] = c[nn - 1] = 0;
	    ++nsing;
	}
    }

    /// helper routine to do the solving work
    template<class V> inline void doSolve(const unsigned nn, V& b) const
    {
	// we'll try hard to calculate around the singularities and still
	// get a meaningful result for the rest - this may or may not be
	// what you want

	// calculate Q^T b
	for (unsigned j = 0; j < (nn - 1); ++j) {
	    if (F(0) == c[j])
		continue;
	    F tmp = 0;
	    for (unsigned i = j; i < nn; ++i)
		tmp += conj(a[pr[i] + pc[j]]) * b[i];
	    tmp /= c[j];
	    for (unsigned i = j; i < nn; ++i)
		b[i] -= tmp * a[pr[i] + pc[j]];
	}

	// ok, solve Rx = Q^T b
	for (unsigned i = nn; i--; ) {
	    if (F(0) == d[i]) {
		b[i] = 0;
		continue;
	    }
	    F tmp = 0;
	    for (unsigned j = i + 1; j < nn; ++j)
		tmp += a[pr[i] + pc[j]] * b[j];
	    b[i] = (b[i] - tmp) / d[i];
	}
    }
};

#endif // _QRDECOMPOSITION_H

// vim: tw=78:shiftwidth=4:ft=cpp
