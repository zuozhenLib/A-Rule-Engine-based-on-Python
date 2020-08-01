# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 20:24:03 2020
以一定格式写下规则文件，保存为txt格式，用ruletable类来消化这种格式的规则
目前只支持每条规则最多两个条件，两个条件间的逻辑运算只支持and 和 or
条件值只接受string，bool，int,float类型，输出目前只支持等于操作符
@author: 77433
"""
import re
import numpy as np
import pandas as  pd
from my_func import get_op_type
from my_func import judge
keyoperator=["!=",">=","<=","=","<",">"]
class ruletable:
    rule_list=None
    rule_table=None
    
    def __init__(self,filename):
        with open(filename,'r',encoding="utf-8") as f :
            self.rule_list=f.readlines()
        self.rule_table=pd.DataFrame(np.zeros((len(self.rule_list),13)),columns=["input_type1","input_value1","input_type2","input_value2",
                          "relationship1","relationship2","input_relationship",
                          "result_type1","result_value1","result_type2","result_value2",
                          "result_relationship1","result_relationship2"])
        self.fill_table()
        self.result={}
    
    def fill_table(self):
        '''
        根据txt文件生成规则表，以供查询
        '''
        index=0 #从索引号开始填表
        for con_res in self.rule_list:
            cr=con_res.split(" then ")
            if re.search(' and',cr[0])!=None:
                self.rule_table.loc[index, 'input_relationship']=1 #输入条件关系为 与
            elif re.search(' or',cr[0])!=None:
                self.rule_table.loc[index, 'input_relationship']=2 #输入条件关系为 或
                
            con=re.split(" and| or",cr[0])#如果有两个或者以上的条件组合 那么将所有 条件分开
            con[0]=con[0][3:]  #把开头的‘if ’去掉,con包含一个或者两个
            condition_num=0
            for conditions in con:
                condition_num=condition_num+1
                if re.search('\(',conditions)!=None: #包含括号则说明有指定类型，不包含则默认为string类型
                    typeflag=abs(conditions.index('(')-conditions.index(')'))   #通过括号内容长度来确定类型
                else:
                    typeflag=0 #默认为字符串
                conditions=re.sub(r'\([a-zA-Z]+\)','',conditions) #delete the '（type）'
                relationship=get_op_type(conditions)
                self.rule_table.loc[index, 'relationship'+str(condition_num)]=relationship
                contype=re.split(keyoperator[relationship],conditions)
                contype[0]=contype[0].strip()
                contype[1]=contype[1].strip()# str.strip()去除首尾空格
                self.rule_table.loc[index, 'input_type'+str(condition_num)]=contype[0]
                if typeflag==4:#类型为int
                    self.rule_table.loc[index, 'input_value'+str(condition_num)]=int(contype[1])
                elif typeflag==5:#类型为bool
                    self.rule_table.loc[index, 'input_value'+str(condition_num)]=bool(int(contype[1]))
                elif typeflag==6:#类型为float
                    self.rule_table.loc[index, 'input_value'+str(condition_num)]=float(contype[1])
                else:
                    self.rule_table.loc[index, 'input_value'+str(condition_num)]=contype[1]
                    #条件部分解析完成，接下来解析结果部分
            
            res=re.split(" and",cr[1])
            result_num=0
            for result in res:
                result_num=result_num+1
                if re.search('\(',result)!=None:
                    typeflag=abs(result.index('(')-result.index(')'))
                else:
                    typeflag=0
                result=re.sub(r'\([a-zA-Z]+\)','',result)
                relationship=get_op_type(result)
                self.rule_table.loc[index, 'result_relationship'+str(result_num)]=relationship
                restype=re.split(keyoperator[relationship],result)
                restype[0]=restype[0].strip()
                restype[1]=restype[1].strip()
                self.rule_table.loc[index, 'result_type'+str(result_num)]=restype[0]
                if typeflag==4:
                    self.rule_table.loc[index, 'result_value'+str(result_num)]=int(restype[1])
                elif typeflag==5:
                    self.rule_table.loc[index, 'result_value'+str(result_num)]=bool(int(restype[1]))
                else:
                    self.rule_table.loc[index, 'result_value'+str(result_num)]=restype[1]
            index=index+1
            print("RULE NO.",index,"has been bulit")
            
    def find_tag(self,tag):
        '''
        根据tag来找到对应的规则处在table表中第几行，返回一个int列表（为规则表中的索引值 ），没有匹配项则返回None
    
        '''
        rule=self.rule_table.copy()
        indexlist=rule[(rule["input_type1"]==tag)|(rule["input_type2"]==tag)].index
        return indexlist
    
    def condition_judge(self,index,case):
        '''
        对于一个case，判断在rule_table中是否满足第index的条件，返回bool
        '''
        rule=self.rule_table.copy()
        condition_type1=rule.loc[index,"input_type1"]
        condition_value1=rule.loc[index,"input_value1"]
        condition_value2=rule.loc[index,"input_value2"]
        condition_type2=rule.loc[index,"input_type2"]
        op_flag1=rule.loc[index,'relationship1']
        op_flag2=rule.loc[index,'relationship2'] 
        if rule.loc[index,"input_relationship"]==1: #对两个条件做与运算
            if case.get(condition_type2) and case.get(condition_type1): #两个标签在case中都 存在
                     bool1=judge(case[condition_type1],condition_value1,op_flag1)
                     bool2=judge(case[condition_type2],condition_value2,op_flag2)
                     if (bool1 and bool2):
                         return True   
        else: #剩下的情况逐个判断即可
            if case.get(condition_type2):
                bool2=judge(case[condition_type2],condition_value2,op_flag2)
                return bool2
            if case.get(condition_type1):
                bool1=judge(case[condition_type1],condition_value1,op_flag1)
                return bool1
        return False  
        
               
    def reason_one_time(self,case):
        '''
        输入case为一个字典类型，输出经过规则表之后得到的结果（字典格式）
        '''
        
        keys=case.keys() #保存所有要匹配的标签到keys，用于后续查找
        for k in keys:
            indexlist=self.find_tag(k)
            if indexlist.size < 1:
                continue  #如果没有找到此标签的规则，那么进行下一标签的查找
            for i in indexlist:
                if self.condition_judge(i,case):# if the condition is satisfied,then add the result info according to the rule table
                    result_type=self.rule_table.loc[i,'result_type1']
                    result_value=self.rule_table.loc[i,'result_value1']
                    self.result[result_type]=result_value
        return self.result


           
    def reason(self,case):
        temp_case=case.copy()
        while(1):
            length1=len(temp_case)
            result=self.reason_one_time(temp_case)
            self.result.update(result)
            temp_case.update(result)
            length2=len(temp_case)
            if length2==length1:  #结果列表中无新成员
                break    
        return self.result
                    
                    

if __name__=='__main__':
    rt=ruletable("RULE1.txt")    
    rule_table= rt.rule_table
    case={'personality':'kind','sex':'male'}
    #case={'function': 'deep learning','price':9000,'brand':'xiaomi','people':'gameplayer','isstudent':True,'factor':0.05}
    #b1=rt.condition_judge(1,case)
    result=rt.reason(case)
    print(result)
