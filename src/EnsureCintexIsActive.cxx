/** @file EnsureCintexIsActive.cxx
 *
 * ensure Cintex is loaded and active on library initialisation
 *
 * @author Manuel Schiller
 * @date 2013-10-01
 *
 * this is only needed for the standalone build
 */
#include "TSystem.h"
#include "Cintex/Cintex.h"

/// routine loading required libs, making sure to activate Cintex
static int EnsureCintexIsActive()
{
    if (gSystem->Load("libRooFit") < 0) return -1;
    if (gSystem->Load("libCintex") < 0) return -1;
    ROOT::Cintex::Cintex::Enable();
    return 0;
}

/// make sure EnsureCintexIsActive is called on library load
static int ensureCintexIsActive = EnsureCintexIsActive();

// vim: tw=78:sw=4:ft=cpp
