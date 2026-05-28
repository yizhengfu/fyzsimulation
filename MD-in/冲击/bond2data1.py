

work_path = "E:\\code_testmuran\\DGE3_0.30\\"

bonds = open(work_path + "bonds.reax","r")
dump = open(work_path + "atom.lammpstrj","r")

N_Frame = 551

n_atom = 9143
n_atomtypes = 7
n_bond = 0
atom_sec = []
bond_sec = []

for i in range(N_Frame):
    for j in range(5):
        line_dump = dump.readline()

    line_dump = dump.readline()
    xlo = float(line_dump.split()[0])
    xhi = float(line_dump.split()[1])
    lx = xhi - xlo
    line_dump = dump.readline()
    ylo = float(line_dump.split()[0])
    yhi = float(line_dump.split()[1])
    ly = yhi - ylo
    line_dump = dump.readline()
    zlo = float(line_dump.split()[0])
    zhi = float(line_dump.split()[1])
    lz = zhi -zlo
    line_dump = dump.readline()
    for k in range(n_atom):
        line_dump = dump.readline()
        x = float(line_dump.split()[2])*lx + xlo
        y = float(line_dump.split()[3])*ly + ylo
        z = float(line_dump.split()[4])*lz + zlo
        tmp1 = line_dump.split()[0] + " " + "1" + " " + line_dump.split()[1] + " " + "0" + " " + str(x) + " " + str(y) + " " + str(z) +"\n"
        atom_sec.append(tmp1)
    if i == 0:
        pre_line = 7
    else:
        pre_line = 8
    for j in range(pre_line):
        line_bond = bonds.readline()
    for k in range(n_atom):
        line_bond = bonds.readline()
        nb = int(line_bond.split()[2])
        if nb > 0 :
            for l in range(nb):
                n_bond += 1
                tmp = str(n_bond) + " " + "1" + " " + line_bond.split()[0] + " " + line_bond.split()[3+l] + "\n"
                bond_sec.append(tmp)
    data = open(work_path + "data" + str(i),"w")
    data.write("LAMMPS data from bonds\n")
    data.write("\n")
    data.write(str(n_atom) + " " + "atoms\n")
    data.write(str(n_atomtypes) + " " + "atom types\n")
    data.write(str(n_bond) + " " + "bonds\n")
    data.write("1 bond types\n")
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







