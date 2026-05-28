import os
import  sys
import tkinter as tk
from tkinter import filedialog
import ctypes

# os.system("dir")
# os.system("git")

exe = tk.Tk()
exe.title("msi2lmp.exe")

# class Operate:
#     def openfile(num):
#         if num == 1:
#             fname = filedialog.askopenfilename(title='打开car文件', filetypes=[('S2out', '*.out'), ('All Files', '*')])
#             print(fname)
#         elif num == 2:
#             fname = filedialog.askopenfilename(title='打开mdf文件',filetypes=[('CGNSdat', '*.dat'), ('All Files', '*')] )
#             print(fname)

def show(num):
    if num == 1:
        global path1
        path1 = filedialog.askopenfilename(title='打开car文件', filetypes=[('car file', '*.car'), ('All Files', '*')])
        print(path1)
        global fname1
        fname1 = os.path.basename(path1)
        print(fname1)
        # print(type(fname1))
        # print(fname1.split(".")[0])
        # print(fname1)
        v.set("car文件已成功载入！")
    elif num == 2:
        global path2
        path2 = filedialog.askopenfilename(title='打开mdf文件', filetypes=[('mdf file', '*.mdf'), ('All Files', '*')])
        print(path2)
        global fname2
        fname2 = os.path.basename(path2)
        print(fname2)
        # print(type(fname1))
        # print(fname1.split(".")[0])
        # print(fname1)
        # strname2 = fname2.split(".")[0]
        v.set("mdf文件已成功载入！")
    elif num == 3:
        def creat(str1, str2):
            if str1.split(".")[0] != str2.split(".")[0]:
                ctypes.windll.user32.MessageBoxW(0, '文件名不一致', "警告", 0)
            else:
                # pass
                current_path = os.getcwd()
                # current_path.replace("\\", "/")
                # print(current_path.replace("\\", "/"))
                print("copy \"%s\" %s\%s" % (path1.replace("/", "\\"), current_path, str1))
                os.system("copy \"%s\" \"%s\%s\" "% (path1.replace("/", "\\"), current_path, str1))
                os.system("copy \"%s\" \"%s\%s\" "% (path2.replace("/", "\\"), current_path, str2))

                strs1 = "..\src\msi2lmp.exe "
                # strs1 = "msi2lmp.exe"
                # strs2 = str1
                strs2 = str1.split(".")[0]
                strs3 = " -p o -frc ..\\frc_files\\cvff -i > data."
                # print("dir %s ; dir %s ; dir %s ; dir %s" % (strs1, strs2, strs3, strs2))
                order_string = strs1+strs2+strs3+strs2
                print(order_string)
                # os.popen(order_string)
                os.system(order_string)

                # os.popen("dir %s ; dir %s ; dir %s ; dir %s" % (strs1, strs2, strs3, strs2))
        creat(fname1, fname2)
        os.remove(fname1)
        os.remove(fname2)
        os.system("exit")
        v.set("已成功生成dat文件！")



# def creat(str1, str2):
#     if str1 is not str2:
#         ctypes.windll.user32.MessageBoxW(0, '文件名不一致', "警告", 0)
#     else:
#         os.system("copy path1 ..")
#         strs1 = "./msi2lmp.exe"
#         strs2 = str1
#         strs3 = "-class I -frc cvff > data."
#
#     # os.system("ls %s ; ls %s ; ls %s ; ls %s" % (strs1, strs2, strs3, strs2))

frame1 = tk.Frame(exe)
frame2 = tk.Frame(exe)
v = tk.StringVar()


lab1 = tk.Label(frame1, textvariable=v, width=40)
lab1.pack()

tk.Button(frame2, text="选择car文件", width=10, command=lambda:show(1))\
    .grid(row=0, column=0, sticky="w", padx=10, pady=5)
tk.Button(frame2, text="选择mdf文件", width=10, command=lambda:show(2))\
    .grid(row=0, column=1, sticky="e", padx=10, pady=5)
tk.Button(frame2, text="生成dat文件", width=10, command=lambda:show(3))\
    .grid(row=0, column=2, sticky="e", padx=10, pady=5)

frame1.pack()
frame2.pack()
tk.mainloop()