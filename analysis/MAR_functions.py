import os
import scipy
import numpy as np

#from MARfit_David import mar    # data fitting


# set the fit parameter
_gap = 1370                 # uV
_punkte = 400               # sample points to interpolate
_vmin = 0.1                 # fitting min partial of gap
_vmax = 3.3                 # max voltage of gap
_iterations = 5000          # iterations for fit
_max_channels = 4           # starting value of channels
additional_info = True     # print additional information in plot
show_plots = True          # show plots after fit (else direct save)

def movingaverage(interval, window_size):
    window= np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window, 'same')
    
def load_iv_files(directory, start="out", end=".txt"):
    iv_files = []
    for _file in os.listdir(directory):
        if _file.endswith(end):
            if not _file.startswith(start):
                iv_files.append(_file)
    iv_files.sort()
    print "Found %i IV-Files."%(len(iv_files))
    return iv_files


def load_iv_data(filename):
    loaded_data = scipy.loadtxt(filename,unpack=True, skiprows=2)
    
    # aquire parameters from file
    f = open(filename)
    line = f.readline()
    parameters =  [x.split(":") for x in line.split(",")]
    params = {}
    for x in parameters:
        if len(x) == 2:
            params[x[0]] = x[1]
    
    print "\nProcessing %s"%filename
    u = loaded_data[1]
    i = loaded_data[2]
    i = np.array(i)/104000.0
    
    return u,i,params

def align_direction(data):
    """Inverses Datasets according to first Dataset"""
    if data[0][0] > data[0][-1]:
        return_data = []
        for axe in data:
            axe = axe[::-1]
            return_data.append(axe)
    else:
        return_data = data        
    return return_data

def find_iv_offset(data=[[],[]],x_adjustment=2.5e-4, y_adjustment=1e-8):
    """Estimates the offset in x and y direction"""
    """ DEPRECATED!"""
    u,i = data[0],data[1]
    [u,i] = align_direction([u,i])
    length = len(u)
    if length%2==1:
        length += 1
        
    interp_factor = 30
    length *= interp_factor
    #print length
    
    limit = min(abs(min(u)),abs(max(u)))*0.2
    new_u = np.linspace(-limit,limit,length,endpoint=True)
    new_i = np.interp(new_u, u, i)
    new_u,new_i = new_u[1:-1],new_i[1:-1]
    length -= 2
    
    import pylab
    
    pylab.close("all")
    pylab.plot(u,i,label="Raw Data")
    pylab.hold(True)
    pylab.plot(new_u,new_i,"b--",linewidth=2,label="Interpolate")
    
    u1,i1 = new_u[0:length/2],new_i[0:length/2]
    u2,i2 = new_u[length/2:],new_i[length/2:]
    diff = i1[:] + i2[::-1]
    diff_sum = np.sum(np.abs(diff))
    pylab.plot(u2,diff)#,label="Diff. before %9.9f"%(diff_sum))    
    
    
    dx_range = int(x_adjustment/(2*limit/length))
    print dx_range
    dy_range = 2e-8
    dx = np.arange(-dx_range,dx_range,10)    # move along array elements
    dy = np.arange(-dy_range,dy_range,1e-9)
    
    xp = new_u[length/2+dx_range]
    pylab.plot([ xp , xp],[-dy_range, dy_range], "k--")
    pylab.plot([ -xp , -xp],[-dy_range, dy_range], "k--")
    pylab.plot([-xp,  xp], [-dy_range, -dy_range], "k--")
    pylab.plot([-xp,  xp], [dy_range, dy_range], "k--")
    
    #pylab.xlim([-5*xp, 5*xp])
    #pylab.ylim([-5*dy_range, 5*dy_range])
    
    _min,min_x,min_y = 999,0,0
    len_x = len(dx)
    len_y = len(dy)
    #matrix = np.zeros((len_y,len_x))
    for y in range(len_y):
        for x in dx:#range(len_x):
            
            u1,i1 = new_u[dx_range+x : length/2+x] , new_i[dx_range+x : length/2+x]+dy[y]
            u2,i2 = new_u[length/2+x:-dx_range+x] , new_i[length/2+x:-dx_range+x]+dy[y]
            #diff_sum = abs(np.sum(i1+i2[::-1]))
            u2,i2 = u2[::-1],i2[::-1]
            diff_sum = np.sum(abs(i1+i2))
            #matrix[y,x] = diff_sum
            if diff_sum < abs(_min):
                _min = abs(diff_sum)
                min_x = x
                min_y = y
                print "Origin: %fuV %fnA"%(u2[0]*1e6,i2[0]*1e9)#,_min,min_x,min_y
            #print y,x,diff_sum   
    #print matrix
    #matrix = np.matrix(matrix)
    print _min,min_x,min_y
    print len_x,len_y
    
    x,y = min_x,min_y

    u1,i1 = new_u[dx_range+x : length/2+x]-new_u[length/2+x] , new_i[dx_range+x : length/2+x]+dy[y]-new_i[length/2+x]
    u2,i2 = new_u[length/2+x:-dx_range+x]-new_u[length/2+x] , new_i[length/2+x:-dx_range+x]+dy[y]-new_i[length/2+x]
    u1,i1 = new_u[dx_range+x : length/2+x] , new_i[dx_range+x : length/2+x]+dy[y]
    u2,i2 = new_u[length/2+x:-dx_range+x] , new_i[length/2+x:-dx_range+x]+dy[y]
    
    diff = i1+i2[::-1]
    diff_sum = np.sum(np.abs(diff))
    pylab.plot(u2,diff)#,label="Diff. after %9.9f"%(diff_sum)) 
    pylab.plot(abs(u1),i1,"+",label="1")
    pylab.plot(u2,i2,"+",label="2")
    print "final diff sum: %9.9f"%(diff_sum)
    
    pylab.plot(u1,i1,"r",label="Corrected")
    pylab.plot(u2,i2,"r")
    
    print "Origin: %fuV %fnA"%(u2[0]*1e6,i2[0]*1e9)
    print "Shift: %fuV %fnA"%(dx[x],dy[y])
    

    
    pylab.grid(True)
    pylab.legend()
    pylab.show()
    
    du,di = 0,0
    #input("Press Enter to continue...")
    return du,di

def find_iv_offset_2(data=[[],[]],x_adjustment=2.5e-4, y_adjustment=1e-8, verbal=False):
    """Estimates the offset in x and y direction"""
    u,i = data[0],data[1]
    [u,i] = align_direction([u,i])
    length = len(u)
    if length%2==1:
        length += 1
        
    interp_factor = 30
    length *= interp_factor
    
    limit = min(abs(min(u)),abs(max(u)))*0.2
    new_u = np.linspace(-limit,limit,length,endpoint=True)
    new_i = np.interp(new_u, u, i)
    new_u,new_i = new_u[1:-1],new_i[1:-1]
    length -= 2
    
    if verbal:
        import pylab
        
        pylab.close("all")
        pylab.plot(u,i,label="Raw Data")
        pylab.hold(True)
        pylab.plot(new_u,new_i,"b--",linewidth=2,label="Interpolate")
    
    u1,i1 = new_u[0:length/2],new_i[0:length/2]
    u2,i2 = new_u[length/2:],new_i[length/2:]
    diff = i1[:] + i2[::-1]
    diff_sum = np.sum(np.abs(diff))
    
    if verbal:
        print "limit %f, sample length %i"%(limit, length)
    dx_range = int(x_adjustment/(2*limit/length))
    #print dx_range
    dx = np.arange(-dx_range,dx_range,10)    # move along array elements
    
    
    _min,min_x = 999,0
    #len_x = len(dx)

    for x in dx:#range(len_x):
        center = length/2+x
        
        u1,i1 = new_u[dx_range+x : center] , new_i[dx_range+x : center]-new_i[center]
        u2,i2 = new_u[center:-dx_range+x] , new_i[center:-dx_range+x]-new_i[center]
        #diff_sum = abs(np.sum(i1+i2[::-1]))
        u2,i2 = u2[::-1],i2[::-1]
        diff_sum = np.sum(abs(i1+i2))
        #matrix[y,x] = diff_sum
        if diff_sum < abs(_min):
            _min = abs(diff_sum)
            min_x = x
            #print "Origin: %fuV %fnA"%(u2[0]*1e6,i2[0]*1e9)#,_min,min_x,min_y
        #print y,x,diff_sum   
    
    #print _min,min_x
    #print len_x
    
    x = min_x
    center = length/2+x
    u1,i1 = new_u[dx_range+x : center]-new_u[center] , new_i[dx_range+x : center]-new_i[center]
    u2,i2 = new_u[center:-dx_range+x]-new_u[center] , new_i[center:-dx_range+x]-new_i[center]
   
    diff = i1+i2[::-1]
    #diff_sum = np.sum(np.abs(diff))
    
    if verbal:
        pylab.plot(u1,i1,"r",label="Corrected")
        pylab.plot(u2,i2,"r")

        print "Offset: %fuV %fnA"%(new_u[center]*1e6,new_i[center]*1e9)

        pylab.grid(True)
        pylab.legend()
        pylab.show()
    
    du,di,shift = new_u[center],new_i[center],x
    
    u,i = u-du,i-di
    u_min = np.argmin(abs(u))
    u,i = u[u_min:],i[u_min:]
    
    return du,di,shift,u,i


if __name__ == "__main__":
    iv_dir = r"C:\Users\David Weber\Desktop\Pb216\\"
    iv_files = load_iv_files(iv_dir)
    iv_file = iv_files[5]

       
    u,i,params = load_iv_data(os.path.join(iv_dir,iv_file))    
    u_min = np.argmin(abs(u))
    find_iv_offset_2([u,i])