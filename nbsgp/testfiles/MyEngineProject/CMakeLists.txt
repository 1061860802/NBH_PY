cmake_minimum_required(VERSION 3.20)
project(MyEngineProject LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${PROJECT_SOURCE_DIR}/${MODE_PATH}/binarys")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${PROJECT_SOURCE_DIR}/${MODE_PATH}/binarys")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${PROJECT_SOURCE_DIR}/${MODE_PATH}/archive")
set(CMAKE_INSTALL_PREFIX "${PROJECT_SOURCE_DIR}/${MODE_PATH}/install")

add_compile_definitions(${MODE_MACROS})
add_compile_options(${COMPILE_OPTIONS})
add_link_options(${LINK_OPTIONS})

string(REPLACE ";" " " ACTIVATED_KEYS_LIST "${ACTIVATED_KEYS}")
function(check_keys_intersection required_keys result_var)
    set(intersection FALSE)
    if("${required_keys}" STREQUAL "InstallAlways")
        set(intersection TRUE)
    else()
        foreach(key ${required_keys})
            list(FIND ACTIVATED_KEYS_LIST "${key}" is_found)
            if(NOT is_found EQUAL -1)
                set(intersection TRUE)
                break()
            endif()
        endforeach()
    endif()
    set(${result_var} ${intersection} PARENT_SCOPE)
endfunction()

# --- Sub-projects (in-source builds) ---

# --- Dependencies (finding external packages) ---

# --- Project module definitions ---
# Module: EngineCore
check_keys_intersection("InstallAlways" ACTIVATE_MOD_EngineCore)
if(ACTIVATE_MOD_EngineCore)
    add_library(EngineCore STATIC)
    target_sources(EngineCore
        PRIVATE
            $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/source/EngineCore/private/EngineCore.cpp>
    )
    target_include_directories(EngineCore
        PUBLIC
            $<INSTALL_INTERFACE:include/EngineCore/public>
            $<INSTALL_INTERFACE:include/EngineCore/include>
            $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/source/EngineCore/public>
            $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/source/EngineCore/include>
    )
    target_compile_definitions(EngineCore PRIVATE ENGINECORE)



    install(TARGETS EngineCore
        EXPORT MyEngineProjectTargets
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin
    )
    set(PUBLIC_INC_ENGINECORE
        "source/EngineCore/public"
        "source/EngineCore/include"
    )

    install(DIRECTORY 
        ${PUBLIC_INC_ENGINECORE}
        DESTINATION include/EngineCore
    )
endif()

# Module: EngineRender
check_keys_intersection("InstallAlways" ACTIVATE_MOD_EngineRender)
if(ACTIVATE_MOD_EngineRender)
    add_library(EngineRender STATIC)
    target_sources(EngineRender
        PRIVATE
            $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/source/EngineRender/private/main.cpp>
    )
    target_include_directories(EngineRender
        PUBLIC
            $<INSTALL_INTERFACE:include/EngineRender/public>
            $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/source/EngineRender/public>
    )
    target_compile_definitions(EngineRender PRIVATE ENGINERENDER)

    check_keys_intersection("InstallAlways" ENGINERENDER_ACTIVATE_DEP_ENGINECORE)
    if(ENGINERENDER_ACTIVATE_DEP_ENGINECORE)
        target_link_libraries(EngineRender PUBLIC EngineCore)
    endif()


    install(TARGETS EngineRender
        EXPORT MyEngineProjectTargets
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin
    )
    set(PUBLIC_INC_ENGINERENDER
        "source/EngineRender/public"
    )

    install(DIRECTORY 
        ${PUBLIC_INC_ENGINERENDER}
        DESTINATION include/EngineRender
    )
endif()

# Module: EngineExe
check_keys_intersection("InstallAlways" ACTIVATE_MOD_EngineExe)
if(ACTIVATE_MOD_EngineExe)
    add_executable(EngineExe)
    target_sources(EngineExe
        PRIVATE
            $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/source/EngineExe/private/main.cpp>
    )
    target_include_directories(EngineExe
        PUBLIC
            $<INSTALL_INTERFACE:include/EngineExe/public>
            $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/source/EngineExe/public>
    )
    target_compile_definitions(EngineExe PRIVATE ENGINEEXE)

    check_keys_intersection("InstallAlways" ENGINEEXE_ACTIVATE_DEP_ENGINECORE)
    if(ENGINEEXE_ACTIVATE_DEP_ENGINECORE)
        target_link_libraries(EngineExe PUBLIC EngineCore)
    endif()
    check_keys_intersection("InstallAlways" ENGINEEXE_ACTIVATE_DEP_ENGINERENDER)
    if(ENGINEEXE_ACTIVATE_DEP_ENGINERENDER)
        target_link_libraries(EngineExe PUBLIC EngineRender)
    endif()


    install(TARGETS EngineExe
        EXPORT MyEngineProjectTargets
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin
    )
    set(PUBLIC_INC_ENGINEEXE
        "source/EngineExe/public"
    )

    install(DIRECTORY 
        ${PUBLIC_INC_ENGINEEXE}
        DESTINATION include/EngineExe
    )
endif()


install(EXPORT MyEngineProjectTargets
    FILE MyEngineProjectConfig.cmake
    NAMESPACE MyEngineProject::
    DESTINATION lib/cmake/MyEngineProject
)