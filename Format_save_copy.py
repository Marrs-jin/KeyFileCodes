#!/usr/bin/env python
# coding: utf-8

# In[1]:


from sympy import pretty_print as pp, latex
from sympy import Symbol
import pandas as pd
def formatter(x):
    """takes in savee_copy and formats it
    puts states into nsl format
    drops uncessary columns
    """
    savee_copy = x.copy()
    savee_copy.fillna(0, inplace = True)
    savee_copy.drop(['Ei','Ef','mat_unc','Ei_unc','Ef_unc', 'Eerr', 'matrix', 'old_unc', 'Berr', 'precise_wave', 'precise_Eerr'], axis = 1, inplace = True)



    ini_hold = []
    dec_hold = []
    n_holdI, l_holdI, s_holdI = [], [], []
    n_holdD, l_holdD, s_holdD = [], [], []
    for i in range(len(savee_copy)):
        #Initial
        n = str(savee_copy.Initial[i][0])
        if savee_copy.Initial[i][1] == 0:
            l = 's'
        elif savee_copy.Initial[i][1] == 1:
            l = 'p'
        elif savee_copy.Initial[i][1] == 2:
            l = 'd'
        elif savee_copy.Initial[i][1] == 3:
            l = 'f'
        if savee_copy.Initial[i][2] == 0.5:
            s = '1/2'
        elif savee_copy.Initial[i][2] == 1.5:
            s = '3/2'
        elif savee_copy.Initial[i][2] == 2.5:
            s = '5/2'
        elif savee_copy.Initial[i][2] == 3.5:
            s = '7/2'
        elif savee_copy.Initial[i][2] == 4.5:
            s = '9/2'
        ini = n+l+s
        ini_hold.append(ini)
        n_holdI.append(n)
        l_holdI.append(l)
        s_holdI.append(s)

        #Decay
        n = str(savee_copy.Decay[i][0])
        if savee_copy.Decay[i][1] == 0:
            l = 's'
        elif savee_copy.Decay[i][1] == 1:
            l = 'p'
        elif savee_copy.Decay[i][1] == 2:
            l = 'd'
        elif savee_copy.Decay[i][1] == 3:
            l = 'f'
        if savee_copy.Decay[i][2] == 0.5:
            s = '1/2'
        elif savee_copy.Decay[i][2] == 1.5:
            s = '3/2'
        elif savee_copy.Decay[i][2] == 2.5:
            s = '5/2'
        elif savee_copy.Decay[i][2] == 3.5:
            s = '7/2'
        elif savee_copy.Decay[i][2] == 4.5:
            s = '9/2'
        dec = n+l+s
        dec_hold.append(dec)
        n_holdD.append(n)
        l_holdD.append(l)
        s_holdD.append(s)
    
    savee_copy['Initial'] = ini_hold
    savee_copy['Decay'] = dec_hold
    savee_copy['nI'] = n_holdI
    savee_copy['lI'] = l_holdI
    savee_copy['sI'] = s_holdI
    savee_copy['nD'] = n_holdD
    savee_copy['lD'] = l_holdD
    savee_copy['sD'] = s_holdD
    
    savee_copy.drop(['nI', 'lI', 'sI', 'nD', 'sD', 'lD'], axis = 1, inplace = True)
    savee_copy = savee_copy[['Initial','Decay','mat_werr','wavelength','transition_rate s-1', 'branching ratio']]
    savee_copy.rename(columns = {"mat_werr": "Matrix element (a.u.)", "wavelength": "Wavelength (nm)", 
                            "transition_rate s-1": "Transition Rate (s-1)", 
                            'branching ratio': "Branching ratio"}, inplace = True)
    return savee_copy


# In[1]:


def format_lifetime(x, y):
    Lifetimes = x
    life_lin = y
    Lifetimes = pd.DataFrame(Lifetimes, columns = ['State', 'Lifetime', 'Error'])

    #sorts by s, p, 1/2, 3/2, etc.
    Lifetimes[['n','l', 's']] = pd.DataFrame(Lifetimes.State.tolist(), index= Lifetimes.index)
    Lifetimes.sort_values(by=['l', 'n', 's'], ascending = [True, True, True], inplace = True)
    Lifetimes.drop(['n','l','s'], axis = 1, inplace = True)
    Lifetimes.reset_index(drop = True, inplace = True)

    Lifetimes['Lifetime'] = Lifetimes['Lifetime'].apply(s_to_ns)
    Lifetimes['Error'] = Lifetimes['Error'].apply(s_to_ns)
    
    #change back to s, p, d
    ini_hold = []
    n_hold = []
    l_hold = []
    s_hold = []
    for i in range(len(Lifetimes)):
        #State
        n = str(Lifetimes.State[i][0])
        if Lifetimes.State[i][1] == 0:
            l = 's'
        elif Lifetimes.State[i][1] == 1:
            l = 'p'
        elif Lifetimes.State[i][1] == 2:
            l = 'd'
        elif Lifetimes.State[i][1] == 3:
            l = 'f'
        if Lifetimes.State[i][2] == 0.5:
            #s = '\u2081\u2082'
            #s = Symbol('_{1/2}')
            s = '1/2'
        elif Lifetimes.State[i][2] == 1.5:
            s = '3/2'
        elif Lifetimes.State[i][2] == 2.5:
            s = '5/2'
        elif Lifetimes.State[i][2] == 3.5:
            s = '7/2'
        elif Lifetimes.State[i][2] == 4.5:
            s = '9/2'
        ini = n+l+s

        n_hold.append(n)
        l_hold.append(l)
        s_hold.append(s)
        ini_hold.append(ini)
    
    
    Lifetimes['State'] = ini_hold
    Lifetimes['n'] = n_hold
    Lifetimes['l'] = l_hold
    Lifetimes['s'] = s_hold
    Lifetimes.drop(['n','l','s'], axis = 1, inplace = True)
    Lifetimes[0:10]
    
    for i in range(len(life_lin)-1,0,-1): #counting backwards
        if life_lin[i][0][1] >= 3:
            del(life_lin[i])
    
    Lifetime_excel = Lifetimes.copy()
    hold_lt = []
    for p in range(len(life_lin)):
        hold_lt.append(round(str(life_lin[p][1]*10**9), str(life_lin[p][2]*10**9), format = 'Drake'))
    Lifetimes['Lifetime'] = hold_lt
    
    
    #reads in experimental lifetimes in exp_l, replaces Lifetime value with () number and *, Lifetime excel with value and uncertainty
    ##########Lifetime_excel need * reference?##############
    #checks if the units are ns, if not assumes 's' and changes
    if 'II' in element:
        #number of ionizations
        element_othernm = element.split('I')[0] + '+' * (len(element.split('I')) - 2)
        exp_l_name = 'Experimental_Data\\%s-lifetimes.csv' % element_othernm
    else:
        exp_l_name = 'Experimental_Data\\%s-lifetimes.csv' % element
    
    #exp_l_name = 'Experimental_Data\\%s-lifetimes.csv' % element
    try:
        exp_l = pd.read_csv(exp_l_name) #experiment
        a = list(Lifetimes.State)
        c = list(zip(a))

        d = list(exp_l.State)
        f = list(zip(d))

        #make list of indices, transitions rates, for me and Safronova. 
        comparison = []
        for i in range(len(c)):
            try:
                if exp_l.Units[f.index(c[i])] == 'ns':
                    Lifetime_excel.iloc[i, Lifetime_excel.columns.get_loc('Lifetime')] = exp_l['Value'][f.index(c[i])]
                    Lifetime_excel.iloc[i, Lifetime_excel.columns.get_loc('Error')] = exp_l['Uncertainty'][f.index(c[i])]
                    life_exp = exp_l['Lifetime'][f.index(c[i])]
                    Lifetimes.iloc[i, Lifetimes.columns.get_loc('Lifetime')] = life_exp + '*'
                else:
                    Lifetime_excel.iloc[i, Lifetime_excel.columns.get_loc('Lifetime')] = exp_l['Value'][f.index(c[i])] * 10**9
                    Lifetime_excel.iloc[i, Lifetime_excel.columns.get_loc('Error')] = exp_l['Uncertainty'][f.index(c[i])] * 10**9
                    life_exp = exp_l['Lifetime'][f.index(c[i])] * 10**9
                    Lifetimes.iloc[i, Lifetimes.columns.get_loc('Lifetime')] = str(float(str(life_exp).replace(parent_num, ''))*10**9) + '*'
        #         comparison.append((i, f.index(c[i]), Lifetime['transition_rate (s-1)'][i], exp['value'][f.index(c[i])], 
        #                           exp['uncertainity'][f.index(c[i])]))
            except ValueError:
                pass
    except FileNotFoundError:
        pass
        
    Lifetimes.drop('Error', axis = 1, inplace = True)
    return Lifetimes, life_lin, Lifetime_excel

