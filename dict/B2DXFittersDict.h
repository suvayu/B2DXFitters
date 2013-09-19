#ifndef DICT_B2DXFITTERSDICT_H
#define DICT_B2DXFITTERSDICT_H 1

// Include files

/** @file DeltaMsRooFitterDict.h dict/DeltaMsRooFitterDict.h
 *
 *
 *  @author Eduardo Rodrigues
 *  @date   2011-05-23
 */

#include <string>
#include <vector>

#include "RooFitResult.h"
#include "RooAbsData.h"

#include "B2DXFitters/FitMeTool.h"
#include "B2DXFitters/CombBkgPTPdf.h"
#include "B2DXFitters/BdPTAcceptance.h"
#include "B2DXFitters/DTAcceptanceLHCbNote2007041.h"
#include "B2DXFitters/IfThreeWayCat.h"
#include "B2DXFitters/IfThreeWayCatPdf.h"
#include "B2DXFitters/IfThreeWay.h"
#include "B2DXFitters/IfThreeWayPdf.h"
#include "B2DXFitters/TagEfficiencyWeight.h"
#include "B2DXFitters/TagEfficiencyWeightNoCat.h"
#include "B2DXFitters/Dilution.h"
#include "B2DXFitters/SquaredSum.h"
#include "B2DXFitters/Inverse.h"
#include "B2DXFitters/MistagDistribution.h"
#include "B2DXFitters/MistagCalibration.h"
#include "B2DXFitters/CPObservable.h"
#include "B2DXFitters/MistagCalibration.h"

#include "B2DXFitters/GeneralModels.h"
#include "B2DXFitters/PropertimeResolutionModels.h"
#include "B2DXFitters/Bd2DhModels.h"
#include "B2DXFitters/Bs2DshModels.h"
#include "B2DXFitters/Bs2Dsh2011TDAnaModels.h"

#include "B2DXFitters/RooBinnedPdf.h"
#include "B2DXFitters/RooAbsEffResModel.h"
#include "B2DXFitters/RooEffConvGenContext.h"
#include "B2DXFitters/RooEffResModel.h"
#include "B2DXFitters/RooEffHistProd.h"

#include "B2DXFitters/PowLawAcceptance.h"

#include "B2DXFitters/GeneralUtils.h"
#include "B2DXFitters/SFitUtils.h"
#include "B2DXFitters/MassFitUtils.h"
#include "B2DXFitters/WeightingUtils.h"
#include "B2DXFitters/KinHack.h"

#include "B2DXFitters/RooGeneralisedSmearingBase.h"
#include "B2DXFitters/RooGenSmearIntegrandBinding.h"
#include "B2DXFitters/RangeAcceptance.h"

template class std::vector<std::pair<std::string,std::string> >;
template class std::vector<RooFitResult*>;
template class std::pair<std::string,RooAbsData*>;

#include "B2DXFitters/SharedArray.h"
#include "B2DXFitters/RooBinned2DBicubicBase.h"
#include "B2DXFitters/RooBinned1DQuinticBase.h"

#include "B2DXFitters/NonOscTaggingPdf.h"
#include "B2DXFitters/DecRateCoeff.h"
#include "B2DXFitters/FinalStateChargePdf.h"
#include "B2DXFitters/TaggingCat.h"

#include "B2DXFitters/RooCruijff.h"

#include "B2DXFitters/RooAbsGaussModelEfficiency.h"
#include "B2DXFitters/RooCubicSplineKnot.h"
#include "B2DXFitters/RooCubicSplineFun.h"
#include "B2DXFitters/RooBinnedFun.h"
#include "B2DXFitters/RooGaussEfficiencyModel.h"
#include "B2DXFitters/RooComplementCoef.h"

#endif // DICT_B2DXFITTERSDICT_H
