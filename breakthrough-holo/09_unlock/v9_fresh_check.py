# Round 9 fresh recomputation (main session): independent re-implementation of the m22/m23 and opus round-4 numbers.
# No imports from m22/m23; the thermal kick uses the exact exponential update instead of Euler integration.
import math, numpy as np
e0=8.854e-12; mu=1.81e-5; kg=0.026
# D kick ratio by explicit simulation with a different integrator (exact exponential update)
def kick(a,rho,c,K=1000,td=1e-4):
    tau=rho*c*a*a/(3*kg); T=K*td
    # exact periodic steady state via iteration of exact solution
    x=0.0
    for _ in range(200):
        x = x*math.exp(-td/tau) + K*(1-math.exp(-td/tau))   # heating phase, forcing K (mean=1)
        peak=x
        x = x*math.exp(-(T-td)/tau)
    return tau, peak
for a,rho,c in ((40e-6,600,800),(20e-6,300,800),(5e-6,1190,1420)):
    tau,p=kick(a,rho,c); print(f"D a {a*1e6:.0f}: tau {tau*1e3:.3f} ms, peak/ss {p:.2f}")
# B charges
a=20e-6
Ev=27.2e5*(1+0.54/math.sqrt(a*100)); ql=4*math.pi*e0*a*a*Ev
print(f"B Peek {Ev:.3e} V/m q_lim {ql:.3e}; recapture {4*math.pi*e0*(a+5e-6)**2*1e3:.3e}; Pauth room {12*math.pi*e0*a*a*1e3:.3e}; corona {12*math.pi*e0*a*a*1e6:.3e}")
# E pump bound
lam=1.55e-6; X=0.6; w=40e-6; G=(X*lam/(math.pi*w))**2; Gp=math.sqrt(1/0.7); L=math.log(Gp)
for name,sig,tau,g,lp in (("ErYb",7e-25,8e-3,100,976e-9),("NdYAG",2.8e-23,2.3e-4,300,808e-9),("InGaAsP",5e-20,1e-9,1.5e5,1.2e-6)):
    hnu=6.626e-34*3e8/lp; P=G*L*L*hnu/(2*lam*g*sig*tau); print(f"E {name}: {P:.3e} W")
# F
a=5e-6; d=3e-3; n=1/d**3; aws=(3/(4*math.pi*n))**(1/3)
qmax=4*math.pi*e0*a*a*27.2e5*(1+0.54/math.sqrt(a*100))
for f in (0.03,0.3,1.0):
    q=f*qmax; mus=0.1*n*q*q/(4*math.pi*e0*aws); st=n*6*math.pi*mu*a*0.01*0.1
    print(f"F q {q:.2e}: shear {mus:.2e} stress {st:.2e} strain {st/mus:.1e}")
# H
for cap,hs,lab in ((0.785e-3,2.14*1.1,'skin'),(10e-3,7.1,'eye static')):
    for v in (0.01,0.03,0.1):
        w=math.sqrt(2*cap/(math.pi*hs*1.5e7*v)); print(f"H {lab} v {v}: w {w*1e6:.1f} um modes {(0.6/(math.pi*w))**2:.2e} loop {10*v/w:.0f}")
# m23 room case
U=0.25; a=7e-6; rho=1520; vs=2*rho*9.81*a*a/(9*mu); Uf=U+vs
n=1*20/(Uf*3e-3*1e-3); m=4/3*math.pi*a**3*rho
print(f"m23 vs {vs*1e3:.2f} mm/s n {n:.3e} mass {n*m*1e6:.1f} mg/m3 tau {n*2*math.pi*a*a*0.8*100:.2f}% g/h {n*Uf*0.64*m*3600*1e3:.1f}")
kl=0.5/3600+vs/2.5; print(f"  room ug/m3 at 99.9%: {n*Uf*0.64*m*1e-3/(kl*50)*1e9:.1f}")
print(f"  drop {math.exp(-2):.3f} vert {n*1e-6*Uf*0.05:.2f}")
J=3*1e-3*3e-3; D=20*1e-3/Uf; p=0.9*8/(3*math.pi)*1*0.66
psc=4*math.pi*(J/D)/(p*683*0.71)
for wv in (140e-6,80e-6):
    eff=(1-math.exp(-2*a*a/wv**2))*0.9; tc=1e-3/Uf; E=psc/eff*tc
    zR=math.pi*wv*wv/520e-9
    print(f"  w_v {wv*1e6:.0f}: P {E/tc*1e3:.2f} mW E {E*1e6:.2f} uJ AEL {7e-4*tc**0.75*1e6:.2f} uJ spots {1026*20*tc:.0f} ghost dots {n*math.pi*wv*wv/2*2*zR:.3f} zR {zR*100:.1f} cm")
# probe photoelectrons
Pp=0.2e-3; wp=0.35e-3; inter=1-math.exp(-2*a*a/wp**2); om=math.pi*(0.0175)**2/1.6**2
ph=Pp*inter*0.9*om/(4*math.pi)*0.76*(2*wp/Uf)/(6.626e-34*3e8/850e-9)
print(f"  probe e- {ph*0.35:.0f}")
# opus checks
d0=(6*30e-15/math.pi)**(1/3); dm=d0*(0.03*1010/1550)**(1/3)
psat=2.339e3; rv=psat/(461.5*293)*0.5
tdry=1000*d0**2/(8*2.5e-5*rv)
print(f"opus: d0 {d0*1e6:.1f} um mote {dm*1e6:.1f} um dry {tdry:.2f} s latent {30e-15*1000*2.45e6*1.6e5:.1f} W p90 {0.9*8/(3*math.pi):.3f}")
