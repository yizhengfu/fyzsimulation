#!/usr/bin/python3
 
print("Hello, World!")
print('word')
print(520)
print('hellow')
fp=open('D:/try.txt','a+')
print('hellow',file=fp)
fp.close()
import keyword
print(keyword.kwlist)
name="word"
print('标识',id(name))
print('类型',type(name))
print('值',name)


n1=1.1
n2=2.2
print(n1+n2)
from decimal import Decimal
print(Decimal(n1)+Decimal(n2))
print(Decimal(1.1)+Decimal(2.2))
print(Decimal('1.1')+Decimal('2.2'))
# print(Decimal('n1')+Decimal('n2'))

f1=True
f2=False
print(f1,type(f1))
print(f2,type(f2))
print(f1+1)
print(f2+1)

name='张三'
age=20
#print('我叫'+name+'今年'+age+'岁')
print('我叫'+name+'今年'+str(age)+'岁')

# 输入函数
present=input('大圣想要什么')
print(present,type(present))



