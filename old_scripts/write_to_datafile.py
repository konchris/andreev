# -*- coding: utf-8 -*-
"""
Created on Sat Nov 02 17:21:14 2013

@author: David Weber
"""

def write_datafile(data, path='', filename='', header='',datafield=''):
    """Writes data to desired file with given header
    Data is accepted in twodimensional list of type [[x..],[y..]]
    The header is expected without ending '\n'!"""

    comment_string = '#'   
 
    if not path[len(path)-1] == '\\':
        path = path+'\\'
    
    ensure_dir(path)

    filename = filename+'.csv'
    
    try:
        f = open(path+filename, 'w')
        dimension = len(data)
        length = len(data[0])

        # comment the header        
        
        header = header.replace('\n',comment_string+'\n'+comment_string)
        f.write(comment_string+header+comment_string+'\n')
        datafield = datafield.replace('\n',comment_string+'\n'+comment_string)
        f.write(comment_string+datafield+comment_string+'\n')
        
        for index in range(0,length):
            row = ''
            for index2 in range(0,dimension):
                if row == '':
                    row = str(data[index2][index])
                else:
                    row = row + '\t' + str(data[index2][index])
            f.write(row+'\n')
        f.close();
    except Exception,e:
        log("Problems at writing data",e)
        print "Data backup follows:"
        print data