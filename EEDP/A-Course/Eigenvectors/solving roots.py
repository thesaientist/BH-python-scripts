# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 17:48:58 2018

@author: 212601900
"""
mr=9500#lbs
ms=33480#lbs
mb=30*300*2#lbs
ks=6.66e6*2#lb/in(two supports)
E=29e6 #psi
I=20290 #in^4
l=30*12 #in
kb1=48*E*I/l**3 #lb/in
#kb1=kb1/48*192 #uncomment for clamped condition
kb2=kb1*2
ke=1e6 #lb/in

import sympy as sy
M=sy.Matrix([[mb,0,0],[0,ms,0],[0,0,mr]])
K=sy.Matrix([[ks+kb2,-kb2,0],[-kb2,kb2+ke,-ke],[0,-ke,ke]])
lam=sy.symbols('lambda')
cp=sy.det(K-lam*M)
eigs=sy.solveset(cp,lam)
print(eigs)