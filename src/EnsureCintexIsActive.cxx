/** @file EnsureCintexIsActive.cxx
 *
 * ensure Cintex is loaded and active on library initialisation
 *
 * @author Manuel Schiller
 * @date 2013-10-01
 *
 * this is only needed for the standalone build
 */
#include "RVersion.h"
#include "TSystem.h"
// we only need Cintex in the ROOT 5 series, ROOT 6 doesn't need it
#if ROOT_VERSION(5,99,0) < ROOT_CODE
#include "Cintex/Cintex.h"
#endif

/// routine loading required libs, making sure to activate Cintex
static int EnsureCintexIsActive()
{
    if (gSystem->Load("libRooFit") < 0) return -1;
    // we only need Cintex in the ROOT 5 series, ROOT 6 doesn't need it
#if ROOT_VERSION(5,99,0) < ROOT_CODE
    if (gSystem->Load("libCintex") < 0) return -1;
    ROOT::Cintex::Cintex::Enable();
#endif
    return 0;
}

/// make sure EnsureCintexIsActive is called on library load
static int ensureCintexIsActive = EnsureCintexIsActive();

// vim: tw=78:sw=4:ft=cpp
