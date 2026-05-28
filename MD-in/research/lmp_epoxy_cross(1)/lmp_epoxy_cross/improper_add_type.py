  # -*- coding: UTF-8 -*-
def loadTuopu(tuopuguiji1,tuoputype1,tuoputype2):
    inFile = open(tuopuguiji1, 'r')
    tuopuinfls = []
    numline = 0
    numtuopu = 1000000
    tuopupanduan = 0
    for line in inFile:
        trainingSetls = line.split(' ')
        numline = numline + 1
        lenyh = len(trainingSetls)
        trainingSetls[lenyh-1] = trainingSetls[lenyh-1][0:\
                                (len(trainingSetls[lenyh-1])-1)]
        trainingSet = []
        for num_data in range(0,len(trainingSetls)):
            if trainingSetls[num_data] != '':
                trainingSet.append(trainingSetls[num_data])
        if trainingSet == []:
            trainingSet.append('')
        if len(trainingSet) > 1:
            if str(trainingSet[1]) == str(tuoputype1):
                numtuopu = int(trainingSet[0])
        if str(trainingSet[0]) == str(tuoputype2):
            tuopupanduan = 1
        if tuopupanduan == 1 and str(trainingSet[0]) != str(tuoputype2) \
           and trainingSet != ['']:
            tuopuinfls.append(trainingSet)
        if len(tuopuinfls) == numtuopu:
            break                          
    return tuopuinfls
def loadcoeff(tuopuguiji1):
    inFile = open(tuopuguiji1, 'r')
    tuopuinfls = []
    numline = 0
    numtuopu = 1000000
    tuopupanduan = 0
    for line in inFile:
        trainingSetls = line.split(' ')
        numline = numline + 1
        #if numline > 588:
            #break  
        lenyh = len(trainingSetls)
        trainingSetls[lenyh-1] = trainingSetls[lenyh-1][0:\
                                (len(trainingSetls[lenyh-1])-1)]
        trainingSet = []
        for num_data in range(0,len(trainingSetls)):
            if trainingSetls[num_data] != '':
                trainingSet.append(trainingSetls[num_data])
        if trainingSet != []:
            if trainingSet[0] == 'Atoms':
                break   
        tuopuinfls.append(trainingSet) 
                           
    return tuopuinfls
def sort_atom(atom_infls):
    atom_inflsls = []
    for atom_id in range(0,len(atom_infls)):
        atom_inflsls.append([])
    for atom_id in range(0,len(atom_infls)):
        atom_id_vale = int(atom_infls[atom_id][0])
        atom_inflsls[atom_id_vale-1] = atom_infls[atom_id]
    return atom_inflsls
def allocate_coeff(coeff_all):
    coeff_str = []
    for num_coeff in range(0,len(coeff_all)):
        coeff_str.append(coeff_all[num_coeff][len(coeff_all[num_coeff])-1])
    return coeff_str
def out_put_data(out_data_inf,out_data_name):
    with open(out_data_name, 'w') as INPUT_LAMMPS:
        for i in range(0,len(out_data_inf)):
            INPUT_LAMMPS.write("%s %s %s %s %s \n"%(\
              out_data_inf[i][0],out_data_inf[i][1],out_data_inf[i][2],out_data_inf[i][3],\
              out_data_inf[i][4]))
###########################################
###########################################
initial_data = "SU8pcff.data"#初始data文件名
coeff_data_name = "coeff.data"#单独存放参数的文件名
###########################################
###########################################
mass_coeff_all = loadTuopu(coeff_data_name,"atom_types","Masses")
pair_coeff_all = loadTuopu(coeff_data_name,"atom_types","Pair")
bond_coeff_all = loadTuopu(coeff_data_name,"bond_types","Bond")
angle_coeff_all = loadTuopu(coeff_data_name,"angle_types","Angle")
dihedral_coeff_all = loadTuopu(coeff_data_name,"dihedral_types","Dihedral")
improper_coeff_all = loadTuopu(coeff_data_name,"improper_types","Improper")
mass_coeff_str = allocate_coeff(mass_coeff_all)
pair_coeff_str = allocate_coeff(pair_coeff_all)
bond_coeff_str = allocate_coeff(bond_coeff_all)
angle_coeff_str = allocate_coeff(angle_coeff_all)
dihedral_coeff_str = allocate_coeff(dihedral_coeff_all)
improper_coeff_str = allocate_coeff(improper_coeff_all)
coeff_inf = loadcoeff(initial_data)
atom_infls = loadTuopu(initial_data,"atoms","Atoms")
atom_inf = sort_atom(atom_infls)
bond_inf = loadTuopu(initial_data,"bonds","Bonds")
angle_inf = loadTuopu(initial_data,"angles","Angles")
dihedral_inf = loadTuopu(initial_data,"dihedrals","Dihedrals")
improper_inf = loadTuopu(initial_data,"impropers","Impropers")
improper_collect_pd = []
improper_collect = []
for i in range(0,len(improper_inf)):
    if int(improper_inf[i][1]) not in improper_collect_pd:
        improper_collect_pd.append(int(improper_inf[i][1]))
        improper_collect.append(improper_inf[i])
for i in range(0,29):
    improper_collect_type = int(improper_collect[i][1])
    improper_type = mass_coeff_str[int(atom_inf[int(improper_collect[i][2])-1][2])-1] + '-' + \
                    mass_coeff_str[int(atom_inf[int(improper_collect[i][3])-1][2])-1] + '-' + \
                    mass_coeff_str[int(atom_inf[int(improper_collect[i][4])-1][2])-1] + '-' + \
                    mass_coeff_str[int(atom_inf[int(improper_collect[i][5])-1][2])-1]
    if improper_collect_type > 4:
        improper_coeff_all[improper_collect_type-1].append('#')
        improper_coeff_all[improper_collect_type-1].append(improper_type)
out_put_data(improper_coeff_all,"improper_add_coeff.data")
print("补充的Improper类型在%s文件中"%("improper_add_coeff.data"))
