from Phase1 import factor1, factor2, factor3, dict, _factorHnL
import numpy as np
import pandas as pd

f1 = factor1()
f2 =factor2()
f3 = factor3()

def factorA_01(factor):
    return pd.DataFrame(np.where(factor>0,1,-1))

def factorB_01(factor, rocp):
    """
    factor: globar variable ex)f1
    rocp is rocp required for comparison
    """
    dict1={}
    for x in dict:
        dict1[x] = dict[x][rocp]
    #dict1 is rocp 21 for all commodities
    df = pd.DataFrame(dict1)
    df['omega']=factor[factor.columns[0]]
    df = df.truncate(after=len(factor))
    def temp(val, x):
        t = df['omega'][x]
        if np.isnan(val):
            return None
        if val >t:
            return 1
        elif val != t:
            return -1
        return None
    for x in range(len(df)):
        temp_row = df.loc[x].apply(temp,args=(x,))
        df.loc[x] =temp_row
    df.drop(columns=['omega'], inplace=True)
    return df

def factor1A():
    return factorA_01(f1)

def factor1B():
    """
    factor_name must be the global variable for the output of factor 
    from Phase 1
    """
    return factorB_01(f1,'rocp 21 day')

def factor2A():
    return factorA_01(f2)

def factor2B():
    """
    factor_name must be the global variable for the output of factor 
    from Phase 1
    """
    return factorB_01(f2,'rocp 252 day')

def factorA_0304():
    """
    similar to tfactorB row by row operation, _factorHnL[1] return a list of all
    high and low terms so use that
    define f which is output of _factorHnL() differently depending on whether A or B
    """
    f = _factorHnL()
    dict2 ={}
    for x in dict.keys():
        dict2[x]=[]
    for comm in dict2.keys():
        for i in range(len(f[1]['H'])):
            if comm in f[1]['H'][i]:
                dict2[comm].append(1)
            else:
                dict2[comm].append(-1)

    return pd.DataFrame(dict2)

def factorB_0304():
    f = _factorHnL(Rule='B')
    dict2 ={}
    for x in dict.keys():
        dict2[x]=[]
    for comm in dict2.keys():
        for i in range(len(f[1]['H'])):
            if comm in f[1]['H'][i]:
                dict2[comm].append(1)
            elif comm in f[1]['L'][i]:
                dict2[comm].append(-1)
            else:
                dict2[comm].append(0)
    return pd.DataFrame(dict2)



    
