  # -*- coding: UTF-8 -*-
###从指定的文件中读取拓扑数据
#这段代码定义了一个名为loadTuopu的函数，该函数需要三个参数tuopuguiji1、tuoputype1 和 tuoputype2。函数的主要功能是从指定文件中读取数据并返回一个列表。
#具体地，函数打开名为tuopuguiji1的文件，并逐行读取其中的内容。对于每一行，函数将其按空格分割成多个字段，并对字段进行处理。
#如果字段数量大于 1 并且第二个字段的值等于变量tuoputype1的值，则将第一个字段的值转换为整数并存储到变量numtuopu 中。如果第一个字段的值等于变量 
#tuoputype2 的值，则将变量tuopupanduan 的值设为 1。
#如果变量 tuopupanduan 的值为 1 并且第一个字段的值不等于变量 tuoputype2 的值且该行不为空，则将该行数据添加到列表 tuopuinfls 中。
#当 tuopuinfls 列表长度等于变量 numtuopu 的值时，函数停止读取文件，返回 tuopuinfls 列表。
def loadTuopu(tuopuguiji1,tuoputype1,tuoputype2):######在572行这，这个函数体中def data_check(out_data_name,str1,str2,num_tuopu):
    inFile = open(tuopuguiji1, 'r') #这行代码打开了一个名为 tuopuguiji1 的文件，并将其分配给变量 inFile，使用'r' 参数表示以只读模式打开该文件。在Python中，open()函数用于打开文件，并返回一个文件对象，可以使用该对象执行各种文件操作，如读取、写入等。
    tuopuinfls = [] #这行代码创建了一个空的列表tuopuinfls，用于存储后续从文件中读取的数据。
    numline = 0 #这行代码定义了一个名为numline 的变量，并将其初始化为整数0。
    numtuopu = 1000000 #这行代码将变量numtuopu 的初始值设为 1000000（一百万）。
    tuopupanduan = 0 #这行代码定义了一个名为tuopupanduan的变量，并将其初始化为整数0。
    for line in inFile: #这行代码通过循环逐行读取文件inFile 中的内容，每次处理一行。
        trainingSetls = line.split(' ') #这段代码将字符串变量 line 按照空格分隔符进行切割，并将分割后的结果存储在一个列表（list）类型的变量 trainingSetls 中。
        #换句话说，该代码将 line 中的内容以空格为界，拆分成多个子串，并将这些子串组成的列表赋值给变量 trainingSetls。
        ### line.中.的意思？
        numline = numline + 1 #这行代码的作用是将变量numline 的值加一。具体来说，它会先获取当前numline变量的值，然后将其加一，并将结果重新赋值给numline变量。
        #这可以用于在程序中跟踪处理文件或数据集中的行数等计数任务。
        lenyh = len(trainingSetls) #这行代码将列表变量trainingSetls中元素的数量（即列表长度）计算并赋值给变量lenyh。
        trainingSetls[lenyh-1] = trainingSetls[lenyh-1][0:\
                                (len(trainingSetls[lenyh-1])-1)] #这段代码将 trainingSetls列表中的最后一个元素的最后一个字符删除。具体过程是先获取trainingSetls 的长度，
        #并将其存储在变量lenyh 中；然后通过下标索引获取到最后一个元素，再使用切片操作[0:(len(trainingSetls[lenyh-1])-1)]，即从第 0 个字符开始，删除到倒数第二个字符，最后将其更新回原来的位置
        trainingSet = [] #这行代码创建了一个空列表trainingSet，用于存储训练集数据。
        for num_data in range(0,len(trainingSetls)): #这段代码使用 for 循环对trainingSetls 列表进行迭代，从第一个元素开始到最后一个元素结束。
            #在循环的每一次迭代中，会将当前元素的索引存储在num_data 变量中，以便在循环体内访问和处理。
            if trainingSetls[num_data] != '':
                trainingSet.append(trainingSetls[num_data]) #这段代码会遍历列表trainingSetls中的每个元素，如果当前元素不为空字符串，则将其添加到新列表trainingSet中。
                #换句话说，它会过滤掉原列表中的空字符串，生成一个仅包含非空元素的新列表
        if trainingSet == []:
            trainingSet.append('') #这段代码会检查trainingSet列表是否为空。如果是，则向其中添加一个空字符串，否则不执行任何操作。这通常用于确保某些代码在处理空列表时不会出错。
        if len(trainingSet) > 1:
            if str(trainingSet[1]) == str(tuoputype1):
                numtuopu = int(trainingSet[0]) #如果trainingSet 列表的长度大于1，那么就执行以下操作：如果trainingSet 中第二个元素的字符串形式等于变量tuoputype1 的字符串形式，
                #则将trainingSet 中第一个元素转换为整数并赋值给变量numtuopu
        if str(trainingSet[0]) == str(tuoputype2):
            tuopupanduan = 1 #这段代码会判断trainingSet 列表的第一个元素是否等于tuoputype2 变量，如果相等则将tuopupanduan 变量赋值为 1
        if tuopupanduan == 1 and str(trainingSet[0]) != str(tuoputype2) \
           and trainingSet != ['']:
            tuopuinfls.append(trainingSet) #如果tuopupanduan为1且trainingSet[0]不等于tuoputype2并且trainingSet不是空列表，则将trainingSet添加到tuopuinfls列表中
        if len(tuopuinfls) == numtuopu: 
            break  # 此代码用于在 Python 中的循环语句中检查列表tuopuinfls 的长度是否等于变量numtuopu 的值。如果相等，则跳出循环并停止执行后续代码                       
    return tuopuinfls #这段代码返回变量tuopuinfls 的值。
###这个函数的作用是从指定的文件中读取拓扑系数数据，并返回一个包含拓扑系数信息的列表。
  # 具体来说，函数会打开一个文件，逐行读取文件中的内容，将每行数据按空格分割成一个列表，
  # 然后根据数据的内容进行过滤，将符合条件的数据添加到一个列表中，最终返回这个列表。
  #这段代码定义了一个名为loadcoeff 的函数，函数的输入参数是一个字符串tuopuguiji1。函数的主要作用是读取文件中的数据，并将其转换为列表形式返回。
  # 具体来说，该函数首先以只读方式打开指定的文件（文件路径存储在tuopuguiji1 中），并初始化一些变量。
  # 然后，它循环遍历文件中的每一行，将其按空格分隔成单个数据，并去除末尾的换行符。接着，它将所有非空数据组成一个列表，再将该列表添加到名为tuopuinfls 的列表中，表示读取到的数据。
  # 遇到特定标识符Atoms 后，该函数就会结束循环并返回tuopuinfls 列表。
def loadcoeff(tuopuguiji1):###在683行，在for循环体中for loop_times in range (0,max_loop_times):
    inFile = open(tuopuguiji1, 'r') #这行代码打开一个文件，文件名是变量tuopuguiji1 所代表的字符串，以只读模式（'r'）打开。它将返回一个文件对象，程序可以使用该对象对文件进行读取操作
    tuopuinfls = [] #这段代码创建了一个空列表tuopuinfls，该列表可以用于存储数据或其他信息
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
                break   #这段代码检查trainingSet是否为空列表，如果不是空列表，则检查该列表的第一个元素是否为字符串'Atoms'。如果是，则跳出当前的for 循环
        tuopuinfls.append(trainingSet)                            
    return tuopuinfls

####这个函数的作用是从指定的文件中读取数据，并将数据按行分割成一个列表，最终返回这个列表。
  # 具体来说，函数会打开一个文件，逐行读取文件中的内容，将每行数据按空格分割成一个列表，
  # 然后将这个列表添加到一个大列表中，最终返回这个大列表。
#这是一个Python函数，名为loadcheck。它打开一个文件（文件名由参数tuopuguiji1指定），将其读入内存中，并将每一行拆分成一个列表，
# 然后将所有的列表添加到一个名为tuopuinfls的列表中。最后，它返回tuopuinfls列表。
def loadcheck(tuopuguiji1):###在586行def data_check2(out_data_name):
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
        tuopuinfls.append(trainingSet)                            
    return tuopuinfls
#allocate_coeff(coeff_all): 这个函数的作用是从输入的列表 coeff_all 中提取出每个元素的最后一个值，
  # 并将这些值组成一个新的列表 coeff_str 并返回。该函数的作用是将 coeff_all 列表中每个元素的最后一个值提取出来。
#这段代码定义了一个名为allocate_coeff的函数，该函数接受一个参数coeff_all。在函数中，它使用一个for循环来遍历coeff_all中的
# 每个成员并提取它们的最后一个元素，将这些元素添加到名为coeff_str的列表中，并返回coeff_str。
def allocate_coeff(coeff_all):##在for循环体中,for loop_times in range (0,max_loop_times):
    coeff_str = []
    for num_coeff in range(0,len(coeff_all)):
        coeff_str.append(coeff_all[num_coeff][len(coeff_all[num_coeff])-1]) 
        # 这段代码使用一个for循环，遍历了名为coeff_all的列表中的所有元素，并将每个元素的最后一个字符提取出来，并添加到名为coeff_str的空列表中。
        # 因此，最终coeff_str将包含与coeff_all相同数量的元素，但是这些元素都只是原先元素的最后一个字符
    return coeff_str

###sort_atom(atom_infls): 这个函数的作用是对输入的列表 atom_infls 中的元素进行排序，
  # 并返回排序后的列表 atom_inflsls。
  # 该函数的作用是对 atom_infls 列表中的元素按照第一个值进行排序。
  #这段代码定义了一个名为sort_atom 的函数，它接受一个参数 atom_infls。函数首先创建了一个空列表 atom_inflsls，然后使用两个 for 循环将原始列表
  # atom_infls 中的元素按照其第一个值（整数）进行排序并存储到 atom_inflsls 中。最后返回排好序的列表 atom_inflsls

def sort_atom(atom_infls):#还是for循环体中
    atom_inflsls = []
    for atom_id in range(0,len(atom_infls)): #这段代码创建了一个空列表atom_inflsls，并将其长度设置为和输入的atom_infls相同，
        #并用循环逐个添加空列表元素到atom_inflsls中。整个过程中，atom_inflsls列表中的每个元素都是一个空列表。
        atom_inflsls.append([])
    for atom_id in range(0,len(atom_infls)): #这段代码通过循环迭代atom_infls列表中的元素，对其中每个子列表的第一个元素进行整数转换，
        #并将其作为下标存储到新创建的列表atom_inflsls的对应位置。具体来说，如果原列表中第k个子列表的第一个元素为n，
        # 则在新列表atom_inflsls的第n-1个位置存储这个子列表。最终返回排序后的atom_inflsls列表。
        atom_id_vale = int(atom_infls[atom_id][0])
        atom_inflsls[atom_id_vale-1] = atom_infls[atom_id]
    return atom_inflsls

###select_coord(atom_inf): 这个函数的作用是从输入的列表 atom_inf 中提取出每个元素的第四、五、六个值，
  # 并将这些值组成一个新的列表 coord_infls 并返回。
  # 该函数的作用是将 atom_inf 列表中每个元素的第四、五、六个值提取出来。
  #这段代码定义了一个函数select_coord，其输入参数为atom_inf，表示原子信息列表。函数首先创建一个名为coord_infls的空列表，
  # 然后遍历原子信息列表中的每个原子坐标，并将其坐标值（第4、5和6个元素）以浮点数类型添加到coord_infls列表中。 最后返回coord_infls列表。
  # 因此，该函数的作用是从原子信息列表中提取出所有的原子坐标。
def select_coord(atom_inf):
    coord_infls = []
    for atom_coord_id in range(0,len(atom_inf)):
        coord_infls.append(float(atom_inf[atom_coord_id][4]))
        coord_infls.append(float(atom_inf[atom_coord_id][5]))
        coord_infls.append(float(atom_inf[atom_coord_id][6]))
    return coord_infls
##int_bond(bond_inf): 这个函数的作用是将输入的列表 bond_inf 中的元素转换成整数，
  # 并将转换后的元素组成一个新的列表 bondls 并返回。
  # 该函数的作用是将 bond_inf 列表中的元素转换成整数类型。
  #这段代码定义了一个函数int_bond，它的作用是将输入的二维列表 bond_inf 中的所有元素转换为整数，并返回一个一维列表 bondls。具体实现过程如下：
  # 创建一个空列表 bondls通过两个嵌套的 for 循环遍历 bond_inf 的所有元素，将每个元素转换成整数并添加到 bondls 中返回 bondls 列表
def int_bond(bond_inf):
    bondls = []
    for bond_inf_id in range(0,len(bond_inf)):
        for one_bond_inf_id in range(0,len(bond_inf[bond_inf_id])):
            bondls.append(int(bond_inf[bond_inf_id][one_bond_inf_id]))
    return bondls
##这个函数的作用是将原子和拓扑信息进行关联，并返回两个列表 atom_tuopu_inf 和 atom_tuopu_inf_all。
##具体来说，函数接受两个输入参数：atom_inf 和 tuopu_inf，分别表示原子信息列表和拓扑信息列表。
  ##函数首先创建两个空列表 atom_tuopu_inf 和 atom_tuopu_inf_all，用于存储原子和拓扑信息的关联结果。
  ###然后，通过两个 for 循环，遍历拓扑信息列表中的每个元素，并将拓扑信息与对应的原子信息相关联。
  ###具体来说，对于每个拓扑信息，函数会将其第二个元素的值转换成整数，
  # 并将拓扑信息中剩余的所有元素所表示的原子编号添加到 atom_tuopu_inf 列表中的对应位置。
  # 同时，函数还会将整个拓扑信息添加到 atom_tuopu_inf_all 列表中的对应位置。
  # 最后，函数返回两个列表 atom_tuopu_inf 和 atom_tuopu_inf_all，分别表示原子和拓扑信息的关联结果。
#这段代码定义了一个函数atom_tuopu_allocate，它的作用是对原子信息和拓扑信息进行处理，返回两个列表。具体实现过程如下：
# 首先，创建两个空列表atom_tuopu_inf和atom_tuopu_inf_all。然后，通过for循环遍历原子信息列表atom_inf中的每一个元素，为atom_tuopu_inf和atom_tuopu_inf_all
# 添加一个空列表。接着，通过for循环遍历拓扑信息列表tuopu_inf中的每一个元素，获取其中第二个元素，并将其转换成整型变量tuopu_type_vale。
# 在第二个for循环中，再次通过for循环遍历tuopu_inf中的每一个元素中从第三个元素开始的元素，将其中每一个对应原子编号所在的位置的atom_tuopu_inf列表中添加上tuopu_type_vale。
# 同时，将相同的信息添加到atom_tuopu_inf_all列表中。最后，返回两个列表atom_tuopu_inf和atom_tuopu_inf_all。
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
##这个函数的作用是将原子类型为 ch3_type 且与原子编号为 c3h_c2 的原子相连接的原子的类型改为 c1_vale。
  # 具体来说，函数接受五个输入参数：atom_inf、ch3_type、c1_vale、c3h_c2 和 atom_bond_inf，
  # 分别表示原子信息列表、CH3 基团的类型、C1 基团的类型、连接 C3H 和 C2 的原子的编号以及原子间键的信息列表。
  # 函数通过一个 for 循环，遍历原子信息列表中的每个元素。
  # 对于类型为 ch3_type 的原子，如果它与原子编号为 c3h_c2 的原子相连接，则将其类型改为 c1_vale。
  # 最后，函数不返回值，而是直接修改了输入的原子信息列表 atom_inf。
def change_c1_type(atom_inf,ch3_type,c1_vale,c3h_c2,atom_bond_inf):
    for atom_id in range(0,len(atom_inf)):
        atom_type_vale = int(atom_inf[atom_id][2])
        if atom_type_vale == ch3_type:
            if c3h_c2 in atom_bond_inf[atom_id]:
                atom_inf[atom_id][2] = str(c1_vale)
##这个函数的作用是从一个包含分子体系原子坐标的列表中提取指定原子的坐标，并将其返回。具体来说，函数接受三个参数：
    # index_of_atom：需要提取坐标的原子在原子列表中的索引
    # coord：包含所有原子坐标的列表
  # lmp：一个未使用的参数，可能是该函数原本设计时的一个参数，
  # 但在这里没有用到函数内部首先根据原子的索引计算出其在 coord 列表中对应的起始位置 a。
  # 然后，它创建一个长度为 3 的空列表 target_atom_coord，用于存储目标原子的坐标。
  # 接下来，函数使用一个循环，将 coord 列表中从 a 开始的连续三个元素，即目标原子的三个坐标值，
  # 分别存储到 target_atom_coord 列表的三个位置上。最后，函数将 target_atom_coord 列表返回，即为指定原子的坐标。
def atom_coord(index_of_atom,coord,lmp):
	a=3 * (index_of_atom - 1)                     
	a=int(a)                              
	target_atom_coord=[0]*3
	for i in range (3):
		target_atom_coord[i]=coord[a+i]   	
	return target_atom_coord
#这个函数的作用是从一个包含原子信息的列表中提取原子类型，并将其返回。
  # 具体来说，函数接受一个参数：atom_inf：包含所有原子信息的列表，每个元素为一个包含原子信息的列表，
  # 其中第三个元素为原子类型函数内部首先创建一个空列表 atom_type_infls，用于存储所有原子的类型。
  # 然后，函数使用一个循环遍历 atom_inf 列表中的所有元素。对于每个元素，
  # 函数提取其中第三个元素（即原子类型）并将其转换为整数类型，然后将其添加到 atom_type_infls 列表的末尾。
  # 最后，函数将 atom_type_infls 列表返回，即为所有原子的类型。
def get_atoms_type(atom_inf):
    atom_type_infls = []
    for atom_type_id in range(0,len(atom_inf)):
        atom_type_infls.append(int(atom_inf[atom_type_id][2]))
    return atom_type_infls

##这个函数的作用是从一个包含原子和键信息的列表中提取指定类型的原子及其相关信息，并将其返回。
##函数内部首先创建一个空列表 get_atom_inf，用于存储符合要求的原子及其相关信息。
  # 然后，函数使用一个循环遍历 atom_inf 列表中的所有元素。
  # 对于每个元素，函数提取其中第三个元素（即原子类型）并将其转换为整数类型，
  # 如果该类型与 number_of_attribute 相同，且该原子与类型为 c3h_c2 的原子之间有键，
  # 则将该原子的编号添加到 get_atom_inf 列表中。接下来，函数使用两个嵌套的循环，
  # 遍历 get_atom_inf 列表中的所有元素及其相关的键信息。对于每个元素，函数首先提取其中的原子编号，并将其转换为整数类型。
  # 然后，函数遍历该原子与其他原子之间的所有键信息，如果有一条键连接了该原子与类型为 c3h_c3h 的原子，
  # 则将该键连接的另一个原子的编号添加到 get_atom_inf 列表中该元素的末尾；
  # 如果有一条键连接了该原子与类型为 c3h_o3e 的原子，则将该键连接的另一个原子的编号添加到 get_atom_inf 列表中该元素的末尾。
  # 最后，函数将 get_atom_inf 列表返回，即为所有符合要求的原子及其相关信息。
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
##这个函数的作用是检查两个原子之间的距离是否小于等于给定的反应半径，如果是，则返回 1，否则返回 0。
##函数内部首先创建一个变量 react_distance 并将其初始化为 0，用于存储两个原子之间距离是否小于等于反应半径。
  # 然后，函数分别从 atom_inf 列表中提取出两个原子的 x、y、z 坐标，并计算它们之间的距离 d。
  # 接下来，函数判断 d 是否小于等于反应半径，如果是，则将 react_distance 的值设为 1。
  # 最后，函数将 react_distance 的值返回，即为两个原子之间距离是否小于等于反应半径的判断结果。
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
##函数 check_reacted(reacted_c1,c1_id_1,c1_id_2) 的作用是检查两个 C1 原子是否都没有参与过反应，
  # 如果是，则返回 1，否则返回 0。
  # 函数内部首先创建一个变量 if_reacted_ls 并将其初始化为 0，
  # 用于存储两个 C1 原子是否都没有参与过反应的判断结果。
  # 然后，函数判断 c1_id_1 和 c1_id_2 是否都不在 reacted_c1 列表中，
  # 如果是，则将 if_reacted_ls 的值设为 1。最后，函数将 if_reacted_ls 的值返回，即为两个 C1 原子是否都没有参与过反应的判断结果。
def check_reacted(reacted_c1,c1_id_1,c1_id_2):
    if_reacted_ls = 0
    if c1_id_1 not in reacted_c1 and c1_id_2 not in reacted_c1:
        if_reacted_ls = 1
    return if_reacted_ls
##函数 check_boundary(atom_inf,atom_id_1,atom_id_2) 的作用是检查两个原子是否在同一晶胞内，如果是，则返回 1，否则返回 0。
  # 函数内部首先创建一个变量 if_boundary_ls 并将其初始化为 0，用于存储两个原子是否在同一晶胞内的判断结果。
  # 然后，函数分别从 atom_inf 列表中提取出两个原子所在晶胞的编号，并比较它们是否相同。
  # 如果两个原子在同一晶胞内，则将 if_boundary_ls 的值设为 1。最后，函数将 if_boundary_ls 的值返回，即为两个原子是否在同一晶胞内的判断结果。
def check_boundary(atom_inf,atom_id_1,atom_id_2):
    if_boundary_ls = 0
    if int(atom_inf[atom_id_1-1][7]) == int(atom_inf[atom_id_2-1][7]) and \
       int(atom_inf[atom_id_1-1][8]) == int(atom_inf[atom_id_2-1][8]) and \
       int(atom_inf[atom_id_1-1][9]) == int(atom_inf[atom_id_2-1][9]):
        if_boundary_ls = 1
    return if_boundary_ls
##这个函数的作用是更改原子所在分子的编号，使得编号较大的分子编号变更为编号较小的分子编号。
  # 函数内部首先根据两个分子编号的大小比较，选择较小的分子编号作为目标分子，较大的分子编号作为需要更改的分子。
  # 然后，函数创建一个空列表 atom_mol_collect，用于存储所有原子所在分子的编号，并将需要更改的分子的编号修改为目标分子的编号。
  # 接下来，函数遍历 atom_inf 列表中的所有元素，对于每个元素，
  # 如果其分子编号为需要更改的分子的编号，就将其分子编号修改为目标分子的编号，
  # 并将该原子所在分子的编号添加到 atom_mol_collect 列表中，以便后续更新所有原子分子编号的顺序。
  # 接着，函数对 atom_mol_collect 列表进行排序，并再次遍历 atom_inf 列表中的所有元素，
  # 对于每个元素，将其分子编号更新为 atom_mol_collect 列表中该分子编号的索引加 1，
  # 即为该分子在所有分子中的排序位置，最后将更新后的 atom_inf 列表返回。
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
##这个函数的作用是通过创建两个新的原子，将两个碳原子之间的碳-碳双键转化为酯键。
##
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

#这个函数的作用是根据两个原子之间的化学键类型和原子质量信息，从 bond_coeff_str 和 mass_coeff_str 中获取化学键类型的编号。
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
        print(bond_1_type)
        x
    return bond_type_valels

####这个函数的作用是根据原子之间的化学键信息和化学键类型，生成新的化学键信息。
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
#

  ##这个函数的作用是根据三个原子之间的角度和原子质量信息，从 angle_coeff_str 和 mass_coeff_str 中获取角度类型的编号
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


####这个函数的作用是根据原子之间的化学键信息和角度类型，生成新的角度信息
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

###这个函数的作用是根据四个原子之间的二面角和原子质量信息，从 dihedral_coeff_str 和 mass_coeff_str 中获取二面角类型的编号。
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
    if dihedral_type_valels == 64:
        print(dihedral_1_type)
        print(dihedral_coeff_str)
        x
    return dihedral_type_valels

###这个函数的作用是根据原子之间的化学键信息和二面角类型，生成新的二面角信息。
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


#####这个函数的作用是根据四个原子的质量信息，生成一个表示不当二面角类型的字符串
def make_improper_type(improper_atom_1,improper_atom_2,improper_atom_3,improper_atom_4):
    make_improper_type = mass_coeff_str[int(atom_inf[improper_atom_1-1][2])-1] + "-" +\
                         mass_coeff_str[int(atom_inf[improper_atom_2-1][2])-1] + "-" +\
                         mass_coeff_str[int(atom_inf[improper_atom_3-1][2])-1] + "-" +\
                         mass_coeff_str[int(atom_inf[improper_atom_4-1][2])-1]
    return make_improper_type

####这个函数的作用是根据四个原子之间的不当二面角和原子质量信息，从 improper_coeff_str 和 mass_coeff_str 中获取不当二面角类型的编号
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

####这个函数的作用是根据原子之间的化学键信息和不当二面角类型，生成新的不当二面角信息。
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

##change_data_num 函数：根据行号、要修改的内容和目标内容，修改输出数据中的指定行的内容。
def change_data_num(out_data_inf,num_line,change_content,goal_content):
    if out_data_inf[num_line][1] == change_content:
            out_data_inf[num_line][0] = goal_content
###out_data_modify 函数：将输出数据的每行长度扩展到 13，
  # 然后根据输入的原子、化学键、角度、二面角和不当二面角信息，
  # 调用 change_data_num 函数，更新输出数据中的相应行
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
##out_put_data 函数：将输出数据写入指定文件中。
def out_put_data(out_data_inf,out_data_name):
    with open(out_data_name, 'w') as INPUT_LAMMPS:
        for i in range(0,len(out_data_inf)):
            INPUT_LAMMPS.write("%s %s %s %s %s %s %s %s %s %s %s %s %s \n"%(\
              out_data_inf[i][0],out_data_inf[i][1],out_data_inf[i][2],out_data_inf[i][3],\
              out_data_inf[i][4],out_data_inf[i][5],out_data_inf[i][6],out_data_inf[i][7],\
              out_data_inf[i][8],out_data_inf[i][9],out_data_inf[i][10],out_data_inf[i][11],\
              out_data_inf[i][12]))
##data_check 函数：检查输出数据文件中的拓扑信息是否正确，如果有问题则重新生成输出数据文件。
def data_check(out_data_name,str1,str2,num_tuopu):
    tuopu_check_ls = 0
    tuopu_check_inf = loadTuopu(out_data_name,str1,str2)
    for num_tuopu_id in range(0,len(tuopu_check_inf)):
        if len(tuopu_check_inf[num_tuopu_id]) != num_tuopu:
            tuopu_check_ls = 1
    if tuopu_check_ls == 0:
        print("%s检查完成，未发现问题"%(str1))
    else:
        print("%s部分输出内容错乱，重新输出data"%(str1))
    return tuopu_check_ls
##这个函数的作用是检查输出数据文件中是否存在多余的行。
def data_check2(out_data_name):
    if_have_useless_pd = 0
    check_inf_all = loadcheck(out_data_name)
    check_inf_slice = check_inf_all[len(check_inf_all)-100:len(check_inf_all)]
    #improper_last = improper_check_inf[len(improper_check_inf)-1]
    ##improper_last.extend([' ']*7)
    #m = out_data_inf.index(improper_last) + 1
    for num_check in range(0,len(check_inf_slice)):
        if len(check_inf_slice[num_check]) != 6:
            if check_inf_slice[num_check] != []:
                print(check_inf_slice[num_check])
                if_have_useless_pd = 1
    """
    if m < len(out_data_inf):
        for num_line in range(m,len(out_data_inf)):
            for num_line_data in range(0,len(out_data_inf[num_line])):
                if out_data_inf[num_line][num_line_data] != ' ':
                    if_have_useless_pd = 1
    """
    if if_have_useless_pd == 0:
        print("data中未发现多余内容")
    else:
        print("data文件中发现多余内容，重新输出data")
    return if_have_useless_pd

####这个函数的作用是替换输入文件中的指定字符串
def alter_in_data(in_file_name,in_file_new,old_str,new_str):
    file_data = ""
    with open(in_file_name,"r",encoding = "utf-8") as f:
        for line in f:
            if old_str in line:
                line = line.replace(old_str,new_str)
            file_data += line
    with open(in_file_new,"w",encoding = "utf-8") as f:
        f.write(file_data)
#---------------------------------------------------------------------------------------------------#
import os
import math
#from mpi4py import MPI 
#from lammps import lammps
import numpy as np
import random
import subprocess
#lmp = lammps()
input_name = "in.puhcfc"#in文件名
input_name_last = "in.puhcfc2"#用于最后弛豫达到目标交联度data的in文件名
data_name_input_last = "cross_degree.data"#用于最后弛豫达到目标交联度data的in文件
                                          #中read_data 的data文件名
initial_data = "su820pcff.data"#初始data文件名
coeff_data_name = "coeffpcff.data"#单独存放参数的文件名
max_loop_times = 150#最大交联循环次数
react_radius = 3.0  #初始交联截断半径
max_react_radius = 12.5#最大交联截断半径
react_radius_step = 0.5 #交联截断半径的增大步长
total_C1 = 158#初始体系中的C1原子数
cross_degree_goal = 1.0#小数表示，如0.8为80%交联度
react_c1 = 0 #之前已经反应的C1原子数量，有时候交联后弛豫时可能会丢原子导致程序停止，
             #这时候需要让交联从断掉的地方接着跑，为了准确地计算交联度，需要把断掉
             #之前已经参加反应的C1原子也考虑进来，比如，断掉之前反应的C1原子数量为 
             #100，react_c1 = 100,初始状态时react_c1 = 0
num_cpu = 24#计算的核数
c1_type = 9         
c3h_type = 7
oh_type = 11
ho_type = 10
hc_type = 2
c3_type = 6
oc_type = 3
c2_type = 5
c3h_c3h = 11
c3h_o3e = 12
c3h_c2 = 8
reacted_c1=[]
#me = MPI.COMM_WORLD.Get_rank()
#nprocs = MPI.COMM_WORLD.Get_size()
#print("Proc %d out of %d procs has"%(me,nprocs)),lmp
print("计算的核数为%d"%(num_cpu))
num_cross = react_c1
for loop_times in range (0,max_loop_times):
    command = "mpirun -np %d /home/msi/lammps-23Jun2022/src/lmp_mpi < %s"%(num_cpu,input_name)
    back = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,\
             stderr=subprocess.PIPE).communicate()
    print("back0----", back[0].decode())
    print("back1----", back[1].decode())
    #lmp.file("%s"%(input_name))
    #lmp.command("write_data %s"%(initial_data))
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
    print("第%d次交联，交联截止半径为%f"%(loop_times+1,react_radius))
    for num_c1_1 in range(0,len(index_c1_carbon)):
        for num_c1_2 in range(num_c1_1+1,len(index_c1_carbon)):
            d_1_2 = check_distance(atom_inf,index_c1_carbon[num_c1_1][2],\
                            index_c1_carbon[num_c1_2][1],react_radius)
            if_reacted = check_reacted(reacted_c1,index_c1_carbon[num_c1_1][0],\
                            index_c1_carbon[num_c1_2][0])
            if_boundary = check_boundary(atom_inf,index_c1_carbon[num_c1_1-1][2],\
                            index_c1_carbon[num_c1_2][1])
            if d_1_2 == 1 and if_reacted == 1 and if_boundary == 1:
                cross_link(atom_inf,num_c1_1,num_c1_2,index_c1_carbon,ho_type,hc_type,c1_type,\
                            c3_type,oc_type,c2_type,oh_type,atom_bond_atom_inf)
                reacted_c1.append(index_c1_carbon[num_c1_1][0])
                reacted_c1.append(index_c1_carbon[num_c1_2][0])
    if num_cross < len(reacted_c1) + react_c1:#去掉/2
        num_cross = len(reacted_c1) + react_c1#去掉/2
        print("第%d次交联后，参与交联反应的c1数量为%d"%(loop_times+1,num_cross))
    else:
        print("第%d次交联后，参与交联反应的c1数量为%d"%(loop_times+1,num_cross))
        react_radius = react_radius + react_radius_step
        if react_radius > max_react_radius:
            print("最大反应半径已大于最大设定值%f"%(max_react_radius))
            break
    cross_degree = num_cross / total_C1
    if loop_times + 1 == max_loop_times:
        print()
        print("经过%d次循环后体系仍未达到目标交联度"%(loop_times + 1))
        print()
    bond_cross_inf = creat_bond(atom_bond_atom_inf,bond_coeff_str,mass_coeff_str,atom_inf)
    angle_cross_inf = creat_angle(atom_bond_atom_inf,angle_coeff_str,mass_coeff_str,atom_inf)
    dihedral_cross_inf = creat_dihedral(atom_bond_atom_inf,bond_cross_inf,dihedral_coeff_str,\
                                                   mass_coeff_str,atom_inf)
    dihedral_type_collect = []
    #for i in range(0,len(dihedral_cross_inf)):
        #if int(dihedral_cross_inf[i][1]) not in dihedral_type_collect:
            #dihedral_type_collect.append(int(dihedral_cross_inf[i][1]))
    #print(len(dihedral_type_collect))
    #print(dihedral_type_collect)
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
    out_data_name = "su8pcff_after_cross_" + str(cross_degree) + ".data"
    for check_id in range(0,max_loop_times):
        print("第%d次检查%s......"%(check_id+1,out_data_name))
        print()
        out_put_data(out_data_inf,out_data_name)
        #for num_useless in range(0,1000):
            #out_put_data(out_data_inf,"out_data_useless.data")
        bond_check_vale = data_check(out_data_name,"bonds","Bonds",4)
        angle_check_vale = data_check(out_data_name,"angles","Angles",5)
        dihedral_check_vale = data_check(out_data_name,"dihedrals","Dihedrals",6)
        improper_check_vale = data_check(out_data_name,"impropers","Impropers",6)
        if_have_useless_inf = data_check2(out_data_name)
        if bond_check_vale == 0 and angle_check_vale == 0 and dihedral_check_vale == 0 \
           and improper_check_vale == 0 and if_have_useless_inf == 0:
            print("对%s检查完成，未发现问题"%(out_data_name))
            break
        else:
            for num_useless in range(0,1000):
                out_put_data(out_data_inf,"out_data_useless.data")
            print("重新输出data")
    #out_put_data(out_data_inf,initial_data)
    input_name_new = input_name[0:9] + "_"\
                                       "_" + str(loop_times+1)
    alter_in_data(input_name,input_name,initial_data,out_data_name)
    initial_data = out_data_name
    if cross_degree >= cross_degree_goal:
        print()
        print("已达到目标交联度")
        print("对最后的交联data进行弛豫________")
        alter_in_data(input_name_last,input_name_last,\
                        data_name_input_last,initial_data)
        command = "mpirun -np %d /home/msi/lammps-23Jun2022/src/lmp_mpi < %s"\
                              %(num_cpu,input_name_last)
        back = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,\
             stderr=subprocess.PIPE).communicate()
        print("back0----", back[0].decode())
        print("back1----", back[1].decode())
        break
    #input_name = input_name_new
    #lmp.command("clear")
#nprocs = MPI.COMM_WORLD.Get_size()
#print "Proc %d out of %d procs has" % (me,nprocs),lmp
#MPI.Finalize()
