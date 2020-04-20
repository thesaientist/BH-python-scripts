# test script

import numpy as np
import matplotlib.pyplot as plt


# function
def return_fig():
    fig1 = plt.figure()
    # fig1.show()
    return fig1

fig = return_fig()
fig.savefig('sample.png')


print('Done')