/** @file B2DXFitters/icc_fpclass_workaround.h
 *
 * @author Manuel Schiller <manuel.schiller@nikhef.nl>
 * @date 2013-02-14
 *
 * work around Intel C++ compiler bug
 *
 * for details, see
 * http://software.intel.com/en-us/forums/topic/297833
 *
 * the functions implemented here should be reasonably portable (any processor
 * with IEEE 754 floating point arithmetic should work just fine)
 *
 * there is one difference to the C++ style version of these functions:
 * in C++. these guys return a bool, we return an int, in line with the way
 * things are done in C. the advantage is that isinf(x) can return the sign of
 * the infinity as well...
 *
 * I know this is far from perfect, but it's the best I can do for now...
 * 	- M. Schiller <manuel.schiller@cern.ch> 2013-02-14
 */
#ifndef _ICC_FPCLASS_WORKAROUND
#define _ICC_FPCLASS_WORKAROUND 1

#include <cmath>
#include <limits>

#undef isnan
#undef isinf
#undef isfinite
#undef isnormal
#undef fpclassify

// declare and implement isnan, isinf, isnormal, isfinite, fpclassify in a
// namespace of its own, available irrespective of the compiler used so
// verifying correctness is a bit easier
#undef __DE_C_L__
#define __DE_C_L__(X) X __attribute((unused)); X
namespace __intel_compiler_fixes {
    // provide explicit overloads to make the compiler prefer them over
    // the templated versions in the standard library
    
    //  float versions
    __DE_C_L__(static __inline int isnan(float x))
    { return x != x; }
    __DE_C_L__(static __inline int isinf(float x))
    { return (x && x == float(2) * x) * (x > float(0) ? 1 : -1); }
    __DE_C_L__(static __inline int isfinite(float x))
    { return !isnan(x) && !isinf(x); }
    __DE_C_L__(static __inline int isnormal(float x))
    { return isfinite(x) && std::abs(x) >= std::numeric_limits<float>::min(); }
    __DE_C_L__(static __inline int fpclassify(float x))
    {
	if (isnan(x)) return FP_NAN;
	if (isinf(x)) return FP_INFINITE;
	if (float(0) == std::abs(x)) return FP_ZERO;
	if (isnormal(x)) return FP_NORMAL;
	else return FP_SUBNORMAL;
    }

    // double versions
    __DE_C_L__(static __inline int isnan(double x))
    { return x != x; }
    __DE_C_L__(static __inline int isinf(double x))
    { return (x && x == double(2) * x) * (x > double(0) ? 1 : -1); }
    __DE_C_L__(static __inline int isfinite(double x))
    { return !isnan(x) && !isinf(x); }
    __DE_C_L__(static __inline int isnormal(double x))
    { return isfinite(x) && std::abs(x) >= std::numeric_limits<double>::min(); }
    __DE_C_L__(static __inline int fpclassify(double x))
    {
	if (isnan(x)) return FP_NAN;
	if (isinf(x)) return FP_INFINITE;
	if (double(0) == std::abs(x)) return FP_ZERO;
	if (isnormal(x)) return FP_NORMAL;
	else return FP_SUBNORMAL;
    }

    // long double versions
    __DE_C_L__(static __inline int isnan(long double x))
    { return x != x; }
    __DE_C_L__(static __inline int isinf(long double x))
    {
	return (x && x == static_cast<long double>(2) * x) *
	    (x > static_cast<long double>(0) ? 1 : -1);
    }
    __DE_C_L__(static __inline int isfinite(long double x))
    { return !isnan(x) && !isinf(x); }
    __DE_C_L__(static __inline int isnormal(long double x))
    {
	return isfinite(x) &&
	    std::abs(x) >= std::numeric_limits<long double>::min();
    }
    __DE_C_L__(static __inline int fpclassify(long double x))
    {
	if (isnan(x)) return FP_NAN;
	if (isinf(x)) return FP_INFINITE;
	if (static_cast<long double>(0) == std::abs(x)) return FP_ZERO;
	if (isnormal(x)) return FP_NORMAL;
	else return FP_SUBNORMAL;
    }

    // templated versions
    __DE_C_L__(template <class F> static __inline int isnan(F x))
    { return x != x; }
    __DE_C_L__(template <class F> static __inline int isinf(F x))
    { return (x && x == F(2) * x) * (x > F(0) ? 1 : -1); }
    __DE_C_L__(template <class F> static __inline int isfinite(F x))
    { return !isnan(x) && !isinf(x); }
    __DE_C_L__(template <class F> static __inline int isnormal(F x))
    { return isfinite(x) && std::abs(x) >= std::numeric_limits<F>::min(); }
    __DE_C_L__(template <class F> static __inline int fpclassify(F x))
    {
	if (isnan(x)) return FP_NAN;
	if (isinf(x)) return FP_INFINITE;
	if (F(0) == std::abs(x)) return FP_ZERO;
	if (isnormal(x)) return FP_NORMAL;
	else return FP_SUBNORMAL;
    }
}
#undef __DE_C_L__

#if (defined __ICC) or (defined __INTEL_COMPILER)
#warning "[HACK]: Intel Compiler detected, activating workaround for isnan/isinf bug..."
// make sure we use them in the std namespace
namespace std {
    using __intel_compiler_fixes::isnan;
    using __intel_compiler_fixes::isinf;
    using __intel_compiler_fixes::isfinite;
    using __intel_compiler_fixes::isnormal;
    using __intel_compiler_fixes::fpclassify;
}
// make them available in the global namespace as well
#define __DE_C_L__(n) \
static __inline int n(float x) __attribute((unused)); \
static __inline int n(float x) { return __intel_compiler_fixes::n(x); } \
static __inline int n(long double x) __attribute((unused)); \
static __inline int n(long double x) { return __intel_compiler_fixes::n(x); }
__DE_C_L__(isnan)
__DE_C_L__(isinf)
__DE_C_L__(isfinite)
__DE_C_L__(isnormal)
__DE_C_L__(fpclassify)
#undef __DE_C_L__
#endif

#endif // _ICC_FPCLASS_WORKAROUND

// vim: sw=4:tw=78:ft=cpp
