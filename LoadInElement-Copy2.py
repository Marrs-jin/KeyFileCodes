#!/usr/bin/env python
# coding: utf-8

# In[1]:



#Read in file paths based on element name as it is saved. 
#Verify skiprows for each element


# In[2]:


#%run -i LoadFunctions.py


# In[3]:


import numpy as np
import pandas as pd
from fractions import Fraction
import xlsxwriter
import decimal
from decimal import *
import re
from modsigfig import round #does this need to be done 
from fractions import Fraction
pd.set_option('display.max_rows', 500)
getcontext().prec = 20


# In[4]:


element = input('Element name in files:')
skiprows_data = 0 #for database
skiprows_mats = 2 #for datapol
matname = f'Data\\{element}_datapol.csv' #the rest of the data
checkratesname = f"Data\\{element}_rates1.csv" 
checklifesname = f"Data\\{element}_rates2.csv" 
state_keys = pd.read_csv(f'Data/{element}_Key.csv', skiprows = 1, names = ['key', 'state', 'html', 'j'])


# In[39]:


rates1 = pd.read_csv(checkratesname, skiprows = 1)
rates2 = pd.read_csv(checklifesname, skiprows = 1)


# In[5]:




#have to read in as str or else pandas does weird rounding. Convert numbers back to float after
ele = pd.read_csv(matname, sep = ',', engine = 'python', header = None, skiprows = skiprows_mats, dtype = 'str')
cutoff_index = ele[ele[1].isnull()].index[0]
mats = ele[:cutoff_index]
energies = ele[cutoff_index+1:]

columns = ['start', 'end', 'start_name', 'end_name', 'matrix', 'unc']
mats.columns = columns
#mats['old_unc'] = database['unc']
columns2 = ['level', 'name', 'ene', 'unc', 'modif' ]
energies.drop([4], axis = 1, inplace = True) #drops two unneccesary column at end of energies. 
energies.columns = columns2
energies.reset_index(inplace = True, drop = True)
mats.reset_index(inplace = True,drop = True)


# In[6]:


state_keys['key'] = state_keys['key'].astype(str)
#removes spaces from state_key column headers
new_columns = state_keys.columns.map(lambda x: x.strip(' '))
for i in range(len(state_keys.columns)):
    state_keys.rename(columns = {state_keys.columns[i]: new_columns[i]}, inplace = True)
#removes spacing from html names
state_keys['html'] = state_keys['html'].map(lambda x: x.replace(" ", ""))
    
#remove commas from states to match with key file
for column in mats: 
    mats[column] = mats[column].map(lambda x: x.strip(','))
    mats[column] = mats[column].map(lambda x: x.strip(' '))
energies['level'] = energies['level'].map(lambda x: x.strip(','))
energies['level'] = energies['level'].map(lambda x: x.strip(' '))

#adds J to mats dataframe
mats['Ji'] = pd.merge(mats, state_keys, left_on=  ['start'],
                   right_on= ['key'], 
                   how = 'left')['j']
mats['Jf'] = pd.merge(mats, state_keys, left_on=  ['end'],
                   right_on= ['key'], 
                   how = 'left')['j']
mats


# In[7]:


#combines starts, decays and energies into one dataframe "all_state"
Initial_en = []
Final_en = []
Initial_unc = []
Final_unc = []
modif_hold = []
for i in range(len(mats)):
    Initial_en.append(energies[energies['level'] == mats['start'][i]]['ene'].values[0])
    Final_en.append(energies[energies['level'] == mats['end'][i]]['ene'].values[0])
    
    Initial_unc.append(energies[energies['level'] == mats['start'][i]]['unc'].values[0])
    Final_unc.append(energies[energies['level'] == mats['end'][i]]['unc'].values[0])
    if ('*' in energies[energies['level'] == mats['start'][i]]['modif']) or ('*' in energies[energies['level'] == mats['end'][i]]['modif']):
        modif_hold.append('*')
    else:
        modif_hold.append('')
all_state = pd.DataFrame({'Initial':mats['start'].values, 'Decay': mats['end'].values, 'NameI': mats['start_name'].values, 
                    'NameF': mats['end_name'].values, 'matrix': mats['matrix'].values,
                   'mat_unc': mats['unc'].values, 'Ei': Initial_en, 'Ei_unc': Initial_unc, 'Ef': Final_en, 
                   'Ef_unc': Final_unc, 'Ji': mats['Ji'], 'Jf': mats['Jf'], 'modif': modif_hold})
all_state


# In[8]:


#strips commas from values, relic of the csv read-in. 
for column in all_state:
    all_state[column] = all_state[column].astype(str) #convert to string to you can you strip
    all_state[column] = all_state[column].map(lambda x: x.strip(','))
#removes empty spaces from Ji, Jf so they can later be made into float
all_state['Ji'] = all_state['Ji'].map(lambda x: x.strip(' '))
all_state['Jf'] = all_state['Jf'].map(lambda x: x.strip(' '))


# In[9]:


# Initial_en = []
# Final_en = []
# Initial_unc = []
# Final_unc = []
# decay = []
# hold = []
# for i in range(len(starts)):
#     for j in range(len(nist)):
#         if starts['n'][i] == nist['n'][j] and starts['j'][i] == nist['j'][j] and starts['l'][i] == nist['l'][j]:
#             Initial_en.append(nist['ene'][j])
#             Initial_unc.append(nist['unc'][j])
#             hold.append([[starts['n'][i],starts['l'][i],starts['j'][i]], starts['m'][i], starts['unc'][i],
#                          [ends['n'][i], ends['l'][i], ends['j'][i]],
#                          nist['ene'][j],nist['unc'][j]])
#         elif ends['n'][i] == nist['n'][j] and ends['j'][i] == nist['j'][j] and ends['l'][i] == nist['l'][j]:
#             Final_en.append(nist['ene'][j])
#             Final_unc.append(nist['unc'][j])
# hold = pd.DataFrame(hold, columns = ['Initial', 'matrix', 'mat_unc', 'Decay', 'Ei', 'Ei_unc'])
# hold['Ef'] = Final_en
# hold['Ef_unc'] = Final_unc
# columns = ['Initial', 'Decay', 'matrix', 'Ei', 'Ef', 'mat_unc', 'Ei_unc', 'Ef_unc']
# all_state = hold[columns]

# # unc_hold = []
# # for i in all_state['Ef_unc']:
# #     unc_hold.append("{:.2e}".format(i))
# # all_state['Ef_unc'] = unc_hold
# all_state['old_unc'] = database['unc']


# In[10]:


# #appends the nist modification value ('' or '*') of the initial/final state to all _state. If either has '*' all-state does too
# mod_hold = []
# for i in range(len(all_state)):
#     mod_initial = nist[(nist['n'] == all_state.Initial[i][0]) & (nist['l'] == all_state.Initial[i][1]) & (nist['j'] == all_state.Initial[i][2])]['modif'].values[0]
#     mod_final = nist[(nist['n'] == all_state.Decay[i][0]) & (nist['l'] == all_state.Decay[i][1]) & (nist['j'] == all_state.Decay[i][2])]['modif'].values[0]
#     mod_hold.append((mod_initial, mod_final))
    
# all_state['modif'] = ''
# for i in range(len(mod_hold)):
#     if '*' in mod_hold[i]:
#         all_state.loc[i, 'modif'] = '*'
#     #mod_final = 


# In[11]:


all_state[all_state.modif == '*']


# In[12]:


#puts higher energy in Initial, sorts by energy
#does not sort decay states FIX?
eis = []
efs = []
inits = []
decs = []
eis_unc = []
efs_unc = []
flipped_mat = []
jis = []
jfs = []
for i in range(len(all_state)):
    if float(all_state.Ei[i]) < float(all_state.Ef[i]): #if we need to switch
        a = all_state.Ef[i]
        b = all_state.Ei[i]
        unc1 = all_state.Ef_unc[i]
        unc2 = all_state.Ei_unc[i]
        c2 = all_state.Decay[i]
        d = all_state.Initial[i]
        eis.append(a)
        eis_unc.append(unc1)
        efs.append(b)
        efs_unc.append(unc2)
        inits.append(c2)
        decs.append(d)
        jis.append(all_state['Jf'][i])
        jfs.append(all_state['Ji'][i])
        flipped_mat.append((all_state['matrix'][i]))

    else:
        a = all_state.Ei[i]
        b = all_state.Ef[i]
        unc1 = all_state.Ei_unc[i]
        unc2 = all_state.Ef_unc[i]
        c2 = all_state.Initial[i]
        d = all_state.Decay[i]
        eis.append(a)
        eis_unc.append(unc1)
        efs.append(b)
        efs_unc.append(unc2)
        inits.append(c2)
        decs.append(d)
        jis.append(all_state['Ji'][i])
        jfs.append(all_state['Jf'][i])
        #print(unc1)
        
all_state['Initial'] = inits
all_state['Decay'] = decs
all_state['Ei'] = eis
all_state['Ef'] = efs
all_state['Ei_unc'] = eis_unc
all_state['Ef_unc'] = efs_unc
all_state['Ji'] = jis
all_state['Jf'] = jfs
#mat_page = all_state.copy()
#mat_page.reset_index(inplace = True, drop = True)
all_state.sort_values('Ei', inplace = True)
all_state.reset_index(inplace = True, drop = True)
#HERE IS ORDERING?


# In[13]:


#indices of all spots where the ordering of the states was flipped
flipped_ind = []
for i in range(len(flipped_mat)):
    indx = np.where(all_state.matrix == flipped_mat[i])[0][0]
    flipped_ind.append(indx)


# In[14]:


#old code that checked for duplicate values


# In[15]:


initial_holds = list(all_state.Initial)
ends_holds = list(all_state.Decay)
mat_holds = list(all_state.matrix)
dups = []
for k, i in enumerate(all_state.matrix):
    ms = all_state.matrix[k]
    ini = all_state.Initial[k]
    end = all_state.Decay[k]
    res_list = [i for i in range(len(mat_holds)) if (mat_holds[i] == ms) 
                and (initial_holds[i] == ini) and (ends_holds[i] == end)]
    if len(res_list) > 1:
        dups.append(res_list[1:])
dups


# In[16]:


#Removes duplicates, resets index. 
if len(dups) != 0:
    dups = pd.DataFrame(dups)
    dups.drop_duplicates(inplace = True)
    dups = list(dups[0])
    all_state.drop(index = dups, inplace = True)
    all_state.reset_index(inplace = True, drop = True)
    all_state['matrix'] = pd.to_numeric(all_state.matrix)


# In[17]:


#replaces Nan with 0 values in uncertainty, changes energy, matrix and their errors to strings then to Decimals
###############possibly source of precision loss##########################


# In[18]:


all_state['Ef_unc'].fillna(0, inplace = True)
Ef_uncs = []
for i in all_state.Ef_unc:
    #print(i)
    if i == 'nan':
        Ef_uncs.append(0)
    else:
        Ef_uncs.append(i)
#     try: 
#         if np.isnan(i) == True or i == 'nan':
#             print(i)
#     except TypeError:
#         if i == 'nan':
            #print(i)

all_state.Ef_unc = Ef_uncs
all_state.Ei = all_state.Ei.apply(str).apply(Decimal)
all_state.Ef = all_state.Ef.apply(str).apply(Decimal)
all_state.Ei_unc = all_state.Ei_unc.apply(str).apply(Decimal)
all_state.Ef_unc = all_state.Ef_unc.apply(str).apply(Decimal)
all_state.mat_unc = all_state.mat_unc.apply(str).apply(Decimal)
all_state.matrix = all_state.matrix.apply(str).apply(Decimal)


# In[19]:


#creates new column mat_werr that has the matrix plus (#) format of error in one column
mat_werr = []
for i in range(len(all_state)):
    try:
        mat_werr.append(round(str(all_state.matrix[i]), str(all_state.mat_unc[i]), format = 'Drake'))
    except ValueError:
        print(i)
all_state['mat_werr'] = mat_werr


# In[20]:


# #changes nls format to list to order correctly
# old_state = all_state.copy() #version before ordering
# all_state[['n','l', 's']] = pd.DataFrame(all_state.Initial.tolist(), index= all_state.index)
# all_state[['nf','lf', 'sf']] = pd.DataFrame(all_state.Decay.tolist(), index= all_state.index)
# all_state.sort_values(by=['l', 'n', 's','nf', 'lf', 'sf'], ascending = [True, True, True, True, True, True], inplace = True)
# all_state.reset_index(drop = True, inplace = True)


# In[21]:


# #creates new all_state columns with Initial, Decay in '7s1/2' format
# from sympy import pretty_print as pp, latex
# from sympy import Symbol

# ini_hold = []
# dec_hold = []
# n_holdI, l_holdI, s_holdI = [], [], []
# n_holdD, l_holdD, s_holdD = [], [], []
# for i in range(len(all_state)):
#     #Initial
#     n = str(all_state.Initial[i][0])
#     if all_state.Initial[i][1] == 0:
#         l = 's'
#     elif all_state.Initial[i][1] == 1:
#         l = 'p'
#     elif all_state.Initial[i][1] == 2:
#         l = 'd'
#     elif all_state.Initial[i][1] == 3:
#         l = 'f'
#     elif all_state.Initial[i][1] == 4:
#         l = 'g'
#     if all_state.Initial[i][2] == 0.5:
#         s = '1/2'
#     elif all_state.Initial[i][2] == 1.5:
#         s = '3/2'
#     elif all_state.Initial[i][2] == 2.5:
#         s = '5/2'
#     elif all_state.Initial[i][2] == 3.5:
#         s = '7/2'
#     elif all_state.Initial[i][2] == 4.5:
#         s = '9/2'
#     ini = n+l+s
#     ini_hold.append(ini)
#     n_holdI.append(n)
#     l_holdI.append(l)
#     s_holdI.append(s)
    
#     #Decay
#     n = str(all_state.Decay[i][0])
#     if all_state.Decay[i][1] == 0:
#         l = 's'
#     elif all_state.Decay[i][1] == 1:
#         l = 'p'
#     elif all_state.Decay[i][1] == 2:
#         l = 'd'
#     elif all_state.Decay[i][1] == 3:
#         l = 'f'
#     if all_state.Decay[i][2] == 0.5:
#         s = '1/2'
#     elif all_state.Decay[i][2] == 1.5:
#         s = '3/2'
#     elif all_state.Decay[i][2] == 2.5:
#         s = '5/2'
#     elif all_state.Decay[i][2] == 3.5:
#         s = '7/2'
#     elif all_state.Decay[i][2] == 4.5:
#         s = '9/2'
#     dec = n+l+s
#     dec_hold.append(dec)
#     n_holdD.append(n)
#     l_holdD.append(l)
#     s_holdD.append(s)
    
# all_state['Initial_form'] = ini_hold #formatted 
# all_state['Decay_form'] = dec_hold


# In[22]:


exp_data_name = "Experimental_Data\\%s-matrix-elements.csv" % element


# In[23]:


# #puts in the experimental matrix values into all_state in matrix, uncertainty, and combined () format
# #has to run for loop twice because experimental data are not ordered in Initial Decay format, Decay may be first
# if 'II' in element:
#     #number of ionizations
#     element_othernm = element.split('I')[0] + '+' * (len(element.split('I')) - 2)
#     exp_data_name = "Experimental_Data\\%s-matrix-elements.csv" % element_othernm
# else:
#     exp_data_name = "Experimental_Data\\%s-matrix-elements.csv" % element


# In[24]:


#indices of all spots where the ordering of the states was flipped
flipped_ind = []
for i in range(len(flipped_mat)):
    indx = np.where(all_state.matrix == Decimal(flipped_mat[i]))[0][0]
    flipped_ind.append(indx)


# In[25]:


all_state


# In[26]:


#reads in experimental data
try:
    exp = pd.read_csv(exp_data_name) #experiment
    a = list(all_state.Initial)
    b = list(all_state.Decay)
    c = list(zip(a,b))

    d = list(exp.From)
    e = list(exp.To)
    f = list(zip(d,e))
    replaced_ind = []
    for i in range(len(f)):
        #print(np.where((all_state['Initial'] == str(f[i][1])) & (all_state['Decay'] == str(f[i][0])))[0][0], 'hi')
        try:
            l = np.where((all_state['Initial'] == str(f[i][1])) & (all_state['Decay'] == str(f[i][0])))[0][0]
            all_state.iloc[l, all_state.columns.get_loc('matrix')] = exp['value'][i]
            all_state.iloc[l, all_state.columns.get_loc('mat_unc')] = exp['uncertainity'][i]
            all_state.iloc[l, all_state.columns.get_loc('mat_werr')] = exp['Matrixelement'][i] + exp['Ref'][i]
            replaced_ind.append(l)
            print(i,l)
        except IndexError:
            pass
    for i in range(len(f)):
        try:
            l = np.where((all_state['Initial'] == str(f[i][0])) & (all_state['Decay'] == str(f[i][1])))[0][0]
            all_state.iloc[l, all_state.columns.get_loc('matrix')] = exp['value'][i]
            all_state.iloc[l, all_state.columns.get_loc('mat_unc')] = exp['uncertainity'][i]
            all_state.iloc[l, all_state.columns.get_loc('mat_werr')] = exp['Matrixelement'][i] + exp['Ref'][i]
            replaced_ind.append(l)
            print(i, l)
        except IndexError:
            pass
except FileNotFoundError:
    pass


# In[27]:


# #reads in experimental data
# try:
#     exp = pd.read_csv(exp_data_name) #experiment
#     a = list(all_state.Initial_form)
#     b = list(all_state.Decay_form)
#     c = list(zip(a,b))

#     d = list(exp.From)
#     e = list(exp.To)
#     f = list(zip(d,e))
#     replaced_ind = []
#     print('Replaced Values, experimental index, all_state index')
#     for i in range(len(f)):
#         try:
#             l = np.where((all_state['Initial_form'] == f[i][1]) & (all_state['Decay_form'] == f[i][0]))[0][0]
#             all_state.iloc[l, all_state.columns.get_loc('matrix')] = exp['value'][i]
#             all_state.iloc[l, all_state.columns.get_loc('mat_unc')] = exp['uncertainity'][i]
#             all_state.iloc[l, all_state.columns.get_loc('mat_werr')] = exp['Matrixelement'][i] + exp['Ref'][i]
#             replaced_ind.append(l)
#             print(i, l)
#         except IndexError:
#             pass
#     for i in range(len(f)):
#         try:
#             l = np.where((all_state['Initial_form'] == f[i][0]) & (all_state['Decay_form'] == f[i][1]))[0][0]
#             all_state.iloc[l, all_state.columns.get_loc('matrix')] = exp['value'][i]
#             all_state.iloc[l, all_state.columns.get_loc('mat_unc')] = exp['uncertainity'][i]
#             all_state.iloc[l, all_state.columns.get_loc('mat_werr')] = exp['Matrixelement'][i] + exp['Ref'][i]
#             replaced_ind.append(l)
#             print(i, l)
#         except IndexError:
#             pass
# except FileNotFoundError:
#     pass


# In[28]:


#all_state.drop(['Initial_form', 'Decay_form'], axis = 1, inplace = True)


# In[29]:


#Creates Transition Rates, Lifetimes, Branching ratios, and errors
#lifetimes put into new array
#changes wavelengths to nm, t_rates are in s-1


# In[30]:


get_ipython().run_line_magic('run', '-i LoadFunctions.py')


# In[31]:


states = list(all_state.Initial)
MatrixErrors, WavelengthsCm, WavelengthsUncAng, TransitionRates = [], [], [], []
TransitionRateErrors, TransitionsForLifetime, TerrorsForLifetime, Lifetimes, LifetimeErrors = [], [], [], [], []
BranchingRatios, BranchingRatioErrors = [], []
for i in range(len(all_state)):
    Ei = all_state.Ei[i]
    Ef = all_state.Ef[i]
    Eierr = all_state.Ei_unc[i]
    Eferr = all_state.Ef_unc[i]

    m = float(all_state.matrix[i])
    j = float(Fraction(all_state['Ji'][i]))
    lam = float(1 / (Ei - Ef))

    #d = decimal.Decimal(str(all_state.matrix[i])) #how many decimals spots to go out to
    #d = -1 * d.as_tuple().exponent
    #merr = all_state.mat_unc[i] / (10 ** d)
    merr = float(all_state.mat_unc[i])
    
    lamerr = float(energy_err_calc(Ei, Ef, Eierr, Eferr))
    TR = transition_rate_calc(m,j,lam)
    
    TRerr = transition_err_calc(m,j,lam,merr,lamerr)
    
    MatrixErrors.append(merr)

    WavelengthsCm.append(lam)
    WavelengthsUncAng.append(lamerr)

    TransitionRates.append(TR)
    TransitionRateErrors.append(TRerr)
    
    #n_dec = all_state.Decay[i][0]
    #l_dec = all_state.Decay[i][1]
    #s_dec = all_state.Decay[i][2]
    TransitionsForLifetime.append(TR)
    TerrorsForLifetime.append(TRerr)
    
    try:
        if all_state.Initial[i] not in states[i+1:]: #If next state NOT have same Initial State Name as the current one, i.e. new transition
            Lftime = lifetime_calc(TransitionsForLifetime)
            #print(Lftime, TransitionsForLifetime)
            LftimeError = lifetime_err_calc(TransitionsForLifetime, TerrorsForLifetime)
            
            Lifetimes.append((all_state.Initial[i], Lftime, LftimeError))
            for i in range(0, len(TransitionsForLifetime)): #all the transitions
                
                BR = branching_ratio_calc(TransitionsForLifetime[i], Lftime)
                BRerr = branching_ratio_error(TransitionsForLifetime[i], TransitionsForLifetime, 
                                                  TerrorsForLifetime[i], [trerr for trerr in TerrorsForLifetime], Lftime)
                BranchingRatios.append(BR)
                BranchingRatioErrors.append(BRerr)
                
                
            TransitionsForLifetime = []
            TerrorsForLifetime = [] #reset for next initial state
    except KeyError:
        print(i)
        
all_state['wavelength'] = WavelengthsCm
all_state.wavelength = all_state.wavelength.apply(cm_to_nm)
all_state['Eerr'] = WavelengthsUncAng
all_state.Eerr = all_state.Eerr.apply(ang_to_nm)
all_state['transition_rate s-1'] = TransitionRates
all_state['Terr'] = TransitionRateErrors
all_state['branching ratio'] = BranchingRatios
all_state['Berr'] = BranchingRatioErrors
life_linear = Lifetimes.copy()
all_linear = all_state.copy()


# In[32]:


# def branching_ratio_error(Tr, Trs, TrError, TrErrors, lifetime):
#     sums = 1/lifetime #sum of all transition rates
#     all_errors = []
#     for i in range(len(Trs)):
#         #if the transition rate is for the transition we are calculating branching ratio for
#         if Trs[i] == Tr:
#             numer = sums - Trs[i] #top is All transition rates - TR of interest
#             denom = sums**2 #denom is all transition rates
#             Error1 = (numer / denom)**2 # ((sum - TR) / (sum**2)) ** 2
#             Error1 = Error1 * (TrErrors[i]**2) #Error1 * errors for this transition rate **2
#         else:
#             numer = Tr
#             denom = sums**2
#             Error1 = (numer / denom)**2
#             Error1 = Error1 * (TrErrors[i]**2)
#         all_errors.append(Error1)
#     Br_error = np.sqrt(np.sum(all_errors))
#     if len(all_errors) == 1:
#         Br_error = 0
#     return Br_error


# In[33]:


#makes 20 decimal float approximations of wavelenght and error for "exact" calculation


# In[34]:


precise_wave = []
precise_Eerr = []
for i in range(len(all_state)): #saves new columns of all_state to be used in calculation, that aren't rounded yet
    precise_wave.append((1/(all_state.Ei[i] - all_state.Ef[i]))*10**7)
    precise_Eerr.append(Decimal(all_state.Eerr[i]))
all_state['precise_wave'] = precise_wave
all_state['precise_Eerr'] = precise_Eerr


# In[35]:


#saves the wavelength and its error with the same number of digits past the decimal as the original initial energy had
new_wavelength = []
new_wave_error = []
for p in range(len(all_state)):
    getcontext().prec = 10
    num_digits = len(str(all_state.Ei[p]).split('.')[1]) #how many digits past the decimal spot
    new_wavelength.append(round(str(all_state.wavelength[p]), decimals = num_digits))
    new_wave_error.append(round(str(all_state.Eerr[p]), decimals = num_digits))

all_state['wavelength'] = new_wavelength
all_state['Eerr'] = new_wave_error


# In[36]:


#mat_page is what is going to be stored in matrix elements page
mat_page = all_state.copy()
mat_page

flipped_cols = [('Initial', 'Decay'), ('Ei', 'Ef'), ('Ei_unc', 'Ef_unc')]
for i in flipped_cols:
    mat_page.loc[flipped_ind,i[0]] = all_state.loc[flipped_ind, i[1]]
    mat_page.loc[flipped_ind, i[1]] = all_state.loc[flipped_ind, i[0]]

#reorder
#mat_page[['n','l', 's']] = pd.DataFrame(mat_page.Initial.tolist(), index= mat_page.index)
#mat_page[['nf','lf', 'sf']] = pd.DataFrame(mat_page.Decay.tolist(), index= mat_page.index)
#mat_page.sort_values(by=['l', 'n', 's','nf', 'lf', 'sf'], ascending = [True, True, True, True, True, True], inplace = True)
#mat_page.reset_index(drop = True, inplace = True)

