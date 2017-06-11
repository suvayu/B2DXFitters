################################################################################
# Package: B2DXFitters
################################################################################
gaudi_subdir(B2DXFitters v3r1)

find_package(RELAX)
find_package(ROOT COMPONENTS Core RooFitCore RooStats RooFit Hist Tree RIO
                             Matrix MathCore MathMore Physics Gpad Graf)

# override the genreflex call to wrap it in the right environment
set(ROOT_genreflex_CMD ${env_cmd} --xml ${env_xml} ${ROOT_genreflex_CMD})

include_directories(${ROOT_INCLUDE_DIRS})
reflex_generate_dictionary(B2DXFitters
                           dict/B2DXFittersDict.h dict/B2DXFittersDict.xml
                           SPLIT_CLASSDEF)

add_definitions(-UNDEBUG)
gaudi_add_library(B2DXFittersLib
                  src/*.cxx
                  B2DXFittersDict_classdef.cpp
                  PUBLIC_HEADERS B2DXFitters
                  INCLUDE_DIRS ROOT
                  LINK_LIBRARIES ROOT)

# ensure that genreflex is not called twice (in parallel builds)
add_dependencies(B2DXFittersLib B2DXFittersGen)

gaudi_install_python_modules()

