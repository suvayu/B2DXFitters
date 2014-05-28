#include "B2DXFitters/RooAbsGaussModelEfficiency.h"
#include "RVersion.h"
#include "RooMath.h"
#include "TMath.h"

//ClassImp(RooAbsGaussModelEfficiency);
RooAbsGaussModelEfficiency::~RooAbsGaussModelEfficiency()  {};

namespace {
    static const Double_t rootpi(sqrt(TMath::Pi())) ;
    std::complex<double> evalApprox(Double_t x, const std::complex<double>& z) {
      // compute exp(-x^2)cwerf(-i(z-x)), cwerf(z) = exp(-z^2)erfc(-iz)
      // use the approximation: erfc(z) = exp(-z*z)/(sqrt(pi)*z)
      // to explicitly cancel the divergent exp(y*y) behaviour of
      // CWERF for z = x + i y with large negative y
      static const std::complex<double> mi(0,-1);
      std::complex<double> zp  = mi*(z-x);
      std::complex<double> zsq = zp*zp;
      std::complex<double> v = -zsq - x*x;
      std::complex<double> iz(z.imag()+x,z.real()-x); // ???
      return exp(v)*(exp(zsq)/(iz*rootpi) + 1.)*2. ;
    }

    // Calculate exp(-x^2) cwerf(i(z-x)), taking care of numerical instabilities
    std::complex<double> eval(Double_t x, const std::complex<double>& z) {
      Double_t re = z.real()-x;
#if ROOT_VERSION_CODE >= ROOT_VERSION(5,34,8)
      return (re>-5.0) ? RooMath::faddeeva_fast(std::complex<double>(-z.imag(),re))*exp(-x*x)
                       : evalApprox(x,z) ;
#else
      if (re > -5.0) {
      RooComplex erfc = RooMath::FastComplexErrFunc(RooComplex(-z.imag(),re));
      return std::complex<double>(erfc.re(), erfc.im())*exp(-x*x);
      } else {
	  return evalApprox(x,z) ;
      }
#endif
    }

  class N {
    public:
        N(double x, const std::complex<double>& z) ;
        std::complex<double> operator()(unsigned i) const { return _N[i]; }
    private:
        std::complex<double> _N[3];
  };

  class L {
      double _x;
  public:
      L(double x) : _x(x) { }
      double operator()(unsigned j, unsigned k) const ;
  };

}

N::N(double x, const std::complex<double>& z)
{
          _N[0] =  RooMath::erf(x);
          _N[1] =  exp(-x*x);
          _N[2] =  eval(x,z);
}

double
L::operator()(unsigned j, unsigned k) const
{
    // k=0: erf(x) coefficient
    // k=1: exp(-x*x) coefficient
    // k=2: eval(x,z) = exp(-x*x)*cwerf(i(z-x)) coefficient
    assert(j<18);
    assert(k<3);
    switch(k) {
        case 0: return j==0 ? 1 : 0 ;
        case 1: return j>0 ? 2*(*this)(j-1,2)/sqrt(TMath::Pi()) : 0;
        case 2: { double x2 = _x*_x;
                switch(j) {
                // Mathematica:
                // W[z_] = Exp[-z^2]*Erfc[-I*z]
                // J[x_, z_, y_] = Erf[x - y] - Exp[-(x - y)^2] W[I*(z - x)]
                // M[x_, z_, n_] = Derivative[0, 0, n][J][x, z, 0]
                // case n:
                // pick Erfc[-x+z]*Exp[(x-z)^2] coefficient, Simplify[Exp[x*x]/2 *M[x, z, n]]
                // This next bit could be done much more elegantly in C++11 with variadic templates...
                case 0 : return   -1.;
                case 1 : return   -2.*_x;
                case 2 : return    2.*   (       1.-x2*2.);
                case 3 : return    4.*_x*(       3.-x2*2.);
                case 4 : return   -4.*   (       3.-x2*(       12.-x2*4.));
                case 5 : return   -8.*_x*(      15.-x2*(       20.-x2*4.));
                case 6 : return    8.*   (      15.-x2*(       90.-x2*(       60.-x2*8.)));
                case 7 : return   16.*_x*(     105.-x2*(      210.-x2*(       84.-x2*8.)));
                case 8 : return  -16.*   (     105.-x2*(      840.-x2*(      840.-x2*(      224.-x2*16.))));
                case 9 : return  -32.*_x*(     945.-x2*(     2520.-x2*(     1512.-x2*(      288.-x2*16.))));
                case 10: return   32.*   (     945.-x2*(     9450.-x2*(    12600.-x2*(     5040.-x2*(     720.-x2*32.)))));
                case 11: return   64.*_x*(   10395.-x2*(    34650.-x2*(    27720.-x2*(     7920.-x2*(     880.-x2*32.)))));
                case 12: return  -64.*   (   10395.-x2*(   124740.-x2*(   207900.-x2*(   110880.-x2*(   23760.-x2*(   2112.-x2*64.))))));
                case 13: return -128.*_x*(  135135.-x2*(   540540.-x2*(   540540.-x2*(   205920.-x2*(   34320.-x2*(   2496.-x2*64.))))));
                case 14: return  128.*   (  135135.-x2*(  1891890.-x2*(  3783780.-x2*(  2522520.-x2*(  720720.-x2*(  96096.-x2*(  5824.-x2*128.)))))));
                case 15: return  256.*_x*( 2027025.-x2*(  9459450.-x2*( 11351340.-x2*(  5405400.-x2*( 1201200.-x2*( 131040.-x2*(  6720.-x2*128.)))))));
                case 16: return -256.*   ( 2027025.-x2*( 32432400.-x2*( 75675600.-x2*( 60540480.-x2*(21621600.-x2*(3843840.-x2*(349440.-x2*(15360.-x2*256.))))))));
                case 17: return -512.*_x*(34459425.-x2*(183783600.-x2*(257297040.-x2*(147026880.-x2*(40840800.-x2*(5940480.-x2*(456960.-x2*(17408.-x2*256.))))))));
                default : assert(1==0); return 0;
    }   }  }
    assert(1==0);
    return 0;
}

template <unsigned MaxOrder>
RooGaussModelAcceptance::M_n<MaxOrder>::M_n(double x, const std::complex<double>& z)
{
          L l(x);
          std::complex<double> n[3]; n[0] =  RooMath::erf(x); n[1] =  exp(-x*x); n[2] =  eval(x,z);
          for (unsigned i=0;i<MaxOrder;++i) _m[i] = n[0]*l(i,0) + n[1]*l(i,1) + n[2]*l(i,2);
}


#include <iostream>

std::complex<double>
RooGaussModelAcceptance::K_n::operator()(unsigned i) const {
          assert(0<=i&&i<=14);
          std::complex<double> zi2 = _zi*_zi ; 
          std::complex<double> f(1,0);
          switch(i) {
              // mathematica:
              // K[z_, y_] = Exp[y*y]/(2*(z - y))
              // F[z_, y_] = Derivative[0, y][K][z, 0]
              // case n: F[z,n]
              case 13: f *= 13.*_zi;
              case 12: return f*  332640.*_zi*(1.+6.*zi2*(1.+5.*zi2*(1.+4.*zi2*(1.+3.*zi2*(1.+2.*zi2*(1.+zi2))))));
              case 11: f *= 11.*_zi;
              case 10: return f*              15120.*_zi*(1.+5.*zi2*(1.+4.*zi2*(1.+3.*zi2*(1.+2.*zi2*(1.+zi2)))));
              case 9 : f *= 9.*_zi;
              case 8 : return f*                           840.*_zi*(1.+4.*zi2*(1.+3.*zi2*(1.+2.*zi2*(1.+zi2))));
              case 7 : f *= 7.*_zi;
              case 6 : return f*                                       60.*_zi*(1.+3.*zi2*(1.+2.*zi2*(1.+zi2)));
              case 5 : f *= 5.*_zi;
              case 4 : return f*                                                   6.*_zi*(1.+2.*zi2*(1.+zi2));
              case 3 : f *= 3.*_zi;
              case 2 : return f*                                                                 _zi*(1.+zi2);
              case 1 : f *= _zi;
              case 0 : return f*                                                                     0.5*_zi;
          }
          std::cerr << "K_n only implemented upto (and including) 13th order" << std::endl;
          assert(1==0);
          return 0;
}

// explicitly instantiate some templates...
template class RooGaussModelAcceptance::M_n<1U>;
template class RooGaussModelAcceptance::M_n<2U>;
template class RooGaussModelAcceptance::M_n<3U>;
template class RooGaussModelAcceptance::M_n<4U>;
// template class RooGaussModelAcceptance::M_n<5U>;
// template class RooGaussModelAcceptance::M_n<6U>;
