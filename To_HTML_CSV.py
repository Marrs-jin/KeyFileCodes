#!/usr/bin/env python
# coding: utf-8

# In[1]:


#table to be used in excel, has more error places. 
excel_copy = all_state.copy()

#drops calculation columns
excel_copy.drop(['Ei', 'Ef', 'Ei_unc', 'Ef_unc', 'mat_werr'], axis = 1, inplace = True)
excel_copy.rename(columns = {'matrix': 'Matrix Element (a.u.)', 
                             'mat_unc': 'Matrix Error', 'wavelength': 'Wavelength (nm)', 'Eerr': 'Wavelength Error',
                             'transition_rate s-1': 'Transition Rate (s-1)', 'Terr': 'Transition Rate Error',
                            'branching ratio': "Branching Ratio", 'Berr': "Branching Ratio Error"}, inplace = True)
excel_copy.drop([ 'precise_wave', 'precise_Eerr'], axis = 1, inplace = True)

#reorder to put modification after wavelength error, then rename
excel_copy = excel_copy[['Initial', 'Decay', 'NameI', 'NameF', 'Matrix Element (a.u.)', 'Matrix Error', 
       'Wavelength (nm)', 'Wavelength Error', 'modif', 'Transition Rate (s-1)',
       'Transition Rate Error', 'Branching Ratio', 'Branching Ratio Error']]
excel_copy.rename(columns = {'modif': 'Flag'}, inplace = True)


# In[ ]:


#to get branching ratios out of scientific notation in html
Br_not_sci = [] 
Brer_not_sci = []
for i in range(len(excel_copy)):
    Br_not_sci.append(str(excel_copy['Branching Ratio'][i]))
    Brer_not_sci.append(str(excel_copy['Branching Ratio Error'][i]))
excel_copy['Branching Ratio'] = Br_not_sci
excel_copy['Branching Ratio Error'] = Brer_not_sci


# In[ ]:


#Gets rid of "Flag columns"
Flags = excel_copy['Flag']
excel_copy.drop(columns = {'Flag'}, inplace = True)


# In[ ]:


#going to have html replaced for Initial, Final, drop NameI, NameF
save_html = save_copy.copy() 
save_html['Initial'] = save_copy.merge(state_keys, left_on='Initial', right_on='key')['html']
save_html['Decay'] = save_copy.merge(state_keys, left_on='Decay', right_on='key')['html']
save_html.drop(columns = ['NameI'], axis = 1, inplace = True)
save_html.drop(columns = ['NameF'], axis = 1, inplace = True)


# In[ ]:


#no_errors is the version that will be shown when they click "all"
no_errors = save_html.copy()
matrixx = []
wavell = []
transrr = []
branchh = []
for i in range(len(no_errors)):
    matrixx.append(no_errors['Matrix element (a.u.)'][i].split('(')[0])
    wavell.append(no_errors['Wavelength (nm)'][i].split('(')[0])
    transrr.append(no_errors['Transition Rate (s-1)'][i].split('(')[0] + no_errors['Transition Rate (s-1)'][i].split(')')[1])
    branchh.append(no_errors['Branching ratio'][i].split('(')[0])
no_errors['Matrix element (a.u.)'] = matrixx
no_errors['Wavelength (nm)'] = wavell
no_errors['Transition Rate (s-1)'] = transrr
no_errors['Branching ratio'] = branchh


# In[ ]:


Lifetimes_html = Lifetimes.copy()
Lifetimes_html['State'] = Lifetimes.merge(state_keys, left_on = 'key', right_on = 'key')['html']
Lifetimes_html.drop(columns = ['key'], axis = 1, inplace = True)


# In[ ]:


#changes to HTML tabular format
html = save_html.to_html(index = False)
html2 = Lifetimes_html.to_html(index = False)
html3 = no_errors.to_html(index = False)
htmls = [html, html2, html3]


# In[ ]:


#to_html produces artifacts for sup, sup. Needs to be replaced
for i in range(len(htmls)):
    htmls[i] = htmls[i].replace('&lt;sup&gt;', '<sup>')
    htmls[i] = htmls[i].replace('&lt;/sup&gt;', '</sup>')
    htmls[i] = htmls[i].replace('&lt;sub&gt;', '<sub>')
    htmls[i] = htmls[i].replace('&lt;/sub&gt;', '</sub>')
    htmls[i] = htmls[i].replace('NaN', "")

