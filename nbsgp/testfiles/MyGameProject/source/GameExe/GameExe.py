from pathlib import Path
from nbsgp_interface import *

module_root = Path(__file__).parent.resolve()

Module = ModuleDefinition(
    name="GameExe",
    private_macros=["GameEXE"],
    path=Path(module_root),
    library_type="executable",
    public_depends_modules=[
        ModuleDependency(
            project_name = "MyEngineProject",
            module_name = "EngineCore" 
            ),
        ],
    private_source=["private"],
    public_include=["public"]  
)