from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem import rdMolDescriptors  # 显式导入描述符模块
import os


def draw_smiles(smiles_str, filename="molecule.png"):
    # 1. 转换分子对象
    mol = Chem.MolFromSmiles(smiles_str)

    if mol is None:
        print(f"解析失败: '{smiles_str}' 格式有误。")
        return

    # 2. 计算分子式 (修正后的调用)
    formula = rdMolDescriptors.CalcMolFormula(mol)
    print(f"成功解析！分子式为: {formula}")

    # 3. 保存图片
    Draw.MolToFile(mol, filename, size=(300, 300))
    print(f"图片已保存至: {os.path.abspath(filename)}")

    # 4. 尝试弹出窗口预览
    try:
        from PIL import Image
        img = Draw.MolToImage(mol, size=(300, 300))
        img.show()
    except Exception as e:
        print("无法弹出窗口预览，请直接查看保存的 PNG 文件。")


if __name__ == "__main__":
    test_smiles = "[H][O][C]([H])([C]([H])([H])[N]=[N]=[N])[C]([H])([H])[O][C]([H])([C]([H])([H])[N]=[N]=[N])[C]([H])([H])[O][C]([H])([C]([H])([H])[N]=[N]=[N])[C]([H])([H])[O][C]([H])([C]([H])([H])[N]=[N]=[N])[C]([H])([H])[O][C]([H])([C]([H])([H])[N]=[N]=[N])[C]([H])([H])[O][C]([H])([C]([H])([H])[N]=[N]=[N])[C]([H])([H])[O][C]([H])([C]([H])([H])[N]=[N]=[N])[C]([H])([H])[O][C]([H])([C]([H])([H])[N]=[N]=[N])[C]([H])([H])[O][C]([H])([C]([H])([H])[N]=[N]=[N])[C]([H])([H])[O][C]([H])([C]([H])([H])[N]=[N]=[N])[C]([H])([H])[O][C](=[O])[N]([H])[C]([H])([H])[C]([H])([H])[C]([H])([H])[C]([H])([H])[C]([H])([H])[C]([H])([H])[C](=[O])[N]([C](=[O])[C]([H])([H])[C]([H])([H])[C]([H])([H])[C]([H])([H])[C]([H])([H])[C]([H])([H])[N]([H])[C](=[O])[O][C]([H])([H])[C]([H])([O][C]([H])([H])[C]([H])([O][C]([H])([H])[C]([H])([O][C]([H])([H])[C]([H])([O][C]([H])([H])[C]([H])([O][C]([H])([H])[C]([H])([O][C]([H])([H])[C]([H])([O][C]([H])([H])[C]([H])([O][C]([H])([H])[C]([H])([O][C]([H])([H])[C]([H])([O][H])[C]([H])([H])[N]=[N]=[N])[C]([H])([H])[N]=[N]=[N])[C]([H])([H])[N]=[N]=[N])[C]([H])([H])[N]=[N]=[N])[C]([H])([H])[N]=[N]=[N])[C]([H])([H])[N]=[N]=[N])[C]([H])([H])[N]=[N]=[N])[C]([H])([H])[N]=[N]=[N])[C]([H])([H])[N]=[N]=[N])[C]([H])([H])[N]=[N]=[N])[C]([H])([H])[C]([H])([H])[C]([H])([H])[C]([H])([H])[C]([H])([H])[C]([H])([H])[N]([H])[C](=[O])[O][C]([H])([H])[C]([H])([O][C]([H])([H])[C]([H])([O][C]([H])([H])[C]([H])([O][C]([H])([H])[C]([H])([O][C]([H])([H])[C]([H])([O][C]([H])([H])[C]([H])([O][C]([H])([H])[C]([H])([O][C]([H])([H])[C]([H])([O][C]([H])([H])[C]([H])([O][C]([H])([H])[C]([H])([O][H])[C]([H])([H])[N]=[N]=[N])[C]([H])([H])[N]=[N]=[N])[C]([H])([H])[N]=[N]=[N])[C]([H])([H])[N]=[N]=[N])[C]([H])([H])[N]=[N]=[N])[C]([H])([H])[N]=[N]=[N])[C]([H])([H])[N]=[N]=[N])[C]([H])([H])[N]=[N]=[N])[C]([H])([H])[N]=[N]=[N])[C]([H])([H])[N]=[N]=[N]"
    draw_smiles(test_smiles)