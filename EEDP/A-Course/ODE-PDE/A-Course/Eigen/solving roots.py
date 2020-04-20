# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 17:48:58 2018

@author: 212601900
"""
import numpy as np
mr=4309
ms=15186
mb=4081.882
ks=1.17e9
#kb=1.06e8/48*192
kb=1.06e8
ke=1.75e8
#
#coef1=-1*mb*mr*ms
#coef2=ks*mr*ms+kb*mr*ms+kb*mb*mr+ke*mb*mr+ke*mb*ms
#coef3=-1*ks*kb*mr-ks*ke*mr-ks*ke*ms-kb**2*mr-kb*ke*mr-kb*ke*ms-kb*ke*mb
#coef4=ks*kb*ke+kb**2*ke
#totcoef=[coef1,coef2,coef3,coef4]
#print(np.roots(totcoef))


#M=np.matrix([[mb,0,0],[0,ms,0],[0,0,mr]])
#K=np.matrix([[ks+kb,-kb,0],[-kb,kb+ke,-ke],[0,-ke,ke]])
import sympy as sy
#x=sy.symbols("x",real=True)
M=sy.Matrix([[mb,0,0],[0,ms,0],[0,0,mr]])
K=sy.Matrix([[ks+kb,-kb,0],[-kb,kb+ke,-ke],[0,-ke,ke]])
#solvethis=K-x*M
#obj=solvethis.det()
#simple=sy.simplify(obj)
#print(simple)
#ans=sy.solve(simple,x)
#print(ans)

lam=sy.symbols('lambda')
cp=sy.det(K-lam*M)
eigs=sy.solveset(cp,lam)
print(eigs)