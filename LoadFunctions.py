#!/usr/bin/env python
# coding: utf-8

# In[1]:


c_val = 2.02613 * 10**18 
#Calculates transition rates
def transition_rate_calc(m,j,lam): #takes in matrix element, total momentum, wavelength in cm-1
    lam = lam * 10**8 #converts to Angstrom from cm-1
    jval = 2 * j + 1 #bottom part of first half
    m2 = m**2 #matrix element squared. Will need to be variable
    lam3 = lam**3
    A = (c_val / jval) * (m2 / lam3)
    return A

#calculates Lifetime
def lifetime_calc(amas): #takes in list of all transition rates in format of transition_rate_calc (s-1)
    return 1/np.sum(amas)

#calculates branching ratio off of lifetime
def branching_ratio_calc(a, lifet): #takes in a transition rate, lifetime of state
    return a*lifet


# In[1]:


#reads a CSV and returns as a list. Not used anymore
def ReadCsv(fileToRead,colDelim = ",", rowDelim = "\n"):
    fileHandle = open(fileToRead,"r")
    fileContent = fileHandle.read()
    fileLines = fileContent.split(rowDelim)
    fileAsListOfLists = [k.split(colDelim) for k in fileLines]
    return fileAsListOfLists


# In[2]:


#Uncertainty calculations
#uncertainty in energy 
def energy_err_calc(Ei, Ef, Eierr, Eferr): 
    """initial energy, final energy, initial energy error, final energy error"""
    a = Ei #higher energy state
    b = Ef
    err_a = Eierr
    err_b = Eferr
    return (1/(a-b)**2) * np.sqrt( (err_a)**2 + (err_b)**2 ) * 10**8 #into Angstrom from cm-1

#error in transtion rate
def transition_err_calc(m,j,lam, merr, lamerr): 
    """takes in matrix element, total momentum, wavelength in Angstrom, errors. Lamerr is in Angstrom"""
    m, j, lam, merr, lamerr = m, j, lam, merr, lamerr
    m2 = m**2 #matrix element squared. 
    lam = lam * 10**8 #converting to Angstrom from cm -1. Lamerr is already converted.
    lam3 = lam**3
    jval = 2 * j + 1
    return (c_val / jval) * (m2/lam3) * np.sqrt( ((m2 * 2 * merr / m) / m2)**2 + ((lam3 * 3 * lamerr / lam) / lam3)**2 )

#error in lifetime
def lifetime_err_calc(trs, errs): 
    """takes in list of all transition rates, all TR errros"""
    X = np.sum(trs) #1/Lifetime
    errs = [i ** 2 for i in errs]
    return (1 / X)**2 * np.sqrt(np.sum(errs))


#More complicated Lifetime Error calculation, which is what is used
def lifetime_err_calc2(trs, errs): 
    """takes in list of all transition rates and their errors, in format of (s-1)
    this version takes into account that some states are correlated and will have correlated errors"""
    num_trans = len(errs) #number of transition rates
    errs = pd.DataFrame(errs, columns = ['n', 'l', 's', 'error']) #convert to pandas
    errs.sort_values(by=['l', 'n', 's'], ascending = [True, True, True], inplace = True)
    errs.reset_index(drop = True, inplace = True)
    X = np.sum(trs) #1/Lifetime
    direct_add = [] #holder for individual sets of correlated states
    quad_add = [] #holder for sets which add in quadrature, non-correlated
    all_corr = [] #holds all the lists of errors for correlated states
    if num_trans > 1: #multiple transitions
        for i in range(len(errs)-1):
            #same n and l state as next transition, ignores spin states
            if errs['n'][i] == errs['n'][i+1] and errs['l'][i] == errs['l'][i+1]:
                direct_add.append(errs['error'][i])
                direct_add.append(errs['error'][i+1])
            else:
                #if next state isnt coupled, add these errors in pair to all_correlated
                #reset list, add this new state error to quad_add, which calculates error in tradional way
                #will remove from quad add if the state ends up on a different "direct addition" pair
                direct_add = list(dict.fromkeys(direct_add))
                all_corr.append(direct_add)
                direct_add = []
                quad_add.append(errs['error'][i])
                quad_add.append(errs['error'][i+1])
            
        direct_add = list(dict.fromkeys(direct_add)) #remove duplicates
        all_corr.append(direct_add) #added here in case there is no "else" case
        flat_all = [item for sublist in all_corr for item in sublist] #flattened all_corraleted to become one list
        flat_all = list(dict.fromkeys(flat_all)) #remove duplicate errors
        quad_add = list(dict.fromkeys(quad_add)) #remove duplicates
        quad_add = [elem for elem in quad_add if elem not in flat_all] #removed quadratic adding elements if they should be linear

        corr_sum = [] #directly added errors of correlated values 
        for i in all_corr: #add the directly added errors together
            corr_sum.append(np.sum(i))
        all_errs = corr_sum + quad_add #combines two lists, does not add elements
        squares = [i**2 for i in all_errs]
        #return np.sqrt(np.sum(squares))

        return (1 / X)**2 * np.sqrt(np.sum(squares))
    else: #just one error 
        error = float(errs['error'])
        return (1 / X)**2 * np.sqrt(error**2)

#error in branching ratio
def branching_ratio_error(Tr, Trs, TrError, TrErrors, lifetime): #
    """ All transition rates, All TR errors, singular TR and its error, Lifetime"""
    sums = 1/lifetime #sum of all transition rates
    all_errors = []
    #based on math of Branching ratio errors
    for i in range(len(Trs)):
        #if this is the state we are calculating BR for:
        if Trs[i] == Tr:
            numer = sums - Trs[i] #numerator
            denom = sums**2 #denominator
            Error1 = (numer / denom)**2
            Error1 = Error1 * (TrErrors[i]**2)
        else:
            #for other TR's
            numer = Tr
            denom = sums**2
            Error1 = (numer / denom)**2
            Error1 = Error1 * (TrErrors[i]**2)
        all_errors.append(Error1)
    Br_error = np.sqrt(np.sum(all_errors))
    if len(all_errors) == 1: #exception for 1 state
        Br_error = 0
    return Br_error


# In[3]:


#conversions for pandas
def ang_to_nm(x): #angstorm to nm
    return x*(10**-1)
def cm_to_nm(x):
    return x*(10**7)
def cm_to_ang(x):
    return x*(10**8)
def s_to_ns(x):
    return x*(10**9)
def conversion(x): #old formatting, scientific digit
    #return np.format_float_scientific(x, 3)
    return "{:.3e}".format(x)


# In[ ]:


#code to have scientific format numbers be in ## (#) E+# format instead of ##E+#(#)
def format_e(n): #input number
    a = '%E' % float(n)
    nn = str(n)
    #20 will have 1, 200 will have 2. Otherwise they get structure to 2E+1 and lose precision
    num_zeroes = len(nn) - len(nn.rstrip('0'))
    if num_zeroes != 0:
        return a.split('E')[0].rstrip('0').rstrip('.') + '.' + '0' * num_zeroes + 'E' + a.split('E')[1]
    else:
        return a.split('E')[0].rstrip('0').rstrip('.') + 'E' + a.split('E')[1]


# In[ ]:


def to_one_dig(wavelength, error):
    """
    "takes in a wavelength and error and uses it to produce ####(#) format"
    "could possibly be used to do a different number of (###) digits
    pattern is pattern = re.compile(r"\((\d+)\)") which is just finding number in ()
    old code is included in case changes are needed"
    """
    wavelength = wavelength
    error = error
#     original = round(wavelength, error, format = 'Drake') #number with 2 err_dig and ()   
#     og_err = pattern.findall(original)[0] #just the error if it has one
#     new_err = round(og_err, sigfigs = 1)[0]
        
#     og_num = original.split('(')[0] #just the number  
#     if 'E' in original:
#         err_in_paren = re.search('\(([^)]+)', original).group(1)
#         og_num = str(float(original.replace('(%s)' % err_in_paren, '' ))) #gets it out of scientific notation and back into str
#     new_sfigs = len(og_num.replace('.', '')) - 1 #how many digits new 1 number should have
#     new_num = round(wavelength, sigfigs = new_sfigs) #number moved back one sig fig

#     try:

        
#         num_deci = len(og_num.split('.')[1]) - 1
#     except IndexError:
#         num_deci = new_sfigs
#     deci_format = "%%.%sf" % num_deci
#     new_num = deci_format % new_num
#     #if you want to use scientific notation, keep original as round(wavelength, error, format = 'Drake')

#     final_value = new_num + '(' + new_err + ')'

    ###########
    numb = round(wavelength, error).split('±')[0]
    #erb = round(wavelength, error, format = 'Drake')
    #erb is the first two digits of the error, ignores '.'
    erb = re.compile('[1-9]*\.?[1-9]+').findall(str(error))[0].replace('.', '')[0:2]
    #erb = re.search('\(([^)]+)', erb).group(1)
    #first digit of error, ronded
    dig1 = round(erb, sigfigs = 1)[0]
    final_value = numb + '(' + dig1 + ')'
    ###############
    if float(error) == 0:
        final_value = wavelength
    return final_value


# In[4]:


# #error formatting code
# #version used is in "TransitionManualInput"
# def to_one_dig(wavelength, error):
#     """
#     "takes in a wavelength and error and uses it to produce ####(#) format"
#     "could possibly be used to do a different number of (###) digits"
#     """
#     wavelength = wavelength
#     error = error
#     original = round(wavelength, error, format = 'Drake') #number with 2 err_dig and ()
    
#     og_err = pattern.findall(original)[0] #just the error if it has one
#     new_err = round(og_err, sigfigs = 1)[0]
        
#     og_num = original.split('(')[0] #just the number
# #     except (IndexError, TypeError): #if there is no Error
# #         og_err = ''
# #         new_err = ''
# #         og_num = original #number doesn't have ()
        
#     if 'E' in original:
#         err_in_paren = re.search('\(([^)]+)', original).group(1)
#         og_num = str(float(original.replace('(%s)' % err_in_paren, '' ))) #gets it out of scientific notation and back into str
#     new_sfigs = len(og_num.replace('.', '')) - 1 #how many digits new 1 number should have
#     new_num = round(wavelength, sigfigs = new_sfigs) #number moved back one sig fig
#     #print(new_num, 'nn')
#     #find how many decimal spots there are
#     #print(original, new_sfigs, og_num, og_num.split('.'))
#     #print(og_num.split('.')[1])
#     try:
#         #num_deci = new_sfigs - len(og_num.split('.')[1])
        
#         num_deci = len(og_num.split('.')[1]) - 1
#         #print(new_sfigs, og_num, num_deci)
#         #heres the problem: og_num adds 0 to the end of the number if the error is at the last digit
#         #so 1359.2016, .0006 goes to 1359.20160, which if you subtract the decimals gives one number less than you want
#     except IndexError:
#         num_deci = new_sfigs
#     #run condition to see if the wavleneght has an added '0' at end for sig_figs
# #     if len(og_num.split('.')[1]) > len(str(wavelength).split('.')[1]):
# #         #add one since we don't want to include that in sig fig calc
# #         num_deci += 1
#     deci_format = "%%.%sf" % num_deci
#     new_num = deci_format % new_num
#     #print(original, 'original', og_num, 'og_num', new_num, 'new_num2', deci_format)
#     #print(og_err, new_err)
#     #print('errors', error, og_err, new_err)
    
#     #new_num = str("")
#     #if you want to use scientific notation, keep original as round(wavelength, error, format = 'Drake')

#     final_value = new_num + '(' + new_err + ')'
#     if float(error) == 0:
#         final_value = wavelength
#     return final_value


# In[5]:


#to_one_dig messes up if the number is something like .09452
#need separate case for small numbers
def to_one_dig_small(wavelength, error):
    """
    "takes in a wavelength and error and uses it to produce ####(#) format"
    "could possibly be used to do a different number of (###) digits"
    """
    wavelength = wavelength
    error = error
    original = round(wavelength, error, format = 'Drake') #number with 2 err_dig and ()
    
    og_err = pattern.findall(original)[0] #just the error if it has one
    new_err = round(og_err, sigfigs = 1)[0] #1 digit
        
    og_num = original.split('(')[0] #just the number
#     except (IndexError, TypeError): #if there is no Error
#         og_err = ''
#         new_err = ''
#         og_num = original #number doesn't have ()
        
    if 'E' in original:
        err_in_paren = re.search('\(([^)]+)', original).group(1)
        og_num = str(float(original.replace('(%s)' % err_in_paren, '' ))) #gets it out of scientific notation and back into str
    new_sfigs = len(og_num.replace('.', '')) - 1 #how many digits new 1 number should have
    new_num = round(wavelength, sigfigs = new_sfigs) #number moved back one sig fig
    #print(new_num, 'nn')
    #find how many decimal spots there are
    #print(original, new_sfigs, og_num, og_num.split('.'))
    #print(og_num.split('.')[1])
    try:
        #num_deci = new_sfigs - len(og_num.split('.')[1])
        
        num_deci = len(og_num.split('.')[1]) - 1 
        #print(new_sfigs, og_num, num_deci)
        #heres the problem: og_num adds 0 to the end of the number if the error is at the last digit
        #so 1359.2016, .0006 goes to 1359.20160, which if you subtract the decimals gives one number less than you want
    except IndexError:
        num_deci = new_sfigs
    #run condition to see if the wavlenegth has an added '0' at end for sig_figs
#     if len(og_num.split('.')[1]) > len(str(wavelength).split('.')[1]):
#         #add one since we don't want to include that in sig fig calc
#         num_deci += 1
    deci_format = "%%.%sf" % num_deci
    new_num = deci_format % new_num
    #print(original, 'original', og_num, 'og_num', new_num, 'new_num2', deci_format)
    #print(og_err, new_err)
    #print('errors', error, og_err, new_err)
    
    #new_num = str("")
    #if you want to use scientific notation, keep original as round(wavelength, error, format = 'Drake')
    #print(('%.1g' % error)[-1])
    one_dig_error = ('%.1g' % error)[-1] #general format
    final_value = new_num + '(' + one_dig_error + ')'
    if float(error) == 0 or float(error) < .0001:
        final_value = '%.4f' % wavelength #always 4 decimals 
    return final_value


# In[ ]:


#gets lifetimes into "#A#/#" format i.e. 4s1/2
def format_lifetime(x, y):
    """takes in Lifetimes, quantum orbital numbers (0,1,2,3)"""
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

