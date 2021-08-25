#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import re
#NOTE: IF HYPERFINE/NUCLEAR EVER DISAGREE WITH WEBSITE DISPLAY, MIGHT NEED TO CONVERT TO CSV


# In[2]:


subscripts = pd.read_csv('Data/Subscript_list.txt', header = None)
sub_scripts = subscripts.values.tolist()[0]
#['1/2', '3/2', '5/2', '7/2', '9/2', '11/2'] as of 6/6/2020


# In[3]:


# #read in variables
# element = "Rb"
# #element = 'Cs'
#old_width = pd.get_option('display.max_colwidth')
#pd.set_option('display.max_colwidth', None)


# In[4]:


try:
    element
except NameError:
    element = input("Enter name of element: ")


# In[5]:


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


# In[6]:


element_info = name_to_display(element)
ele_display = element_info[0]


# In[7]:


excel_fname = r"OtherData\KEY-hyperfine.xlsx"
ref_exl = pd.read_excel(excel_fname, 
                    engine='openpyxl', header = None, names = ['Ref', 'Name'])


# In[8]:


# meta_fname2 = r"C:\Users\dmgame\Documents\SafronovaResearch\LifetimesWebsite\OtherData\%s_Metastable.xlsx" % (element)
# metastable2 = pd.read_csv(meta_fname, skiprows = [0,1,2], dtype = str)


# In[9]:


#element = "CaII"
meta_all_fname = r"OtherData\Metastable_elements.txt"
meta_all = pd.read_csv(meta_all_fname, engine='python', header = None, names = ['element'], dtype = str)
metastable_elements = list(meta_all['element'])

if element in metastable_elements:
    #metastable needs to be csv with dtype = str to get same precision as excel display. 
    meta_fname = r"OtherData\%s_Metastable_csv.csv" % (element)
    metastable = pd.read_csv(meta_fname, skiprows = [0,1,2], dtype = str)
else:
    print('no metastable state')
    metastable = ''


# In[10]:


if element in metastable_elements:
    metastable_states = [] #names of states
    for i in metastable.iloc[:, 0]: #first column of metastable
        if i == i and i not in metastable_states: #not a nan value
            metastable_states.append(i)
    for i in sub_scripts: #change 1/2 style to subscript for HTML 
        for j, k in enumerate(metastable_states):
            metastable_states[j] = metastable_states[j].replace('%s' % i, '<sub>%s</sub>' % i)


# In[11]:


#set up key file with refs
doi_holder = []
name_holder = []
for i in range(len(ref_exl)):
    try:
        doi_name = 'DOI' + ref_exl['Name'][i].split('DOI')[1]
    except IndexError:
        doi_name = ''
    doi_holder.append(doi_name)
    name_str = ref_exl['Name'][i].split('DOI')[0]
    last_comma = name_str.rfind(',')#finds last comma
    name_holder.append(name_str[:last_comma]) #removes last comma
ref_exl['DOI'] = doi_holder
ref_exl['Name'] = name_holder
ref_exl


# In[12]:


element_just_name = element_info[1] #Cs, Ca, etc. Just the name, used to search through the table
nuclear_fname = r"OtherData\Nuclear-data.xlsx"
nuclear = pd.read_excel(nuclear_fname, 
                    engine='openpyxl', skiprows = [0,1,2,3,4], nrows = 82, usecols = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14], dtype = 'str')
nuc_sub = nuclear[nuclear['Atom'] == element_just_name]
nuc_sub.reset_index(inplace = True, drop = True)


# In[13]:


#find x106 etc. values in half-life, replace with superscript html tags
for i in nuc_sub.index:
    if 'x' in  nuc_sub['Half-life Ref. [1]'][i]:
        #has sig fig incorrectly applied
        faulty = nuc_sub['Half-life Ref. [1]'][i]
        corrected = faulty.split(' ')[0]
        fault_unit = ' ' + faulty.split(' ')[1]
        corrected = corrected.split('10', 1)[0] + '10' + '<sup>' + corrected.split('10', 1)[1] + '</sup>' + fault_unit
        nuc_sub.loc[i,'Half-life Ref. [1]'] = corrected
nuc_sub


# In[14]:


with open(r"Format_csvs\OtherData\Intro_to_nuclear.txt", encoding="utf8") as file:
    format_hold_intro = file.read()


# In[15]:


with open(r"Format_csvs\OtherData\Nuclear_to_hyperfine.txt", encoding="utf8") as file:
    format_hold_hyp = file.read()


# In[16]:


with open(r"Format_csvs\OtherData\Hyperfine_to_metastable1.txt", encoding="utf8") as file:
    format_hold_met1 = file.read()


# In[17]:


with open(r"Format_csvs\OtherData\Metastable1_to_2.txt", encoding="utf8") as file:
    format_hold_met2 = file.read()


# In[18]:


with open(r"Format_csvs\OtherData\End_formatting.txt", encoding="utf8") as file:
    format_hold_end = file.read()


# In[19]:


nist_urls = pd.read_csv(r"Data\nist_urls.csv",
                        header = None, names = ["Element", "URL"], index_col = 0)


# In[20]:


key = 'Fr1' #the last element to have the modfications done, so what needs to be replaced for the others

key_info = name_to_display(key) #returns: display, just name, number of ionization
key_display = key_info[0]

#str1 rep1 takes the default active dropdown and removes the active key
#str2 rep2 finds the correct dropdown and adds the active key
#the if statement is in case the key is also the correct element
str1 = f'<a class="dropdown-item active" href="{key}Other.html">{key_display}</a>'
rep1 = f'<a class="dropdown-item" href="{key}Other.html">{key_display}</a>'
ind1 = format_hold_intro.find(str1) #index of where string1 is

#change the filename of the excel file to this element
stra = f"filename: '{key}OtherData',"
repa = f"filename: '{element}OtherData',"

str2 = f'<a class="dropdown-item" href="{element}Other.html">{ele_display}</a>'
rep2 = f'<a class="dropdown-item active" href="{element}Other.html">{ele_display}</a>'

ind2 = format_hold_intro.find(str2)
#Key element case, it is already active so there is no inactive version
if ind2 < 0:
    rep2 = str1
print(ind1, 'ind1')
print(ind2, 'ind2')

str3 = f'Other data for {key_info[1]}<sup>{key_info[2]*"+"}</sup>' #ex: {Ca}, {1} * '+'
rep3 = f'Other data for {element_info[1]}<sup>{element_info[2]*"+"}</sup>'
ind3 = format_hold_intro.find(str3)
print(ind3, 'ind3')

str4 = f'<title>{key_display}</title>'
rep4 = f'<title>{ele_display}</title>'
ind4 = format_hold_intro.find(str4)
print(ind4, 'ind4')

#NIST is in format 'Rb+I' or "Ca+II", so need to combine the name without the number with the ionization number (+ 1) times 'I'
strRef = f'href="https://physics.nist.gov/cgi-bin/ASD/energy1.pl?de=0&spectrum={key_info[1]}+{(key_info[2] + 1) * "I"}&submit=Retrieve+Data&units=0&format=0&output=0&page_size=15&multiplet_ordered=0&conf_out=on&term_out=on&level_out=on&unc_out=1&j_out=on&lande_out=on&perc_out=on&biblio=on&temp=">'
url_ref = nist_urls[nist_urls.index == element]['URL'][0]
urlRef = 'href='+ '\"' + url_ref+'\">'

#the file locations of the property switching buttons in the header are changed from the key to the current element
str_MEbut = f'onclick="location.href = \'{key}.html\';">Matrix elements'
str_TRbut = f'onclick="location.href = \'{key}TranAuto.html\';">Transition rates'
str_Polbut = f'onclick="location.href = \'{key}Polarizability.html\';">Polarizability'

rep_MEbut = f'onclick="location.href = \'{element}.html\';">Matrix elements'
rep_TRbut = f'onclick="location.href = \'{element}TranAuto.html\';">Transition rates'
rep_Polbut = f'onclick="location.href = \'{element}Polarizability.html\';">Polarizability'

ind_MEbut = format_hold_intro.find(str_MEbut)
ind_TRbut = format_hold_intro.find(str_TRbut)
ind_Polbut = format_hold_intro.find(str_Polbut)

print(ind_MEbut, 'ME property ind', ind_TRbut, 'OD button ind', ind_Polbut, 'Pol button ind', )

intro_format = format_hold_intro.replace(str1, rep1, 2)
intro_format = intro_format.replace(stra, repa, 2)
intro_format = intro_format.replace(str2, rep2, 2)
intro_format = intro_format.replace(str3, rep3, 2)
intro_format = intro_format.replace(str4, rep4, 2)
intro_format = intro_format.replace(strRef, urlRef, 2)
intro_format = intro_format.replace(str_MEbut, rep_MEbut, 2)
intro_format = intro_format.replace(str_TRbut, rep_TRbut, 2)
intro_format = intro_format.replace(str_Polbut, rep_Polbut, 2)

if type(metastable) == str: #if not metastable, then remove metastable button
    str_metbut = 'value="Metastable state data"'
    rep_metbut = 'value="Metastable state data" style = "visibility: hidden;"'
    #str_metbut = '<button class="button btn noprint " id="showTable3" value="Metastable state data"  onmouseout="this.innerHTML=\'Metastable state data\'" style=\'width:120pt; color: black;\'>Metastable state data </button>'
    #rep_metbut = ''
    indmb = intro_format.find(str_metbut)
    intro_format = intro_format.replace(str_metbut, rep_metbut)
    
if type(metastable) != str: #if metastable, add bottom text listing states
    str_metnames = '<b></b><!--metastable breaker-->'
    rep_metnames = '<b>'
    for k in metastable_states:
        rep_metnames += k + ' '
    rep_metnames += '</b>'
    intro_format = intro_format.replace(str_metnames, rep_metnames)


# In[21]:


#nuclear table data for element
s = nuc_sub.to_html(index = False)
num_tr = s.count('<tr>')
rows = ''
for i in range(num_tr):
    rows += '<tr>\n' + '\t'
    start = s.find('<tr>')
    end = start + s[start:].find('</tr>') + 7 #the tr blocks
    subset = s[start:end]
    num_td = subset.count('<td>')

#     subset = subset.replace('<td>NaN', '<td style = "display:none">NaN') #hide NaNs
#     subset = subset.replace('<td></td>', '<td style = "display:none"></td>') #hide empty rows
#     subset = subset.replace('<td>E', '<td style = "display:none">E') #hide Keys
    for j in range(num_td):
        
        result = re.search('<td>(.*)</td>', subset)
        row = '<td>' +result.group(1)+'</td>'
        q = subset.find(row)
        subset = subset[q + len(row):] #iterates through rows
        if j == 0:
            #superscript the isotope number. Look for "Cs", 'Ca' etc. remember elemetn_info[1] is only the name, no +
            #this splits <td>43Ca</td> into <td><sup>43</sup>Ca</td>
            row = '<td>' + '<sup>' + row.split(element_info[1])[0].split('<td>')[1] + '</sup>' + element_info[1] + '</td>' 
        if j in [1, 2, 7, 8,10, 11, 13, 14]: #keys, theory numbers
            row = row.replace('<td>', '<td style = "display: none">')

        if j == (num_td - 1): #don't tab on last entry
            rows += row + '\n'
        else:
            rows += row + '\n' + '\t'
    rows += '</tr>\n'
        #print(row, i)
        
    #print(subset)
    s = s[end:]


# In[22]:


#fixes some strange to_html artifacts for proper superscript, removes NaN strings
rows = rows.replace('&lt;sup&gt;', '<sup>')
rows = rows.replace('&lt;/sup&gt;', '</sup>')
rows = rows.replace('NaN', "")
rows_nuc = rows
# print('NUCLEAR')
# print(rows)


# In[23]:


#nuclear to subscript. Nuclear does not need to go to subscript, throws off another column
# sub_scripts = ['1/2', '3/2', '5/2', '7/2', '9/2', '11/2']
# htmls = [rows] 
# for i in sub_scripts:
#     for j, k in enumerate(htmls):
#         htmls[j] = htmls[j].replace('%s' % i, '<sub>%s</sub>' % i)
# nuc_tabl = htmls[0]
# print(nuc_tabl)


# In[24]:


#excel data, nuclear
# nuc_exl = nuc_sub.to_html(index = False)
# nuc_exl = nuc_exl[nuc_exl.find('<tbody>'):]
# nuc_exl = nuc_exl.replace("NaN", "")
# print(nuc_exl)


# In[25]:


#plus_versEle = element_info[0]
hyper_fname = r'OtherData\%s_hyperfine.xlsx' % (element)
hyper = pd.read_excel(hyper_fname, 
                    engine='openpyxl', header = 0,  usecols = [0,1, 2, 3, 4, 5], dtype = str)
hyper.dropna(how = 'all', inplace = True)


# In[26]:


col1 = hyper.columns[0] #column 1 name
if 'Unnamed' in hyper.columns[0]: #isotope not in header row
    #rename columns to isotope, and done
    hyper.rename(columns = {col1: "Isotope"}, inplace = True)
#     empty_row = pd.DataFrame([[np.nan] * len(hyper.columns)], columns=hyper.columns)
#     hyper = empty_row.append(hyper, ignore_index=True)
#     hyper.loc[0, 'Isotope'] = hyper['Isotope'][1] #put in isotope name
#     hyper.loc[1, 'Isotope'] = ''
#     hyper.loc[0, col1] = col1
#     hyper = hyper[1:] # drop first now NaN row
    
else: #need to put first isotope name in value row
    col1 = hyper.columns[0]
    #empty_row = pd.DataFrame([[np.nan] * len(hyper.columns)], columns=hyper.columns)
    #hyper = empty_row.append(hyper, ignore_index=True)
    hyper.loc[0, col1] = col1
    hyper.rename(columns = {col1: "Isotope"}, inplace = True)
hyper[['Isotope']] = hyper[['Isotope']].replace([' '], ['NaN']) #some read ins have ' ' in value place need to be NaN
hyper[0:3]


# In[27]:


#rename hyper, draw title
# hyper_ele = hyper['Unnamed: 0'][0]
# hyper.drop(columns = ['Unnamed: 0'], inplace = True)
# print(hyper_ele)

hyper = hyper.rename(columns = {"Ref.": "Key1", "Ref..1": "Key2"})
hyper.reset_index(inplace = True, drop = True)
hyper_html = hyper.to_html(index = False)


# In[28]:


#add in correct titles, doi and ref values
ref1s = []
ref2s = []
doi1s = []
doi2s = []
for i in range(len(hyper)):
    if 'E' in str(hyper['Key1'][i]):
        ref1s.append(ref_exl.loc[ref_exl['Ref'] == hyper['Key1'][i]]['Name'].values[0]) #the full reference
        doi1s.append(ref_exl.loc[ref_exl['Ref'] == hyper['Key1'][i]]['DOI'].values[0])
    else:
        ref1s.append('')
        doi1s.append('')
    if 'E' in str(hyper['Key2'][i]):
        
        if str(hyper['Key2'][i]).count('E') == 1: #1 reference
            ref2s.append(ref_exl.loc[ref_exl['Ref'] == hyper['Key2'][i]]['Name'].values[0])
            doi2s.append(ref_exl.loc[ref_exl['Ref'] == hyper['Key2'][i]]['DOI'].values[0])#the full reference
        else:
            #print(i, str(hyper['Key2'][i]), str(hyper['Key2'][i]).count('E'))
            r1 = hyper['Key2'][i].split(',')[0]
            r2 = hyper['Key2'][i].split(',')[1].strip(' ')
            print((ref_exl.loc[ref_exl['Ref'] == r1]['DOI'].values[0], ref_exl.loc[ref_exl['Ref'] == r2]['DOI'].values[0]))
            #appends two references, separated by comma, str to get rid of start and stop ( )
            ref2s.append(str((ref_exl.loc[ref_exl['Ref'] == r1]['Name'].values[0], ref_exl.loc[ref_exl['Ref'] == r2]['Name'].values[0]))[1:-1])
            doi2s.append((ref_exl.loc[ref_exl['Ref'] == r1]['DOI'].values[0], ref_exl.loc[ref_exl['Ref'] == r2]['DOI'].values[0]))
    else:
        ref2s.append('')
        doi2s.append('')
    
#iterate through doi2 looking for reference with no first DOI
#if so, make doi just the second doi. repeat if second doi is empty
for j, i in enumerate(doi2s):
    if type(i) == tuple:
        if i[0] == '':
            doi2s[j] = i[1]
        elif i[1] == '':
            doi2s[j] = i[0]
hyper['Ref1'] = ref1s
hyper['DOI1'] = doi1s
hyper['Ref2'] = ref2s
hyper['DOI2'] = doi2s
hyper[0:3]


# In[29]:


#get the hyperfine constant tabular data
s = hyper.to_html(index = False)
num_tr = s.count('<tr>')
rows = ''

#will use index 6, 8 or 7, 9 to decide which nr# row needs
nr_decider13 = ['','','','','','nr','','nr3']
nr_decider24 = ['','','','','','','nr2','', 'nr4']

for i in range(num_tr):
    rows += '<tr>\n' + '\t'
    start = s.find('<tr>')
    end = start + s[start:].find('</tr>') + 7 #the tr blocks
    subset = s[start:end]
    num_td = subset.count('<td>')

    for j in range(num_td):
        result = re.search('<td>(.*)</td>', subset) 
        row = '<td>' +result.group(1)+'</td>'
        q = subset.find(row)
        subset = subset[q + len(row):] #iterates through rows
        if j == 0:
            #superscript the isotope number
            #if plus_versEle in row: #one of the isotope names
            if 'NaN' not in row:
                #display 43Ca+ as <sup>43</sup>Ca<sup>43</sup>
                #display 43Cs as <sup>CS</sup>
                if '+' in ele_display:
                    #print(plus_versEle)
                    row = '<td>' + '<sup>' + row.split(ele_display)[0].split('<td>')[1] + '</sup>' + ele_display.split('+')[0] + '<sup>' + '+' '</sup>' + '</td>'
                else:
                    row = '<td>' + '<sup>' + row.split(ele_display)[0].split('<td>')[1] + '</sup>' + ele_display + '</td>'
                print(row)

        
        if 'E' in subset: #need to have ref button
            if (j == 2) and ('NaN') not in row: #theory row value
                row = row.replace('</td>', ' <button type="button" class="btn btn-primary Ref1" data-toggle="modal" data-target="#exampleModalCenter">Ref</button></td>')
            if j == 4: #Experiment value row
                row = row.replace('</td>', ' <button type="button" class="btn btn-primary Ref2" data-toggle="modal" data-target="#exampleModalCenter">Ref</button></td>')
        if j in [3, 5]: #keys
            row = row.replace('<td>', '<td style = "display: none">')
            

            
        elif j in [6, 7, 8, 9]: #references
            inside = re.search('<td>(.*)</td>', row).group(1) #text inside <td>

            if j in [6, 8]: #the references
                if inside != '': #i.e. there is a reference
                    #nr1 or 3
                    row = row.replace('<td>', f'<td style = "display: none" class="{nr_decider13[j-1]}">')
                else:
                    row = row.replace('<td></td>', '<td style = "display: none">')
                
            elif j in [7, 9]: #the doi's
                #nr2 or 4
                row = row.replace('<td>DOI:', f'<td style = "display: none" class="{nr_decider24[j-1]}">')
                row = row.replace('<td></td>', '<td style = "display: none">') #if no DOI
                
        if j == (num_td - 1): #don't tab on last entry
            rows += row + '\n'
        else:
            rows += row + '\n' + '\t'
    rows += '</tr>\n'
    s = s[end:] #next section
    
rows = rows.replace('NaN', '')


# In[30]:


#turn hfine into subscript
htmls = [rows] #save_copy, Lifetimes, no_error, excel_copy
for i in sub_scripts:
    for j, k in enumerate(htmls):
        htmls[j] = htmls[j].replace('%s' % i, '<sub>%s</sub>' % i)
hfine_tabl = htmls[0]
# print("HYPER")
# print(hfine_tabl)


# In[31]:


# #excel table hyperfine constants
# hfine_exl = hyper.to_html(index = False)
# hfine_exl = hfine_exl[hfine_exl.find('<tbody>'):]
# hfine_exl = hfine_exl.replace("NaN", "")
# print(hfine_exl)


# In[32]:


meta_key_name = r"OtherData\Metastable_key.xlsx"
meta_key = pd.read_excel(meta_key_name, engine = "openpyxl", header = None, names = ['Ref', 'Name'], dtype = str)
meta_key.dropna(how = 'all', inplace = True)


# In[33]:


#set up key file with refs
doi_holder = []
name_holder = []
for i in range(len(meta_key)):
    try:
        doi_name = meta_key['Name'][i].split('DOI:')[1]
    except IndexError:
        doi_name = ''
    doi_holder.append(doi_name)
    name_str = meta_key['Name'][i].split('DOI')[0]
    last_comma = name_str.rfind(',')#finds last comma
    name_holder.append(name_str[:last_comma]) #removes last comma
meta_key['DOI'] = doi_holder
meta_key['Name'] = name_holder
meta_key


# In[34]:


if type(metastable) != str: #it IS metastable element, top table
    split = metastable[metastable['Theory'] == 'Transition'].index[0]
    top_tbl = metastable[:split].copy()
    bot_tbl = metastable[split:].copy()

    top_tbl = top_tbl.rename(columns = {'Unnamed: 0': 'State'})
    top_tbl.dropna(axis = 1, how = 'all', inplace = True)
    top_tbl.dropna(axis = 0, how = 'all', inplace = True)
    try:
        for i in range(len(top_tbl)):
            if top_tbl['Expt. Ref.'][i] == top_tbl['Expt. Ref.'][i]: #string value, not a NaN
                #print(top_tbl['Expt. '][i] + top_tbl['Expt. Ref.'][i])
                top_tbl.loc[i,'Expt. '] = top_tbl['Expt. '][i] + ' ' + top_tbl['Expt. Ref.'][i]
            if top_tbl['Theory Ref.'][i] == top_tbl['Theory Ref.'][i]: #string value, not a NaN
                #print(top_tbl['Expt. '][i] + top_tbl['Expt. Ref.'][i])
                top_tbl.loc[i,'Theory'] = top_tbl['Theory'][i] + ' ' + top_tbl['Theory Ref.'][i]
        top_tbl.drop(axis = 1, columns = ['Theory Ref.', 'Expt. Ref.'], inplace = True)
    except KeyError: #RaII case, missing entire columns
        pass
    top_tbl
    


# In[35]:


if type(metastable) != str:
    for i in meta_key.Ref.values:
        #print(i)
        pass


# In[36]:


if type(metastable) != str: #It IS metastable, top table formatting
    s = top_tbl.to_html(index = False)
    num_tr = s.count('<tr>')
    rows = ''
    for i in range(num_tr):
        rows += '<tr>\n' + '\t'
        start = s.find('<tr>')
        end = start + s[start:].find('</tr>') + 7 #the tr blocks
        subset = s[start:end]
        num_td = subset.count('<td>')
        for j in range(num_td):
            result = re.search('<td>(.*)</td>', subset) 
            row = '<td>' +result.group(1)+'</td>'
            q = subset.find(row)
            subset = subset[q + len(row):] #iterates through rows
            for k in meta_key.Ref.values: #'Ref1, Ref2, etc'
                if k in row:
                    if j == 2: #theory reference
                        nr_num1 = '' #for nr
                        nr_num2 = 2 #for nr2
                        ref_num = 1
                    elif j == 3: #experimental reference
                        nr_num1 = 3
                        nr_num2 = 4
                        ref_num = 2
                    ref_repl = f'<button type="button" class="btn btn-primary Ref{ref_num}" data-toggle="modal" data-target="#exampleModalCenter"> Ref</button></td>'
                    #name of the reference
                    name_rep = '\n' +  '\t' + f'<td style = "display:none" class="nr{nr_num1}">' + meta_key[meta_key['Ref']== k]['Name'].values[0] + '</td>' 
                    #doi of the reference
                    doi_rep = '\n' + '\t' + f'<td style = "display:none" class="nr{nr_num2}">' + meta_key[meta_key['Ref']== k]['DOI'].values[0] + '</td>'
                    row = row.replace(f'{k}</td>', ref_repl + name_rep + doi_rep)
            if j == (num_td - 1): #don't tab on last entry
                rows += row + '\n'
            else:
                rows += row + '\n' + '\t'
        rows += '</tr>\n'
        s = s[end:] #next section
    rows = rows.replace('NaN', '')


# In[37]:


if type(metastable) != str: #It IS metastable, subscripts
    htmls = [rows] #
    for i in sub_scripts:
        for j, k in enumerate(htmls):
            htmls[j] = htmls[j].replace('%s' % i, '<sub>%s</sub>' % i)
    mettop_tabl = htmls[0]
#     print("Meta Top")
#     print(hfine_tabl)
    


# In[38]:


if type(metastable) != str: #It IS metastable, bttom row and formatting
    #split index where second table starts
    split = metastable[metastable['Theory'] == 'Transition'].index[0]
    #top_tbl = metastable[:split].copy()
    
    bot_tbl = metastable[split:].copy()
    
#     top_tbl = top_tbl.rename(columns = {'Unnamed: 0': 'State'})
#     top_tbl.dropna(axis = 1, how = 'all', inplace = True)
#     top_tbl.dropna(axis = 0, how = 'all', inplace = True)
    
    bot_tbl.at[split, 'Unnamed: 0'] = 'Initial'
    bot_tbl.at[split, 'Property'] = 'Final'
    bot_tbl.dropna(axis = 1, how = 'all', inplace = True)
    
    
    for i in range(len(bot_tbl.columns)):
        #rename header into the correct titles from excel file
        bot_tbl = bot_tbl.rename(columns = {bot_tbl.columns[i] : bot_tbl[bot_tbl.columns[i]][split]}) 

    #drop now unneccesary row
    bot_tbl.drop(axis = 0, index = split, inplace = True)

    bot_tbl.dropna(axis = 0, how = 'all', inplace = True)
    bot_tbl.reset_index(inplace = True, drop = True)
    
    #top half metastable state
#     mtop_html = top_tbl.to_html(index = False)
#     mtop_html = mtop_html[mtop_html.find('<tbody>'):]
#     mtop_html = mtop_html.replace('NaN', '')
    
#     sub_scripts = ['1/2', '3/2', '5/2', '7/2', '9/2', '11/2']
#     htmls = [mtop_html] #save_copy, Lifetimes, no_error, excel_copy
#     for i in sub_scripts:
#         for j, k in enumerate(htmls):
#             htmls[j] = htmls[j].replace('%s' % i, '<sub>%s</sub>' % i)
#     mtop_html = htmls[0]
    #print(mtop_html)
    #print('--------')
    
    #bottom half metastable 
    mbot_html = bot_tbl.to_html(index = False)
    mbot_html = mbot_html[mbot_html.find('<tbody>'):]
    mbot_html = mbot_html.replace('NaN', '')
    
    sub_scripts = ['1/2', '3/2', '5/2', '7/2', '9/2', '11/2']
    htmls = [mbot_html] #save_copy, Lifetimes, no_error, excel_copy
    for i in sub_scripts:
        for j, k in enumerate(htmls):
            htmls[j] = htmls[j].replace('%s' % i, '<sub>%s</sub>' % i)
    mbot_html = htmls[0]
    metbot_tabl = mbot_html.replace('mB', '&mu;<sub>B</sub>')
#     print("Meta Bot")
#     print(mbot_html.replace('mB', '&mu;<sub>B</sub>'))
#     print(intro_format + '\n' + rows_nuc + '\n' + format_hold_hyp + '\n' + 
#           hfine_tabl + '\n' + format_hold_met1 + '\n' + mettop_tabl + '\n' + 
#           format_hold_met2 + metbot_tabl + '\n' + format_hold_end)


# In[39]:


if type(metastable) != str: #It IS metastable
    if 'Expt. ' not in top_tbl.columns: #no experiment value,  load in different css
        print('no experiment values')
        with open(r"Format_csvs\OtherData\Hyperfine_to_metastableNoExp.txt", encoding="utf8") as file:
            format_hold_met1 = file.read()


# In[40]:


#form_tables.count('style = "visibility: hidden;"')


# In[41]:


form_tables = intro_format + '\n' + rows_nuc + '\n' + format_hold_hyp + '\n' 
form_tables += hfine_tabl + '\n'
if type(metastable) != str:
    form_tables = form_tables.replace('style = "visibility: hidden;"', '') #unhide metastable button
    form_tables += format_hold_met1 + '\n' + mettop_tabl + '\n'
    form_tables += format_hold_met2 + metbot_tabl + '\n' 
else: #have empty tables for javascript
    form_tables += format_hold_met1.replace('"table3"', '"table3" style = "visibility: hidden;"') + '\n'
    form_tables += format_hold_met2.replace('"table4"', '"table4" style = "visibility: hidden;"') + '\n'
form_tables += format_hold_end
#print(form_tables)


# In[42]:


fname = "ElementsHTMLs\%sOther.html" % (element)
fname


# In[43]:


text_file = open(fname, "wb")
text_file.write(form_tables.encode('utf8'))
text_file.close()

