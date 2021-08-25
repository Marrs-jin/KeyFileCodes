#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
from fractions import Fraction
import xlsxwriter
import decimal
from decimal import *
import re
from modsigfig import round #does this need to be done 
pd.set_option('display.max_rows', 500)
getcontext().prec = 20
#allowed: p to s, d, p. s to p. d to s, d.
# n anything below energy
# j = 1/2 to 1/2, 3/2. j = 3/2 to 3/2, 1/2, 5/2. j = 5/2 to 5/2, 3/2, 7/2. 


# In[2]:


# element_list = ['BaII', 'BeII', 'CaII', 'Cs', 'Fr', 'K', 'Li', 
#                 'MgII', 'Na', 'RaII', 'Rb', 'SrII']


# In[3]:


get_ipython().run_line_magic('run', '-i LoadFunctions.py')


# In[4]:


get_ipython().run_line_magic('run', '-i Format_save_copy.py')


# In[5]:


get_ipython().run_line_magic('run', '-i LoadInElement.py')


# In[6]:


duplicated_error = all_state[all_state.duplicated(['Terr'])]
if len(duplicated_error) == 0:
    print('No duplicated Errors, can run error calc2')
else:
    print('There are duplicated Transition rate Errors')
    raise SystemExit(0)


# In[7]:


og_lifetimes = Lifetimes.copy()


# In[8]:


save_copy = all_state.copy() #used to display error formatted numbers in TR table on main page


# In[9]:


#At this point:
#Wavelength and Error are in nm
#Transition Rate and Error are in s-1


# In[10]:


f_copy = save_copy.copy() #keeps f states
#Removes 'f' States and above
for i in range(len(save_copy)-1, 0, -1):
    if save_copy.Initial[i][1] >= 3:
        save_copy.drop(i, axis = 0, inplace = True)
save_copy.reset_index(drop = True, inplace = True)


# In[11]:


#Removes 'f' States and above
for i in range(len(Lifetimes)-1,0,-1): #counting backwards
    if Lifetimes[i][0][1] >= 3:
        del(Lifetimes[i])


# In[12]:


#this code is used to get the matrix values into the correct error format
#one to use if you haven't already modified mat_page
pattern = re.compile(r"\((\d+)\)")
holder = [] #holds the new numbers
big_terr = [] #holds transition rate indices with error > number
for p in range(len(mat_page)):
#for p in range(0, 3):
    ini = mat_page.Initial[p]
    end = mat_page.Decay[p]
    test_val = mat_page.precise_wave[p]
    test_err = mat_page.precise_Eerr[p]
    if float(test_err) == 0: #if there is no wavelength error
        #value_wl is wavelength to be stored
        value_wl = '%.4f' % test_val
    else:
        #condition 1 is for wavleenghts and Errors > 9.5
        if float(mat_page.wavelength[p]) and float(mat_page.Eerr[p]) > 9.5: #need to avoid sci. notat
            #len_figs = the difference between the digit placement of the number and its error. I.e. ####.## - ##.## will be 2
            len_figs = len(str(test_val).split('.')[0]) - len(str(test_err).split('.')[0])
            
            #9.5-10 will round up to 1 and lose a zero digit
            if float(str(test_err).replace('.', '').lstrip('0')[0:2]) >= 95 and float(str(test_err).replace('.', '').lstrip('0')[0:2]) >= 95:
                num_w = str(round(str(test_val), sigfigs = len_figs)).split('.')[0] #dont need to add one if it isnt double digits
                added_digit = 1
            else:
                num_w = str(round(str(test_val), len_figs + 1)).split('.')[0]
                added_digit = 0
    
            #number of zeroes is length of digits to the left of the decimal in the error, subtracted by 1
            if float(test_err) > 1: 
                numb = round(test_val, test_err).split('±')[0]
                erb = round(test_val, test_err, format = 'Drake')
                erb = re.search('\(([^)]+)', erb).group(1) #find number in ()
                num_zeroes = len(str(test_err).split('.')[0]) - 1 + added_digit
                num_e = '(' + round(str(test_err), sigfigs = 1)[0] + '0'*num_zeroes + ')'
                value_wl = num_w + num_e
            else:
                value_wl = to_one_dig(test_val, test_err) 
        #condition 2 is for Errors smaller than 9.5
        else: #small enough to not use sci.not
            one_dig = to_one_dig(test_val, test_err)
            two_dig = round(test_val, test_err, format = 'Drake') 

            if test_err == 0: #if no error use 4 digit wavelength 
                value_wl = mat_page.wavelength[p]

            #if two dig has error something like (97), one_dig has error (1). It rounds to 10 but then cuts the 0, which appears wrong
            #needs to be pushed up one digit spot. I.e. (2.45 (97) needs to be 2.5(1))
            elif one_dig[one_dig.find("(")+1:one_dig.find(")")][0] < two_dig[two_dig.find("(")+1:two_dig.find(")")][0]: 
                
#                 left_sigfs = len(one_dig.split('(')[0][0:-1]) - 1 #rounding to one less digit instead of slicing for rounding
#                 #Rounds original number to correct number of sig figs
#                 value_wl = str(round(test_val, sigfigs = left_sigfs)) + '(' + one_dig[one_dig.find("(")+1:one_dig.find(")")][0] + ')'  
                if test_err < .00005:
                    value_wl = mat_page.wavelength[p] #don't store error
                elif test_err < .0001:
                    value_wl = to_one_dig(test_val, '%.4f' % test_err)
                else:
                    #to_one_dig messes up if the number is something like .09452, so this uses to one dig small for those cases
                    #looks at first two digits
                    if float(str(test_err).split('.')[1].lstrip('0')[0:2]) >= 95 and float(str(test_err).split('.')[1].lstrip('0')[0:2]) < 95:
                        value_wl = to_one_dig_small(test_val, test_err)
                    else:
                        value_wl = to_one_dig(test_val, '%.4f' % test_err)
                    #value_wl = one_dig
                
                
            #otherwise, standard case
            else:
                #use the original error if the error is less than the .0001 cutoff, since otherwise error will not show up
                if test_err < .00005:
                    value_wl = mat_page.wavelength[p]
                    #code breaks if you pass in 0 error
                #smaller than .0001, needs to round to 4 digits
                elif test_err < .0001:
                    value_wl = to_one_dig(test_val, '%.4f' % test_err)
                #any other normal case error
                else:
                    value_wl = to_one_dig_small(test_val, test_err)
                    
    holder.append((value_wl))
#holder
mat_page['wavelength'] = [i for i in holder]


# In[13]:


bf_format = save_copy.copy() #to renew save_copy if you test anything below


# In[14]:


save_copy = bf_format.copy()


# In[15]:


#one to use if you haven't already modified save_copy
pattern = re.compile(r"\((\d+)\)")
holder = []
big_terr = [] #holds transition rate indices with error > number
for p in range(len(save_copy)):
#for p in range(0, 3):
    ini = save_copy.Initial[p]
    end = save_copy.Decay[p]
    test_val = save_copy.precise_wave[p]
    test_err = save_copy.precise_Eerr[p]
    if float(test_err) == 0:
        value_wl = '%.4f' % test_val
    else:
        #condition 1 is for wavleenghts and Errors > 9.5
        if float(save_copy.wavelength[p]) and float(save_copy.Eerr[p]) > 9.5: #need to avoid sci. notat
            #len_figs = the difference between the digit placement of the number and its error. I.e. ####.## - ##.## will be 2
            len_figs = len(str(test_val).split('.')[0]) - len(str(test_err).split('.')[0])
            
            #9.5-10 will round up to 1 and lose a zero digit
            if float(str(test_err).replace('.', '').lstrip('0')[0:2]) >= 95 and float(str(test_err).replace('.', '').lstrip('0')[0:2]) >= 95:
                num_w = str(round(str(test_val), sigfigs = len_figs)).split('.')[0] #dont need to add one if it isnt double digits
                added_digit = 1
            else:
                num_w = str(round(str(test_val), len_figs + 1)).split('.')[0]
                added_digit = 0
    
            #number of zeroes is length of digits to the left of the decimal in the error, subtracted by 1
            if float(test_err) > 1: 
                numb = round(test_val, test_err).split('±')[0]
                erb = round(test_val, test_err, format = 'Drake')
                erb = re.search('\(([^)]+)', erb).group(1)
                num_zeroes = len(str(test_err).split('.')[0]) - 1 + added_digit
                num_e = '(' + round(str(test_err), sigfigs = 1)[0] + '0'*num_zeroes + ')'
                value_wl = num_w + num_e
            else:
                value_wl = to_one_dig(test_val, test_err) 
        #condition 2 is for Errors smaller than 9.5
        else: #small enough to not use sci.not
            one_dig = to_one_dig(test_val, test_err)
            two_dig = round(test_val, test_err, format = 'Drake') 

            if test_err == 0: #if no error use 4 digit wavelength 
                value_wl = save_copy.wavelength[p]

            #if two dig has error something like (97), one_dig has error (1). It rounds to 10 but then cuts the 0, which appears wrong
            #needs to be pushed up one digit spot. I.e. (2.45 (97) needs to be 2.5(1))
            elif one_dig[one_dig.find("(")+1:one_dig.find(")")][0] < two_dig[two_dig.find("(")+1:two_dig.find(")")][0]: 
                
#                 left_sigfs = len(one_dig.split('(')[0][0:-1]) - 1 #rounding to one less digit instead of slicing for rounding
#                 #Rounds original number to correct number of sig figs
#                 value_wl = str(round(test_val, sigfigs = left_sigfs)) + '(' + one_dig[one_dig.find("(")+1:one_dig.find(")")][0] + ')'  
                if test_err < .00005:
                    value_wl = save_copy.wavelength[p]
                elif test_err < .0001:
                    value_wl = to_one_dig(test_val, '%.4f' % test_err)
                else:
                    #to_one_dig messes up if the number is something like .09452, so this uses to one dig small for those cases
                    #looks at first two digits
                    if float(str(test_err).split('.')[1].lstrip('0')[0:2]) >= 95 and float(str(test_err).split('.')[1].lstrip('0')[0:2]) < 95:
                        value_wl = to_one_dig_small(test_val, test_err)
                    else:
                        value_wl = to_one_dig(test_val, '%.4f' % test_err)
                    #value_wl = one_dig
                
                
            #otherwise, standard case
            else:
                #use the original error if the error is less than the .0001 cutoff, since otherwise error will not show up
                if test_err < .00005:
                    value_wl = save_copy.wavelength[p]
                    #code breaks if you pass in 0 error
                #smaller than .0001, needs to round to 4 digits
                elif test_err < .0001:
                    value_wl = to_one_dig(test_val, '%.4f' % test_err)
                #any other normal case error
                else:
                    value_wl = to_one_dig_small(test_val, test_err)
    
    #repeat for Transition Rates, Branching Ratios
    if save_copy.Terr[p] > save_copy['transition_rate s-1'][p]: 
        #round breaks if error is greater, mark it on big_terr and it is fixed later
        big_terr.append(p)
        value_tr = round(str(save_copy['transition_rate s-1'][p]), str(save_copy.Terr[p]), format = "Drake")
        try:
            if value_tr.split('.')[1][0] == '(': #sometimes there is #. with nothing to the right
                value_tr = value_tr.replace('.', '')
            else:
                pass
        except IndexError:
            pass
        #print(value_tr, float(value_tr.split('(')[0]), float(value_tr.split('(')[0][-2:]))
        #if there are 2 or more numbers in parentheses, no exponents, not a decimal, and the number is greater than 1
        if len(value_tr.split('(')[0]) >= 2 and 'E' not in value_tr and '.' not in value_tr and float(value_tr.split('(')[0]) > 1:
            value_tr_num = format_e(value_tr.split('(')[0])
            value_tr_err = '('  + value_tr.split('(')[1]
            value_tr = value_tr_num.split('E')[0] + value_tr_err + 'E' + value_tr_num.split('E')[1]
        #if the first two digits of the number are greater than 2? and no exponent and number is less than 1
        elif len(value_tr.split('(')[0]) >= 2  and 'E' not in value_tr and float(value_tr.split('(')[0]) < 1:
            value_tr_num = format_e(value_tr.split('(')[0])
            value_tr_err = '('  + value_tr.split('(')[1]
            value_tr = value_tr_num.split('E')[0] + value_tr_err + 'E' + value_tr_num.split('E')[1]
    else: 
        value_tr = round(str(save_copy['transition_rate s-1'][p]), str(save_copy.Terr[p]), format = "Drake")
        if 'E' in value_tr:
            pass
        else:
            numt = "{:E}".format(Decimal(value_tr.split('(')[0])).split('E')
            if float(numt[1]) < 10 and float(numt[1]) != 0: #need to add '0' in front of value if exponent power is less than 10
                if float(value_tr.split('(')[0]) >= 1:
                    value_tr = numt[0] + '(' + value_tr.split('(')[1] + 'E' + '+' + '0' + str(int(numt[1]))
                else: #negative case: use -, get rid of - in front of number
                    value_tr = numt[0] + '(' + value_tr.split('(')[1] + 'E' + '-' + '0' + str(int(numt[1].replace('-','')))
            elif float(numt[1]) == 0:
                value_tr = numt[0] + '(' + value_tr.split('(')[1]
            else:
                value_tr = numt[0] + '(' + value_tr.split('(')[1] + 'E' + numt[1]
    if float(save_copy.Berr[p]) == 0:
        value_br = '1.0'
    else:
        value_br = round(str(save_copy['branching ratio'][p]), str(save_copy.Berr[p]), format = "Drake")
    holder.append((value_wl, value_tr, value_br))
save_copy['wavelength'] = [i[0] for i in holder]
save_copy['transition_rate s-1'] = [i[1] for i in holder]
save_copy['branching ratio'] = [i[2] for i in holder]


# In[16]:


#changes values in wavelength to sci. not if the (####) format is 4 digits or more
#for matrix values
for p in range(len(mat_page)):
    wav_val = mat_page['wavelength'][p]
    try:
        err_dig = re.search('\(([^)]+)', wav_val).group(1)
    #does the except loop when there is no error () 
    except AttributeError:
        break
    if len(err_dig) >= 4:
        num_figs = len(wav_val.split('(')[0]) - len(err_dig)
        dec_format = "%%.%sE" % np.abs(int(num_figs))
        new_wav = dec_format % float(all_state.wavelength[p])
        #number before exponent, first digit of (####), rest of Exponenent
        new_wav_num = new_wav.split('E')[0]
        new_wav_err = err_dig[0] 
        new_wav_exp = new_wav.split('E')[1]
        new_wav_val = new_wav_num + '(' + new_wav_err + ')' + 'E' + new_wav_exp
        mat_page.loc[p, 'wavelength'] = new_wav_val


# In[17]:


#changes values in wavelenght to sci. not if the (####) format is 4 digits or more
#for TR, BR
for p in range(len(save_copy)):
    wav_val = save_copy['wavelength'][p]
    try:
        err_dig = re.search('\(([^)]+)', wav_val).group(1)
    #does the except loop when there is no error () 
    except AttributeError:
        break
    if len(err_dig) >= 4:
        num_figs = len(wav_val.split('(')[0]) - len(err_dig)
        dec_format = "%%.%sE" % int(num_figs)
        new_wav = dec_format % float(all_state.wavelength[p])
        #number before exponent, first digit of (####), rest of Exponenent
        new_wav_num = new_wav.split('E')[0]
        new_wav_err = err_dig[0] 
        new_wav_exp = new_wav.split('E')[1]
        new_wav_val = new_wav_num + '(' + new_wav_err + ')' + 'E' + new_wav_exp
        save_copy.loc[p, 'wavelength'] = new_wav_val


# In[18]:


#changes out of scientific notation if the error in parentheses (###) could be 3 or less digits
#transition rates where the error is > Number

for j, i in enumerate(save_copy['transition_rate s-1']):
    if ('E' in i) and (j not in big_terr):
        num_in_par = '(' + re.search('\(([^)]+)', i).group(1) + ')' #number in parentheses
        len_sfigs = len(i.split('(')[0]) - 1 #number of digits before expontial, minus the decimal point
        float_num = round(i.replace(num_in_par, ''), sigfigs = len_sfigs) #number in float format
        num_zeroes = len(str(i.split('.')[0])) - (len(num_in_par) - 2) #difference in original number digits - two error format digits
        new_error = re.search('\(([^)]+)', i).group(1) + '0'*num_zeroes #error with correct number of '0's
        if len(new_error) > 4: #keep it in scientific notation if you have to go past 4 digits in error parentheses
            save_copy.loc[j,'transition_rate s-1'] = float_num + '(' + new_error + ')'
            #print(new_error, float_num + '(' + new_error + ')')
        else:
            pass


# In[19]:


#gets lifetimes into "#A#/#" format i.e. 4s1/2
def format_lifetime(x, y):
    """takes in Lifetimes as pandas DF, Lifetimes as list"""
    Lifetimes = x
    life_lin = y
    Lifetimes = pd.DataFrame(Lifetimes, columns = ['State', 'Lifetime', 'Error'])
    repl_ind = []

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
    
    #delete f and above
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
    exp_l_name = 'Experimental_Data\\%s-lifetimes.csv' % element
    
    #exp_l_name = 'Experimental_Data\\%s-lifetimes.csv' % element
    try:
        exp_l = pd.read_csv(exp_l_name) #experiment
        a = list(Lifetimes.State)
        c = list(zip(a))

        d = list(exp_l.State)
        f = list(zip(d))

        
        comparison = []
        
        for i in range(len(c)):
            try:
                
                if exp_l.Units[f.index(c[i])] == 'ns':
                    Lifetime_excel.iloc[i, Lifetime_excel.columns.get_loc('Lifetime')] = exp_l['Value'][f.index(c[i])]
                    Lifetime_excel.iloc[i, Lifetime_excel.columns.get_loc('Error')] = exp_l['Uncertainty'][f.index(c[i])]
                    life_exp = exp_l['Lifetime'][f.index(c[i])]
                    Lifetimes.iloc[i, Lifetimes.columns.get_loc('Lifetime')] = life_exp + exp_l['Ref'][f.index(c[i])]
                    repl_ind.append(i) #index to be replaced
                else:
                    Lifetime_excel.iloc[i, Lifetime_excel.columns.get_loc('Lifetime')] = exp_l['Value'][f.index(c[i])] * 10**9
                    Lifetime_excel.iloc[i, Lifetime_excel.columns.get_loc('Error')] = exp_l['Uncertainty'][f.index(c[i])] * 10**9
                    life_exp = exp_l['Lifetime'][f.index(c[i])] * 10**9
                    Lifetimes.iloc[i, Lifetimes.columns.get_loc('Lifetime')] = str(float(str(life_exp).replace(parent_num, ''))*10**9) + exp_l['Ref'][f.index(c[i])]
                    repl_ind.append(i)
        #         comparison.append((i, f.index(c[i]), Lifetime['transition_rate (s-1)'][i], exp['value'][f.index(c[i])], 
        #                           exp['uncertainity'][f.index(c[i])]))
            except ValueError:
                pass
    except FileNotFoundError:
        pass
        
    Lifetimes.drop('Error', axis = 1, inplace = True)
    return Lifetimes, life_lin, Lifetime_excel, repl_ind


# In[20]:


#call format lifetime to get Lifetime into display format
#returns Lifetimes as pandas, lifetimes as list, Lifetime for excel format, indices of replaced values
Lifetime_excel = Lifetimes.copy()
Lifetimes2 = Lifetimes.copy()

#formats the Lifetime into spd and such
tl1, tl2, tl3, tl4 = format_lifetime(Lifetimes, life_linear)
Lifetimes = tl1
Lifetime_excel = tl3
life_rep_ind = tl4


# In[21]:


#changes lifetime to sci. notation if 4 errors digits in ()
for j, i in enumerate(Lifetimes.Lifetime):
    if ('E+' in i) or ('E-' in i):
        #print(i)
        num_in_par = '(' + re.search('\(([^)]+)', i).group(1) + ')' #number in parentheses
        len_sfigs = len(i.split('(')[0]) - 1 #number of digits before expontial, minus the decimal point
        float_num = round(i.replace(num_in_par, ''), sigfigs = len_sfigs) #number in float format
        num_zeroes = len(str(life_linear[j][2]*10**9).split('.')[0]) - (len(num_in_par) - 2) #difference in original number digits - two error format digits
        new_error = re.search('\(([^)]+)', i).group(1) + '0'*num_zeroes #error with correct number of '0's
        if len(new_error) < 4: #keep it in scientific notation if you have to go past 4 digits in error parentheses
            Lifetimes.loc[j,'Lifetime'] = float_num + '(' + new_error + ')'
            #print(j, float_num + '(' + new_error + ')')
        else:
            pass


# In[22]:


#gets save_copy into display format
test = formatter(save_copy)
#since formatter doesn't change indices the columns are still in same order and this is ok
#modif just stores the * mark
test['modif'] = save_copy['modif']
save_copy = test


# In[23]:


df2 = pd.read_fwf(checklifesname, dtype = str)


# In[24]:


def ReadCsv(fileToRead,colDelim = ",", rowDelim = "\n"):
    fileHandle = open(fileToRead,"r")
    fileContent = fileHandle.read()
    fileLines = fileContent.split(rowDelim)
    fileAsListOfLists = [k.split(colDelim) for k in fileLines]
    return fileAsListOfLists


# In[25]:


file_values = ReadCsv(checkratesname, colDelim = "s+")
my_cols = ['Initial', 'Decay',     'Wavelength', 'Wave Ref',  'Matrix', 'Mat Ref',
             'Br. ratio',  'Tran. rate',    'wave2',     'UncW', 'UncW %', 'Matrix el.', 
             'uncM', 'uncM %', 'Br2', 'uncB', 'uncB %', 'Tran2',  'UncT',   'UncT %'] 
df = pd.DataFrame(columns = my_cols)


#start at 1 to avoid header
#goes to -1 because last row is blank
df_values = []
for i in range(1, len(file_values) -1):
    #the values
    test_list = file_values[i][0].split(' ')
    #removes blank spaces
    while("" in test_list) : 
        test_list.remove("") 
    #there is no reference for either Wavelength or Matrix Element, or both
    if len(test_list) < 20:
        #if no reference for wavelength, put in blank space
        if ('*' in test_list) == False:
            test_list.insert(3, '')
        #if length still low, there is no matrix reference
        if len(test_list) < 20:
            test_list.insert(5, '')
        
    df_values.append(test_list)
    
df_series = []
for i in df_values:
    ser = pd.Series(i, index = df.columns)
    df_series.append(ser)
df = df.append(df_series, ignore_index = True)


# In[26]:


#Wavelengths
all_differences = []
diff_holdt = []
for i in range(len(save_copy)):
    t_ind = np.where((save_copy.Initial == df.Initial[i]) & (save_copy.Decay == df.Decay[i]))[0][0] #same transition
    #print(save_copy['Wavelength (nm)'][t_ind], df['Wavelength'][i])
    if save_copy['Wavelength (nm)'][t_ind] == df.Wavelength[i]:
        pass
    else:
        diff_holdt.append((i, t_ind, save_copy.Initial[t_ind], save_copy.Decay[t_ind], save_copy['Wavelength (nm)'][t_ind], df.Wavelength[i], all_state.wavelength[t_ind], all_state.Eerr[t_ind]))
all_differences.append(diff_holdt)
#diff_holdt


# In[27]:


#should it be in range len(df)?
#Matrices
#Note, my matrices have "E" in the number
diff_holdt = []
for i in range(len(save_copy)):
    t_ind = np.where((save_copy.Initial == df.Initial[i]) & (save_copy.Decay == df.Decay[i]))[0][0] #same transition
    #print(save_copy['Wavelength (nm)'][t_ind], df['Wavelength'][i])
    if save_copy['Matrix element (a.u.)'][t_ind].lstrip('0').lstrip('.').lstrip('0').split('E')[0] == df.Matrix[i].lstrip('0').lstrip('.').lstrip('0'):
        pass
    else:
        diff_holdt.append((i, t_ind, save_copy['Matrix element (a.u.)'][t_ind], df.Matrix[i], all_state.matrix[t_ind], all_state.mat_unc[t_ind]))

all_differences.append(diff_holdt)
#diff_holdt


# In[28]:


#Transition Rates
diff_holdt = []
for i in range(len(save_copy)):
    t_ind = np.where((save_copy.Initial == df.Initial[i]) & (save_copy.Decay == df.Decay[i]))[0][0] #same transition
    #print(save_copy['Wavelength (nm)'][t_ind], df['Wavelength'][i])
    #print(holder[t_ind][2].lstrip('0').lstrip('.').lstrip('0'), df['Br. ratio'][i].lstrip('0').lstrip('.').lstrip('0'))
    if save_copy['Transition Rate (s-1)'][t_ind] == df['Tran. rate'][i]:
        pass
    else:
        diff_holdt.append((i, t_ind, save_copy['Transition Rate (s-1)'][t_ind], df['Tran. rate'][i], all_state['transition_rate s-1'][t_ind], all_state.Terr[t_ind]))

all_differences.append(diff_holdt)
#diff_holdt


# In[29]:


#branching ratios
diff_holdt = []
for i in range(len(save_copy)):
    t_ind = np.where((save_copy.Initial == df.Initial[i]) & (save_copy.Decay == df.Decay[i]))[0][0] #same transition
    if save_copy['Branching ratio'][t_ind].lstrip('0').lstrip('.').lstrip('0') == df['Br. ratio'][i].lstrip('0').lstrip('.').lstrip('0'):
        pass
    else:
        diff_holdt.append((i, t_ind, save_copy['Branching ratio'][t_ind], df['Br. ratio'][i], all_state['branching ratio'][t_ind], all_state.Berr[t_ind]))

all_differences.append(diff_holdt)
#diff_holdt


# In[30]:


#Lifetimes
#Note: my lifetimes have '*' in the number
diff_holdt = []
for i in range(len(df2)):
    t_ind = np.where(Lifetimes.State == df2.State[i]) #same transition
    #print(save_copy['Wavelength (nm)'][t_ind], df['Wavelength'][i])
    #print(holder[t_ind][2].lstrip('0').lstrip('.').lstrip('0'), df['Br. ratio'][i].lstrip('0').lstrip('.').lstrip('0'))
    if Lifetimes.Lifetime[t_ind[0][0]].replace('*', '') == df2['Lifetime'][i]:
        pass
    else:
        diff_holdt.append((i, t_ind, Lifetimes.Lifetime[t_ind[0][0]], df2['Lifetime'][i]))

all_differences.append(diff_holdt)
#diff_holdt


# In[31]:


summed_differences = 0
there_are_dff = False
for i in all_differences:
    summed_differences += len(i)
    
array_names = ['Wavelengths', 'Matrices', 'Transition Rates', 'Branching Ratios', 'Lifetimes']
print(summed_differences, f"Number of different data points in all arrays for element {element}")
if summed_differences > 0:
    for i, j in enumerate(all_differences):
        #print(array_names[i], j)
        there_are_dff = True
    if there_are_dff == True:
        print('Not all values match between Adam and Safronova error format')
        #raise SystemExit("Stop right there! Not all Values match")


# In[32]:


Life_holder = Lifetimes.copy()


# In[33]:


#sanity check that no branching ratio is greater than 1
for i,j in enumerate(all_state['branching ratio']):
    if float(j) > 1: 
        print(i, j, all_state['Initial'][i], all_state['Decay'][i], 'BRANCHING RATIO > 1!')
        break


# In[34]:


#print(len(save_copy), len(df))
if len(save_copy) != len(df):
    raise SystemExit("Stop right there! My array and df array are not same length")


# In[35]:


#puts '*' on wavelength value if if needs it, removes 'modif' columns
for i in range(len(save_copy)):
    if save_copy['modif'][i] == '*':
        save_copy['Wavelength (nm)'][i] += '*'
save_copy.drop(columns = ['modif'], inplace = True)


# In[36]:


get_ipython().run_line_magic('run', '-i To_HTML_CSV')


# In[37]:


with open('Format_csvs/TransitionRates/Intro_to_life_formatting.txt', 'r') as file:
    format_hold_intro = file.read()


# In[38]:


with open(f'Format_csvs/TransitionRates/{element}ButtonList.txt', 'r') as file:
    button_lst = file.read()


# In[39]:


with open('Format_csvs/TransitionRates/Life_to_excel_formatting.txt', 'r') as file:
    format_hold_excel = file.read()


# In[40]:


with open('Format_csvs/TransitionRates/Excel_to_main_formatting.txt', 'r') as file:
    format_hold_main = file.read()


# In[41]:


with open('Format_csvs/TransitionRates/End_formatting.txt', 'r') as file:
    format_hold_end = file.read()


# In[42]:


nist_urls = pd.read_csv(r"Data\nist_urls.csv",
                        header = None, names = ["Element", "URL"], index_col = 0)


# In[43]:


def name_to_display(name):
    """takes in an element or key in format 'Rb1', 'CsII', etc
        and makes the appropriate display like 'Rb', 'Cs+'
        Output is (display format, just_element with no number, number of ionization (starting at 0))
    """
    
    #number attached to name of element
    element_ion_number = (re.findall('\d+', name ))[0] #replace with element
    #the name without the number
    element_just_name = name.split(element_ion_number)[0] #replace with element
    element_ion_number = int(element_ion_number) - 1 #reduce one for correct number of '+'
    element_display = element_just_name + '+' * element_ion_number #name combined with number of '+'
    return element_display, element_just_name, element_ion_number
#name_to_display('Ca2')


# In[44]:


#NOTE: YOU NEED TO GO INTO THE KEY FILE AND CHANGE IT TO <sup></sup> for the header!
#########
#NOTE: NEED TO INCLUDE IN DOCUMENTATION THAT NIST_URLS HAS TO BE UPDATED PER ELEMENT
#######
#NOTE: MAKE UNIVERSAL SUBSCRIPT LIST


# In[45]:


#the active tag of the top menu is currently on {key} is removed. i.e. if Rb is active it will change to non-active and not
#be highlighted
key = 'Cs1' #the last element to have the modfications done, so what needs to be replaced for the others

key_info = name_to_display(key) #display, just name, number of ionization
element_info = name_to_display(element)
key_display = key_info[0]
ele_display = element_info[0]

#str1 rep1 takes the default active dropdown and removes the active key
#str2 rep2 finds the correct dropdown and adds the active key
#the if statement is in case the key is also the correct element
str1 = f'<a class="dropdown-item active" href="{key}TranAuto.html">{key_display}</a>'
rep1 = f'<a class="dropdown-item" href="{key}TranAuto.html">{key_display}</a>'
ind1 = format_hold_intro.find(str1) #index of where string1 is

#change the filename of the excel file to this element
stra = f"filename: '{key}TransitionRates',"
repa = f"filename: '{element}TransitionRates',"

str2 = f'<a class="dropdown-item" href="{element}TranAuto.html">{ele_display}</a>'
rep2 = f'<a class="dropdown-item active" href="{element}TranAuto.html">{ele_display}</a>'

ind2 = format_hold_intro.find(str2)
#Key element case, it is already active so there is no inactive version
if ind2 < 0:
    rep2 = str1
print(ind1, 'ind1')
print(ind2, 'ind2')

str3 = f'E1 Transition data for {key_info[1]}<sup>{key_info[2]*"+"}</sup>' #ex: {Ca}, {1} * '+'
rep3 = f'E1 Transition data for {element_info[1]}<sup>{element_info[2]*"+"}</sup>'
ind3 = format_hold_intro.find(str3)
print(ind3, 'ind3')

str4 = f'<td><button class="button"id="All"onclick="location.href=\'{key}TranFull.html\'"> All</button></td>'
rep4 = f'<td><button class="button"id="All" onclick="location.href=\'{element}TranFull.html\';">All</button></td>'
ind4i = format_hold_intro.find(str4)
ind4f = ind4i + format_hold_intro[ind4i:].find('</tr>') + 7
print(ind4i, 'ind4')

str5 = f'<title>{key_display}</title>'
rep5 = f'<title>{ele_display}</title>'
ind5 = format_hold_intro.find(str5)
print(ind5, 'ind5')

#NIST is in format 'Rb+I' or "Ca+II", so need to combine the name without the number with the ionization number (+ 1) times 'I'
strRef = f'href="https://physics.nist.gov/cgi-bin/ASD/energy1.pl?de=0&spectrum={key_info[1]}+{(key_info[2] + 1) * "I"}&submit=Retrieve+Data&units=0&format=0&output=0&page_size=15&multiplet_ordered=0&conf_out=on&term_out=on&level_out=on&unc_out=1&j_out=on&lande_out=on&perc_out=on&biblio=on&temp=">'
url_ref = nist_urls[nist_urls.index == element]['URL'][0]
urlRef = 'href='+ '\"' + url_ref+'\">'

#the file locations of the property switching buttons in the header are changed from the key to the current element
str_MEbut = f'onclick="location.href = \'{key}.html\';">Matrix elements'
str_Polbut = f'onclick="location.href = \'{key}Polarizability.html\';">Polarizability'
str_ODbut = f'onclick="location.href = \'{key}Other.html\';">Other data'

rep_MEbut = f'onclick="location.href = \'{element}.html\';">Matrix elements'
rep_Polbut = f'onclick="location.href = \'{element}Polarizability.html\';">Polarizability'
rep_ODbut = f'onclick="location.href = \'{element}Other.html\';">Other data'

ind_MEbut = format_hold_intro.find(str_MEbut)
ind_Polbut = format_hold_intro.find(str_Polbut)
ind_ODbut = format_hold_intro.find(str_ODbut)
print(ind_MEbut, 'ME property ind', ind_Polbut, 'Pol button ind', ind_ODbut, 'OD button ind')

intro_format = format_hold_intro.replace(str1, rep1, 2)
intro_format = intro_format.replace(stra, repa, 2)
intro_format = intro_format.replace(str2, rep2, 2)
intro_format = intro_format.replace(str3, rep3, 2)
intro_format = intro_format.replace(str4, rep4, 2)
intro_format = intro_format.replace(str5, rep5, 2)
intro_format = intro_format.replace(strRef, urlRef, 2)
intro_format = intro_format.replace(str_MEbut, rep_MEbut, 2)
intro_format = intro_format.replace(str_Polbut, rep_Polbut, 2)
intro_format = intro_format.replace(str_ODbut, rep_ODbut, 2)

#index of the "all" line, start of when we need to add buttons
split_start = intro_format.find(rep4)
#index of the end of that line 
split_ind = split_start + intro_format[split_start:].find('</tr>') + 7
#all the text before the button list
first_half = intro_format[:split_ind]


# In[46]:


#load in metastable elements
meta_all_fname = r"OtherData\Metastable_elements.txt"
meta_all = pd.read_csv(meta_all_fname, engine='python', header = None, names = ['element'])
metastable_elements = list(meta_all['element'])


# In[47]:


#add in bottom metastable warning for select elements
#list of metastable states is taken from Metastble states.xlsx file
if element in metastable_elements:
    metastable_states = [['3d3/2', '3d5/2'], ['4d3/2', '4d5/2'], ['5d3/2', '5d5/2'], ['6d3/2', '6d5/2']] #need to be in same element order
    sub_scriptsMet = ['1/2', '3/2', '5/2', '7/2', '9/2', '11/2']
    for q in sub_scriptsMet:
        for j in metastable_states:
            for i in j:
                val = i
                index_row = [metastable_states.index(row) for row in metastable_states if val in row]
                index_column = [row.index(val) for row in metastable_states if val in row]

                i = i.replace('%s' % q, '<sub>%s</sub>' % q)
                metastable_states[index_row[0]][index_column[0]] = i

    b_front = button_lst[:button_lst.find('</table>')] #all the buttons of the button list
    b_end = button_lst[button_lst.find('</table>'):] #end styling </table>
    el_ind = metastable_elements.index(element) #which state to use

    #the actual text
    click_text = f'<caption align="bottom" style = "color: black; padding-top: 15px;">Click <a href = "{element}Other.html" target="_blank" >here </a> for the metastable state properties'
    click_text += f'\n<br> <p align = "center" style = "font-size: 15px;"> {metastable_states[el_ind][0]}  {metastable_states[el_ind][1]}</p> </caption>'
    button_lst = b_front + click_text + '\n\n' + b_end



#where to start cutoff of button list, where to stop Button button cutoff and start again. 7 to remove </td> /n
strBi = '<td><button class="button"id="All" onclick="window.location.href'
indBi = button_lst.find(strBi)
indBf = indBi + button_lst[indBi:].find('</tr>') + 7

#where to start the formatting again, find where the list from button says 'navpol'
split_end = intro_format.find('</navpol>')
end_ind = split_end + 11
second_half = intro_format[end_ind:]
#combine 3 items together
intro_format = first_half + button_lst[indBf:] + second_half
        


# In[48]:


#makes list of display format references for table. This will be searched for in the experimental data
#list of reference names
refr_names = []
#list of indices that have references
refr_ind = []
#makes list of all Initial and Final state names for items with references
for i, j in enumerate(save_copy['Matrix element (a.u.)']):
    if 'E' in j:
        refr_names.append((save_copy.Initial[i], save_copy.Decay[i]))
        refr_ind.append(i)
        
sub_scripts = ['1/2', '3/2', '5/2', '7/2', '9/2', '11/2']
inis = []
ends = []
#changes 1/2, 3/2, ... to subscript. stores in refrnamessub
for j, k in enumerate(refr_names):
    for i in sub_scripts:
        if i in k[0]:
            #print(i, k[0].replace('%s' % i, '<sub>%s</sub>' % i))
            inis.append(k[0].replace('%s' % i, '<sub>%s</sub>' % i))
        if i in k[1]:
            ends.append(k[1].replace('%s' % i, '<sub>%s</sub>' % i))
        #refr_namessub.append((a,b))
a = np.array(inis)
b = np.array(ends)
refr_namessub = np.vstack((a, b)).T
#refr_namessub


# In[49]:


tabl_main = htmls[0] #save_copy
excel_fname = r"Experimental_Data\Key-File.csv"
ref_exl = pd.read_csv(excel_fname, usecols = ['Key', 'Reference', 'DOI'])
for i in range(len(refr_namessub)):
    #where the Initial Final state shows up
    name_start = tabl_main.find(f'<td>{refr_namessub[i][0]}</td>\n      <td>{refr_namessub[i][1]}</td>')
    #How many characters until where the 'E' reference starts in that substring
    E_start = tabl_main[name_start:].find('E')
    #print(name_start, E_start)


# In[50]:


#set up references for display table
style = "display:none"
tabl_main = htmls[0] #save_copy
ref_exl = pd.read_csv(excel_fname, usecols = ['Key', 'Reference', 'DOI'])
for i in range(len(refr_namessub)):
    #where the Initial Final state shows up
    name_start = tabl_main.find(f'<td>{refr_namessub[i][0]}</td>\n      <td>{refr_namessub[i][1]}</td>')
    #How many characters until where the 'E' reference starts in that substring
    E_start = tabl_main[name_start:].find('E')
    #How many characters until Where the reference ends
    E_end = tabl_main[name_start+E_start:].find('<')
    #The reference name
    E_name = tabl_main[name_start + E_start: name_start + E_start + E_end]
    

    #only 1 reference
    if '/' not in E_name:
        #the button html text
        btn_name = tabl_main[name_start + E_start: name_start + E_start + E_end].replace(f'{E_name}', f' <button type="button" class="btn btn-primary Ref1" data-toggle="modal" data-target="#exampleModalCenter">Ref</button></td> \n \t\t\t<td style = "display:none">{E_name}</td>')
        
        #reference name 
        reference = ref_exl['Reference'][ref_exl[ref_exl['Key'] == f'{E_name}'].index[0]]
        #DOI URl
        doi = ref_exl['DOI'][ref_exl[ref_exl['Key'] == f'{E_name}'].index[0]]
        td1 = f'\t\t\t<td style = "display:none" class="nr">{reference}</td>'
        td2 = f'\t\t\t<td style = "display:none" class="nr2">{doi}</td>'
        td3 = ''
        td4 = ''
        td5 = ''
    
    #2 references
    else:
        #first reference, second reference
        E_name1 = E_name.split('/')[0]
        E_name2 = E_name.split('/')[1]
        btn_name = tabl_main[name_start + E_start: name_start + E_start + E_end].replace(f'{E_name}', f' <button type="button" class="btn btn-primary Ref1" data-toggle="modal" data-target="#exampleModalCenter">Ref</button></td> \n \t\t\t<td style = "display:none">{E_name1}</td>')
        
        reference1 = ref_exl['Reference'][ref_exl[ref_exl['Key'] == f'{E_name1}'].index[0]]
        doi1 = ref_exl['DOI'][ref_exl[ref_exl['Key'] == f'{E_name1}'].index[0]]
        td1 = f'\t\t\t<td style = "display:none" class="nr">{reference}</td>'
        td2 = f'\t\t\t<td style = "display:none" class="nr2">{doi}</td>'
        
        td3 = f'\t\t\t<td style = "display:none">{E_name2}</td>'
        reference2 = ref_exl['Reference'][ref_exl[ref_exl['Key'] == f'{E_name2}'].index[0]]
        doi2 = ref_exl['DOI'][ref_exl[ref_exl['Key'] == f'{E_name2}'].index[0]]
        td4 = f'\t\t\t<td style = "display:none" class="nr3">{reference2}</td>'
        td5 = f'\t\t\t<td style = "display:none" class="nr4">{doi2}</td>'
    #print(name_start, E_start, E_name,  tabl_main[name_start + E_start + E_end+5:])
    tabl_main = tabl_main[:name_start + E_start] + btn_name + '\n' +     td1 + '\n' + td2 + '\n' + td3 + '\n' + td4 + td5 + '\n' + tabl_main[name_start + E_start + E_end+5:] + '\n'


# In[51]:


#LIFETIMES
refr_names = []
#makes list of all Initial and Final state names for items with references
for i, j in enumerate(Lifetimes['Lifetime']):
    if 'E' in j and (i in life_rep_ind):
        refr_names.append(Lifetimes.State[i])
        
sub_scripts = ['1/2', '3/2', '5/2', '7/2', '9/2', '11/2']
inis = []
ends = []
#changes 1/2, 3/2, ... to subscript. stores in refrnamessub
for j, k in enumerate(refr_names):
    for i in sub_scripts:
        if i in k:
            inis.append(k.replace('%s' % i, '<sub>%s</sub>' % i))
#a = np.array(inis)
refr_namessub_life = inis
refr_namessub_life

style = "display:none"
tabl_life = htmls[1] #save_copy

ref_exl = pd.read_csv(excel_fname, usecols = ['Key', 'Reference', 'DOI'])
for i in range(len(refr_namessub_life)):
    #where the Initial Final state shows up
    name_start = tabl_life.find(f'<td>{refr_namessub_life[i]}</td>')
    #How many characters until where the 'E' reference starts in that substring
    E_start = tabl_life[name_start:].find('E')
    #How many characters until Where the reference ends
    E_end = tabl_life[name_start+E_start:].find('<')
    #The reference name
    E_name = tabl_life[name_start + E_start: name_start + E_start + E_end]
    

    #only 1 reference
    if '/' not in E_name:
        #the button html text
        btn_name = tabl_life[name_start + E_start: name_start + E_start + E_end].replace(f'{E_name}', f' <button type="button" class="btn btn-primary Ref1" data-toggle="modal" data-target="#exampleModalCenter">Ref</button></td> \n \t\t\t<td style = "display:none">{E_name}</td>')
        
        #reference name 
        reference = ref_exl['Reference'][ref_exl[ref_exl['Key'] == f'{E_name}'].index[0]]
        #DOI URl
        doi = ref_exl['DOI'][ref_exl[ref_exl['Key'] == f'{E_name}'].index[0]]
        td1 = f'\t\t\t<td style = "display:none" class="nr">{reference}</td>'
        td2 = f'\t\t\t<td style = "display:none" class="nr2">{doi}</td>'
        td3 = ''
        td4 = ''
        td5 = ''
    
    #2 references
    else:
        #first reference, second reference
        E_name1 = E_name.split('/')[0]
        E_name2 = E_name.split('/')[1]
        btn_name = tabl_life[name_start + E_start: name_start + E_start + E_end].replace(f'{E_name}', f' <button type="button" class="btn btn-primary Ref1" data-toggle="modal" data-target="#exampleModalCenter">Ref</button></td> \n \t\t\t<td style = "display:none">{E_name1}</td>')
        
        reference1 = ref_exl['Reference'][ref_exl[ref_exl['Key'] == f'{E_name1}'].index[0]]
        doi1 = ref_exl['DOI'][ref_exl[ref_exl['Key'] == f'{E_name1}'].index[0]]
        td1 = f'\t\t\t<td style = "display:none" class="nr">{reference}</td>'
        td2 = f'\t\t\t<td style = "display:none" class="nr2">{doi}</td>'
        
        td3 = f'\t\t\t<td style = "display:none">{E_name2}</td>'
        reference2 = ref_exl['Reference'][ref_exl[ref_exl['Key'] == f'{E_name2}'].index[0]]
        doi2 = ref_exl['DOI'][ref_exl[ref_exl['Key'] == f'{E_name2}'].index[0]]
        td4 = f'\t\t\t<td style = "display:none" class="nr3">{reference2}</td>'
        td5 = f'\t\t\t<td style = "display:none" class="nr4">{doi2}</td>'
    #print(name_start, E_start, E_name,  tabl_life[name_start + E_start + E_end+5:])
    tabl_life = tabl_life[:name_start + E_start] + btn_name + '\n' +     td1 + '\n' + td2 + '\n' + td3 + '\n' + td4 + td5 + '\n' + tabl_life[name_start + E_start + E_end+5:] + '\n'


# In[52]:



#have to do this before adding references
tabl_excel = htmls[3]
swap_e = str.maketrans("e", "E") 
tabl_excel = tabl_excel[tabl_excel.find('<tbody>\n') + 9:].translate(swap_e) 
#note, this makes the final </tablE>


# In[53]:


#ap is what will be used for excel table
ap = excel_copy.copy()
#set up column names for () format
ap['Matrix Element'] = ''
ap['Wavelength'] = ''
ap['Transition Rate'] = ''
ap['Branching Rat.'] = ''
ap['Reference'] = ''
ap['DOI'] = ''
ap['Reference 2'] = ''
ap['DOI 2'] = ''

#re-order columns
new_cols = ap.columns
cols = []
new_cols = list(new_cols)
new_cols = ['Initial', 'Decay', 'Matrix Element (a.u.)', 'Matrix Error', 'Matrix Element', 
            'Wavelength (nm)', 'Wavelength Error', 'Wavelength', 'Transition Rate (s-1)', 
            'Transition Rate Error',  'Transition Rate', 'Branching Ratio', 'Branching Ratio Error' , 
            'Branching Rat.', 'Reference', 'DOI', 'Reference 2', 'DOI 2']
ap = ap[new_cols]

#fill in () columns with save_copy values
for i in range(len(save_copy)):
    ap.loc[i, 'Matrix Element'] = save_copy['Matrix element (a.u.)'][i]
    ap.loc[i, 'Wavelength'] = save_copy['Wavelength (nm)'][i]
    ap.loc[i, 'Transition Rate'] = save_copy['Transition Rate (s-1)'][i]
    ap.loc[i, 'Branching Rat.'] = save_copy['Branching ratio'][i]
    #ap.loc[i, 'Flag'] = excel_copy['Flag'][i]

#adds in references and doi
for i in refr_ind:
    refer, refer1, refer2  = '', '', ''
    #index of start of reference
    ref_start = ap['Matrix Element'][i].find('E')
    #reference
    refer = ap['Matrix Element'][i][ref_start:]
    if '/' in refer:
        refer1 = refer.split('/')[0]
        refer2 = refer.split('/')[1]
        ap.loc[i, 'Reference'] = ref_exl[ref_exl['Key'] == refer1]['Reference'].values[0]
        ap.loc[i, 'Reference 2'] = ref_exl[ref_exl['Key'] == refer2]['Reference'].values[0]
        ap.loc[i, 'DOI'] = ref_exl[ref_exl['Key'] == refer1]['DOI'].values[0]
        ap.loc[i, 'DOI 2'] = ref_exl[ref_exl['Key'] == refer2]['DOI'].values[0]
    else:
        refer1 = refer
        refer2 = ''
        ap.loc[i, 'Reference'] = ref_exl[ref_exl['Key'] == refer1]['Reference'].values[0]
        ap.loc[i, 'Reference 2'] = ''
        ap.loc[i, 'DOI'] = ref_exl[ref_exl['Key'] == refer1]['DOI'].values[0]
        ap.loc[i, 'DOI 2'] = ''

ap.rename(columns = {"Decay": "Final"}, inplace = True)

#ap.drop(['Transition Rate (s-1)', 'Transition Rate Error', 'Transition Rate', 'Branching Ratio', 'Branching Ratio Error', 'Branching Rat.'], axis = 1, inplace = True)


# In[54]:


#Removes "E##" reference format from Matrix Element column
for i, jj in enumerate(ap['Matrix Element']):
    ap.loc[i, 'Matrix Element'] = jj.split(')')[0] + ')'

#changes excel transition Rate errors to full Decimal based on "all state"
#note, this is more accuracy than is technically correct. Save_copy has correct number of digits
for ii in range(len(ap)):
    matched_ind = all_state.loc[all_state['matrix'] == ap['Matrix Element (a.u.)'][ii]].index[0]
    ap.loc[ii, 'Transition Rate (s-1)'] = all_state['transition_rate s-1'][matched_ind]
    
#gets Transition Rates to have 4 decimal points
ap['Transition Rate (s-1)'] = ap['Transition Rate (s-1)'].apply(lambda x: '{:.4f}'.format(x))
#changes so all columns have units, but now multiple columns have same name, so its stored in new variable
ap_presentable = ap.rename(columns={"Matrix Element": "Matrix Element (a.u.)", "Matrix Error": "Matrix El. Error (a.u.)", 
                   "Wavelength Error": "Wavelength Error (nm)", "Wavelength": "Wavelength (nm)", 
                   "Transition Rate Error": "Transition Rate Error (s-1)", 
                   "Transition Rate": "Transition Rate (s-1)"})


# In[55]:


#need to change transition rate errors to 'E' instead of 'e', thats why it isn't registering as a number


# In[56]:


tabl_excel = ap_presentable.to_html(index = False)
tabl_life = tabl_life #lifetimes
#tabl_excel = htmls[3] #excel_copy
#tabl_main = htmls[0] #save_copy

#table indexed from when tbody starts, ignoring initial headers
#table1 is up to lifetime_table
#+9 is number of characters in tbody, which we don't want to include
form_table1 = intro_format + '\n' 

#form_table1 += header_name

#form_table1 += '\n' + button_lst

#form_table1 += '\n' + format_hold_title

form_table1 += '\n' + '\n' + tabl_life[tabl_life.find('<tbody>\n') + 9:]

form_table1 += '\n' + '\n' + format_hold_excel
form_table1 += '\n' + '\n' + tabl_excel[tabl_excel.find('<tbody>\n') + 9:]

form_table1 += '\n' + '\n' + format_hold_main
form_table1 += '\n' + '\n' + tabl_main[tabl_main.find('<tbody>\n') + 9:]

form_table1 += format_hold_end
form_tables = form_table1 


# In[57]:


# fname = "ElementsHTMLs\%s\%sTranAuto.html" % (element, element)
# fname


# In[58]:


fname = "ElementsHTMLs\%sTranAuto.html" % (element)
#fname


# In[59]:


text_file = open(fname, "wb")
text_file.write(form_tables.encode('utf8'))
text_file.close()


# In[60]:


with open('Format_csvs/TransitionRates/All_states/Intro_to_table_formatting.txt', 'r') as file:
    format_hold_introA = file.read()
with open('Format_csvs/TransitionRates/All_states/End_formatting.txt', 'r') as file:
    format_hold_endA = file.read()


# In[61]:


key = 'Cs1'
key_info = name_to_display(key) #display, just name, number of ionization
element_info = name_to_display(element)
key_display = key_info[0]
ele_display = element_info[0]

#str1 rep1 takes the default active dropdown and removes the active key
#str2 rep2 finds the correct dropdown and adds the active key
#the if statement is in case the key is also the correct element
str1 = f'<a class="dropdown-item active" href="{key}TranAuto.html">{key_display}</a>'
rep1 = f'<a class="dropdown-item" href="{key}TranAuto.html">{key_display}</a>'
ind1 = format_hold_introA.find(str1) #index of where string1 is

#change the filename of the excel file to this element
stra = f"filename: '{key}TransitionRates',"
repa = f"filename: '{element}TransitionRates',"

str2 = f'<a class="dropdown-item" href="{element}TranAuto.html">{ele_display}</a>'
rep2 = f'<a class="dropdown-item active" href="{element}TranAuto.html">{ele_display}</a>'

ind2 = format_hold_introA.find(str2)
#Key element case, it is already active so there is no inactive version
if ind2 < 0:
    rep2 = str1
print(ind1, 'ind1')
print(ind2, 'ind2')

#header title
str3 = f'E1 Transition data for {key_info[1]}<sup>{key_info[2]*"+"}</sup>' #ex: {Ca}, {1} * '+'
rep3 = f'E1 Transition data for {element_info[1]}<sup>{element_info[2]*"+"}</sup>'
ind3 = format_hold_introA.find(str3)
print(ind3, 'ind3')

str4 = f'<a href=\'{key}TranAuto.html\' button class="btn2 noprint back"> Back </a>'
rep4 = f'<a href=\'{element}TranAuto.html\' button class="btn2 noprint back"> Back </a>'
ind4 = format_hold_introA.find(str4)

#change the title name
str5 = f'<title>{key_display}</title>'
rep5 = f'<title>{ele_display}</title>'
ind5 = format_hold_introA.find(str5)
print(ind5, 'ind5')



#NIST is in format 'Rb+I' or "Ca+II", so need to combine the name without the number with the ionization number (+ 1) times 'I'
strRef = f'href="https://physics.nist.gov/cgi-bin/ASD/energy1.pl?de=0&spectrum={key_info[1]}+{(key_info[2] + 1) * "I"}&submit=Retrieve+Data&units=0&format=0&output=0&page_size=15&multiplet_ordered=0&conf_out=on&term_out=on&level_out=on&unc_out=1&j_out=on&lande_out=on&perc_out=on&biblio=on&temp=">'
url_ref = nist_urls[nist_urls.index == element]['URL'][0]
urlRef = 'href='+ '\"' + url_ref+'\">'

#the file locations of the property switching buttons in the header are changed from the key to the current element
str_MEbut = f'onclick="location.href = \'{key}.html\';">Matrix elements'
str_Polbut = f'onclick="location.href = \'{key}Polarizability.html\';">Polarizability'
str_ODbut = f'onclick="location.href = \'{key}Other.html\';">Other data'

rep_MEbut = f'onclick="location.href = \'{element}.html\';">Matrix elements'
rep_Polbut = f'onclick="location.href = \'{element}Polarizability.html\';">Polarizability'
rep_ODbut = f'onclick="location.href = \'{element}Other.html\';">Other data'

ind_MEbut = format_hold_introA.find(str_MEbut)
ind_Polbut = format_hold_introA.find(str_Polbut)
ind_ODbut = format_hold_introA.find(str_ODbut)
print(ind_MEbut, 'ME property ind', ind_Polbut, 'Pol button ind', ind_ODbut, 'OD button ind')

intro_formatA = format_hold_introA.replace(str1, rep1, 2)
intro_formatA = intro_formatA.replace(stra, repa, 2)
intro_formatA = intro_formatA.replace(str2, rep2, 2)
intro_formatA = intro_formatA.replace(str3, rep3, 2)
intro_formatA = intro_formatA.replace(str4, rep4, 2)
intro_formatA = intro_formatA.replace(str5, rep5, 2)
intro_formatA = intro_formatA.replace(strRef, urlRef, 2)
intro_formatA = intro_formatA.replace(str_MEbut, rep_MEbut, 2)
intro_formatA = intro_formatA.replace(str_Polbut, rep_Polbut, 2)
intro_formatA = intro_formatA.replace(str_ODbut, rep_ODbut, 2)


# In[62]:


#removes "()" error format for "All" page
ap2 = ap.copy()
for i in range(len(ap2)):
    ap2.loc[i, ['Branching Rat.']] = save_copy['Branching ratio'][i].split('(')[0]
    ap2.loc[i, ['Transition Rate']] = save_copy['Transition Rate (s-1)'][i].split('(')[0] + save_copy['Transition Rate (s-1)'][i].split(')')[1]
    #ap2.loc[i, ['Wavelength']] = save_copy['Wavelength (nm)'][i].split('(')[0] + Flags[i] #blank or '*'
    #number before parentheses, marker (if there is one) after parenteshes
    try:
        ap2.loc[i, ['Wavelength']] = save_copy['Wavelength (nm)'][i].split('(')[0] + save_copy['Wavelength (nm)'][i].split(')')[1]
    except IndexError: #there is no () error so [1] is out of range
         ap2.loc[i, ['Wavelength']] = save_copy['Wavelength (nm)'][i].split('(')[0]
    ap2.loc[i, ['Matrix Element']] = save_copy['Matrix element (a.u.)'][i].split('(')[0]


# In[63]:


ap2.rename(columns={"Matrix Element (a.u.)": "Matrix element (a.u.)", "Matrix Element": "Matrix element (a.u.)", 
                    "Matrix Error": "Matrix error", "Wavelength Error": "Wavelength error",
                    "Transition Rate (s-1)": "Transition rate (s-1)", "Transition Rate": "Transition rate (s-1)",
                   "Transition Rate Error": "Transition rate error",
                   "Branching Ratio": "Branching ratio", "Branching Ratio Error": "Branching ratio error"}, inplace = True)
ap2.rename(columns={"Branching Rat.": "Branching ratio", "Wavelength": "Wavelength (nm)"}, inplace = True)


# In[64]:


#remove * from wavelength display
for i in range(len(ap2)):
    if '*' in ap2.iloc[i, 7]: #column 7 is the display wavelength
        ap2.iloc[i,5] = ap2.iloc[i, 5] + '*' #add asterisk to excel
        ap2.iloc[i, 7] = ap2.iloc[i, 7].replace('*', '') #remove asterisk from display so sorting works
        #print(ap2.iloc[i, 7], ap2.iloc[i, 5])


# In[65]:


all_ap = ap2.copy()
all_html = all_ap.to_html(index = False)

sub_scripts = ['1/2', '3/2', '5/2', '7/2', '9/2', '11/2', '13/2']
htmlsA = [all_html] #save_copy, Lifetimes, no_error, excel_copy
for i in sub_scripts:
    for j, k in enumerate(htmlsA):
        htmlsA[j] = htmlsA[j].replace('%s' % i, '<sub>%s</sub>' % i)
all_html = htmlsA[0]
all_html = all_html.replace('<th>Transition rate (s-1)</th>', '<th>Transition rate (s<sup>-1</sup>)</th>')
        
start_ind = all_html.find('tbody>') + 8
all_html[start_ind:]

count = 0
#good_cols = [1,2,3,6,9, 12]
#counting backwards

#good_cols = [5, 8, 11, 14, 17,18]
#good cols are the ones we want to show in the webpage
good_cols = [5, 8, 11, 14, 17, 18]
num_cols = 18
for i in reversed(range(len(all_html))):
    if all_html[i:i+4] == '<td>':
        count += 1
        if count not in good_cols:
            all_html = all_html[:i] + all_html[i:].replace('<td>', '<td style = \'display: none\'>', 1)
        if count == num_cols:
            count = 0
                
start_cut = all_html.find('<thead>\n')
end_cut = all_html[start_cut:].find('<tbody>')
col_heads = all_html[start_cut:start_cut + end_cut]

count = 0
for i in reversed(range(len(col_heads))):
    if col_heads[i:i+4] == '<th>': #check if its a header
        count += 1 #marker to see if its a visible column or not
        if count not in good_cols:
            col_heads = col_heads[:i] + col_heads[i:].replace('<th>', '<th style = \'display: none; text-align: center;\'>', 1)
        if count == num_cols: #reset at end
            count = 0
    #print(col_heads)
all_html = all_html[:start_cut] + col_heads + all_html[start_cut + end_cut:]
all_html = all_html.replace('<tr style="text-align: right;">', '<tr style="text-align: center;">')
#ini_str = all_html[start_ind:]
# substr = '\n'
# occurrence = 4

# inilist = [m.start() for m in re.finditer(substr, ini_str)] 
# print ("Nth occurrence of substring at", inilist[occurrence-1]) 


# In[66]:


#for "All" webpage
#tabl_all = htmls[2] 

#table indexed from when tbody starts, ignoring initial headers
#table1 is up to lifetime_table
#+9 is number of characters in tbody, which we don't want to include
form_table1 = intro_formatA + '\n' 


form_table1 += all_html[all_html.find('<thead>\n') + 9:]

form_table1 += '\n' + format_hold_endA
form_tables = form_table1 


# In[67]:


# fnameA = "ElementsHTMLs\%s\%sTranFull.html" % (element, element)
# fnameA


# In[68]:


fnameA = "ElementsHTMLs\%sTranFull.html" % (element)
fnameA


# In[69]:


text_file = open(fnameA, "wb")
n = text_file.write(form_tables.encode('utf8'))
text_file.close()


# In[70]:


#dont forget to comment/check button list modification
#put it in before transition rate change
#why is branching ratio error not being converted to number in Li? Because "E" needs to be put in, not 'e'


# In[71]:


f_copy = mat_page.copy() #mat page is like all_state, has 'f' states still around
f2_copy = f_copy.copy()

col_titles = list(f2_copy.columns)
col_titles[1], col_titles[0] = col_titles[0], col_titles[1]
f2_copy = f2_copy[col_titles]

f2_copy.rename(columns = {"Decay": "Initial", "Initial": "Decay"}, inplace = True)

dupa = f_copy.copy()
#HERE IS THE PROBLEM. ONE OF THESE NEEDS TO BE UNFLIPPED VERSION
dupa['Index'] = range(len(f_copy), len(f_copy)*2) #set it so indicies aren't repeated in second array
dupa.set_index('Index', inplace = True)
f_comb = f2_copy.append(dupa) #has both original and duplicated array stacked on each other

#sorts the values
f_comb[['n','l', 's']] = pd.DataFrame(f_comb.Initial.tolist(), index= f_comb.index)
f_comb[['nf','lf', 'sf']] = pd.DataFrame(f_comb.Decay.tolist(), index= f_comb.index)
f_comb.sort_values(by=['l', 'n', 's','nf', 'lf', 'sf'], ascending = [True, True, True, True, True, True], inplace = True)
f_comb.reset_index(drop = True, inplace = True)

f_combb = formatter(f_comb)
f_combb.drop(['Transition Rate (s-1)', 'Branching ratio'], axis = 1, inplace = True)
#swap ordering of columns
new_cols = ['Initial', 'Decay', 'Wavelength (nm)', 'Matrix element (a.u.)']
f_combb = f_combb[new_cols]


# In[72]:


#add in '*'
for i in range(len(f_comb)):
    f_combb.loc[i, 'Wavelength (nm)'] += f_comb['modif'][i]


# In[73]:


#Matrix elements    
refr_names = []
refr_ind = []
#makes list of all Initial and Final state names for items with references
for i, j in enumerate(f_combb['Matrix element (a.u.)']):
    if 'E' in j:
        refr_names.append((f_combb.Initial[i], f_combb.Decay[i]))
        refr_ind.append(i)
        
sub_scripts = ['1/2', '3/2', '5/2', '7/2', '9/2', '11/2']
inis = []
ends = []
#changes 1/2, 3/2, ... to subscript. stores in refrnamessub
for j, k in enumerate(refr_names):
    for i in sub_scripts:
        if i in k[0]:
            #print(i, k[0].replace('%s' % i, '<sub>%s</sub>' % i))
            inis.append(k[0].replace('%s' % i, '<sub>%s</sub>' % i))
        if i in k[1]:
            ends.append(k[1].replace('%s' % i, '<sub>%s</sub>' % i))
        #refr_namessub.append((a,b))
a = np.array(inis)
b = np.array(ends)
refr_namessub = np.vstack((a, b)).T
#refr_namessub


# In[74]:


htmlf = f_combb.to_html(index = False)
sub_scripts = ['1/2', '3/2', '5/2', '7/2', '9/2', '11/2', '13/2']
htmlsm = [htmlf] #save_copy, Lifetimes, no_error, excel_copy
for i in sub_scripts:
    for j, k in enumerate(htmlsm):
        htmlsm[j] = htmlsm[j].replace('%s' % i, '<sub>%s</sub>' % i)


# In[75]:


tabl_mat = htmlsm[0]
for i in range(len(refr_namessub)):
    #where the Initial Final state shows up
    name_start = tabl_mat.find(f'<td>{refr_namessub[i][0]}</td>\n      <td>{refr_namessub[i][1]}</td>')
    #How many characters until where the 'E' reference starts in that substring
    E_start = tabl_mat[name_start:].find('E')
    #How many characters until Where the reference ends
    E_end = tabl_mat[name_start+E_start:].find('<')
    #The reference name
    E_name = tabl_mat[name_start + E_start: name_start + E_start + E_end]


# In[76]:


style = "display:none"
tabl_mat = htmlsm[0] #save_copy
ref_exl = pd.read_csv(excel_fname, usecols = ['Key', 'Reference', 'DOI'])
for i in range(len(refr_namessub)):
    #where the Initial Final state shows up
    name_start = tabl_mat.find(f'<td>{refr_namessub[i][0]}</td>\n      <td>{refr_namessub[i][1]}</td>')
    #How many characters until where the 'E' reference starts in that substring
    E_start = tabl_mat[name_start:].find('E')
    #How many characters until Where the reference ends
    E_end = tabl_mat[name_start+E_start:].find('<')
    #The reference name
    E_name = tabl_mat[name_start + E_start: name_start + E_start + E_end]
    

    #only 1 reference
    if '/' not in E_name:
        #the button html text
        btn_name = tabl_mat[name_start + E_start: name_start + E_start + E_end].replace(f'{E_name}', f' <button type="button" class="btn btn-primary Ref1" data-toggle="modal" data-target="#exampleModalCenter">Ref</button></td> \n \t\t\t<td style = "display:none">{E_name}</td>')
        
        #reference name 
        reference = ref_exl['Reference'][ref_exl[ref_exl['Key'] == f'{E_name}'].index[0]]
        #DOI URl
        doi = ref_exl['DOI'][ref_exl[ref_exl['Key'] == f'{E_name}'].index[0]]
        td1 = f'\t\t\t<td style = "display:none" class="nr">{reference}</td>'
        td2 = f'\t\t\t<td style = "display:none" class="nr2">{doi}</td>'
        td3 = ''
        td4 = ''
        td5 = ''
    
    #2 references
    else:
        #first reference, second reference
        E_name1 = E_name.split('/')[0]
        E_name2 = E_name.split('/')[1]
        btn_name = tabl_mat[name_start + E_start: name_start + E_start + E_end].replace(f'{E_name}', f' <button type="button" class="btn btn-primary Ref1" data-toggle="modal" data-target="#exampleModalCenter">Ref</button></td> \n \t\t\t<td style = "display:none">{E_name1}</td>')
        
        reference1 = ref_exl['Reference'][ref_exl[ref_exl['Key'] == f'{E_name1}'].index[0]]
        doi1 = ref_exl['DOI'][ref_exl[ref_exl['Key'] == f'{E_name1}'].index[0]]
        td1 = f'\t\t\t<td style = "display:none" class="nr">{reference}</td>'
        td2 = f'\t\t\t<td style = "display:none" class="nr2">{doi}</td>'
        
        td3 = f'\t\t\t<td style = "display:none">{E_name2}</td>'
        reference2 = ref_exl['Reference'][ref_exl[ref_exl['Key'] == f'{E_name2}'].index[0]]
        doi2 = ref_exl['DOI'][ref_exl[ref_exl['Key'] == f'{E_name2}'].index[0]]
        td4 = f'\t\t\t<td style = "display:none" class="nr3">{reference2}</td>'
        td5 = f'\t\t\t<td style = "display:none" class="nr4">{doi2}</td>'
    #print(name_start, E_start, E_name,  tabl_mat[name_start + E_start + E_end+5:])
    tabl_mat = tabl_mat[:name_start + E_start] + btn_name + '\n' +     td1 + '\n' + td2 + '\n' + td3 + '\n' + td4 + td5 + '\n' + tabl_mat[name_start + E_start + E_end+5:] + '\n'


# In[77]:


#Sets up mat_excel for matrix pages
mat_excel = all_state.copy()
m_copy = mat_excel.copy() #mat page is like all_state, has 'f' states still around
m2_copy = m_copy.copy()

#swaps Intial and Decay columns
col_titles = list(m2_copy.columns)
col_titles[1], col_titles[0] = col_titles[0], col_titles[1]
m2_copy = m2_copy[col_titles]

m2_copy.rename(columns = {"Decay": "Initial", "Initial": "Decay"}, inplace = True)

dupa = m_copy.copy()
dupa['Index'] = range(len(m_copy), len(m_copy)*2) #set it so indicies aren't repeated in second array
dupa.set_index('Index', inplace = True)
m_comb = m2_copy.append(dupa) #has both original and duplicated array stacked on each other




#sorts the values
m_comb[['n','l', 's']] = pd.DataFrame(m_comb.Initial.tolist(), index= m_comb.index)
m_comb[['nf','lf', 'sf']] = pd.DataFrame(m_comb.Decay.tolist(), index= m_comb.index)
m_comb.sort_values(by=['l', 'n', 's','nf', 'lf', 'sf'], ascending = [True, True, True, True, True, True], inplace = True)
m_comb.reset_index(drop = True, inplace = True)

#changes to proper Initial Decay format
matt_excel = m_comb.copy()
tmp_hold = formatter(m_comb) #used to store Initial and Decay names, but don't want the other columns
mat_excel = matt_excel.copy()
mat_excel['Initial'] = tmp_hold['Initial']
mat_excel['Decay'] = tmp_hold['Decay']


#drops calculation columns
mat_excel.drop(['Ei', 'Ef', 'Ei_unc', 'Ef_unc', 'mat_werr', 'old_unc', 'n', 'l', 's'], axis = 1, inplace = True)
mat_excel.rename(columns = {'matrix': 'Matrix Element (a.u.)', 
                             'mat_unc': 'Matrix El. Error (a.u.)', 'wavelength': 'Wavelength (nm)', 'Eerr': 'Wavelength Error (nm)',
                             'modif': 'Flag', 'transition_rate s-1': 'Transition Rate (s-1)', 'Terr': 'Transition Rate Error (s-1)',
                            'branching ratio': "Branching Ratio", 'Berr': "Branching Ratio Error"}, inplace = True)
mat_excel.drop(['nf', 'lf', 'sf', 'precise_wave', 'precise_Eerr', 
                'Transition Rate (s-1)', 'Transition Rate Error (s-1)', 'Branching Ratio', 
                'Branching Ratio Error' ], axis = 1, inplace = True)


#versions with () format
#works because both have been sorted in same manner
mat_excel['Matrix Element'] = f_combb['Matrix element (a.u.)']
mat_excel['Wavelength'] = f_combb['Wavelength (nm)']
#reorder columns:
columns = mat_excel.columns.to_list()
new_columns = ['Initial', 'Decay', 'Wavelength (nm)', 'Wavelength Error (nm)', 'Flag', 'Wavelength',
               'Matrix Element (a.u.)', 'Matrix El. Error (a.u.)', 'Matrix Element']
mat_excel = mat_excel[new_columns]
#mat_excel


# In[78]:


bc = mat_excel.copy()
#set up column names for () format
bc['Reference'] = ''
bc['DOI'] = ''
bc['Reference 2'] = ''
bc['DOI 2'] = ''

#adds in references and doi
for i in refr_ind:
    refer, refer1, refer2  = '', '', ''
    #index of start of reference
    ref_start = bc['Matrix Element'][i].find('E')
    #reference
    refer = bc['Matrix Element'][i][ref_start:]
    if '/' in refer:
        refer1 = refer.split('/')[0]
        refer2 = refer.split('/')[1]
        bc.loc[i, 'Reference'] = ref_exl[ref_exl['Key'] == refer1]['Reference'].values[0]
        bc.loc[i, 'Reference 2'] = ref_exl[ref_exl['Key'] == refer2]['Reference'].values[0]
        bc.loc[i, 'DOI'] = ref_exl[ref_exl['Key'] == refer1]['DOI'].values[0]
        bc.loc[i, 'DOI 2'] = ref_exl[ref_exl['Key'] == refer2]['DOI'].values[0]
    else:
        refer1 = refer
        refer2 = ''
        bc.loc[i, 'Reference'] = ref_exl[ref_exl['Key'] == refer1]['Reference'].values[0]
        bc.loc[i, 'Reference 2'] = ''
        bc.loc[i, 'DOI'] = ref_exl[ref_exl['Key'] == refer1]['DOI'].values[0]
        bc.loc[i, 'DOI 2'] = ''

bc.rename(columns = {"Decay": "Final"}, inplace = True)

#Removes "E##" reference format from Matrix Element column
for i, jj in enumerate(bc['Matrix Element']):
    bc.loc[i, 'Matrix Element'] = jj.split(')')[0] + ')'
bc.rename(columns = {"Wavelength": "Wavelength (nm)", "Matrix Element": "Matrix Element (a.u.)"}, inplace = True)
bc.drop(columns = {"Flag"}, inplace = True)


# In[79]:


with open('Format_csvs/MatrixEle/Intro_to_excel_formatting.txt', 'r') as file:
    format_hold_introM = file.read()
    
with open(f'Format_csvs/MatrixEle/{element}MatButtons.txt', 'r') as file:
    button_lstM = file.read()
    
with open('Format_csvs/MatrixEle/Excel_to_main_formatting.txt', 'r') as file:
    format_hold_mainM = file.read()
    
with open('Format_csvs/MatrixEle/End_formatting.txt', 'r') as file:
    format_hold_endM = file.read()


# In[80]:


# #the active tag of the top menu is currently on {key} is removed. i.e. if Rb is active it will change to non-active and not
# #be highlighted
# key = 'Cs1' #the last element to have the modfications done, so what needs to be replaced for the others

# key_info = name_to_display(key) #display, just name, number of ionization
# element_info = name_to_display(element)
# key_display = key_info[0]
# ele_display = element_info[0]

# #str1 rep1 takes the default active dropdown and removes the active key
# #str2 rep2 finds the correct dropdown and adds the active key
# #the if statement is in case the key is also the correct element
# str1 = f'<a class="dropdown-item active" href="{key}TranAuto.html">{key_display}</a>'
# rep1 = f'<a class="dropdown-item" href="{key}TranAuto.html">{key_display}</a>'
# ind1 = format_hold_intro.find(str1) #index of where string1 is

# #change the filename of the excel file to this element
# stra = f"filename: '{key}TransitionRates',"
# repa = f"filename: '{element}TransitionRates',"

# str2 = f'<a class="dropdown-item" href="{element}TranAuto.html">{ele_display}</a>'
# rep2 = f'<a class="dropdown-item active" href="{element}TranAuto.html">{ele_display}</a>'

# ind2 = format_hold_intro.find(str2)
# #Key element case, it is already active so there is no inactive version
# if ind2 < 0:
#     rep2 = str1
# print(ind1, 'ind1')
# print(ind2, 'ind2')

# str3 = f'E1 Transition data for {key_info[1]}<sup>{key_info[2]*"+"}</sup>' #ex: {Ca}, {1} * '+'
# rep3 = f'E1 Transition data for {element_info[1]}<sup>{element_info[2]*"+"}</sup>'
# ind3 = format_hold_intro.find(str3)
# print(ind3, 'ind3')

# str4 = f'<td><button class="button"id="All"onclick="location.href=\'{key}TranFull.html\'"> All</button></td>'
# rep4 = f'<td><button class="button"id="All" onclick="location.href=\'{element}TranFull.html\';">All</button></td>'
# ind4i = format_hold_intro.find(str4)
# ind4f = ind4i + format_hold_intro[ind4i:].find('</tr>') + 7
# print(ind4i, 'ind4')

# str5 = f'<title>{key_display}</title>'
# rep5 = f'<title>{ele_display}</title>'
# ind5 = format_hold_intro.find(str5)
# print(ind5, 'ind5')

# #NIST is in format 'Rb+I' or "Ca+II", so need to combine the name without the number with the ionization number (+ 1) times 'I'
# strRef = f'href="https://physics.nist.gov/cgi-bin/ASD/energy1.pl?de=0&spectrum={key_info[1]}+{(key_info[2] + 1) * "I"}&submit=Retrieve+Data&units=0&format=0&output=0&page_size=15&multiplet_ordered=0&conf_out=on&term_out=on&level_out=on&unc_out=1&j_out=on&lande_out=on&perc_out=on&biblio=on&temp=">'
# url_ref = nist_urls[nist_urls.index == element]['URL'][0]
# urlRef = 'href='+ '\"' + url_ref+'\">'

# #the file locations of the property switching buttons in the header are changed from the key to the current element
# str_MEbut = f'onclick="location.href = \'{key}.html\';">Matrix elements'
# str_Polbut = f'onclick="location.href = \'{key}Polarizability.html\';">Polarizability'
# str_ODbut = f'onclick="location.href = \'{key}Other.html\';">Other data'

# rep_MEbut = f'onclick="location.href = \'{element}.html\';">Matrix elements'
# rep_Polbut = f'onclick="location.href = \'{element}Polarizability.html\';">Polarizability'
# rep_ODbut = f'onclick="location.href = \'{element}Other.html\';">Other data'

# ind_MEbut = format_hold_intro.find(str_MEbut)
# ind_Polbut = format_hold_intro.find(str_Polbut)
# ind_ODbut = format_hold_intro.find(str_ODbut)
# print(ind_MEbut, 'ME property ind', ind_Polbut, 'Pol button ind', ind_ODbut, 'OD button ind')

# intro_format = format_hold_intro.replace(str1, rep1, 2)
# intro_format = intro_format.replace(stra, repa, 2)
# intro_format = intro_format.replace(str2, rep2, 2)
# intro_format = intro_format.replace(str3, rep3, 2)
# intro_format = intro_format.replace(str4, rep4, 2)
# intro_format = intro_format.replace(str5, rep5, 2)
# intro_format = intro_format.replace(strRef, urlRef, 2)
# intro_format = intro_format.replace(str_MEbut, rep_MEbut, 2)
# intro_format = intro_format.replace(str_Polbut, rep_Polbut, 2)
# intro_format = intro_format.replace(str_ODbut, rep_ODbut, 2)

# #index of the "all" line, start of when we need to add buttons
# split_start = intro_format.find(rep4)
# #index of the end of that line 
# split_ind = split_start + intro_format[split_start:].find('</tr>') + 7
# #all the text before the button list
# first_half = intro_format[:split_ind]


# In[81]:


key = 'Cs1' #the last element to have the modfications done, so what needs to be replaced for the others

key_info = name_to_display(key) #display, just name, number of ionization
element_info = name_to_display(element)
key_display = key_info[0]
ele_display = element_info[0]

#str1 rep1 takes the default active dropdown and removes the active key
#str2 rep2 finds the correct dropdown and adds the active key
#the if statement is in case the key is also the correct element
str1 = f'<a class="dropdown-item active" href="{key}TranAuto.html">{key_display}</a>'
rep1 = f'<a class="dropdown-item" href="{key}TranAuto.html">{key_display}</a>'
ind1 = format_hold_introM.find(str1) #index of where string1 is

#change the filename of the excel file to this element
stra = f"filename: '{key}MatrixElements',"
repa = f"filename: '{element}MatrixElements',"

str2 = f'<a class="dropdown-item" href="{element}TranAuto.html">{ele_display}</a>'
rep2 = f'<a class="dropdown-item active" href="{element}TranAuto.html">{ele_display}</a>'

ind2 = format_hold_introM.find(str2)
#Key element case, it is already active so there is no inactive version
if ind2 < 0:
    rep2 = str1
print(ind1, 'ind1')
print(ind2, 'ind2')




#header title
str3 = f'E1 Matrix elements for {key_info[1]}<sup>{key_info[2]*"+"}</sup>' #ex: {Ca}, {1} * '+'
rep3 = f'E1 Matrix elements for {element_info[1]}<sup>{element_info[2]*"+"}</sup>'
ind3 = format_hold_introM.find(str3)
print(ind3, 'ind3')

#change title name
str5 = f'<title>{key_display}</title>'
rep5 = f'<title>{ele_display}</title>'
ind5 = format_hold_introM.find(str5)
print(ind5, 'ind5')

#NIST is in format 'Rb+I' or "Ca+II", so need to combine the name without the number with the ionization number (+ 1) times 'I'
strRef = f'href="https://physics.nist.gov/cgi-bin/ASD/energy1.pl?de=0&spectrum={key_info[1]}+{(key_info[2] + 1) * "I"}&submit=Retrieve+Data&units=0&format=0&output=0&page_size=15&multiplet_ordered=0&conf_out=on&term_out=on&level_out=on&unc_out=1&j_out=on&lande_out=on&perc_out=on&biblio=on&temp=">'
url_ref = nist_urls[nist_urls.index == element]['URL'][0]
urlRef = 'href='+ '\"' + url_ref+'\">'

#the file locations of the property switching buttons in the header are changed from the key to the current element
str_TRbut = f'onclick="location.href = \'{key}TranAuto.html\';">Transition rates'
str_Polbut = f'onclick="location.href = \'{key}Polarizability.html\';">Polarizability'
str_ODbut = f'onclick="location.href = \'{key}Other.html\';">Other data'

rep_TRbut = f'onclick="location.href = \'{element}TranAuto.html\';">Transition rates'
rep_Polbut = f'onclick="location.href = \'{element}Polarizability.html\';">Polarizability'
rep_ODbut = f'onclick="location.href = \'{element}Other.html\';">Other data'

ind_TRbut = format_hold_introM.find(str_TRbut)
ind_Polbut = format_hold_introM.find(str_Polbut)
ind_ODbut = format_hold_introM.find(str_ODbut)
print(ind_TRbut, 'TR property index', ind_Polbut, 'Pol button ind', ind_ODbut, 'OD button ind')


intro_format = format_hold_introM.replace(str1, rep1, 2)
intro_format =  intro_format.replace(stra, repa, 2)
intro_format =  intro_format.replace(str2, rep2, 2)
intro_format = intro_format.replace(str3, rep3, 2)
intro_format = intro_format.replace(str5, rep5, 2)
intro_format = intro_format.replace(strRef, urlRef, 2)
intro_format = intro_format.replace(str_TRbut, rep_TRbut, 2)
intro_format = intro_format.replace(str_Polbut, rep_Polbut, 2)
intro_format = intro_format.replace(str_ODbut, rep_ODbut, 2)


rep4 = '<td colspan=4>Select a state to see available data</td>'
#index of the "all" line, start of when we need to add buttons
split_start = intro_format.find(rep4)
#index of the end of that line 
split_ind = split_start + intro_format[split_start:].find('</tr>') + 7
#all the text before the button list
first_half = intro_format[:split_ind]
#where to start cutoff of button list, where to stop Button button cutoff and start again. 7 to remove </td> /n
strBi = rep4
indBi = button_lstM.find(strBi)
indBf = indBi + button_lstM[indBi:].find('</tr>') + 6

#where to start the formatting again, find where the list from button says 'navpol'
split_end = intro_format.find('</navpol>')
end_ind = split_end + 11
second_half = intro_format[end_ind:]
#combine 3 items together
intro_format = first_half + button_lstM[indBf:] + '\n' + second_half


# In[82]:


excel_body = bc.to_html(index = False)

#table indexed from when tbody starts, ignoring initial headers
#table1 is up to lifetime_table
#+9 is number of characters in tbody, which we don't want to include
form_table1 = intro_format + '\n' 
form_table1 += '\n' + excel_body[excel_body.find('<tbody>') + 9:]


form_table1 += '\n' + '\n' + format_hold_mainM
form_table1 += '\n' + '\n' + tabl_mat[tabl_mat.find('<tbody>\n') + 9:]


form_table1 += '\n' + format_hold_endM
form_tables = form_table1 


# In[83]:


# fnameA = "ElementsHTMLs\%s\%s.html" % (element, element)
# fnameA


# In[84]:


fnameA = "ElementsHTMLs\%s.html" % (element)
fnameA


# In[85]:


text_file = open(fnameA, "wb")
n = text_file.write(form_tables.encode('utf8'))
text_file.close()

