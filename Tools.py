#cape(R)
#various utility functions used by the Classes...

import numpy as np

	 
def line_remove_strings(L): # takes the lines of section 2.1 L1E, and returns a line without strings
    return [x for x in L if is_float(x)]

def is_float(s):
    ''' little functions to verify if a string can be converted into a number '''
    try:
        float(s)
        return True
    except ValueError:
        return False
	
## Multiprocessing
MULTIPROC=6

mapfunc = None
def pmap(*args):
	global MULTIPROC
	try:
		MULTIPROC
	except NameError:
		MULTIPROC = None 
	if MULTIPROC != None and MULTIPROC > 1:
		global mapfunc
		if mapfunc == None:
			from multiprocessing import Pool
			mapfunc = Pool(MULTIPROC).map
		return mapfunc(*args)
	else:
		return map(*args)



    

def approx_jacobian(x, f, epsilon, *args):
    """Approximate the Jacobian matrix of callable function f

       * Parameters
         x       - The state vector at which the Jacobian matrix is
		 desired
         f    - A vector-valued function of the form f(x,*args)
         epsilon - The peturbation used to determine the partial derivatives
         *args   - Additional arguments passed to f

       * Returns
         An array of dimensions (lenf, lenx) where lenf is the length
         of the outputs of f, and lenx is the number of

       * Notes
         The approximation is done using forward differences

    """
    x0 = np.asfarray(x)
    f0 = f(*((x0,)+args))
    # print f0
    jac = np.zeros([len(x0),len(f0)])
    dx = np.zeros(len(x0))
    for i in range(len(x0)):
       dx[i] = epsilon
       # print func(*((x0+dx,)+args))
       jac[i] = (f(*((x0+dx,)+args)) - f0)/epsilon
       dx[i] = 0.0
    return jac.transpose()

def test_grad(x, f, Df, alfa): #Df(x;alfa Df(x))/alfa Df(x)^2-->1
    '''Arthur's gradient Test'''
    res = (f(x+alfa*Df(x))-f(x))/(alfa*norm(Df(x))**2)
    return res