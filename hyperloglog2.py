#!/usr/bin/env python3
"""hyperloglog2 - HyperLogLog cardinality estimation."""
import sys,hashlib,math
class HyperLogLog:
    def __init__(s,p=14):s.p=p;s.m=1<<p;s.registers=[0]*s.m;s.alpha=0.7213/(1+1.079/s.m)
    def _hash(s,item):return int(hashlib.sha256(str(item).encode()).hexdigest(),16)
    def add(s,item):
        h=s._hash(item);idx=h&(s.m-1);w=h>>s.p;s.registers[idx]=max(s.registers[idx],s._rho(w))
    def _rho(s,w):
        if w==0:return 64-s.p
        return(w&-w).bit_length()
    def count(s):
        Z=sum(2**(-r) for r in s.registers);E=s.alpha*s.m**2/Z
        if E<=2.5*s.m:V=s.registers.count(0);return round(s.m*math.log(s.m/V)) if V else round(E)
        return round(E)
    def merge(s,other):
        for i in range(s.m):s.registers[i]=max(s.registers[i],other.registers[i])
if __name__=="__main__":
    import random;hll=HyperLogLog(14)
    n=100000;
    for i in range(n):hll.add(f"item_{i}")
    est=hll.count();err=abs(est-n)/n*100
    print(f"Actual: {n}, Estimated: {est}, Error: {err:.2f}%")
    for dup in range(n):hll.add(f"item_{dup}")
    print(f"After adding duplicates: {hll.count()} (should still be ~{n})")
