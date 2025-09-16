# -*- coding: utf-8 -*-
# builder.py

from ast import Global, Set
import json
import os
import subprocess
import sys
from pathlib import Path
import shutil
import glob
from turtle import delay

nbsgp_module = sys.modules[__name__]
sys.modules['nbsgp'] = nbsgp_module

def _find_files(path):
    p = Path(path)
    path_str = str(path)

    if any(c in path_str for c in '*?['):
        found_paths = [Path(p) for p in glob.glob(path_str, recursive=True)]
        
        return [p for p in found_paths if p.is_file()]
    
    if path.is_file():
        return [path]
    
    if path.is_dir():
        found_files = []
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = Path(root) / file
                found_files.append(file_path)
        return found_files
    raise AttributeError(f"Try find files in {path},but not found")
    return []

# --- Helper Functions ---
def _load_definition(file_path: Path, definition_name: str, class_type: str):
    """
    Dynamically loads a definition (Module, Project) from a .py file.
    Args:
        file_path (Path): The absolute path to the .py definition file.
        definition_name (str): The expected name of the object in the .py file (e.g., 'Module', 'Project').
        class_type (str): A descriptive string for logging (e.g., 'module', 'project').
    Returns:
        object: The loaded definition object.
    Raises:
        AttributeError: If the expected definition object is not found in the file.
        Exception: For other loading errors.
    """
    file_stem = file_path.stem
    sys.path.insert(0, str(file_path.parent))
    try:
        if file_stem in sys.modules:
            import importlib
            definition_module = importlib.reload(sys.modules[file_stem])
        else:
            definition_module = __import__(file_stem)
        
        if hasattr(definition_module, definition_name):
            definition_obj = getattr(definition_module, definition_name)
            
            if hasattr(definition_obj, 'Name') and definition_obj.Name is None:
                definition_obj.Name = file_stem
            if hasattr(definition_obj, 'RootPath') and definition_obj.RootPath is None:
                definition_obj.RootPath = file_path.parent
            if hasattr(definition_obj, 'Path') and definition_obj.Path is None:
                definition_obj.Path = file_path.parent

            return definition_obj
        else:
            raise AttributeError(f"{class_type.capitalize()} '{file_stem}' from '{file_path}' does not contain a '{definition_name}' object.")
    except Exception as e:
        print(f"Error loading {class_type} definition from {file_path}: {e}")
        raise
    finally:
        sys.path.pop(0)
        
class ExternalModuleDefinitionBase:
    def __init__(self, name: str = None, path: Path|str = None): 
        if name is None:
            raise AttributeError(f"ExternalModuleDefinition name not found")
        if path is None:
            raise AttributeError(f"ExternalModuleDefinition path no define")
        if not path.is_absolute():
            raise ValueError(f"The path of module {name} must be an absolute path.")
        self.name = name
        self.path = path
    
    def _to_abs_path(self,path:Path|str)->Path:
        if not os.path.isabs(path):
            return Path(os.path.join(self.path,path))
        else:
            return Path(path)
    
    def _init_real_paths(self):
        return
    
    def _set_owner(self,owner):
        return
    
    def _init_dependency(self):
        return
    
    def _check_dependency_legitimacy(self):
        return
        
    def get_name(self)->str:
        return self.name
    
    def get_use_absolute_name(self)->bool:
        return False
    
    def get_path(self)->Path:
        return self.path
    
    def get_condition_keys(self) -> list[str]:
        return None
    
    def get_library_name(self)->str:
        return None

    def get_library_type(self)->str:
        return None
    
    def get_owner_project(self):
        return None
    
class ExternalProjectDefinitionBase:
    def __init__(self, name: str = None, path: Path|str = None): 
        if name is None:
            raise AttributeError(f"ExternalProjectDefinition name not found")
        if path is None:
            raise AttributeError(f"ExternalProjectDefinition path no define")
        if not path.is_absolute():
            raise ValueError(f"The path of project {name} must be an absolute path.")
        self.name = name
        self.path = path

    def _to_abs_path(self,path:Path|str)->Path:
        if not os.path.isabs(path):
            return Path(os.path.join(self.path,path))
        else:
            return Path(path)
    
    def _init_real_paths(self):
        return
    
    def _init_dependency(self):
        return
    
    def _check_dependency_legitimacy(self):
        return
    
    def _get_relative_path(self, path: Path) -> Path:
        """Converts an absolute path to a relative path from the current project's root directory."""
        return os.path.relpath(path, self.path).replace("\\","/")
        
    def get_name(self)->str:
        return self.name
    
    def get_path(self)->Path:
        return self.path
    
    def get_project_type(self)->str: #decide use add_subdirectory or find_package or just link
        return None
    
    def get_package_name(self)->str:
        return None
    
    def get_condition_keys(self) -> list[str]:
        return None
    
    def get_modules(self) -> list[ExternalModuleDefinitionBase]:
        return None
    
    def from_name_get_module(self,module_name:str) -> ExternalModuleDefinitionBase:
        moudles = self.get_modules()
        for i in moudles:
            if i.get_name() is module_name:
                return i
        return None
    
    def get_install_dir(self) -> Path|str:
        return None
    

class ExternalModuleDependencyBase:
    def __init__(self, module: ExternalModuleDefinitionBase = None, required_keys: list[str] = None):
        self.module = module
        self.required_keys = required_keys if required_keys is not None else ["InstallAlways"]
    def _init_real(self):
        return

class ExternalProjectDependencyBase:
    def __init__(self, project: ExternalProjectDefinitionBase = None, required_keys: list[str] = None,use_relative_path:bool = True):
        self.project = project
        self.required_keys = required_keys if required_keys is not None else ["InstallAlways"]
        self.use_relative_path = use_relative_path
    def _init_real(self):
        return
        

class MakefileGeneratorBase:
    def __init__(self):
        return
    
    def generate_makefile(self):
        return
    
    def clean_makefile(self):
        return


class ModuleDefinitionBase:
    def __init__(self, name: str = None, path: Path|str = None): 
        if name is None:
            raise AttributeError(f"ModuleDefinition name not found")
        if path is None:
            raise AttributeError(f"ModuleDefinition path no define")
        if not path.is_absolute():
            raise ValueError(f"The path of module {name} must be an absolute path.")
        self.name = name
        self.path = path
    
    def _to_abs_path(self,path:Path|str)->Path:
        if not os.path.isabs(path):
            return Path(os.path.join(self.path,path))
        else:
            return Path(path)
    
    def _init_real_paths(self):
        return
    
    def _set_owner(self,owner):
        return
    
    def _init_dependency(self):
        return
    
    def _check_dependency_legitimacy(self):
        return
        
    def get_name(self)->str:
        return self.name
    
    def get_path(self)->Path:
        return self.path
    
    def get_condition_keys(self) -> list[str]:
        return None
    
    def get_library_type(self)->str:
        return None
        
    def get_public_source_files(self) -> list[Path|str]:#not include inherit from depends
        return None
    
    def get_private_source_files(self) -> list[Path|str]:
        return None
    
    def get_public_include_files(self) -> list[Path|str]:#not include inherit from depends
        return None
    
    def get_private_include_files(self) -> list[Path|str]:
        return None
    
    def get_public_macros(self) -> list[str]:
        return None
    
    def get_private_macros(self) -> list[str]:
        return None
    
    def get_public_depends_modules(self):#not include inherit from depends
        return None
    
    def get_private_depends_modules(self):
        return None
    
    def get_public_external_depends(self)->list[ExternalModuleDependencyBase]:#not include inherit from depends
        return None
    
    def get_private_external_depends(self)->list[ExternalModuleDependencyBase]:
        return None
    
    def get_owner_project(self):
        return None
    
class ProjectDefinitionBase:
    def __init__(self, name: str = None, path: Path|str = None): 
        if name is None:
            raise AttributeError(f"ProjectDefinition name not found")
        if path is None:
            raise AttributeError(f"ProjectDefinition path no define")
        if not path.is_absolute():
            raise ValueError(f"The path of project {name} must be an absolute path.")
        self.name = name
        self.path = path
    
    def _to_abs_path(self,path:Path|str)->Path:
        if not os.path.isabs(path):
            return Path(os.path.join(self.path,path))
        else:
            return Path(path)
    
    def _init_real_paths(self):
        return
    
    def _init_dependency(self):
        return
    
    def _check_dependency_legitimacy(self):
        return
    
    def _get_relative_path(self, path: Path) -> Path:
        """Converts an absolute path to a relative path from the current project's root directory."""
        return os.path.relpath(path, self.path).replace("\\","/")

    def get_name(self)->str:
        return self.name
    
    def get_path(self)->Path:
        return self.path
    
    def get_condition_keys(self) -> list[str]:
        return None
    
    def get_binarys_dir(self) -> Path:
        return None
    
    def get_archive_dir(self) -> Path:
        return None
    
    def get_cache_dir(self) -> Path:
        return None
    
    def get_install_dir(self) -> Path:
        return None
    
    def get_should_install(self) ->bool:
        return True
    
    def get_makefile_generator(self) -> MakefileGeneratorBase:
        return None
    
    def get_public_macros(self) -> list[str]: #not include inherit from depends
        return None

    def get_private_macros(self) -> list[str]:
        return None
    
    def get_public_modules(self) -> list[ModuleDefinitionBase]:  #not include inherit from depends
        return None
    
    def from_name_get_public_module(self,module_name:str) -> ModuleDefinitionBase:
        moudles = self.get_public_modules()
        for i in moudles:
            if i.get_name() is module_name:
                return i
        return None
    
    def get_private_modules(self)-> list[ModuleDefinitionBase]:
        return None
    
    def from_name_get_private_module(self,module_name:str) -> ModuleDefinitionBase:
        moudles = self.get_private_modules()
        for i in moudles:
            if i.get_name() is module_name:
                return i
        return None
    
    def from_name_get_module(self,module_name:str) -> ModuleDefinitionBase:
        moudles = self.get_private_modules() + self.get_public_modules()
        for i in moudles:
            if i.get_name() is module_name:
                return i
        return None

    def get_public_depends(self):#not include inherit from depends
        return None
    
    def get_private_depends(self):
        return None
    
    def get_sub_project(self):
        return None
    
    def get_public_external_depends(self)->list[ExternalProjectDependencyBase]:#not include inherit from depends
        return None
    
    def get_private_external_depends(self)->list[ExternalProjectDependencyBase]:
        return None
    

class ModuleDependencyBase:
    def __init__(self, module: ModuleDefinitionBase = None, required_keys: list[str] = None):
        self.module = module
        self.required_keys = required_keys if required_keys is not None else ["InstallAlways"]
    def _init_real(self):
        return

class ProjectDependencyBase:
    def __init__(self, project: ProjectDefinitionBase = None, required_keys: list[str] = None,use_relative_path:bool = True):
        self.project = project
        self.required_keys = required_keys if required_keys is not None else ["InstallAlways"]
        self.use_relative_path = use_relative_path
    def _init_real(self):
        return

        
##############################################################################################################

default_binarys_dir = "binarys"
default_archive_dir = "archive"
default_cache_dir = "cache"
default_install_dir = "install"

##############################################################################################################

class MakefileGeneratorBase:
    def __init__(self):
        pass

    def generate_makefile(self):
        raise NotImplementedError

    def clean_makefile(self):
        raise NotImplementedError

class CmakeListsGenerator:
    """Generates a CMakeLists.txt file for a given project."""
    def __init__(self, project: 'ProjectDefinitionBase'):
        self.project = project
        self.output_path = project.get_path()
        self.content = []

    def _get_relative_path(self, path: Path) -> Path:
        """Converts an absolute path to a relative path from the current project's root directory."""
        return os.path.relpath(path, self.output_path).replace("\\","/")

    def _generate_header(self):
        """Generates the header information for the CMake project."""
        self.content.append("cmake_minimum_required(VERSION 3.20)")
        self.content.append(f"project({self.project.get_name()} LANGUAGES CXX)")
        self.content.append("")
        self.content.append("set(CMAKE_CXX_STANDARD 17)")
        self.content.append("set(CMAKE_CXX_STANDARD_REQUIRED ON)")
        self.content.append("")

        binarys_dir = self._get_relative_path(self.project.get_binarys_dir())
        archive_dir = self._get_relative_path(self.project.get_archive_dir())
        
        self.content.append(f"set(CMAKE_RUNTIME_OUTPUT_DIRECTORY \"${{PROJECT_SOURCE_DIR}}/${{MODE_PATH}}/{binarys_dir}\")")
        self.content.append(f"set(CMAKE_LIBRARY_OUTPUT_DIRECTORY \"${{PROJECT_SOURCE_DIR}}/${{MODE_PATH}}/{binarys_dir}\")")
        self.content.append(f"set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY \"${{PROJECT_SOURCE_DIR}}/${{MODE_PATH}}/{archive_dir}\")")
        if self.project.get_should_install() is True:
            install_dir = self._get_relative_path(self.project.get_install_dir())
            self.content.append(f"set(CMAKE_INSTALL_PREFIX \"${{PROJECT_SOURCE_DIR}}/${{MODE_PATH}}/{install_dir}\")")
            
        self.content.append("")
        
        self.content.append(f'add_compile_definitions(${{MODE_MACROS}})')

        self.content.append(f'add_compile_options(${{COMPILE_OPTIONS}})')
        
        self.content.append(f'add_link_options(${{LINK_OPTIONS}})')

        self.content.append("")
        
        self.content.extend([
            'string(REPLACE ";" " " ACTIVATED_KEYS_LIST "${ACTIVATED_KEYS}")',
            "function(check_keys_intersection required_keys result_var)",
            "    set(intersection FALSE)",
            "    if(\"${required_keys}\" STREQUAL \"InstallAlways\")",
            "        set(intersection TRUE)",
            "    else()",
            "        foreach(key ${required_keys})",
            '            list(FIND ACTIVATED_KEYS_LIST "${key}" is_found)',
            "            if(NOT is_found EQUAL -1)",
            "                set(intersection TRUE)",
            "                break()",
            "            endif()",
            "        endforeach()",
            "    endif()",
            "    set(${result_var} ${intersection} PARENT_SCOPE)",
            "endfunction()",
            ""
        ])

    def _generate_sub_projects(self):
        """Generates add_subdirectory calls for sub-projects (in-source builds)."""
        self.content.append("# --- Sub-projects (in-source builds) ---")
        sub_projects = self.project.get_sub_project() or []
        for sub in sub_projects:
            required_keys = " ".join(sub.get_condition_keys())
            relative_path = self._get_relative_path(sub.get_path())
            self.content.append(f'check_keys_intersection("{required_keys}" ACTIVATE_SUB_{sub.get_name()})')
            self.content.append(f'if(ACTIVATE_SUB_{sub.get_name()})')
            self.content.append(f'    add_subdirectory({relative_path})')
            self.content.append('endif()')
            self.content.append("")
        self.content.append("")

    def _generate_dependencies(self):
        """Generates find_package calls for all dependencies (regular and external)."""
        self.content.append("# --- Dependencies (finding external packages) ---")
        
        all_deps = (self.project.get_public_depends() or []) + \
                   (self.project.get_private_depends() or [])
        
        all_external_deps = (self.project.get_public_external_depends() or []) + \
                            (self.project.get_private_external_depends() or [])
        
        # Process regular dependencies
        for dep in all_deps:
            dep_project:ProjectDefinitionBase = dep.project
            if not dep_project.get_should_install():
                raise ValueError(f"Error: The dependency project '{dep_project.get_name()}' must be installable (should_install=True) to be found by find_package.")

            required_keys = " ".join(dep.required_keys)
            self.content.append(f'check_keys_intersection("{required_keys}" ACTIVATE_DEP_{dep_project.get_name()})')
            self.content.append(f'if(ACTIVATE_DEP_{dep_project.get_name()})')
            
            # Decide path mode based on use_relative_path
            if dep.use_relative_path:
                # Path is relative to the main project's root
                local_install_path = dep_project._get_relative_path(dep_project.get_install_dir())
                relative_project_path = self._get_relative_path(dep_project.get_path())
                self.content.append(f'    find_package({dep_project.get_name()} REQUIRED PATHS "${{CMAKE_SOURCE_DIR}}/{relative_project_path}/${{MODE_PATH}}/{local_install_path}")')
            else:
                # Use absolute path
                local_install_path = dep_project._get_relative_path(dep_project.get_install_dir())
                absolute_project_path = str(dep_project.get_path()).replace("\\", "/")
                self.content.append(f'    find_package({dep_project.get_name()} REQUIRED PATHS "{absolute_project_path}/${{MODE_PATH}}/{local_install_path}")')
            
            self.content.append('endif()')
            self.content.append("")

        # Process external dependencies
        for dep in all_external_deps:
            dep_project:ExternalProjectDefinitionBase = dep.project
            required_keys = " ".join(dep.required_keys)
            self.content.append(f'check_keys_intersection("{required_keys}" ACTIVATE_EXT_{dep_project.get_name()})')
            self.content.append(f'if(ACTIVATE_EXT_{dep_project.get_name()})')
            if dep.use_relative_path:
                relative_install_path = self._get_relative_path(dep_project.get_install_dir())
                if dep_project.get_project_type().upper() == "Package".upper():
                    self.content.append(f'    find_package({dep_project.get_package_name()} REQUIRED PATHS "${{CMAKE_SOURCE_DIR}}/{relative_install_path}")')
                elif dep_project.get_project_type().upper() == "subdirectory".upper():
                    self.content.append(f'    add_subdirectory(${{CMAKE_SOURCE_DIR}}/{relative_install_path})')                    
                else:
                    raise ValueError(f"Error: The dependency external project '{dep_project.get_name()}' has unknow project type '{dep_project.get_project_type()}'")
            else:
                absolute_install_path = str(dep_project.get_install_dir()).replace("\\", "/")
                if dep_project.get_project_type().upper() == "Package".upper():
                    self.content.append(f'    find_package({dep_project.get_package_name()} REQUIRED PATHS "{absolute_install_path}")')
                elif dep_project.get_project_type().upper() == "subdirectory".upper():
                    self.content.append(f'    add_subdirectory({absolute_install_path})')    
                else:
                    raise ValueError(f"Error: The dependency external project '{dep_project.get_name()}' has unknow project type '{dep_project.get_project_type()}'")
            self.content.append('endif()')
            self.content.append("")
        self.content.append("")

    def _generate_modules(self):
        """Generates targets for the project's own modules."""
        self.content.append("# --- Project module definitions ---")
        all_modules = (self.project.get_public_modules() or []) + (self.project.get_private_modules() or [])
        for module in all_modules:
            self.content.append(f"# Module: {module.get_name()}")
            
            required_keys = " ".join(module.get_condition_keys())
            self.content.append(f'check_keys_intersection("{required_keys}" ACTIVATE_MOD_{module.get_name()})')
            self.content.append(f'if(ACTIVATE_MOD_{module.get_name()})')


            target_name = module.get_name()
            row_lib_type = module.get_library_type().upper()
            lib_type = row_lib_type
            if row_lib_type == "DynamicLibrary".upper() or row_lib_type == "Dynamic".upper() or row_lib_type == "Dll".upper():
                lib_type = "SHARED"
            elif row_lib_type == "STATIC".upper() or row_lib_type == "StaticLibrary".upper() or row_lib_type == "Lib".upper():
                lib_type = "STATIC"
            elif row_lib_type == "INTERFACE".upper():
                lib_type = "INTERFACE"
            elif row_lib_type == "EXECUTABLE":
                lib_type = "EXECUTABLE"
            else:
                raise ValueError(f"Error: The module '{module.get_owner_project().get_name()}::{module.get_name()}' has unknow module type '{row_lib_type}'")
            if lib_type != "EXECUTABLE":
                self.content.append(f"    add_library({target_name} {lib_type})")
            else:
                self.content.append(f"    add_executable({target_name})")               
            
            # Source file processing
            public_sources = self._process_source_list(module.get_public_source_files() or [])
            private_sources = self._process_source_list(module.get_private_source_files() or [])
            
            public_include = self._process_include_list(module.get_public_include_files() or [])
            private_include = self._process_include_list(module.get_private_include_files() or [])

            # Pass the variables to target_sources
            if public_sources or private_sources:
                self.content.append(f"    target_sources({target_name}")
                if public_sources:
                    if lib_type != "INTERFACE":
                        self.content.append(f"        PUBLIC")
                        self.content.extend([f"            $<INSTALL_INTERFACE:src/{target_name}/{os.path.basename(s)}>" for s in public_sources])
                        self.content.extend([f"            $<BUILD_INTERFACE:${{PROJECT_SOURCE_DIR}}/{s}>" for s in public_sources])
                    else:
                        self.content.append(f"        INTERFACE")
                        self.content.extend([f"            $<INSTALL_INTERFACE:src/{target_name}/{os.path.basename(s)}>" for s in public_sources])
                        self.content.extend([f"            $<BUILD_INTERFACE:${{PROJECT_SOURCE_DIR}}/{s}>" for s in public_sources])                        
                if private_sources and lib_type != "INTERFACE":
                    self.content.append(f"        PRIVATE")
                    self.content.extend([f"            $<BUILD_INTERFACE:${{PROJECT_SOURCE_DIR}}/{s}>" for s in private_sources])
                self.content.append("    )")
                
            if public_include or private_include:
                self.content.append(f"    target_include_directories({target_name}")
                if public_include:
                    if lib_type != "INTERFACE":
                        self.content.append(f"        PUBLIC")
                        self.content.extend([f"            $<INSTALL_INTERFACE:include/{target_name}/{os.path.basename(s)}>" for s in public_include])
                        self.content.extend([f"            $<BUILD_INTERFACE:${{PROJECT_SOURCE_DIR}}/{s}>" for s in public_include])
                    else:
                        self.content.append(f"        INTERFACE")
                        self.content.extend([f"            $<INSTALL_INTERFACE:include/{target_name}/{os.path.basename(s)}>" for s in public_include])
                        self.content.extend([f"            $<BUILD_INTERFACE:${{PROJECT_SOURCE_DIR}}/{s}>" for s in public_include])                        
                if private_include and lib_type != "INTERFACE":
                    self.content.append(f"        PRIVATE")
                    self.content.extend([f"            $<BUILD_INTERFACE:${{PROJECT_SOURCE_DIR}}/{s}>" for s in private_include])
                self.content.append("    )")

            # Macro definitions
            public_macros = module.get_public_macros() + module.get_owner_project().get_public_macros()
            private_macros = module.get_private_macros() + module.get_owner_project().get_private_macros()
            if lib_type != "INTERFACE":
                if module.get_public_macros(): self.content.append(f"    target_compile_definitions({target_name} PUBLIC {' '.join(public_macros)})")
                if module.get_private_macros(): self.content.append(f"    target_compile_definitions({target_name} PRIVATE {' '.join(private_macros)})")
            else:
                if module.get_public_macros(): self.content.append(f"    target_compile_definitions({target_name} INTERFACE {' '.join(public_macros)})")
            # Link dependencies

            # Public link dependencies     
            self.content.append("")
            public_deps:list[ModuleDependencyBase] = module.get_public_depends_modules() or []
            for dep in public_deps:
                dep_module_name = f"{dep.module.get_owner_project().get_name()}::{dep.module.get_name()}" if dep.module.get_owner_project().get_name() != self.project.get_name() else f"{dep.module.get_name()}" 
                active_key = f"{module.get_name().upper()}_ACTIVATE_DEP_{dep.module.get_name().upper()}"
                dep_required_keys = " ".join(dep.required_keys)
                self.content.append(f'    check_keys_intersection("{dep_required_keys}" {active_key})')
                self.content.append(f'    if({active_key})')
                if lib_type != "INTERFACE":
                    self.content.append(f"        target_link_libraries({target_name} PUBLIC {dep_module_name})")
                else:
                    self.content.append(f"        target_link_libraries({target_name} INTERFACE {dep_module_name})")                   
                self.content.append(f'    endif()')
                
            # Private link dependencies
            private_deps:list[ModuleDependencyBase] = module.get_private_depends_modules() or []
            for dep in private_deps:
                dep_module_name = f"{dep.module.get_owner_project().get_name()}::{dep.module.get_name()}" if dep.module.get_owner_project().get_name() != self.project.get_name() else f"{dep.module.get_name()}" 
                active_key = f"{module.get_name().upper()}_ACTIVATE_DEP_{dep.module.get_name().upper()}"
                dep_required_keys = " ".join(dep.required_keys)
                self.content.append(f'    check_keys_intersection("{dep_required_keys}" {active_key})')
                self.content.append(f'    if({active_key})')
                if lib_type != "INTERFACE":
                    self.content.append(f"        target_link_libraries({target_name} PUBLIC {dep_module_name})")
                else:
                    self.content.append(f"        target_link_libraries({target_name} INTERFACE {dep_module_name})")
                self.content.append(f'    endif()')
                
            # Public ext link dependencies
            public_ext_deps:list[ExternalModuleDependencyBase] = module.get_public_external_depends() or []
            for dep in public_ext_deps:
                dep_module_name = f"{dep.module.get_owner_project().get_name()}::{dep.module.get_library_name()}" if dep.module.get_owner_project().get_name() != self.project.get_name() and dep.module.get_use_absolute_name() is False else f"{dep.module.get_library_name()}" 
                active_key = f"{module.get_name().upper()}_ACTIVATE_EXT_DEP_{dep.module.get_name().upper()}"
                dep_required_keys = " ".join(dep.required_keys)
                self.content.append(f'    check_keys_intersection("{dep_required_keys}" {active_key})')
                self.content.append(f'    if({active_key})')
                if lib_type != "INTERFACE":
                    self.content.append(f"    target_link_libraries({target_name} PUBLIC {dep_module_name})")
                else:
                    self.content.append(f"    target_link_libraries({target_name} INTERFACE {dep_module_name})")
                self.content.append(f'    endif()')
                
            # Private ext link dependencies
            private_ext_deps:list[ExternalModuleDependencyBase] = module.get_private_external_depends() or []
            for dep in private_ext_deps:
                dep_module_name = f"{dep.module.get_owner_project().get_name()}::{dep.module.get_library_name()}" if dep.module.get_owner_project().get_name() != self.project.get_name() and dep.module.get_use_absolute_name() is False else f"{dep.module.get_library_name()}" 
                active_key = f"{module.get_name().upper()}_ACTIVATE_EXT_DEP_{dep.module.get_name().upper()}"
                dep_required_keys = " ".join(dep.required_keys)
                self.content.append(f'    check_keys_intersection("{dep_required_keys}" {active_key})')
                self.content.append(f'    if({active_key})')
                if lib_type != "INTERFACE":
                    self.content.append(f"    target_link_libraries({target_name} PUBLIC {dep_module_name})")
                else:
                    self.content.append(f"    target_link_libraries({target_name} INTERFACE {dep_module_name})")
                self.content.append(f'    endif()')
                
            self.content.append("")

            # Installation rules
            if self.project.get_should_install():        
                self.content.append(f"""
    install(TARGETS {target_name}
        EXPORT {self.project.get_name()}Targets
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin
    )""")

                if public_include:
                    # Need to do GLOB_RECURSE again for install
                    public_header_inc_var = f"PUBLIC_INC_{target_name.upper()}"
                    self.content.append(f"    set({public_header_inc_var}")
                    self.content.extend([f'        "{s}"' for s in public_include])
                    self.content.append("    )")
                    
                    self.content.append(f"""
    install(DIRECTORY 
        ${{{public_header_inc_var}}}
        DESTINATION include/{target_name}
    )""")
                    
                if public_sources:
                    # Need to do GLOB_RECURSE again for install
                    public_header_glob_var = f"PUBLIC_SRC_{target_name.upper()}"
                    self.content.append(f"    set({public_header_glob_var}")
                    self.content.extend([f"        {s}" for s in public_sources])
                    self.content.append("    )")
                    
                    self.content.append(f"""
    install(FILES
        ${{{public_header_glob_var}}}
        DESTINATION src/{target_name}
    )""")
            self.content.append('endif()')
            self.content.append("")
            
        if self.project.get_should_install():
            self.content.append(f"""
install(EXPORT {self.project.get_name()}Targets
    FILE {self.project.get_name()}Config.cmake
    NAMESPACE {self.project.get_name()}::
    DESTINATION lib/cmake/{self.project.get_name()}
)""")

    def _process_source_list(self, sources: list[Path]) -> list[str]:
        processed = []
        for path in sources:
            if os.path.splitext(path)[1]:
                rel_path = self._get_relative_path(path)
                processed.append(f'{rel_path}')
            else:
                all_files = _find_files(path)
                processed.extend([self._get_relative_path(s) for s in all_files])
        return processed
    
    def _process_include_list(self, sources: list[Path]) -> list[str]:
        processed = []
        for path in sources:
            rel_path = self._get_relative_path(path)
            if os.path.splitext(rel_path)[1]:
                raise AttributeError(f"The include path for {self.project.get_name()} must be a directory path, but a file path was provided {path}")
            else:
                processed.append(f'{rel_path}')
        return processed

    def generate(self):
        """Generates the complete CMakeLists.txt file."""
        self.content = []
        self._generate_header()
        self._generate_sub_projects()
        self._generate_dependencies()
        self._generate_modules()

        with open(self.output_path / "CMakeLists.txt", "w", encoding='utf-8') as f:
            f.write("\n".join(self.content))
        print(f"Successfully generated CMakeLists.txt file at: {self.output_path}")

class CmakePresetGenerator:
    """Generates a CMakePresets.json file for the project."""
    def __init__(self, project: 'ProjectDefinitionBase'):
        self.project = project
        self.output_path = project.get_path()

    def generate(self, build_modes: list[dict]):
        if not build_modes: return
        configure_presets = []
        for mode in build_modes:
            mode_name = mode.get('name')
            if mode_name is None:
                raise AttributeError(f"CmakePresetGenerator get mode failed,no mode name found")
            mode_path = mode.get('mode_path') if mode.get('mode_path') is not None else ''
            cmake_type = mode.get('cmake_type') if  mode.get('cmake_type') is not None else mode_name
            keys = ";".join(mode.get('keys', ['InstallAlways']) if mode.get('keys') is not None else ['InstallAlways'])
            macros = ";".join(mode.get('macros', []) if mode.get('macros') is not None else [])
            compile_options = ";".join(mode.get('compile_options', []) if mode.get('compile_options') is not None else [])
            link_options = ";".join(mode.get('link_options', []) if mode.get('link_options') is not None else [])
            preset = {
                "name": mode_name.lower(),
                "displayName": f"{mode_name} Build",
                "description": f"Builds the project in {mode_name} mode.",
                "generator": "Ninja",
                "binaryDir": f"${{sourceDir}}/build/{mode_name.lower()}",
                "cacheVariables": 
                { 
                 "CMAKE_BUILD_TYPE": cmake_type, 
                 "ACTIVATED_KEYS": keys ,
                 "COMPILE_OPTIONS": compile_options,
                 "LINK_OPTIONS":link_options,
                 "MODE_PATH": mode_path,
                 "MODE_MACROS": macros
                 }
            }
            configure_presets.append(preset)

        presets_data = { "version": 3, "configurePresets": configure_presets }
        with open(self.output_path / "CMakePresets.json", "w", encoding='utf-8') as f:
            json.dump(presets_data, f, indent=2)
        print(f"Successfully generated CMakePresets.json file at: {self.output_path}")

class MakefileGeneratorDefault(MakefileGeneratorBase):
    """Uses CMake's default Makefile generator."""
    def __init__(self, project: ProjectDefinitionBase,build_modes:list[dict[str,any]] = None):
        super().__init__()
        self.project = project
        self.cmakelists_gen = CmakeListsGenerator(self.project)
        self.cmakepreset_gen = CmakePresetGenerator(self.project)
        self.build_modes = build_modes if build_modes is not None else[
            {'name': 'Debug','keys': ['InstallAlways', 'Shoping','Release','Debug']},
            {'name': 'Development','cmake_type':'RelWithDebInfo', 'keys': ['InstallAlways', 'Shoping','Release']},
            {'name': 'Release','cmake_type':'Release','mode_path':'Release', 'keys': ['InstallAlways', 'Shoping']},
            {'name': 'Mini','cmake_type':'MinSizeRel','mode_path':'Mini', 'keys': ['InstallAlways', 'Shoping']}
        ]

    def generate_makefile(self):
        """Generates all necessary CMake files without performing a build."""
        print(f"--- Starting generation of build files for project {self.project.get_name()} ---")
        self.cmakelists_gen.generate()
        self.cmakepreset_gen.generate(self.build_modes)
        print(f"--- Finished generating build files for project {self.project.get_name()} ---")
        
    def clean_makefile(self):
        """Recursively cleans all generated CMake files and build directories."""
        print(f"--- Starting cleanup for project: {self.project.get_name()} ---")
        project_path = self.project.get_path()

        # 1. Recursively clean sub-projects
        cleaned_paths = {project_path}
        for sub_project in (self.project.get_sub_project() or []):
            if sub_project.get_path() not in cleaned_paths:
                sub_project.get_makefile_generator().clean_makefile()
                cleaned_paths.add(sub_project.get_path())
        
        # 2. Delete generated files and directories for the current project
        files_to_delete = ["CMakeLists.txt", "CMakePresets.json"]
        for filename in files_to_delete:
            try:
                file_path = project_path / filename
                if file_path.exists():
                    file_path.unlink()
                    print(f"Deleted {file_path}")
            except OSError as e: print(f"Error deleting file {file_path}: {e}")

        build_root = project_path / "build"
        try:
            if build_root.exists() and build_root.is_dir():
                shutil.rmtree(build_root)
                print(f"Deleted build directory {build_root}")
        except OSError as e: print(f"Error deleting directory {build_root}: {e}")
        
        print(f"--- Finished cleaning up {self.project.get_name()} ---")
        
###############################################################################################################        

class ExternalModuleDefinition(ExternalModuleDefinitionBase):
    def __init__(self, name: str = None, path: Path|str = None,
                 condition_keys:list[str] = None,
                 library_name:str = None,
                 library_type:str = None,
                 use_absolute_name:bool = False,
                 ): 
        ExternalModuleDefinitionBase.__init__(self,name,path)
        self.condition_keys = condition_keys if condition_keys is not None else ["InstallAlways"]
        if library_type is None:
            raise AttributeError(f"an ExternalModuleDefinition named as {name} not found library_type")
        self.library_name = library_name if library_name is not None else name
        self.library_type = library_type
        self.use_absolute_name = use_absolute_name
        self.owner_project:ExternalProjectDefinitionBase = None
        self._init_real_paths()     
        
    def _init_real_paths(self):
        return
        
    def _set_owner(self,owner):
        self.owner_project = owner
        
    def _init_dependency(self):
        return
        
    def _check_dependency_legitimacy(self):
        return

    def get_name(self)->str:
        return self.name
    
    def get_use_absolute_name(self)->bool:
        return self.use_absolute_name
    
    def get_path(self)->Path|str:
        return self.path
    
    def get_condition_keys(self) -> list[str]:
        return self.condition_keys
    
    def get_library_name(self)->str:
        return self.library_name

    def get_library_type(self)->str:
        return self.library_type
    
    def get_owner_project(self)->ExternalProjectDefinitionBase:
        return self.owner_project
    
class ExternalProjectDefinition(ExternalProjectDefinitionBase):
    def __init__(self, name: str = None, path: Path|str = None,
                 project_type:str = None,
                 package_name:str = None,
                 condition_keys:list[str] = None,
                 install_dir:Path|str = None,
                 modules:list[ExternalModuleDefinitionBase] = None
                 ):
        ExternalProjectDefinitionBase.__init__(self,name,path)
        self.project_type = project_type if project_type is not None else "Package"
        self.package_name = package_name if package_name is not None else name
        self.condition_keys = condition_keys if condition_keys is not None else ["InstallAlways"]
        if install_dir is None:
            raise AttributeError(f"an ExternalProjectDefinition named as {name} not found install_dir")
        self.row_install_dir = install_dir
        self.modules = modules if modules is not None else []
        self._init_real_paths()
        self._set_modules_owner()

    def _init_real_paths(self):
        self.install_path:Path = self._to_abs_path(self.row_install_dir)
        
    def _set_modules_owner(self):
        for module in self.modules:
            if module.get_owner_project() is not self and module.get_owner_project() is not None:
                raise AttributeError(f"A module named as {module.get_name()} repeatedly sets its owner."
                                     f"Current owner:{module.get_owner_project()},repeatedly set to:{self}")
            module._set_owner(self)
            
    def _init_dependency(self):
        self._check_dependency_legitimacy()
            
    def _check_dependency_legitimacy(self):
        return

    def get_name(self)->str:
        return self.name
    
    def get_path(self)->Path|str:
        return self.path
    
    def get_project_type(self)->str: #decide use add_subdirectory or find_package
        return self.project_type 
    
    def get_package_name(self)->str:
        return self.package_name
    
    def get_condition_keys(self) -> list[str]:
        return self.condition_keys
    
    def get_modules(self) -> list[ExternalModuleDefinitionBase]:
        return self.modules
    
    def get_install_dir(self) -> Path|str:
        self._init_real_paths()
        return self.install_path
    

class ModuleDefinition(ModuleDefinitionBase):
    def __init__(self, name: str = None, path: Path|str = None,
                 condition_keys:list[str] = None,
                 library_name:str = None,
                 library_type:str = None,
                 public_source:list[Path|str] = None,
                 private_source:list[Path|str] = None,
                 public_include:list[Path|str] = None,
                 private_include:list[Path|str] = None,
                 public_macros:list[str] = None,
                 private_macros:list[str] = None,
                 public_depends_modules:list[ModuleDependencyBase] = None,
                 private_depends_modules:list[ModuleDependencyBase] = None,
                 public_external_depends:list[ExternalModuleDependencyBase] = None,
                 private_external_depends:list[ExternalModuleDependencyBase] = None
                 ): 
        ModuleDefinitionBase.__init__(self,name,path)
        self.condition_keys = condition_keys if condition_keys is not None else ["InstallAlways"]
        if library_type is None:
            raise AttributeError(f"an ModuleDefinition named as {name} not found library_type")
        self.library_type = library_type
        self.row_public_source_files = public_source if public_source is not None else []
        self.row_private_source_files = private_source if private_source is not None else []
        self.row_public_include_dirs = public_include if public_include is not None else []
        self.row_private_include_dirs = private_include if private_include is not None else []
        self.public_macros = public_macros if public_macros is not None else []
        self.private_macros = private_macros if private_macros is not None else []
        self.public_depends_modules = public_depends_modules if public_depends_modules is not None else []
        self.private_depends_modules = private_depends_modules if private_depends_modules is not None else []
        self.public_external_depends = public_external_depends if public_external_depends is not None else []
        self.private_external_depends = private_external_depends if private_external_depends is not None else []
        self.owner_project:ProjectDefinitionBase = None
        self._init_real_paths()
        
    def _init_real_paths(self):
        self.public_source:list[Path|str] = []
        self.private_source:list[Path|str] = []
        self.public_include:list[Path|str] = []
        self.private_include:list[Path|str] = []
        for row_public_source_file in self.row_public_source_files:
            self.public_source.extend(_find_files(self._to_abs_path(row_public_source_file)))
        for row_private_source_file in self.row_private_source_files:
            self.private_source.extend(_find_files(self._to_abs_path(row_private_source_file)))
        for row_public_include_dir in self.row_public_include_dirs:
            self.public_include.append(self._to_abs_path(row_public_include_dir))
        for row_private_include_dir in self.row_private_include_dirs:
            self.private_include.append(self._to_abs_path(row_private_include_dir))
        return
    
    def _set_owner(self,owner):
        self.owner_project = owner
        
    def _init_dependency(self):
        for m in self.public_depends_modules:
            m._init_real()
        for m in self.private_depends_modules:
            m._init_real()
        for m in self.public_external_depends:
            m._init_real()
        for m in self.private_external_depends:
            m._init_real()
        return
        
    def _check_dependency_legitimacy(self):
        owner_project = self.get_owner_project()
        if owner_project is None:
            raise AttributeError(f"Module '{self.get_name()}' does not have an owner project.")

        all_module_dependencies = self.public_depends_modules + self.private_depends_modules
        all_external_dependencies = self.public_external_depends + self.private_external_depends

        for dep in all_module_dependencies:
            dep_module = dep.module
            if dep_module.get_library_type().upper() == "EXECUTABLE":
                raise ValueError(
                    f"Module '{owner_project.get_name()}::{self.get_name()}' dependency on '{dep_module.get_owner_project().get_name()}::{dep_module.get_name()}',but {dep_module.get_name()} is an EXECUTABLE module. "
                )                
            if not set(dep.required_keys).issubset(set(dep_module.get_condition_keys())):
                raise ValueError(
                    f"Module '{owner_project.get_name()}::{self.get_name()}' dependency on '{dep_module.get_owner_project().get_name()}::{dep_module.get_name()}' has invalid required keys. "
                    f"Required keys '{dep.required_keys}' are not a subset of '{dep_module.get_condition_keys()}'."
                )

            is_legit_dependency = False
            
            if dep_module in owner_project.get_public_modules() or dep_module in owner_project.get_private_modules():
                is_legit_dependency = True

            if not is_legit_dependency:
                checked_projects = set()
                
                def check_transitive_dependencies(project_dep):
                    nonlocal is_legit_dependency
                    project = project_dep.project
                    if project in checked_projects:
                        return
                    checked_projects.add(project)
                    
                    if dep_module in project.get_public_modules() or dep_module in project.get_private_modules():
                        is_legit_dependency = True
                        return

                    for transitive_dep in project.get_public_depends():
                        if not is_legit_dependency:
                            check_transitive_dependencies(transitive_dep)

                for direct_dep in owner_project.get_public_depends():
                    if is_legit_dependency:
                        break
                    check_transitive_dependencies(direct_dep)

            if not is_legit_dependency:
                raise ValueError(
                    f"Module '{owner_project.get_name()}::{self.get_name()}' has an illegal dependency on module '{dep_module.get_owner_project().get_name()}::{dep_module.get_name()}'. "
                    f"Dependencies must be sub-modules of the owner project or its public dependencies."
                )

        for dep in all_external_dependencies:
            dep_external_module = dep.module
            
            if not set(dep.required_keys).issubset(set(dep_external_module.get_condition_keys())):
                raise ValueError(
                    f"Module '{owner_project.get_name()}::{self.get_name()}' dependency on external module '{dep_external_module.get_owner_project().get_name()}::{dep_external_module.get_name()}' has invalid required keys. "
                    f"Required keys '{dep.required_keys}' are not a subset of '{dep_external_module.get_condition_keys()}'."
                )
        return

        all_external_dependencies = self.public_external_depends + self.private_external_depends
        for dep in all_external_dependencies:
            dep_external_module = dep.module
            if not set(dep.required_keys).issubset(set(dep_external_module.get_condition_keys())):
                raise ValueError(
                    f"External dependency '{dep_external_module.get_owner_project().get_name()}::{dep_external_module.get_name()}' in module '{owner_project.get_name()}::{self.get_name()}' has invalid required keys. "
                    f"Required keys '{dep.required_keys}' are not a subset of '{dep_external_module.get_condition_keys()}'."
                )
        
    def get_name(self)->str:
        return self.name
    
    def get_path(self)->Path|str:
        return self.path
    
    def get_condition_keys(self) -> list[str]:
        return self.condition_keys
    
    def get_library_type(self)->str:
        return self.library_type
        
    def get_public_source_files(self) -> list[Path|str]:#not include inherit from depends
        return self.public_source
    
    def get_private_source_files(self) -> list[Path|str]:
        return self.private_source
    
    def get_public_include_files(self) -> list[Path|str]:#not include inherit from depends
        return self.public_include
    
    def get_private_include_files(self) -> list[Path|str]:
        return self.private_include
    
    def get_public_macros(self) -> list[str]:
        return self.public_macros
    
    def get_private_macros(self) -> list[str]:
        return self.private_macros
    
    def get_public_depends_modules(self) -> list[ModuleDependencyBase]:#not include inherit from depends
        return self.public_depends_modules
    
    def get_private_depends_modules(self) -> list[ModuleDependencyBase]:
        return self.private_depends_modules
    
    def get_public_external_depends(self)->list[ExternalModuleDependencyBase]:#not include inherit from depends
        return self.public_external_depends
    
    def get_private_external_depends(self)->list[ExternalModuleDependencyBase]:
        return self.private_external_depends
    
    def get_owner_project(self) -> ProjectDefinitionBase:
        return self.owner_project
    
class ProjectDefinition(ProjectDefinitionBase):
    def __init__(self, name: str = None, path: Path|str = None,
                 condition_keys:list[str] = None,
                 binarys_dir:Path|str = None,
                 archive_dir:Path|str = None,
                 cache_dir:Path|str = None,
                 install_dir:Path|str = None,
                 should_install:bool = True,
                 makefile_generator:MakefileGeneratorBase = None,
                 public_macros:list[str] = None,
                 private_macros:list[str] = None,
                 public_modules:list[ModuleDefinitionBase] = None,
                 private_modules:list[ModuleDefinitionBase] = None,
                 public_depends:list[ProjectDependencyBase] = None,
                 private_depends:list[ProjectDependencyBase] = None,
                 sub_project:list[ProjectDefinitionBase] = None,
                 public_external_depends:list[ExternalModuleDependencyBase] = None,
                 private_external_depends:list[ExternalModuleDependencyBase] = None                 
                 ): 
        ProjectDefinitionBase.__init__(self,name,path)
        self.condition_keys = condition_keys if condition_keys is not None else ["InstallAlways"]
        if binarys_dir is None:
            print(f"A project named as '{name}' has no set binarys_dir,use default '{default_binarys_dir}'")
            self.row_binarys_dir = default_binarys_dir
        else:
            self.row_binarys_dir = binarys_dir
        if archive_dir is None:
            print(f"A project named as '{name}' has no set archive_dir,use default '{default_archive_dir}'")
            self.row_archive_dir = default_archive_dir
        else:
            self.row_archive_dir = archive_dir
        if cache_dir is None:
            print(f"A project named as '{name}' has no set cache_dir,use default '{default_cache_dir}'")
            self.row_cache_dir = default_cache_dir
        else:
            self.row_cache_dir = cache_dir
        if cache_dir is None and should_install is True:
            print(f"A project named as '{name}' has no set install_dir,use default '{default_install_dir}'")
            self.row_install_dir = default_install_dir
        else:
            self.row_install_dir = install_dir
        self.should_install = should_install
        if makefile_generator is None:
            print(f"A project named as '{name}' has no set makefile_generator,use default MakefileGenerator")
            self.makefile_generator = MakefileGeneratorDefault(self)
        else:
            self.makefile_generator = makefile_generator
        self.public_macros = public_macros if public_macros is not None else []
        self.private_macros = private_macros if private_macros is not None else []
        self.public_modules = public_modules if public_modules is not None else []
        self.private_modules = private_modules if private_modules is not None else []
        self.public_depends = public_depends if public_depends is not None else []
        self.private_depends = private_depends if private_depends is not None else []
        self.sub_project = sub_project if sub_project is not None else []
        self.public_external_depends = public_external_depends if public_external_depends is not None else []
        self.private_external_depends = private_external_depends if private_external_depends is not None else []
        self._init_real_paths()
        self._set_modules_owner()
    
    def _init_real_paths(self):
        self.binarys_dir:Path|str = self._to_abs_path(self.row_binarys_dir)
        self.archive_dir:Path|str = self._to_abs_path(self.row_archive_dir)
        self.cache_dir:Path|str = self._to_abs_path(self.row_cache_dir)
        
        self.install_dir:Path|str = None
        
        if self.should_install is True:
            if self.row_install_dir is None:
                raise AttributeError(f"a ProjectDefinition named as {self.name} should install,but no set install dir")
            else:
                self.install_dir = self._to_abs_path(self.row_install_dir)
        return

    def _set_modules_owner(self):
        for module in self.public_modules:
            if module.get_owner_project() is not self and module.get_owner_project() is not None:
                raise AttributeError(f"A module named as {module.get_name()} repeatedly sets its owner."
                                     f"Current owner:{module.get_owner_project()},repeatedly set to:{self.get_name}")
            module._set_owner(self)
        for module in self.private_modules:
            if module.get_owner_project() is not self and module.get_owner_project() is not None:
                raise AttributeError(f"A module named as {module.get_name()} repeatedly sets its owner."
                                     f"Current owner:{module.get_owner_project()},repeatedly set to:{self.get_name}")    
            module._set_owner(self)

    def _init_dependency(self):
        for m in self.public_modules:
            m._init_dependency()
        for m in self.private_modules:
            m._init_dependency()
        for p in self.public_depends:
            p._init_real()
        for p in self.private_depends:
            p._init_real()
        for p in self.public_external_depends:
            p._init_real()
        for p in self.private_external_depends:
            p._init_real()            
        self._check_dependency_legitimacy()
    
    def _check_dependency_legitimacy(self):
        all_project_dependencies = self.public_depends + self.private_depends
        all_external_dependencies = self.public_external_depends + self.private_external_depends

        for dep in all_project_dependencies:
            dep_project = dep.project
            if not set(dep.required_keys).issubset(set(dep_project.get_condition_keys())):
                raise ValueError(
                    f"Project '{self.get_name()}' dependency on '{dep_project.get_name()}' has invalid required keys. "
                    f"Required keys '{dep.required_keys}' are not a subset of '{dep_project.get_condition_keys()}'."
                )

        for dep in all_external_dependencies:
            dep_external_project = dep.project
            if not set(dep.required_keys).issubset(set(dep_external_project.get_condition_keys())):
                raise ValueError(
                    f"Project '{self.get_name()}' dependency on external project '{dep_external_project.get_name()}' has invalid required keys. "
                    f"Required keys '{dep.required_keys}' are not a subset of '{dep_external_project.get_condition_keys()}'."
                )

        all_sub_modules = self.get_public_modules() + self.get_private_modules()
        for module in all_sub_modules:
            module._check_dependency_legitimacy()

        return
    
    def get_condition_keys(self) -> list[str]:
        return self.condition_keys
    
    def get_binarys_dir(self) -> Path|str:
        return self.binarys_dir
    
    def get_archive_dir(self) -> Path|str:
        return self.archive_dir
    
    def get_cache_dir(self) -> Path|str:
        return self.cache_dir
    
    def get_install_dir(self) -> Path|str:
        return self.install_dir
    
    def get_should_install(self) ->bool:
        return self.should_install
        
    def get_makefile_generator(self) -> MakefileGeneratorBase:
        return self.makefile_generator
    
    def get_public_macros(self) -> list[str]: #not include inherit from depends
        return self.public_macros

    def get_private_macros(self) -> list[str]:
        return self.private_macros
    
    def get_public_modules(self) -> list[ModuleDefinitionBase]:  #not include inherit from depends
        return self.public_modules
    
    def get_private_modules(self)-> list[ModuleDefinitionBase]:
        return self.private_modules

    def get_public_depends(self) -> list[ProjectDependencyBase]:#not include inherit from depends
        return self.public_depends
    
    def get_private_depends(self) -> list[ProjectDependencyBase]:
        return self.private_depends
    
    def get_sub_project(self) -> list[ProjectDefinitionBase]:
        return self.sub_project
    
    def get_public_external_depends(self)->list[ExternalProjectDependencyBase]:#not include inherit from depends
        return self.public_external_depends
    
    def get_private_external_depends(self)->list[ExternalProjectDependencyBase]:
        return self.private_external_depends
    
def get_all_project_depend(project:ProjectDefinitionBase):
    
    def get_all_project_depend_public(project:ProjectDefinitionBase):
        denepdsset:Set[ProjectDefinitionBase] = []
        denepdsset.add(project)
        depends_public = project.get_public_depends()
        for child_project in depends_public:
            denepdsset.add(get_all_project_depend_public(child_project))
        return denepdsset
    
    denepdsset:Set[ProjectDefinitionBase] = []
    denepdsset.add(project)
    all_depends = project.get_public_depends() + project.get_private_depends()
    for child_projec in all_depends:
        denepdsset.add(get_all_project_depend_public(all_depends))
    return denepdsset

##############################################################################################################

all_extronal_projects_map:map = {}
all_extronal_projects_Path_map:map = {}

def load_extronal_project(abs_project_dir: Path|str) -> ExternalProjectDefinitionBase:
    global all_extronal_projects_map
    global all_extronal_projects_Path_map
    abs_project_path = Path(abs_project_dir)
    project_file_name = abs_project_path.name
    print(f"Start loading project: {project_file_name} form path {abs_project_dir}...")
    if abs_project_path in all_extronal_projects_Path_map:
        project_name = all_extronal_projects_Path_map[abs_project_path]
        return all_extronal_projects_map[project_name]

    project_definition_file = abs_project_path / f"{project_file_name}.py"
    if not project_definition_file.exists():
        print(f"Error: Project definition file '{project_definition_file.name}' not found in '{abs_project_path}'.")
        return None
        
    project_def:ExternalProjectDefinitionBase = _load_definition(project_definition_file, 'Project', 'project')
    project_def.RootPath = abs_project_path
    print(f"Loading project: {project_def.get_name()}")
    project_name = project_def.get_name()
    if project_name in all_extronal_projects_map:
        old_project_def:ExternalProjectDefinitionBase = all_extronal_projects_map[project_name]
        raise AttributeError(f"Two project have same name,but form diferent path:{old_project_def.get_path()}::{project_def.get_path()}")
    all_extronal_projects_map[project_name] = project_def
    try:
        project_def._init_dependency()
    except Exception as e:
        del all_extronal_projects_map[project_name]
        raise AttributeError(f"An error occurred during project loading: {e}")
    print(f"Loaded project: {project_name}")
    all_extronal_projects_Path_map[abs_project_path] = project_name
    return project_def

def load_extronal_module(abs_module_dir: Path|str) -> ExternalModuleDefinitionBase:
    abs_module_path = Path(abs_module_dir)
    module_name = abs_module_path.name
    print(f"Start loading extronal module: {module_name} form path {abs_module_dir}...")
    module_definition_file = abs_module_path / f"{module_name}.py"
    if not module_definition_file.exists():
        print(f"Error: Module definition file '{module_definition_file.name}' not found in '{abs_module_path}'.")
        return None
        
    module_def:ExternalModuleDefinitionBase = _load_definition(module_definition_file, 'Module', 'module')
    module_def.RootPath = abs_module_path
    print(f"Loaded module: {module_def.get_name()}")
        
    return module_def

all_projects_map:map = {}
all_projects_Path_map:map = {}

def load_project(abs_project_dir: Path|str) -> ProjectDefinitionBase:
    global all_projects_map
    global all_projects_Path_map
    abs_project_path = Path(abs_project_dir)
    project_file_name = abs_project_path.name
    print(f"Start loading project: {project_file_name} form path {abs_project_dir}...")
    if abs_project_path in all_projects_Path_map:
        project_name = all_projects_Path_map[abs_project_path]
        return all_projects_map[project_name]

    project_definition_file = abs_project_path / f"{project_file_name}.py"
    if not project_definition_file.exists():
        print(f"Error: Project definition file '{project_definition_file.name}' not found in '{abs_project_path}'.")
        return None
        
    project_def:ProjectDefinitionBase = _load_definition(project_definition_file, 'Project', 'project')
    project_def.RootPath = abs_project_path
    print(f"Loading project: {project_def.get_name()}")
    project_name = project_def.get_name()
    if project_name in all_projects_map:
        old_project_def:ProjectDefinitionBase = all_projects_map[project_name]
        raise AttributeError(f"Two project have same name,but form diferent path:{old_project_def.get_path()}::{project_def.get_path()}")
    all_projects_map[project_name] = project_def
    try:
        project_def._init_dependency()
    except Exception as e:
        del all_projects_map[project_name]
        raise AttributeError(f"An error occurred during project loading: {e}")
    print(f"Loaded project: {project_name}")
    all_projects_Path_map[abs_project_path] = project_name
    return project_def

def load_module(abs_module_dir: Path|str) -> ModuleDefinitionBase:
    abs_module_path = Path(abs_module_dir)
    module_name = abs_module_path.name
    print(f"Start loading module: {module_name} form path {abs_module_dir}...")
    module_definition_file = abs_module_path / f"{module_name}.py"
    if not module_definition_file.exists():
        raise AttributeError(f"Error: Module definition file '{module_definition_file.name}' not found in '{abs_module_path}'.")
        
    module_def:ModuleDefinitionBase = _load_definition(module_definition_file, 'Module', 'module')
    module_def.RootPath = abs_module_path
    print(f"Loaded module: {module_def.get_name()}")
        
    return module_def

##############################################################################################################

class ExternalModuleDependency(ExternalModuleDependencyBase):
    def __init__(self,project_name:str = None,module_name:str = None,module: ExternalModuleDefinitionBase = None, required_keys: list[str] = None):
        ExternalModuleDependencyBase.__init__(self,module,required_keys)
        self.project_name = project_name
        self.module_name = module_name
    def _init_real(self):
        global all_extronal_projects_map
        if self.module is None:
            if self.project_name is None or self.module_name is None:
                raise AttributeError(f"The program declares a module dependency, but does not specify a dependency project_name or module_name")
            project:ExternalProjectDefinitionBase = all_extronal_projects_map.get(self.project_name)
            if project is None:
                raise AttributeError(f"The program declares a module dependency:{self.project_name}::{self.module_name},but no project named {self.project_name} was found")
            module = project.from_name_get_module(self.module_name)
            if module is None:
                raise AttributeError(f"The program declares a module dependency,but the project named {self.project_name} does not have a module named {self.module_name}")
            self.module = module
        return
    
class ExternalProjectDependency(ExternalProjectDependencyBase):
    def __init__(self,project_name:str = None,project:ExternalProjectDefinitionBase = None,required_keys: list[str] = None,use_relative_path:bool = True):
        ExternalProjectDependencyBase.__init__(self,project,required_keys,use_relative_path)
        self.project_name = project_name
    def _init_real(self):
        global all_extronal_projects_map
        if self.project is None:
            if self.project_name is None:
                raise AttributeError(f"The program declares a project dependency, but does not specify a dependency project_name")
            project:ExternalProjectDefinitionBase = all_extronal_projects_map.get(self.project_name)
            if project is None:
                raise AttributeError(f"The program declares a Project dependency,but no project named {self.project_name} was found")
            self.project = project
        return
    
class ModuleDependency(ModuleDependencyBase):
    def __init__(self,project_name:str = None,module_name:str = None,module: ModuleDefinitionBase = None, required_keys: list[str] = None):
        ModuleDependencyBase.__init__(self,module,required_keys)
        self.project_name = project_name
        self.module_name = module_name
    def _init_real(self):
        if self.module is None:
            if self.project_name is None or self.module_name is None:
                raise AttributeError(f"The program declares a dependency, but does not specify a dependency item or module")
            project:ProjectDefinitionBase = all_projects_map.get(self.project_name)
            if project is None:
                raise AttributeError(f"The program declares a module dependency: {self.project_name}::{self.module_name} ,but no project named {self.project_name} was found")
            module = project.from_name_get_module(self.module_name)
            if module is None:
                raise AttributeError(f"The program declares a module dependency,but the project named {self.project_name} does not have a module named {self.module_name}")
            self.module = module
        return

class ProjectDependency(ProjectDependencyBase):
    def __init__(self,project_name:str = None, project: ProjectDefinitionBase = None, required_keys: list[str] = None,use_relative_path:bool = True):
        ProjectDependencyBase.__init__(self,project,required_keys,use_relative_path)
        self.project_name = project_name
    def _init_real(self):
        if self.project is None:
            if self.project_name is None:
                raise AttributeError(f"The program declares a project dependency, but does not specify a dependency project_name")
            project:ProjectDependencyBase = all_projects_map.get(self.project_name)
            if project is None:
                raise ValueError(f"The program declares a Project dependency,but no project named {self.project_name} was found")
            self.project = project
        return

##############################################################################################################

def main_func(argv:list[str]):
    if len(argv) < 2:
        print("Usage: python nbsgp.py <absolute_project_path> [command]")
        print("Example: python nbsgp.py /Users/youruser/Projects/MyGameProject clean")
        raise ValueError(f"Fatel Command Error")
    
    project_path_arg = argv[1]
    root_project_path = Path(project_path_arg).resolve() 
    if not root_project_path.is_dir():
        print(f"Error: Project directory not found at {root_project_path}")
        raise ValueError(f"Fatel Command Error")
    
    target_projects:list[ProjectDefinitionBase] = []
    
    try:
        target_projects.append(load_project(root_project_path))
    except Exception as e:
        print(f"Append project failed:{e}")
        return
    
    command = argv[2] if len(argv) > 2 else "build"

    unknow_command = True
    
    if command == "clean":
        unknow_command = False
        print("Cleaning all build and package directories recursively...")
        for i in target_projects:
            try:
                print(f"Cleaning project {i.get_name()}")               
                i.get_makefile_generator().clean_makefile()
            except Exception as e:
                print(f"Warning: Could not execute cleaning for project named as {i.get_name()} : {e}")
        print("clean all build and package directories complete")
    if command == "build":
        unknow_command = False
        print("Building all porjects makefile...")
        for i in target_projects:
            try:
                print(f"Building project {i.get_name()} makefile") 
                i.get_makefile_generator().generate_makefile()
            except Exception as e:
                print(f"Warning: Could not execute building for project named as {i.get_name()} : {e}")
        print("Build all porjects makefiles complete")
    if command == "help":
        unknow_command = False
        print("Usage: python nbsgp.py <absolute_project_path> [command]")
        print("Example: python nbsgp.py /Users/youruser/Projects/MyGameProject clean")
        print("Commands:")
        print("[build]:Build Target Projects makefile")
        print("[clean]:clean Target Projects makefile")
    if unknow_command is True:
        print(f"{command} is a unknow command,use help to find help")
    return

if __name__ == "__main__":
    in_argvs:list[str] = [sys.argv[0],r"D:\cpp\OpenTest",r"build"] if len(sys.argv) < 2 else sys.argv
    main_func(in_argvs)