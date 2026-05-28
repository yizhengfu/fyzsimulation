  # -*- coding: UTF-8 -*-
    inFile = open(tuopuguiji1, 'r')
    tuopuinfls = []
    numline = 0
    numtuopu = 1000000
    tuopupanduan = 0
    for line in inFileA       trainingSetls = line.split(' ')
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
def allocate_coeff(coeff_all):
    coeff_str = []
    for num_coeff in range(0,len(coeff_all)):
        coeff_str.append(coeff_all[num_coeff][len(coeff_all[num_coeff])-1])
    return coeff_str   
def sort_atom(atom_infls):
    atom_inflsls = []
    for atom_id in range(0,len(atom_infls)):
        atom_inflsls.append([])
    for atom_id in range(0,len(atom_infls)):
        atom_id_vale = int(atom_infls[atom_id][0])
        atom_inflsls[atom_id_vale-1] = atom_infls[atom_id]
    return atom_inflsls
def select_coord(atom_inf):
    coord_infls = []
    for atom_coord_id in range(0,len(atom_inf)):
        coord_infls.append(float(atom_inf[atom_coord_id][4]))
        coord_infls.append(float(atom_inf[atom_coord_id][5]))
        coord_infls.append(float(atom_inf[atom_coord_id][6]))
    return coord_infls
def int_bond(bond_inf):
    bondls = []
    for bond_inf_id in range(0,len(bond_inf)):
        for one_bond_inf_id in range(0,len(bond_inf[bond_inf_id])):
            bondls.append(int(bond_inf[bond_inf_id][one_bond_inf_id]))
    return bondls
def atom_tuopu_allocate(atom_inf,tuopu_inf):
    atom_tuopu_inf = []
    atom_tuopu_inf_all = []
    for atom_id in range(0,len(atom_inf)):
        atom_tuopu_inf.append([])
        atom_tuopu_inf_all.append([])
    for tuopu_id in range(0,len(tuopu_inf)):
        tuopu_type_vale = int(tuopu_inf[tuopu_id][1])
        for one_tuopu_id in range(2,len(tuopu_inf[tuopu_id])):
            atom_tuopu_inf[int(tuopu_inf[tuopu_id][one_tuopu_id])-1].\
                      append(tuopu_type_vale)
            atom_tuopu_inf_all[int(tuopu_inf[tuopu_id][one_tuopu_id])-1]\
                               .append(tuopu_inf[tuopu_id])
    return atom_tuopu_inf,atom_tuopu_inf_all
def atom_bond_atom(atom_inf,bond_inf):
    atom_bond_atom_inf_ls = []
    for atom_id in range(0,len(atom_inf)):
        atom_bond_atom_inf_ls.append([])
    for bond_id in range(0,len(bond_inf)):
        bond_atom1_id = int(bond_inf[bond_id][2])
        bond_atom2_id = int(bond_inf[bond_id][3])
        atom_bond_atom_inf_ls[bond_atom1_id-1].append(bond_atom2_id)
        atom_bond_atom_inf_ls[bond_atom2_id-1].append(bond_atom1_id)
    return atom_bond_atom_inf_ls
def change_c1_type(atom_inf,ch3_type,c1_vale,c3h_c2,atom_bond_inf):
    for atom_id in range(0,len(atom_inf)):
        atom_type_vale = int(atom_inf[atom_id][2])
        if atom_type_vale == ch3_type:
            if c3h_c2 in atom_bond_inf[atom_id]:
                atom_inf[atom_id][2] = str(c1_vale)      
def atom_coord(index_of_atom,coord,lmp):  
	a=3 * (index_of_atom - 1)                     
	a=int(a)                              
	target_atom_coord=[0]*3
	for i in range (3):
		target_atom_coord[i]=coord[a+i]   	
	return target_atom_coord              
def get_atoms_type(atom_inf):
    atom_type_infls = []
    for atom_type_id in range(0,len(atom_inf)):
        atom_type_infls.append(int(atom_inf[atom_type_id][2]))
    return atom_type_infls
def get_atoms(number_of_attribute,atom_inf,atom_bond_inf,c3h_c2,bond_inf,\
              c3h_c3h,atom_bond_inf_all,c3h_o3e):
    get_atom_inf = []
    for atom_id in range(0,len(atom_inf)):
        atom_type = int(atom_inf[atom_id][2])
        if atom_type == number_of_attribute and c3h_c2 in \
                 atom_bond_inf[atom_id]:
            get_atom_inf.append([atom_id+1])
    for get_atom_id in range(0,len(get_atom_inf)):
        c1_atom_id = int(get_atom_inf[get_atom_id][0])
        for atom_bond_id in range(0,len(atom_bond_inf_all[c1_atom_id-1])):
            if int(atom_bond_inf_all[c1_atom_id-1][atom_bond_id][1]) == c3h_c3h:
                if int(atom_bond_inf_all[c1_atom_id-1][atom_bond_id][2]) ==\
                         c1_atom_id:
                    get_atom_inf[get_atom_id].append(int(atom_bond_inf_all\
                                    [c1_atom_id-1][atom_bond_id][3]))
                else:
                    get_atom_inf[get_atom_id].append(int(atom_bond_inf_all\
                                    [c1_atom_id-1][atom_bond_id][2]))
    for get_atom_id in range(0,len(get_atom_inf)):
        c1_atom_id = int(get_atom_inf[get_atom_id][0])
        for atom_bond_id in range(0,len(atom_bond_inf_all[c1_atom_id-1])):
            if int(atom_bond_inf_all[c1_atom_id-1][atom_bond_id][1]) == c3h_o3e:
                if int(atom_bond_inf_all[c1_atom_id-1][atom_bond_id][2]) == \
                   c1_atom_id:
                    get_atom_inf[get_atom_id].append(int(atom_bond_inf_all\
                                    [c1_atom_id-1][atom_bond_id][3]))
                else:
                    get_atom_inf[get_atom_id].append(int(atom_bond_inf_all\
                                    [c1_atom_id-1][atom_bond_id][2]))       
    return get_atom_inf
def check_distance(atom_inf,atom_id_1,atom_id_2,react_radius):
    react_distance = 0
    dx = float(atom_inf[atom_id_1-1][4]) - \
         float(atom_inf[atom_id_2-1][4])
    dy = float(atom_inf[atom_id_1-1][5]) - \
         float(atom_inf[atom_id_2-1][5])
    dz = float(atom_inf[atom_id_1-1][6]) - \
         float(atom_inf[atom_id_2-1][6])
    d = ((dx)**2 + (dy)**2 + (dz)**2) ** 0.5
    if d <= react_radius:
        react_distance = 1
    return react_distance
def check_reacted(reacted_c1,c1_id_1,c1_id_2):
    if_reacted_ls = 0
    if c1_id_1 not in reacted_c1 and c1_id_2 not in reacted_c1:
        if_reacted_ls = 1
    return if_reacted_ls
def check_boundary(atom_inf,atom_id_1,atom_id_2):
    if_boundary_ls = 0
    if int(atom_inf[atom_id_1-1][7]) == int(atom_inf[atom_id_2-1][7]) and \
       int(atom_inf[atom_id_1-1][8]) == int(atom_inf[atom_id_2-1][8]) and \
       int(atom_inf[atom_id_1-1][9]) == int(atom_inf[atom_id_2-1][9]):
        if_boundary_ls = 1
    return if_boundary_ls
def change_atom_mol(atom_inf,oce_mol_vale,c2_mol_vale):
    if oce_mol_vale >= c2_mol_vale:
        goal_mol = c2_mol_vale
        change_mol = oce_mol_vale
    else:
        goal_mol = oce_mol_vale
        change_mol = c2_mol_vale
    atom_mol_collect = []
    for atom_id in range(0,len(atom_inf)):
        if atom_inf[atom_id][1] == change_mol:
            atom_inf[atom_id][1] = str(goal_mol)
        if int(atom_inf[atom_id][1]) not in atom_mol_collect:
            atom_mol_collect.append(int(atom_inf[atom_id][1]))
    atom_mol_collect.sort()
    for atom_id in range(0,len(atom_inf)):
        atom_inf[atom_id][1] = str(atom_mol_collect.index(int(atom_inf[atom_id][1]))+1)
def cross_link(atom_inf,num_c1_1,num_c1_2,index_c1_carbon,ho_type,hc_type,c1_type,\
               c3_type,oc_type,c2_type,oh_type,atom_bond_atom_inf):
    oce_atom_coord = atom_inf[index_c1_carbon[num_c1_2][2]-1][4:7] #c2原子部分的oce           
    c2_atom_coord = atom_inf[index_c1_carbon[num_c1_1][1]-1][4:7]#oce部分的c2
    oce_mol_vale = int(atom_inf[index_c1_carbon[num_c1_1][2]-1][1])
    c2_mol_vale = int(atom_inf[index_c1_carbon[num_c1_2][1]-1][1])
    oce_boundary = atom_inf[index_c1_carbon[num_c1_1][2]-1][7:10]
    c2_boundary = atom_inf[index_c1_carbon[num_c1_2][1]-1][7:10]
    r = 1.100                                                              
    Phi = random.uniform(0.2,6.283)                                        
    Theta = random.uniform(0.2,3.1415)                                     
    x = r * math.sin(Theta) * math.cos(Phi)                                   
    y = r * math.sin(Theta) * math.sin(Phi)                                    
    z = r * math.cos(Theta)                                                  
    ho_coord = [0,0,0]
    hc_coord = [0,0,0]
    ho_coord[0] = float(oce_atom_coord[0]) + x
    ho_coord[1] = float(oce_atom_coord[1]) + y
    ho_coord[2] = float(oce_atom_coord[2]) + z
    hc_coord[0] = float(c2_atom_coord[0]) + x
    hc_coord[1] = float(c2_atom_coord[1]) + y
    hc_coord[2] = float(c2_atom_coord[2]) + z
    num_atom_b = len(atom_inf)
    atom_inf.append([str(num_atom_b+1),str(oce_mol_vale),str(ho_type),\
                     str(0.4241),str(ho_coord[0]),str(ho_coord[1]),\
                     str(ho_coord[2]),str(oce_boundary[0]),\
                     str(oce_boundary[1]),str(oce_boundary[2]),"#","ho"])
    atom_inf.append([str(num_atom_b+2),str(c2_mol_vale),str(hc_type),\
                     str(0.053),str(hc_coord[0]),str(hc_coord[1]),\
                     str(hc_coord[2]),str(c2_boundary[0]),\
                     str(c2_boundary[1]),str(c2_boundary[2]),"#","hc"])
    atom_inf[index_c1_carbon[num_c1_1][0]-1][2] = str(c1_type)
    atom_inf[index_c1_carbon[num_c1_1][1]-1][2] = str(c3_type)
    atom_inf[index_c1_carbon[num_c1_1][1]-1][3] = str(-0.159)
    atom_inf[index_c1_carbon[num_c1_1][2]-1][2] = str(oc_type)
    atom_inf[index_c1_carbon[num_c1_2][0]-1][2] = str(c1_type)
    atom_inf[index_c1_carbon[num_c1_2][1]-1][2] = str(c2_type)
    atom_inf[index_c1_carbon[num_c1_2][2]-1][2] = str(oh_type)
    atom_inf[index_c1_carbon[num_c1_2][2]-1][3] = str(-0.5571)
    change_atom_mol(atom_inf,oce_mol_vale,c2_mol_vale)
    atom_bond_atom_inf[index_c1_carbon[num_c1_1][2]-1].remove\
                                    (index_c1_carbon[num_c1_1][1])
    atom_bond_atom_inf[index_c1_carbon[num_c1_1][2]-1].append\
                                    (index_c1_carbon[num_c1_2][1])
    atom_bond_atom_inf[index_c1_carbon[num_c1_1][1]-1].remove\
                                    (index_c1_carbon[num_c1_1][2])
    atom_bond_atom_inf[index_c1_carbon[num_c1_1][1]-1].append\
                                    (num_atom_b+2)
    atom_bond_atom_inf[index_c1_carbon[num_c1_2][2]-1].remove\
                                    (index_c1_carbon[num_c1_2][1])
    atom_bond_atom_inf[index_c1_carbon[num_c1_2][2]-1].append\
                                     (num_atom_b+1)
    atom_bond_atom_inf[index_c1_carbon[num_c1_2][1]-1].remove\
                                    (index_c1_carbon[num_c1_2][2])
    atom_bond_atom_inf[index_c1_carbon[num_c1_2][1]-1].append\
                                    (index_c1_carbon[num_c1_1][2])
    atom_bond_atom_inf.append([index_c1_carbon[num_c1_2][2]])
    atom_bond_atom_inf.append([index_c1_carbon[num_c1_1][1]])
def get_bond_type(bond_coeff_str,mass_coeff_str,bond_atom1,bond_atom2,atom_inf):
    bond_1_type = mass_coeff_str[int(atom_inf[bond_atom1-1][2])-1] + "-" +\
                      mass_coeff_str[int(atom_inf[bond_atom2-1][2])-1]
    bond_2_type = mass_coeff_str[int(atom_inf[bond_atom2-1][2])-1] + "-" +\
                      mass_coeff_str[int(atom_inf[bond_atom1-1][2])-1]
    if bond_1_type in bond_coeff_str:
        bond_type_valels = bond_coeff_str.index(bond_1_type) + 1
    if bond_2_type in bond_coeff_str:
        bond_type_valels = bond_coeff_str.index(bond_2_type) + 1
    if bond_1_type not in bond_coeff_str and bond_2_type not in bond_coeff_str:
        x
    return bond_type_valels   
def creat_bond(atom_bond_atom_inf,bond_coeff_str,mass_coeff_str,atom_inf):
    creat_bond_inf1 = []
    creat_bond_inf = []
    num_creat_bond = 0
    for num_atom in range(0,len(atom_bond_atom_inf)):
        for atom_bond_id in range(0,len(atom_bond_atom_inf[num_atom])):
            if str(num_atom+1)+str(atom_bond_atom_inf[num_atom][atom_bond_id]) not in \
                creat_bond_inf1 and  str(atom_bond_atom_inf[num_atom][atom_bond_id])+str(num_atom+1)\
                 not in creat_bond_inf1:
                num_creat_bond = num_creat_bond + 1
                creat_bond_inf1.append(str(num_atom+1)+str(atom_bond_atom_inf[num_atom][atom_bond_id]))
                bond_type_vale = get_bond_type(bond_coeff_str,mass_coeff_str,\
                                    num_atom+1,atom_bond_atom_inf[num_atom][atom_bond_id],atom_inf)
                creat_bond_inf.append([str(num_creat_bond),str(bond_type_vale),\
                                       str(num_atom+1),str(atom_bond_atom_inf[num_atom][atom_bond_id])])                
    return creat_bond_inf
def get_angle_type(angle_coeff_str,mass_coeff_str,angle_atom1,angle_atom2,\
                   angle_atom3,atom_inf):
    angle_1_type = mass_coeff_str[int(atom_inf[angle_atom1-1][2])-1] + "-" + \
                   mass_coeff_str[int(atom_inf[angle_atom2-1][2])-1] + "-" + \
                   mass_coeff_str[int(atom_inf[angle_atom3-1][2])-1]
    angle_2_type = mass_coeff_str[int(atom_inf[angle_atom3-1][2])-1] + "-" + \
                   mass_coeff_str[int(atom_inf[angle_atom2-1][2])-1] + "-" + \
                   mass_coeff_str[int(atom_inf[angle_atom1-1][2])-1]
    if angle_1_type in angle_coeff_str:
        angle_type_valels = angle_coeff_str.index(angle_1_type) + 1
    if angle_2_type in angle_coeff_str:
        angle_type_valels = angle_coeff_str.index(angle_2_type) + 1
    if angle_1_type not in angle_coeff_str and angle_2_type not in angle_coeff_str:
        x
    return angle_type_valels
def creat_angle(atom_bond_atom_inf,angle_coeff_str,mass_coeff_str,atom_inf):
    creat_angle_inf = []
    num_creat_angle = 0
    for atom_id in range(0,len(atom_bond_atom_inf)):
        for atom_bond_id_1 in range(0,len(atom_bond_atom_inf[atom_id])):
            for atom_bond_id_2 in range(atom_bond_id_1+1,len(atom_bond_atom_inf[atom_id])):
                num_creat_angle = num_creat_angle + 1 
                angle_type_vale = get_angle_type(angle_coeff_str,mass_coeff_str,\
                                            atom_bond_atom_inf[atom_id][atom_bond_id_1],\
                                        atom_id+1,atom_bond_atom_inf[atom_id][atom_bond_id_2],atom_inf)
                creat_angle_inf.append([str(num_creat_angle),str(angle_type_vale),\
                        str(atom_bond_atom_inf[atom_id][atom_bond_id_1]),str(atom_id+1),\
                                        str(atom_bond_atom_inf[atom_id][atom_bond_id_2])])                
    return creat_angle_inf
def get_dihedral_type(dihedral_coeff_str,mass_coeff_str,dihedral_atom1,dihedral_atom2,\
                      dihedral_atom3,dihedral_atom4,atom_inf):
    dihedral_1_type = mass_coeff_str[int(atom_inf[dihedral_atom1-1][2])-1] + "-" + \
                       mass_coeff_str[int(atom_inf[dihedral_atom2-1][2])-1] + "-" + \
                       mass_coeff_str[int(atom_inf[dihedral_atom3-1][2])-1] + "-" + \
                       mass_coeff_str[int(atom_inf[dihedral_atom4-1][2])-1]
    dihedral_2_type = mass_coeff_str[int(atom_inf[dihedral_atom4-1][2])-1] + "-" + \
                       mass_coeff_str[int(atom_inf[dihedral_atom3-1][2])-1] + "-" + \
                       mass_coeff_str[int(atom_inf[dihedral_atom2-1][2])-1] + "-" + \
                       mass_coeff_str[int(atom_inf[dihedral_atom1-1][2])-1]
    if dihedral_1_type in dihedral_coeff_str:
        dihedral_type_valels = dihedral_coeff_str.index(dihedral_1_type) + 1
    if dihedral_2_type in dihedral_coeff_str:
        dihedral_type_valels = dihedral_coeff_str.index(dihedral_2_type) + 1
    if dihedral_1_type not in dihedral_coeff_str and dihedral_2_type not in dihedral_coeff_str:
        x
    return dihedral_type_valels
def creat_dihedral(atom_bond_atom_inf,bond_inf,dihedral_coeff_str,mass_coeff_str,atom_inf):
    creat_dihedral_inf = []
    num_cross_dihedral = 0
    for bond_id in range(0,len(bond_inf)):
        bond_atom1_id =  int(bond_inf[bond_id][2])
        bond_atom2_id =  int(bond_inf[bond_id][3])
        for bond_1_id in range(0,len(atom_bond_atom_inf[bond_atom1_id-1])):
            for bond_2_id in range(0,len(atom_bond_atom_inf[bond_atom2_id-1])):
                if atom_bond_atom_inf[bond_atom1_id-1][bond_1_id] != bond_atom2_id and \
                   atom_bond_atom_inf[bond_atom2_id-1][bond_2_id] != bond_atom1_id and \
                   atom_bond_atom_inf[bond_atom1_id-1][bond_1_id] != atom_bond_atom_inf\
                   [bond_atom2_id-1][bond_2_id]:
                    num_cross_dihedral = num_cross_dihedral + 1
                    dihedral_type_vale = get_dihedral_type(dihedral_coeff_str,mass_coeff_str,\
                            atom_bond_atom_inf[bond_atom1_id-1][bond_1_id],bond_atom1_id,\
                      bond_atom2_id,atom_bond_atom_inf[bond_atom2_id-1][bond_2_id],atom_inf)
                    creat_dihedral_inf.append([str(num_cross_dihedral),str(dihedral_type_vale),\
                            str(atom_bond_atom_inf[bond_atom1_id-1][bond_1_id]),str(bond_atom1_id),\
                            str(bond_atom2_id),str(atom_bond_atom_inf[bond_atom2_id-1][bond_2_id])])
    return creat_dihedral_inf
def make_improper_type(improper_atom_1,improper_atom_2,improper_atom_3,improper_atom_4):
    make_improper_type = mass_coeff_str[int(atom_inf[improper_atom_1-1][2])-1] + "-" +\
                         mass_coeff_str[int(atom_inf[improper_atom_2-1][2])-1] + "-" +\
                         mass_coeff_str[int(atom_inf[improper_atom_3-1][2])-1] + "-" +\
                         mass_coeff_str[int(atom_inf[improper_atom_4-1][2])-1]
    return make_improper_type
def get_improper_type(improper_coeff_str,mass_coeff_str,improper_atom1,improper_atom2,\
                      improper_atom3,improper_atom4,atom_inf):
    improper_1_type = make_improper_type(improper_atom1,improper_atom2,\
                                         improper_atom3,improper_atom4)
    improper_2_type = make_improper_type(improper_atom1,improper_atom2,\
                                         improper_atom4,improper_atom3)
    improper_3_type = make_improper_type(improper_atom3,improper_atom2,\
                                         improper_atom1,improper_atom4)
    improper_4_type = make_improper_type(improper_atom3,improper_atom2,\
                                         improper_atom4,improper_atom1)
    improper_5_type = make_improper_type(improper_atom4,improper_atom2,\
                                         improper_atom3,improper_atom1)
    improper_6_type = make_improper_type(improper_atom4,improper_atom2,\
                                         improper_atom1,improper_atom3)
    improper_type_inf = [improper_1_type,improper_2_type,improper_3_type,improper_4_type,\
                         improper_5_type,improper_6_type]
    if_improper_type = 0
    for num_improper_type in range(0,12):
        if improper_type_inf[num_improper_type] in improper_coeff_str:
            improper_type_valels = improper_coeff_str.index(improper_type_inf[num_improper_type])+1
            if_improper_type = 1
            break
    if if_improper_type == 0:
        print(improper_1_type)
        x
    return improper_type_valels   
def creat_improper(atom_inf,bond_inf,atom_bond_atom_inf,improper_coeff_str,mass_coeff_str):
    improper_inf_ls = []
    num_cross_improper = 0
    for atom_id in range(0,len(atom_inf)):
        if len(atom_bond_atom_inf[atom_id]) >= 3:
            for atom1_id in range(0,len(atom_bond_atom_inf[atom_id])-2):
                for atom2_id in range(atom1_id+1,len(atom_bond_atom_inf\
                                                    [atom_id])-1):
                    for atom3_id in range(atom2_id+1,len(atom_bond_atom_inf\
                                                         [atom_id])):
                        num_cross_improper = num_cross_improper + 1
                        improper_type_vale = get_improper_type(improper_coeff_str,\
                                mass_coeff_str,atom_bond_atom_inf[atom_id][atom1_id],\
                                                atom_id+1,atom_bond_atom_inf[atom_id][atom2_id],\
                                                    atom_bond_atom_inf[atom_id][atom3_id],atom_inf)
                        improper_inf_ls.append([str(num_cross_improper),str(improper_type_vale),\
                        str(atom_bond_atom_inf[atom_id][atom1_id]),str(atom_id+1),\
                        str(atom_bond_atom_inf[atom_id][atom2_id]),str(atom_bond_atom_inf[atom_id][atom3_id])])
    return improper_inf_ls
def change_data_num(out_data_inf,num_line,change_content,goal_content):
    if out_data_inf[num_line][1] == change_content:
            out_data_inf[num_line][0] = goal_content
def out_data_modify(out_data_inf,atom_inf,bond_cross_inf,angle_cross_inf,\
                            dihedral_cross_inf,improper_cross_inf):
    for num_line in range(0,len(out_data_inf)):
        one_line_add = [' ']*(13 - len(out_data_inf[num_line]))
        out_data_inf[num_line].extend(one_line_add)
        if num_line < 20 and out_data_inf[num_line][0] != ' ':
            change_data_num(out_data_inf,num_line,'atoms',len(atom_inf))
            change_data_num(out_data_inf,num_line,'bonds',len(bond_cross_inf))
            change_data_num(out_data_inf,num_line,'angles',len(angle_cross_inf))
            change_data_num(out_data_inf,num_line,'dihedrals',len(dihedral_cross_inf))
            change_data_num(out_data_inf,num_line,'impropers',len(improper_cross_inf))
def out_put_data(out_data_inf,out_data_name):
    with open(out_data_name, 'w') as INPUT_LAMMPS:
        for i in range(0,len(out_data_inf)):
            INPUT_LAMMPS.write("%s %s %s %s %s %s %s %s %s %s %s %s %s \n"%(\
              out_data_inf[i][0],out_data_inf[i][1],out_data_inf[i][2],out_data_inf[i][3],\
              out_data_inf[i][4],out_data_inf[i][5],out_data_inf[i][6],out_data_inf[i][7],\
              out_data_inf[i][8],out_data_inf[i][9],out_data_inf[i][10],out_data_inf[i][11],\
              out_data_inf[i][12]))
#---------------------------------------------------------------------------------------------------#
import os
import math
from mpi4py import MPI 
from lammps import lammps
import numpy as np
import random
lmp = lammps()
input_name = "in.puhcfc"#in文件名
initial_data = "su8oh.data"#初始data文件名
coeff_data_name = "coeff.data"#单独存放参数的文件名
max_loop_times = 100#最大交联循环次数
react_radius = 3.0  #初始交联截断半径
max_react_radius = 10.0#最大交联截断半径
react_radius_step = 0.5 #交联截断半径的增大步长
total_C1 = 336#初始体系中的C1原子数
cross_degree_goal = 0.8#小数表示，如0.8为80%交联
react_c1 = 0 #之前已经反应的C1原子数量，有时候交联后弛豫时可能会丢原子导致程序停止，
             #这时候需要让交联从断掉的地方接着跑，为了准确地计算交联度，需要把断掉
             #之前已经参加反应的C1原子也考虑进来，比如，断掉之前反应的C1原子数量为 
             #100，react_c1 = 100,初始状态时react_c1 = 0
c1_type = 9         
c3h_type = 6
oh_type = 10
ho_type = 11
hc_type = 8
c3_type = 3
oc_type = 4
c2_type = 5
c3h_c3h = 11
c3h_o3e = 12
c3h_c2 = 9
reacted_c1=[]
#me = MPI.COMM_WORLD.Get_rank()
#nprocs = MPI.COMM_WORLD.Get_size()
#print("Proc %d out of %d procs has"%(me,nprocs)),lmp
num_cross = react_c1 
for loop_times in range (0,max_loop_times):
    lmp.file("%s"%(input_name))
    lmp.command("write_data %s"%(initial_data))
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
    atom_infls = loadTuopu(initial_data,"atoms","Atoms")
    coeff_inf = loadcoeff(initial_data)
    atom_inf = sort_atom(atom_infls)
    bond_inf = loadTuopu(initial_data,"bonds","Bonds")
    angle_inf = loadTuopu(initial_data,"angles","Angles")
    dihedral_inf = loadTuopu(initial_data,"dihedrals","Dihedrals")
    improper_inf = loadTuopu(initial_data,"impropers","Impropers")
    atom_bond_inf,atom_bond_inf_all = atom_tuopu_allocate(atom_inf,bond_inf)
    atom_bond_atom_inf = atom_bond_atom(atom_inf,bond_inf)
    atom_angle_inf,atom_angle_inf_all = atom_tuopu_allocate(atom_inf,angle_inf)
    atom_dihedral_inf,atom_dihedral_inf_all = atom_tuopu_allocate(atom_inf,\
                                                                dihedral_inf)
    index_c1_carbon = get_atoms(c3h_type,atom_inf,atom_bond_inf,c3h_c2,bond_inf,\
                                c3h_c3h,atom_bond_inf_all,c3h_o3e)
    num_react = 0
    print("第%d次交联，交联截止半径为%f"%(loop_times+1,react_radius))
    for num_c1_1 in range(0,len(index_c1_carbon)):
        for num_c1_2 in range(num_c1_1+1,len(index_c1_carbon)):
            d_1_2 = check_distance(atom_inf,index_c1_carbon[num_c1_1][2],\
                            index_c1_carbon[num_c1_2][1],react_radius)
            if_reacted = check_reacted(reacted_c1,index_c1_carbon[num_c1_1][0],\
                            index_c1_carbon[num_c1_2][0])
            if_boundary = check_boundary(atom_inf,index_c1_carbon[num_c1_1-1][2],\
                            index_c1_carbon[num_c1_2][1])
            mmm = 0
            if d_1_2 == 1 and if_reacted == 1 and if_boundary == 1:
                mmm = 1
                cross_link(atom_inf,num_c1_1,num_c1_2,index_c1_carbon,ho_type,hc_type,c1_type,\
                            c3_type,oc_type,c2_type,oh_type,atom_bond_atom_inf)
                reacted_c1.append(index_c1_carbon[num_c1_1][0])
                reacted_c1.append(index_c1_carbon[num_c1_2][0])
    if num_cross < len(reacted_c1) / 2 + react_c1:
        num_cross = len(reacted_c1) / 2 + react_c1
        print("第%d次交联后，参与交联反应的c1数量为%d"%(loop_times+1,num_cross))
    else:
        print("第%d次交联后，参与交联反应的c1数量为%d"%(loop_times+1,num_cross))
        react_radius = react_radius + 0.5
        if react_radius > max_react_radius:
            print("最大反应半径已大于最大设定值%f"%(max_react_radius))
            break
    cross_degree = num_cross / total_C1
    if cross_degree >= cross_degree_goal:
        print()
        print("已达到目标交联度")
    if loop_times + 1 == max_loop_times:
        print()
        print("经过%d次循环后体系仍未达到目标交联度"%(loop_times + 1))
    bond_cross_inf = creat_bond(atom_bond_atom_inf,bond_coeff_str,mass_coeff_str,atom_inf)
    angle_cross_inf = creat_angle(atom_bond_atom_inf,angle_coeff_str,mass_coeff_str,atom_inf)
    dihedral_cross_inf = creat_dihedral(atom_bond_atom_inf,bond_cross_inf,dihedral_coeff_str,\
                                                   mass_coeff_str,atom_inf)
    improper_cross_inf = creat_improper(atom_inf,bond_cross_inf,atom_bond_atom_inf,\
                                         improper_coeff_str,mass_coeff_str)
    out_data_inf = []
    out_data_inf.extend(coeff_inf)
    out_data_inf.extend([['Atoms','#','full'],[]])
    out_data_inf.extend(atom_inf)
    out_data_inf.extend([['Bonds'],[]])
    out_data_inf.extend(bond_cross_inf)
    out_data_inf.extend([['Angles'],[]])
    out_data_inf.extend(angle_cross_inf)
    out_data_inf.extend([['Dihedrals'],[]])
    out_data_inf.extend(dihedral_cross_inf)
    out_data_inf.extend([['Impropers'],[]])
    out_data_inf.extend(improper_cross_inf)
    out_data_modify(out_data_inf,atom_inf,bond_cross_inf,angle_cross_inf,\
                            dihedral_cross_inf,improper_cross_inf)
    out_data_name = "su8_after_cross_" + str(cross_degree) + ".data"
    out_put_data(out_data_inf,out_data_name)
    out_put_data(out_data_inf,initial_data)
    lmp.command("clear")
#nprocs = MPI.COMM_WORLD.Get_size()
#print "Proc %d out of %d procs has" % (me,nprocs),lmp
#MPI.Finalize()
