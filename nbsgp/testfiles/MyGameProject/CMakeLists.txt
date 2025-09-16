cmake_minimum_required(VERSION 3.20)
project(MyGameProject LANGUAGES CXX)

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
check_keys_intersection("InstallAlways" ACTIVATE_DEP_MyEngineProject)
if(ACTIVATE_DEP_MyEngineProject)
    find_package(MyEngineProject REQUIRED PATHS "${CMAKE_SOURCE_DIR}/../MyEngineProject/${MODE_PATH}/install")
endif()


# --- Project module definitions ---
# Module: GameExe
check_keys_intersection("InstallAlways" ACTIVATE_MOD_GameExe)
if(ACTIVATE_MOD_GameExe)
    add_executable(GameExe)
    target_sources(GameExe
        PRIVATE
            $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/source/GameExe/private/main.cpp>
    )
    target_include_directories(GameExe
        PUBLIC
            $<INSTALL_INTERFACE:include/GameExe/public>
            $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/source/GameExe/public>
    )
    target_compile_definitions(GameExe PRIVATE GameEXE)

    check_keys_intersection("InstallAlways" GAMEEXE_ACTIVATE_DEP_ENGINECORE)
    if(GAMEEXE_ACTIVATE_DEP_ENGINECORE)
        target_link_libraries(GameExe PUBLIC MyEngineProject::EngineCore)
    endif()


    install(TARGETS GameExe
        EXPORT MyGameProjectTargets
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin
    )
    set(PUBLIC_INC_GAMEEXE
        "source/GameExe/public"
    )

    install(DIRECTORY 
        ${PUBLIC_INC_GAMEEXE}
        DESTINATION include/GameExe
    )
endif()


install(EXPORT MyGameProjectTargets
    FILE MyGameProjectConfig.cmake
    NAMESPACE MyGameProject::
    DESTINATION lib/cmake/MyGameProject
)