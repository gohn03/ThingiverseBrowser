cmake_minimum_required(VERSION 2.8.8)

set(MODULE_NAME ThingiverseBrowser)

#-----------------------------------------------------------

set(MODULE_PYTHON_SCRIPTS
    ${MODULE_NAME}.py
    )
    
set(MODULE_PYTHON_RESOURCES
    )
    

if(NOT Slicer_SOURCE_DIR)
  find_package(Slicer REQUIRED)
  include(${Slicer_USE_FILE})
endif()


#-----------------------------------------------------------

slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS}
  RESOURCES ${MODULE_PYTHON_RESOURCES}
  WITH_GENERIC_TESTS
  )