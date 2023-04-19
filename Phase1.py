import os
import numpy as np
import pandas as pd
import statistics as st
from pandas import ExcelWriter
# for file in os.listdir('data'):
#to_xlsx

dict = {}

for files in os.listdir('data'):
    #creates a dictionary with key:commodity name, value:df
    dict[files] = pd.read_csv('data/'+files)
n = len(dict)
forward = ['forwardTime 1', 'forwardTime 2', 'forwardTime 3', 'forwardTime 4', 'forwardTime 5',
       'forwardTime 6']
basis = ['basis 1', 'basis 2', 'basis 3', 'basis 4', 'basis 5',
       'basis 6']
#values that do not have rep basis
w_basis_issue = {}

def rocp(k):
    df1 = {}
    for x in dict:
        df1[x]=dict[x][k]
    temp = [len(df1[x]) for x in df1]
    t = min(temp)
    df1 = pd.DataFrame(df1).truncate(after=t)
    return df1
    
def factor1():
    k = 'rocp 21 day'
    #creates a list of the rocp 21 day
    df1 = rocp(k)
    #fills NaN values with row average
    df1.fillna(df1.mean(axis=1), inplace=True)
    rv = df1.sum(axis=1)/n
    rv.name = 'Factor 1'
    return rv.to_frame()

def factor2(average = False):
    """
    if average is True then :
    TSMOMavg(t) = 1/Npos ∑ (rocp 252 days) + 1/Nneg ∑ (rocp 252 days)
    else:
    TSMOM(t) = 1/Npos ∑ (rocp 252 days) - 1/Nneg ∑ (rocp 252 days)
    """
    k = 'rocp 252 day'
    df1 = rocp(k)
    df1.fillna(0, inplace=True)
    def f(row):
        pos = []
        neg = []
        p = 0
        n = 0
        for x in row:
            if x >0:
                pos.append(x)
            else:
                neg.append(x)
        if not len(pos) == 0:
            p = sum(pos)/len(pos)

        if not len(neg) == 0:
            n = sum(neg)/len(neg)
        if average == False:
            return p - n
        return p + n
    rv = df1.apply(f,axis=1)
    rv.name = 'Factor 2'
    return rv.to_frame()

def _factorHnL(HighorLow=None, Rule='A'):
    """
    This function returns representative basis along with H/L commodities
    for each day.
    First need a dataframe with the representative basis
    then we calculate 
    1/g ∑ [1/3 (basis x + basis y + basis z)]
    """
    temp = []
    dict_basis = {}
    for commodities in dict.keys():
        dict_basis[commodities] = rep_basis(dict[commodities],commodities)
        temp.append(len(dict_basis[commodities]))
        print(f'This commodity has been processed:{commodities}')
    m = min(temp)
    for commodities in dict_basis:
        del dict_basis[commodities][m:]
    rb = pd.DataFrame(dict_basis)
    dicthl = {'H':[],'L':[]}
    for i in range(rb.shape[0]):
        curr = rb.iloc[i]
        temp = curr.dropna().to_list()
        if Rule == 'B':
            temp.sort()
            h_threshold = temp[-5]
            l_threshold = temp[4]
        else:
            temp = st.median(temp)
        h1 = []
        l1 = []
        for com in rb.columns:
            if Rule == 'B':
                if curr[com] >= h_threshold:
                    h1.append(com)
                elif curr[com] <= l_threshold:
                    l1.append(com)
                else:
                    pass
            else:
                if curr[com] > temp:
                    h1.append(com)
                elif curr[com] < temp:
                    l1.append(com)
        dicthl['H'].append(h1)
        dicthl['L'].append(l1)
    return rb, dicthl
    
    #rb = pd.DataFrame(dict_basis).truncate(after = m+1)
    #return rb
def rep_basis(df,com=None):
    x = df[forward]
    def t(row):
        ls = []
        i = 1
        for f in row:
            if f <218 and f >27:
                ls.append(i)
            i += 1
        return ls
    ndf = x.apply(t,axis=1)
    #df1 is the basis that we will use
    df1 = ndf.apply(lambda row: [f'basis {x}' for x in row])
    x = df[basis]
    rv =[]
    for ind in df1.index:
        w = df1.loc[ind]
        if len(w) == 0:
            w_basis_issue[com]=w_basis_issue.get(com,[])+[ind]
            rv.append(None)
            continue
        y = x.loc[ind][w].sum()/len(w)
        rv.append(y)
    return rv

def factor3():
    ls = []
    rb, dicthl = _factorHnL()
    for i in range(rb.shape[0]):
        t = dicthl['H'][i]
        ls.append((rb.loc[i][t]).mean())
    return pd.DataFrame({'Factor 3':ls})

def factor4():    
    ls = []
    rb, dicthl = _factorHnL()
    for i in range(rb.shape[0]):
        t = dicthl['L'][i]
        ls.append((rb.loc[i][t]).mean())
    return pd.DataFrame({'Factor 4':ls})

def all(truncate =None):
    """
    Parameters: truncate takes in the number of rows to show for result
    Output:
    """
    rv = [factor1(),factor2(),factor3(),factor4()]
    rv1 = []
    for x in rv:
        x = x.truncate(after = truncate)
        rv1.append(x)
    return rv1

def all_to_xl(truncate = None):
    names = ['Factor 1','Factor 2','Factor 3','Factor 4']
    writer=pd.ExcelWriter('output.xlsx')
    for i, A in enumerate(all(truncate)):
        A.to_excel(writer,sheet_name="{0}".format(names[i]))
    writer.save()
