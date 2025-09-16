from pathlib import Path
from nbsgp_interface import *

module_root = Path(__file__).parent.resolve()

Module = ModuleDefinition(
    name="EngineCore",
    private_macros=["ENGINECORE"],
    path=Path(module_root),
    library_type="STATIC",
    private_source=["private/*.cpp"],
    public_include=["public","include"],
)