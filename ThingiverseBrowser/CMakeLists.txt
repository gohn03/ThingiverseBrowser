set(MODULE_NAME ThingiverseBrowser)

#-----------------------------------------------------------

set(MODULE_PYTHON_SCRIPTS
    #{MODULE_NAME}.py
    )
    
set(MODULE_PYTHON_RESOURCES
    )
    

if(NOT Slicer_SOURCE_DIR)
  find_package(Slicer REQUIRED)
  include(${Slicer_USE_FILE})
endif()