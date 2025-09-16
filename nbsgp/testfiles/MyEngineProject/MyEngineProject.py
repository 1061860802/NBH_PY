from pathlib import Path
from nbsgp import *

# �������������ⲿ���������
# ʹ�� r"..." ԭʼ�ַ��������Ա���ת���ַ�����
project_root = Path(__file__).parent.resolve()

# ������Ϸ��Ŀ
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