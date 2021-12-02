# trying to optimise lensing a galaxy cluster

import numpy as np
import matplotlib.pyplot as plt
import project.lensing_function as lensing
import timeit

# %%

# start the timer
start = timeit.default_timer()

# set the seed for repeatable results
np.random.seed(34563)

# set up some initial parameters
rc = 0.2
eps = 0
size = 400
dom = 2  # abs() of domain of r values (normally -1, 1 --> 1)
max_a = 0.4  # maximum galaxy scale-length, in pixels
minor_max = 21  # max minor axis in pixels
gal_N = 25  # number of galaxies to generate in source image

# ############################################################################
# Generate a random galaxy cluser
# ############################################################################

# begin an empty source image array, with RGB
image = np.zeros((size, size, 3))


# randomly generate the galaxy properties

# randomly generate f_0 in each RGB band, make sure these are integers
# put these in a tuple to append to the pixel
f0r = np.random.randint(0, 255, gal_N)
f0g = np.random.randint(0, 255, gal_N)
f0b = np.random.randint(0, 255, gal_N)
f0 = np.vstack((f0r, f0g, f0b))

# randomly generate a centre pixel indexes
x_centr, y_centr = np.random.randint(0, size, gal_N), np.random.randint(0, size, gal_N)

# randomly generate a, in units of pixels:
a = np.random.rand(gal_N) * max_a

# randomly generate minor and major axis
minor = np.random.randint(1, minor_max+1, gal_N)
# major is larger than minor, therefore generate for each corr. minor
major = []
for g in range(gal_N):
    maj_dummy = np.random.randint(minor[g], 5*minor_max)
    major.append(maj_dummy)

# randomly generate angle of major axis to horizontal, in radians
theta = np.random.rand(gal_N) * np.pi

# loop over generating each galaxy with these properties
for gal in range(gal_N):  
    # loop ver all values in square of side length = major
    for i in range(2*major[gal]+1):
        for j in range(2*major[gal]+1):
            # get x and y from these:
            x = -major[gal] + i
            y = -major[gal] + j
            # get rotation transformed coordinates
            xp = x*np.cos(theta[gal]) - y*np.sin(theta[gal])
            yp = x*np.sin(theta[gal]) + y*np.cos(theta[gal])
            # check if current point is outside the ellipse:
            if (xp/minor[gal])**2 + (yp/major[gal])**2 > 1:
                pass
            else:
                # its in ellipse, add its pixel data accordinly
                try:  # careful about image edges
                    image[x_centr[gal]+i, y_centr[gal]+j, :] += tuple(flux * np.exp(-np.sqrt((xp/minor[gal])**2 + ((yp/major[gal])**2))/a[gal]) for flux in f0[:, gal])                                     
                except IndexError:
                    pass

# ############################################################################
# Lens and present the  end result
# ############################################################################

# set up a figure, axis
fig = plt.figure()
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)

# set up visuals for each axis
ax1.set_aspect('equal')
ax2.set_aspect('equal')
plt.xticks([])  # take off the axis ticks for both, no need for images
plt.yticks([])
plt.sca(ax1)
plt.xticks([])
plt.yticks([])

# plot the soure image
ax1.imshow(image/255)

# plot the lensed image
image_lens = lensing.lens(image, rc, eps, dom)
ax2.imshow(image_lens/255)

# return time to run
stop = timeit.default_timer()
print('Time to run was: {:.4f}'.format(stop - start) + ' s')

# %%