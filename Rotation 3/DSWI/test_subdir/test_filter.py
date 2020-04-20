import numpy as np
filterDef = np.concatenate((np.arange(1,8), np.arange(6,0,-1))) / 49
x = np.array([3, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
print(np.dot(x, filterDef))