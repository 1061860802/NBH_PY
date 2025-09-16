from pathlib import Path
from nbsgp import *

# �������������ⲿ���������
# ʹ�� r"..." ԭʼ�ַ��������Ա���ת���ַ�����
project_root = Path(__file__).parent.resolve()

load_project(r"I:\PythonProject\nbsgp\testfiles\MyEngineProject")

# ������Ϸ��Ŀ
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