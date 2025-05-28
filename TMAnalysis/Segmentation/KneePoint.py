#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   PURPOSE: Get knee point in a data set
#         
#   INPUTS
#      x       x vector of data                      
#      y       y vector of data
#   OUTPUTS
#      minidx  index of the knee point
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
def KneePoint(x,y):  
    #Import Modules
    import numpy as np

    #Normalize the data
    xnorm = np.zeros(x.shape[0])
    ynorm = np.zeros(y.shape[0])
    for i in range(x.shape[0]):
        xnorm[i] = (x[i]-min(x))/(max(x)-min(x))
        ynorm[i] = (y[i]-min(y))/(max(y)-min(y))

    #Create the difference curve
    xdiff = xnorm
    ydiff = abs(ynorm-xnorm)

    #Find max of the difference curve
    maxval = max(ydiff)
    maxidx = np.where(ydiff==maxval)
    kneex_norm = xnorm[maxidx[0][0]]
    kneey_norm = ynorm[maxidx[0][0]]

    #Unnormalize
    kneex = kneex_norm*(max(x)-min(x)) + min(x)

    #Find minimum between x and kneex
    mindat = min(abs(kneex-x))
    minidx = np.where(mindat == abs(kneex-x))

    return minidx