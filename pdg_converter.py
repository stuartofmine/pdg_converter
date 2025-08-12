import os
import subprocess
import img2pdf
from pathlib import Path
import tempfile
import shutil
import re

def extract_number(filename):
    """从文件名中提取数字部分"""
    # 使用正则表达式查找所有数字
    numbers = re.findall(r'\d+', filename)
    if numbers:
        return int(numbers[0])  # 返回第一个数字序列
    return float('inf')  # 如果没有数字，返回无穷大（排在最后）

def pdg_to_pdf(pdg_folder, output_pdf):
    """
    将PDG文件夹转换为PDF
    :param pdg_folder: 包含PDG文件的文件夹路径
    :param output_pdf: 输出PDF文件路径
    """
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    print(f"临时目录: {temp_dir}")
    
    try:
        # 1. 获取所有PDG文件并按数字排序
        pdg_files = sorted(
            [f for f in Path(pdg_folder).glob("*.pdg")],
            key=lambda x: extract_number(x.stem)
        )
        
        if not pdg_files:
            raise FileNotFoundError("未找到任何PDG文件")
        
        print(f"找到 {len(pdg_files)} 个PDG文件")
        
        # 2. 转换每个PDG为TIFF
        tiff_files = []
        for pdg_file in pdg_files:
            tiff_path = os.path.join(temp_dir, f"{pdg_file.stem}.tiff")
            
            # 使用sips转换PDG为TIFF
            cmd = [
                "sips",
                "-s", "format", "tiff",
                str(pdg_file),
                "--out", tiff_path
            ]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                tiff_files.append(tiff_path)
                print(f"转换成功: {pdg_file.name} -> {os.path.basename(tiff_path)}")
            except subprocess.CalledProcessError as e:
                print(f"转换失败 {pdg_file.name}: {e.stderr.decode().strip()}")
                continue
        
        if not tiff_files:
            raise RuntimeError("没有成功转换任何PDG文件")
        
        # 3. 将TIFF合并为PDF
        print("正在生成PDF...")
        with open(output_pdf, "wb") as f:
            f.write(img2pdf.convert(tiff_files))
        
        print(f"PDF已生成: {output_pdf}")
    
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)
        print("临时文件已清理")

if __name__ == "__main__":
    # 使用示例
    pdg_folder = input("请输入PDG文件夹路径: ").strip()
    output_pdf = input("请输入输出PDF路径: ").strip()
    
    if not os.path.isdir(pdg_folder):
        print("错误: PDG文件夹不存在")
    else:
        pdg_to_pdf(pdg_folder, output_pdf)
