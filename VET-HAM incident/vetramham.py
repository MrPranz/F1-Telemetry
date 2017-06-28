import csv
import numpy as np
from scipy import interpolate
from matplotlib import pyplot as plt

with open('vetramham.csv','r') as file:
	reader = csv.reader(file)
	v1,t1,v2,t2 = list(reader)

with open('sc1_hamvet.csv','r') as file:
	reader = csv.reader(file)
	sc1v1,sc1t1,sc1v2,sc1t2 = list(reader)

with open('sc3_ham.csv','r') as file:
	reader = csv.reader(file)
	sc3v1,sc3t1 = list(reader)

v_ham = np.array(v1).astype(float)
t_ham = np.array(t1).astype(float)
v_vet = np.array(v2).astype(float)
t_vet = np.array(t2).astype(float)
sc1_vham = np.array(sc1v1).astype(float)
sc1_tham = np.array(sc1t1).astype(float)
sc1_vvet = np.array(sc1v2).astype(float)
sc1_tvet = np.array(sc1t2).astype(float)
sc3_vham = np.array(sc3v1).astype(float)
sc3_tham = np.array(sc3t1).astype(float)


def calcdist(v,t):
	d = [0]
	for i in range(len(v)-1):
		di = 0.5/3.6*(t[i+1]-t[i])*(v[i]+v[i+1])
		d += [d[i] + di]

	return np.array(d)

d_ham = calcdist(v_ham,t_ham)
d_vet = calcdist(v_vet,t_vet)-19.5

fig = plt.figure(1,figsize=[15,5])
ax1 = fig.add_subplot(1,1,1)
ax1.plot(t_ham,v_ham,'c-',label='HAM')
ax1.plot(t_vet-t_vet[0],v_vet,'r-',label='VET')
# ax1.plot(sc1_tham-1.5,sc1_vham,'c-',alpha=0.2,label='HAM (SC1)')
# ax1.plot(sc1_tvet+0.5-1.5,sc1_vvet,'r-',alpha=0.2,label='VET (SC1)')
# ax1.plot(sc3_tham-0.6-1.5,sc3_vham,color='#004444',alpha=0.25,label='HAM (SC3)')

ax1.annotate('1st Impact',xy=(12.35,56),xytext=(13.5,72),ha='center',
	arrowprops=dict(arrowstyle='-|>',connectionstyle='arc3,rad=0.2',fc='black'))
ax1.annotate('2nd Impact',xy=(16.4,58),xytext=(17.55,74),
	arrowprops=dict(arrowstyle='-|>',connectionstyle='arc3,rad=0.2',fc='black'))
ax1.annotate('',xytext=(9.3,85),xy=(11.5,50),arrowprops=dict(arrowstyle='-|>',fc='c',ec='c',connectionstyle='arc3,rad=0.025'))
ax1.annotate('Steady\n deceleration',xy=(9.4,58),ha='center',va='center')
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Velocity (km/h)')

th = np.linspace(min(t_ham[:1169]),max(t_ham[:1169]),1000)
tv = np.linspace(min(t_vet),max(t_vet),1000)
ph = interpolate.interp1d(t_ham[:1169],d_ham[:1169])
pv = interpolate.interp1d(t_vet,d_vet)
dd = ph(th) - pv(tv)
t = th
ax3 = ax1.twinx()
ax3.set_ylabel('Distance between HAM and VET (m)',color='0.625')
ax3.axis([0,20,-14,24])
ax3.set_yticks(np.arange(-10,30,10))
ax3.tick_params(axis='y',colors='0.625')
ax3.plot(t,dd,'k',alpha=0.25)
ax3.axhline(y=0,color='k',alpha=0.125)

ax1.axvline(x=4,color='k',lw=1.25,ls='--',alpha=0.25)
ax1.axvline(x=11,color='k',lw=1.25,ls='--',alpha=0.25)
ax1.annotate('Turn 14 apex',xy=(4,200),xytext=(2,210),
	arrowprops=dict(arrowstyle='-|>',connectionstyle='arc3,rad=0.2',fc='black'))
ax1.annotate('Turn 15 apex',xy=(11,200),xytext=(12,210),
	arrowprops=dict(arrowstyle='-|>',connectionstyle='arc3,rad=0.2',fc='black'))

ax1.legend(loc='upper right',fontsize=11,fancybox=True)
majxticks = np.arange(0,20,2)
minxticks = np.arange(0,20,0.5)
majyticks = np.arange(0,250,50)
minyticks = np.arange(0,250,10)
ax1.set_xticks(majxticks)
ax1.set_xticks(minxticks,minor=True)
ax1.set_yticks(majyticks)
ax1.set_yticks(minyticks,minor=True)
ax1.grid(which='major',alpha=0.5)
ax1.grid(which='minor',alpha=0.25)
ax1.axis([0,20,30,220])

plt.tight_layout()
plt.show()
# fig.savefig('vetramham2.png',dpi=100)