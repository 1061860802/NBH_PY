from pathlib import Path
from nbsgp import *

# 在这里声明对外部引擎的依赖
# 使用 r"..." 原始字符串，可以避免转义字符问题
project_root = Path(__file__).parent.resolve()

# 定义游戏项目
Project = ProjectDefinition(
    name="MyEngineProject",
    path=project_root,
    public_modules = 
    [
        load_module(project_root / "source\EngineCore"),
        load_module(project_root / "source\EngineRender"),
        load_module(project_root / "source\EngineExe"),
    ]
)