import numpy as np
from matplotlib import pyplot as plt
from telemetry import processtelemetry
from scipy import interpolate
import csv

def plotstyle():
	# makes the plot look pretty :)
	ax1.set_xlabel('Distance(m)')
	ax1.set_ylabel('Velocity (km/h)')
	ax1.legend(loc='upper right',fontsize=11,fancybox=True)
	majxticks = np.arange(0,L,500)
	minxticks = np.arange(0,L,100)
	majyticks = np.arange(vmin,vmax,50)
	minyticks = np.arange(vmin,vmax,10)
	ax1.set_xticks(majxticks)
	ax1.set_xticks(minxticks,minor=True)
	ax1.set_yticks(majyticks)
	ax1.set_yticks(minyticks,minor=True)
	ax1.grid(which='major',alpha=0.5)
	ax1.grid(which='minor',alpha=0.25)
	ax1.axis([0,L,vmin,vmax])
	plt.tight_layout()

def plottimedelta(d1,t1,d2,t2,delta):
	# calculates the time difference at any distance. 
	# requires interpolation of distance and time data since 
	# the datapoints are at different frequencies for each driver. 
	da = np.linspace(min(d1),max(d1),1000)
	db = np.linspace(min(d2),max(d2),1000)
	pa = interpolate.interp1d(d1,t1)
	pb = interpolate.interp1d(d2,t2)

	if max(da) > max(db):
		d = da
	else:
		d = db
	
	dt = pa(da) - pb(db)

	# plots the time delta
	deltalabel = ax1.get_legend_handles_labels()[1]
	ax2 = ax1.twinx()
	ax2.plot(d,dt,'k',alpha=0.375)
	ax2.plot([0,L],[0,0],'k',lw=1,alpha=0.2)
	ax2.annotate(deltalabel[0][:-1-10]+' faster',(25,-delta/5),va='center',alpha=0.66)
	ax2.annotate(deltalabel[1][:-1-10]+' faster',(25,delta/5),va='center',alpha=0.66)
	ax2.axis([0,L,-3*delta,3*delta])
	ax2.set_yticks(np.arange(-3*delta,4*delta,delta))
	ax2.set_ylabel('Time Delta (s)',color='0.625')
	ax2.tick_params(axis='y',colors='0.625')

file1 = '2017_aut_bot.csv'
file2 = '2017_aut_vet.csv'
v1,t1,d1,dtb1 = processtelemetry(file1)
v2,t2,d2,dtb2 = processtelemetry(file2)

vmin, vmax = 50,350
L = 4318

fig = plt.figure(1,figsize=[20,8])

ax1 = fig.add_subplot(1,1,1)
ax1.plot(d1,v1,color='c',label='Bottas: 01:04.251')
ax1.plot(d2,v2,color='r',label='Vettel: 01:04.293')
plt.setp(ax1.lines,lw=1.1,alpha=0.85)

plottimedelta(d1,t1,d2,t2,0.25)
plotstyle()

plt.show()

# fname = file1[:12]+file2[-7:-4]
# fig.savefig(fname+'.png',bbox_inches='tight',dpi=100)
# fig.savefig(fname+'hd.png',bbox_inches='tight',dpi=300)