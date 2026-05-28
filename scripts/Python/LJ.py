from decimal import Decimal
import math as m
pair = open('pair.txt','w')
lj=[['1','0.527', '2.321','Fe'],
    ['2','0.0175','3.826','Si'],
    ['3','0.00994','2.25','Mn'],
    ['4','0.502','2.336','Cr'],
    ['5','0.520','2.282','Ni'],
    ]
for i in range(len(lj)):
    for j in range(len(lj)):
        if(i <= j):         
            epsilon=(m.sqrt(float(lj[i][1])*float(lj[j][1])))
            epsilon=Decimal(epsilon).quantize(Decimal("0.0000"))
            sigma=m.sqrt(float(lj[i][2])*float(lj[j][2]))
            sigma=Decimal(sigma).quantize(Decimal("0.0000"))
            line = 'pair_coeff'+' '+str(i+1)+' '+str(j+1)+' '+'lj/cut'+' ' \
                +str(epsilon)+' '+str(sigma) +' #'+str(lj[i][3])+'-'+str(lj[j][3])+'\n'
            pair.write(line)
pair.close()