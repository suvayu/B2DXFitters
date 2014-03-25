################################################################################
# Package: B2DXFitters
################################################################################
gaudi_subdir(B2DXFitters v2r4)

find_package(RELAX)
find_package(ROOT COMPONENTS Core Cint RooFitCore RooStats RooFit Hist Tree RIO
                             Matrix MathCore MathMore Physics Cintex Gpad Graf)


include_directories(${ROOT_INCLUDE_DIRS})
reflex_generate_dictionary(B2DXFittersDict
                           dict/B2DXFittersDict.h dict/B2DXFittersDict.xml
                           SPLIT_CLASSDEF)

add_definitions(-UNDEBUG)
gaudi_add_library(B2DXFittersLib
                  src/*.cxx
                  B2DXFittersDict_dict_classdef.cpp
                  PUBLIC_HEADERS B2DXFitters
                  INCLUDE_DIRS ROOT
                  LINK_LIBRARIES ROOT)

# ensure that genreflex is not called twice (in parallel builds)
add_dependencies(B2DXFittersLib B2DXFittersDictGen)

gaudi_install_python_modules()

