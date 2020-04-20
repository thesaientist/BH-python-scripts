print("hello world!")
x = 2
y = 4
print("x + y = {}".format(x+y))

import numpy as np

x = np.arange(10)
y = np.sin(x)

import matplotlib.pyplot as plt

plt.figure()
plt.plot(x, y, 'r-')
plt.savefig('sinplot.png')
