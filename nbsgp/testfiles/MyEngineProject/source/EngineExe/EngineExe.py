from pathlib import Path
from nbsgp_interface import *

module_root = Path(__file__).parent.resolve()

Module = ModuleDefinition(
    name="EngineExe",
    private_macros=["ENGINEEXE"],
    path=Path(module_root),
    library_type="executable",
    public_depends_modules=[
        ModuleDependency(
            project_name = "MyEngineProject",
            module_name = "EngineCore" 
            ),
        ModuleDependency(
            project_name = "MyEngineProject",
            module_name = "EngineRender" 
            )
        ],
    private_source=["private"],
    public_include=["public"]  
)