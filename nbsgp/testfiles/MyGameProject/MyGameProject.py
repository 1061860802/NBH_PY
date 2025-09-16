from pathlib import Path
from nbsgp import *

# 在这里声明对外部引擎的依赖
# 使用 r"..." 原始字符串，可以避免转义字符问题
project_root = Path(__file__).parent.resolve()

load_project(r"I:\PythonProject\nbsgp\testfiles\MyEngineProject")

# 定义游戏项目
Project = ProjectDefinition(
    name="MyGameProject",
    path=project_root,
    public_modules = 
    [
        load_module(project_root / "source\GameExe"),
    ],
    public_depends=
    [
        ProjectDependency(
            project_name="MyEngineProject"
            )
    ]
)