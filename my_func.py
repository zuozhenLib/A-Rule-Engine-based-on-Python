# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 20:53:24 2020
其他有用的函数
@author: 77433

"""

import re

def get_op_type(condition):
    '''
    condition为字符串类型
    通过检测来获取condition语句中的关系是keyoperator=["!=",">=","<=","=","<",">"]
    中的哪一个，并且输出对应符号的index
    '''
    keyoperator=["!=",">=","<=","=","<",">"]
    flag=0
    for op in keyoperator:
        if re.search(op,condition) !=None:
            return flag
        else:
            flag=flag+1
    print("条件错误，无关系符号(=,>,<..)")
    return None


def judge(para1,para2,op_flag=3):
    '''
    根据传入的两个参数和运算符标志来决定二者做何种运算，返回一个bool类型
    keyoperator=["!=",">=","<=","=","<",">"] op_flag为运算类型的下标
    在ruletable类中调用
    '''
    try:
        if op_flag==3: #做相等运算，对应“==”
            if para1==para2 : return True
            else: return False
        if op_flag==4: #做大小比较，对应“<”
            if para1<para2: return True
            else: return False
        if op_flag==5:
            if para1>para2: return True
            else: return False
        if op_flag==0:
            if para1!=para2: return True
            else: return False
        if op_flag==1:
            if para1>=para2: return True
            else: return False
        if op_flag==2:
            if para1<=para2: return True
            else: return False
    except TypeError:
        print("jugde type error ,string cant compare to int please check the rule.txt or input")
        
if __name__=="__main__":       
    if(judge("ss",1,2)):
        print("ok")
        
    