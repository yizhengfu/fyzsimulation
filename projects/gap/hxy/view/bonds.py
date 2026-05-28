bonds = open("bonds.reax","r") #修改文件名
dump = open("bonds_ana.lammpstrj","r") #修改文件名
N_Frame = 10001 #总共有多少帧要分析

n_atom = 243 #总原子个数，模拟中不能变

n_bond = 0
atom_sec = []
bond_sec = []

for i in range(N_Frame):
    for j in range(5):
        line_dump = dump.readline()

    line_dump = dump.readline()
    xlo = line_dump.split()[0]
    xhi = line_dump.split()[1]
    line_dump = dump.readline()
    ylo = line_dump.split()[0]
    yhi = line_dump.split()[1]
    line_dump = dump.readline()
    zlo = line_dump.split()[0]
    zhi = line_dump.split()[1]
    line_dump = dump.readline()
    for k in range(n_atom):
        line_dump = dump.readline()
        atom_sec.append(line_dump)
    if i == 0:
        pre_line = 7
    else:
        pre_line = 8
    for j in range(pre_line):
        line_bond = bonds.readline()
    for k in range(n_atom):
        line_bond = bonds.readline()
        nb = int(line_bond.split()[2])
        for l in range(nb):
            n_bond += 1
            tmp = str(n_bond) + " " + "1" + " " + line_bond.split()[0] + " " + line_bond.split()[3+l] + "\n"
            bond_sec.append(tmp)
    data = open("data" + str(i),"w")
    data.write("LAMMPS data from bonds\n")
    data.write("\n")
    data.write(str(n_atom) + " " + "atoms\n")
    data.write("10 atom types\n")
    data.write(str(n_bond) + " " + "bonds\n")
    data.write("13 bond types\n")
    data.write("\n")
    data.write(str(xlo) + " " + str(xhi) + " " + "xlo xhi\n")
    data.write(str(ylo) + " " + str(yhi) + " " + "ylo yhi\n")
    data.write(str(zlo) + " " + str(zhi) + " " + "zlo zhi\n")
    data.write("\n")
    data.write("Atoms\n")
    data.write("\n")
    data.writelines(atom_sec)
    data.write("\n")
    data.write("Bonds\n")
    data.write("\n")
    data.writelines(bond_sec)
    data.close()
    n_bond = 0
    atom_sec = []
    bond_sec = []