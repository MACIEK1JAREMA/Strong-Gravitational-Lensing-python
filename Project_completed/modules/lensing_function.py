'''

define a fucntion that will lens a given image

@author: Maciej Tomasz Jarema ppymj11

'''

# import needed module
import numpy as np

# %%


def lens(image_s, rc, eps, dom=1):
    '''
    Lenses the given image for a planar, transparent, symmetric lensing object
    positioned at the centre of the image
    
    Parameters:
    --------------
    - square image as numpy array of values from 0 to 255 in RGB (N x N x 3)
    - central core radius rc (float)
    - ellipticity eps (float)
    - domain of the image, as absolute value (default=1, giving range [-1, 1])
    
    Returns:
    --------------
    array of the lensed image (N x N x 3)
    '''
    
    # check if the user gave a square image and get number of pixels per side
    if len(image_s[:, 0, 0]) == len(image_s[0, :, 0]):
        size = len(image_s)
    else:
        raise TypeError('Image must be square, can\'t broadcast with different shapes')
    
    # set up an empty array to store lensed image
    image_l = np.zeros([size, size, 3])
    p_width = 2*dom/(size)  # get pixel width
    
    # #########################################################################
    # Vectorised mapping of pixels to source plane and copying data:
    # #########################################################################
    
    # set up an array of index numbers corr. to lensed image array
    i_arr = np.arange(0, size, 1)
    j_arr = np.arange(0, size, 1)
    
    # get reduced coordinates r_1 and r_2 as arrays and use their grids to
    # get s by given equtions for s1 and s2
    r1 = 2*dom*i_arr/(size) - dom + p_width/2
    r2 = 2*dom*j_arr/(size) - dom + p_width/2
    r1g, r2g = np.meshgrid(r1, r2)
    
    # use lens equation to get positions on image_s
    s1 = r1g - ((1 - eps)*r1g)/np.sqrt(rc**2 + (1 - eps)*r1g**2 + (1 + eps)*r2g**2)
    s2 = r2g - ((1 + eps)*r2g)/np.sqrt(rc**2 + (1 - eps)*r1g**2 + (1 + eps)*r2g**2)
    
    # find which pixel the s1's and s2's all lie in, in the original image
    index_1 = np.floor((s1 + dom)/p_width)
    index_2 = np.floor((s2 + dom)/p_width)
    index_1 = index_1.astype(int).transpose()  # change them to integers
    index_2 = index_2.astype(int).transpose()  # and tranpose to match directions
    
    # copy the data from source image at these indexes over to lens image array
    image_l[:, :, :] += image_s[index_1, index_2, :]        
    
    # return the image to the suer
    return image_l


