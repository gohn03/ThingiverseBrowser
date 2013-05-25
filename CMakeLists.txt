cmake_minimum_required(VERSION 2.8.9)

#-----------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
    set(EXTENSION_NAME ThingiverseBrowser)
    set(EXTENSION_HOMEPAGE "http://www.slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions")
    set(EXTENSION_CATEGORY "Thingiverse")
    set(EXTENSION_CONTRIBUTORS "Nigel Goh (UWA)")
    set(EXTENSION_DESCRIPTION "This is an extension that allows Thingiverse browsing and downloading")
endif()

#------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
    find_package(Slicer REQUIRED)
    include(${Slicer_USE_FILE})
endif()

#------------------------------------------------------------------------
add_subdirectory(ThingiverseBrowser)

#------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
    include(${Slicer_EXTENSION_CPACK})
endif()
   