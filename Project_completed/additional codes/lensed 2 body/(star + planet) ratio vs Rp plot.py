'''

pixelated sun and earth in 2D orbit, projected to 1D and lensed, no animation
can extract ratio of radii from lensed data and orig transit data
from this, can see lensing effects on measurement.

Here I investigate the imact on the ratio of lensing by varying planet radius

@author: Maciej Tomasz Jarema ppymj11

'''

# import modules
import numpy as np
import matplotlib.pyplot as plt
import scipy
import Project_completed.modules.lensing_function as lensing
import Project_completed.modules.class_2body as bodies
import Project_completed.modules.draw_pixels as pix_draw
import timeit

# %%

# start the timer
start = timeit.default_timer()

# start up lensing parametrers and constants
size = 400
rc = 0
eps = 0
dom = 4
year = 3.156e7
maxR = 1.496e11  # AU in SI
size_source = 4e11  # size of the source plane

# get pixel size to scale down from full animation to reduced coords
p_width = size_source/size

# set up simualtion time parameters
t_max = 0.6 * year
t_number = 300
t_arr = np.linspace(0, t_max, t_number)
dt = t_arr[-1] - t_arr[-2]

# set up Rp array to test
star_size = 50
P_radii = np.arange(3, 17, 2).astype(int)

# set up 2 body system parameters in SI, using imported classes:
Star = bodies.body_def(Mass=2e30, size=star_size, x=0, y=0, vx=0, vy=0)  # Star
Planet = bodies.body_def(Mass=6e24, size=P_radii[0], x=maxR, y=0, vx=0, vy=-29800)  # Planet

# Merge them into a system:
system = bodies.system_def(Star, Planet)
system.initials()  # produce initial conditions in system instance

# #############################################################################
# simulation of 2 bodies orbiting in plane, for centre positions
# #############################################################################

# call odeint to solve it:
solution = scipy.integrate.odeint(system.jacobian_get, system.init, t_arr, rtol=1e-10)

# from it extract wanted positions
xs_anim = solution[:, 0]
xp_anim = solution[:, 2]

ys_anim = solution[:, 1]
yp_anim = solution[:, 3]

# #############################################################################
# from animated solution, get the pixelated images of the bodies
# and light curves with and without gravitationally lensing
# #############################################################################

# set lists to store produced data
orig_ratios_lst = []
lens_ratios_lst = []

# loop over transit frame with different R_p, collect light curves and get ratii
for rp in P_radii:
    
    # upgrade the planet size
    Planet.size_change(rp)
    
    # initialise the lists that will store integrated, bolometric 'luminosity'
    # for both transit data and lensed transit
    lumin_bol = []
    lumin_bol_lensed = []
    
    # loop over the simulation result values and get data from transit and lensed transit
    for t_index in range(len(t_arr)):
        
        # reset the image and get current x values for planet and star
        image_s = np.zeros((size, size, 3))
        x = [xs_anim[t_index], xp_anim[t_index]]
        
        # scale down to domain and find which x pixels these lie in
        # NB y index is always half way up
        index_s = np.floor((x[0] + size_source/2)/p_width)
        index_p = np.floor((x[1] + size_source/2)/p_width)
        index_s = index_s.astype(int).transpose()  # change them to integers
        index_p = index_p.astype(int).transpose()  # and shape correctly
        
        # initial checker: (if planet is in front when in line of star), using the y data
        pfront = True
        if abs(index_s + Star.size) > abs(index_p - Planet.size) and abs(index_s - Star.size) < abs(index_p + Planet.size):
            if yp_anim[t_index] > ys_anim[t_index]:
                pfront = False
        
        # draw on the star as a big, white circle, use prepared function.
        image_s = pix_draw.draw_sphere(Star.size, image_s, index_s, (255, 255, 255))
        
        # draw on the planet as a smaller, dark circle, if not behind star
        if pfront:
            image_s = pix_draw.draw_sphere(Planet.size, image_s, index_p, (0, 0, 0))
    
        # save the luminosities into the list, lens, and save the new luminosities
        lumin_bol.append(np.sum(image_s/255))
        image_lens = lensing.lens(image_s, rc, eps, dom)
        lumin_bol_lensed.append(np.sum(image_lens/255))
    
    # turn resulting lists into arrays to slice
    lumin_bol = np.array(lumin_bol)
    lumin_bol_lensed = np.array(lumin_bol_lensed)
    
    # from dip sizes get Radii for each and print
    ratio_lens = (lumin_bol_lensed[0] - np.min(lumin_bol_lensed))/lumin_bol_lensed[0]
    ratio_orig = (lumin_bol[0] - np.min(lumin_bol))/lumin_bol[0]
    
    # save these to lists
    orig_ratios_lst.append(np.sqrt(ratio_orig))
    lens_ratios_lst.append(np.sqrt(ratio_lens))
    
    if rp == P_radii[-2]:
        plt.figure()
        plt.plot(np.arange(0, len(lumin_bol), 1), lumin_bol)


# set up a figure, axis and visuals for the light curves
fig = plt.figure()
ax = fig.gca()
ax.tick_params(labelsize=20)
ax.set_xlabel('Rp [pixels]', fontsize=20)
ax.set_ylabel(r'$R_{p} \ / \ R_{s}$',fontsize=20)
ax.plot(P_radii, orig_ratios_lst, 'r-.', label='original')
ax.plot(P_radii, lens_ratios_lst, 'k', label='lensed')
ax.legend(fontsize=20)

# return time to run
stop = timeit.default_timer()
print('Time to run was: {:.4f}'.format(stop - start) + ' s')

