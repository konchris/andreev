import os

userList = os.listdir('C:\\Users')

for i in userList:
    if userList[i] == '1K_Stick_Clone':
        userIndex = 2
        break
    elif userList[i] == 'David Weber':
        userIndex = 1
        break
    else:
        print 'Can not detect defined User.'
        

if userIndex == 2:
    """ Defines which yoko driver to load"""
    installed_yoko = "7651"

    """ Defines weather to save txt files as well"""
    save_good_old_txt = False

    """ Defines the addresses of the different devices."""
    installed_agilent_current = "USB0::0x0957::0x0607::MY53008595::0::INSTR"
    installed_agilent_voltage = "USB0::0x0957::0x0607::MY53006248::0::INSTR"
    
    """ Motor address"""
    installed_motor = "COM1"
    
if userIndex == 1:
    """ Defines which yoko driver to load"""
    installed_yoko = "GS200"

    """ Defines weather to save txt files as well"""
    save_good_old_txt = False

    """ Defines the addresses of the different devices."""
    installed_agilent_current = "USB0::0x0957::0x0607::MY47031049::0::INSTR"
    installed_agilent_voltage = "USB0::0x0957::0x0607::MY47030989::0::INSTR"
    
    """ Motor address"""
    installed_motor = "ASRL3"
    
    