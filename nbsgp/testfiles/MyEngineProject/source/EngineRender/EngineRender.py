from pathlib import Path
from nbsgp_interface import *

module_root = Path(__file__).parent.resolve()

Module = ModuleDefinition(
    name="EngineRender",
    private_macros=["ENGINERENDER"],
    path=Path(module_root),
    library_type="STATIC",
    public_depends_modules=[
        ModuleDependency(
            project_name = "MyEngineProject",
            module_name = "EngineCore" 
            )
        ],
    private_source=["private"],
    public_include=["public"],
)