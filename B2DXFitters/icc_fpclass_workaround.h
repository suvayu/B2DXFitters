/** @file B2DXFitters.icc_fpclass_workaround.h
 *
 * @author Manuel Schiller <manuel.schiller@nikhef.nl>
 * @date 2013-02-14
 *
 * work around Intel C++ compiler bug
 *
 * for details, see
 * http://software.intel.com/en-us/forums/topic/297833
 *
 * I know this is far from perfect, but it's the best I can do for now...
 * 	- M. Schiller <manuel.schiller@cern.ch> 2013-02-14
 */
#ifndef _ICC_FPCLASS_WORKAROUND
#define _ICC_FPCLASS_WORKAROUND 1

#if (defined __ICC) or (defined __INTEL_COMPILER)
#warning "[HACK]: Intel Compiler detected, activating workaround for isnan/isinf bug..."
#include <cmath>
#include <limits>
#define DECL(X) X __attribute((unused)); X
namespace __intel_compiler_fixes {
  // provide explicit overloads to make the compiler prefer them over
  // the templated versions in the standard library
  DECL(static __inline int isnan(float x))
  { return x != x; }
  DECL(static __inline int isinf(float x))
  { return (x && x == float(2) * x) * (x > float(0) ? float(1) : float(-1)); }
  DECL(static __inline int isfinite(float x))
  { return !isnan(x) && !isinf(x); }
  DECL(static __inline int isnormal(float x))
  { return isfinite(x) && std::abs(x) >= std::numeric_limits<float>::min(); }
  DECL(static __inline int fpclassify(float x))
  {
    if (isnan(x)) return FP_NAN;
    if (isinf(x)) return FP_INFINITE;
    if (float(0) == std::abs(x)) return FP_ZERO;
    if (isnormal(x)) return FP_NORMAL;
    else return FP_SUBNORMAL;
  }
  DECL(static __inline int isnan(double x))
  { return x != x; }
  DECL(static __inline int isinf(double x))
  {
    return (x && x == double(2) * x) *
      (x > double(0) ? double(1) : double(-1));
  }
  DECL(static __inline int isfinite(double x))
  { return !isnan(x) && !isinf(x); }
  DECL(static __inline int isnormal(double x))
  { return isfinite(x) && std::abs(x) >= std::numeric_limits<double>::min(); }
  DECL(static __inline int fpclassify(double x))
  {
    if (isnan(x)) return FP_NAN;
    if (isinf(x)) return FP_INFINITE;
    if (double(0) == std::abs(x)) return FP_ZERO;
    if (isnormal(x)) return FP_NORMAL;
    else return FP_SUBNORMAL;
  }
  DECL(static __inline int isnan(long double x))
  { return x != x; }
  DECL(static __inline int isinf(long double x))
  {
    return (x && x == static_cast<long double>(2) * x) *
      (x > static_cast<long double>(0) ? static_cast<long double>(1) :
		  static_cast<long double>(-1));
  }
  DECL(static __inline int isfinite(long double x))
  { return !isnan(x) && !isinf(x); }
  DECL(static __inline int isnormal(long double x))
  {
    return isfinite(x) &&
      std::abs(x) >= std::numeric_limits<long double>::min();
  }
  DECL(static __inline int fpclassify(long double x))
  {
    if (isnan(x)) return FP_NAN;
    if (isinf(x)) return FP_INFINITE;
    if (static_cast<long double>(0) == std::abs(x)) return FP_ZERO;
    if (isnormal(x)) return FP_NORMAL;
    else return FP_SUBNORMAL;
  }
}
// make sure we use them in the std namespace
namespace std {
  using __intel_compiler_fixes::isnan;
  using __intel_compiler_fixes::isinf;
  using __intel_compiler_fixes::isfinite;
  using __intel_compiler_fixes::isnormal;
  using __intel_compiler_fixes::fpclassify;
}
#undef DECL
#endif

#endif // _ICC_FPCLASS_WORKAROUND

// vim: sw=4:tw=78:ft=cpp
