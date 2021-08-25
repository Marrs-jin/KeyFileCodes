#!/usr/bin/env python
# coding: utf-8

# In[1]:


element_list = ['BaII', 'BeII', 'CaII', 'Cs', 'Fr', 'K', 'Li', 
                'MgII', 'Na', 'RaII', 'Rb', 'SrII']
for tt in range(len(element_list)):
    element = element_list[tt]
    try:
        get_ipython().run_line_magic('run', '-i TransitionManualInput.py')
    except (RuntimeError, TypeError, NameError, IndexError):
        print("THERE IS SOME ERROR in TR, ME, ALL!")
        break
for tt in range(len(element_list)):
    element = element_list[tt]
    try:
        get_ipython().run_line_magic('run', '-i OtherData.py')
    except (RuntimeError, TypeError, NameError, IndexError):
        print("THERE IS SOME ERROR in Other!")
        break

