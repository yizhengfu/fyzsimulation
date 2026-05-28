# 打开输入文件
with open(r"F:/DillonHuang/GAP_DI_RE/N-100/jili/3000K/species.txt", "r") as input_file:
    content = input_file.read()

# 删除所有的 "# "，将多个连续的空格替换为单个空格
cleaned_content = content.replace("# ", "").replace("  ", " ")

# 将清理后的内容写入到 "1.txt" 文件中
with open("1.txt", "w") as output_file:
    output_file.write(cleaned_content)

print("已将清理后的内容保存到 1.txt 文件中")
