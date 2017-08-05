import numpy as np
import csv
import datetime
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.patches as patches

def getcsvdata(fname):
	q1,q2,q3 = [],[],[]
	with open(fname, 'r') as f:
		r = csv.reader(f,delimiter=',')
		for row in r:
			q1i = datetime.datetime.strptime(row[0],'%M:%S.%f')
			q2i = datetime.datetime.strptime(row[1],'%M:%S.%f')
			q3i = datetime.datetime.strptime(row[2],'%M:%S.%f')
			q1 += [q1i.minute*60 + q1i.second + q1i.microsecond/1e6]
			q2 += [q2i.minute*60 + q2i.second + q2i.microsecond/1e6]
			q3 += [q3i.minute*60 + q3i.second + q3i.microsecond/1e6]

	return [q1,q2,q3]

def reject_outliers(data,m):
	d = np.abs(data - np.median(data))
	mdev = np.median(d)
	s = d/mdev if mdev else 0.
	idxrem = np.where(s > m)[0]
	idxkeep = np.where(s < m)[0]
	
	return idxkeep,idxrem

def quali(q,m,r):
	rs = r[0] - 1
	split = len(q)//2
	ylimit = 5
	d1 = np.array(q[:split])
	d2 = np.array(q[split:])
	tdelta = d2[rs:r[1]]-d1[rs:r[1]]
	pdelta = tdelta/d1[rs:r[1]]*100
	pdelta = np.where(pdelta == 0.,ylimit,pdelta)
	idx = reject_outliers(pdelta,m)
	avg = np.mean(pdelta[idx[0]])
	pdelta = np.where(abs(pdelta) > ylimit,np.nan,pdelta)

	return avg,pdelta,idx

def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[N:] - cumsum[:-N]) / N 

def movingaverage(x,y,N):
	mavg = []
	mavgx = []
	for i in range(max(x)):
		indexes = np.where((x > i) & (x <= i+N))
		mavg += [np.mean(y[indexes])]
		mavgx += [i+(N+1)//2]
	return mavgx,mavg

def avgqualigap(fname,q=3,genplot=True,m=1.,r=[1,None],seasons=[]):
	qdata = getcsvdata(fname)[q-1]
	avg,pdelta,idx = quali(qdata,m,r)
	avg10 = np.mean(pdelta[idx[0]][idx[0] > len(pdelta)-11])

	if genplot:
		x = np.arange(1,len(pdelta)+1,1)
		figt = plt.figure(1,figsize=[x[-1]*0.25,5])
		ax1 = figt.add_subplot(1,1,1)
		ax1.axhline(y=0,color='#aaaaaa')
		xs = 0
		for season in seasons:
			xs0 = xs
			xs += seasonraceno[season]
			ax1.text(xs/2+xs0/2,2.625,season)
			ax1.axvline(x=xs,color='#bbbbbb')

		ax1.plot(x,pdelta,'bx',label='Counted')
		ax1.plot(x[idx[1]],pdelta[idx[1]],'o',ms=10,mfc='None',mec='r',label='Ignored')
		N = 5
		mavgx,mavgy = movingaverage(x[idx[0]],pdelta[idx[0]],N)
		ax1.plot(mavgx,mavgy,'k',alpha=0.5,label=str(N)+'-pt moving average')
		leg = ax1.legend(loc='upper right',fontsize=10,fancybox=True,numpoints=1)
		ax1.add_artist(leg)
		# print(leg.get_window_extent())
		# print(leg.get_frame().get_bbox().bounds)
		ax1.text(-2,2.5,fname[8:11].upper()+'\n faster',ha='center',va='center')
		ax1.text(-2,-2.5,fname[11:14].upper()+'\n faster',ha='center',va='center')
		ax1.text(-2,0,'% Difference',rotation='vertical',ha='center',va='center')
		ax1.set_xlabel('Race No. as teammates')
		ax1.annotate('',xytext=(-2,1),xy=(-2,2.25),
			xycoords='data',arrowprops=dict(arrowstyle="->",connectionstyle="arc3"),annotation_clip=False)
		ax1.annotate('',xytext=(-2,-1),xy=(-2,-2.25),
			xycoords='data',arrowprops=dict(arrowstyle="->",connectionstyle="arc3"),annotation_clip=False)
		majxticks = np.arange(0,xs+2,2)
		minxticks = np.arange(0,xs+1,1)
		majyticks = np.arange(-3,3,1)
		minyticks = np.arange(-3,3,0.25)
		ax1.set_xticks(majxticks)
		ax1.set_xticks(minxticks,minor=True)
		ax1.set_yticks(majyticks)
		ax1.set_yticks(minyticks,minor=True)
		ax1.grid(which='major',alpha=0.5)
		ax1.grid(which='minor',alpha=0.25)
		ax1.axis([0,xs+1,-2.5,2.5])
		ax1.tick_params(labelsize=11)

		d1count = len(pdelta[idx[0]][pdelta[idx[0]] > 0])
		d2count = len(pdelta[idx[0]][pdelta[idx[0]] < 0])
		ax1.text(x[0]-0.5,-1.5,'All times Q'+str(q),ha='left',va='center',color='#333333',fontsize=11)
		ax1.text(x[0]-0.5,-1.75,fname[8:11].upper()+' '+str(d1count)+' - '+str(d2count)+' '+fname[11:14].upper(),
			ha='left',va='center',color='#333333',fontsize=11)
		ax1.text(x[0]-0.5,-2.,'Overall Average: '+str.format('{0:+.3f}%',avg),
			ha='left',va='center',color='#333333',fontsize=11)
		ax1.text(x[0]-0.5,-2.25,'Average Last 10 Races: '+str.format('{0:+.3f}%',avg10),
			ha='left',va='center',color='#333333',fontsize=11)

		proxy1, = ax1.plot(-10,2,'r',lw=0,zorder=0,label=str(N)+'-pt moving average')
		proxy2, = ax1.plot(-10,2,'bx',zorder=10,label=' ')
		leg2 = ax1.legend(handles=[proxy1,proxy2],loc='upper right',fontsize=10,frameon=False,framealpha=1,numpoints=1)
		for text in leg2.get_texts():
			text.set_alpha(0)
		ax1.set_axisbelow(True)
		plt.tight_layout()
		plt.show()
		figt.savefig(fname[:-4]+'q'+str(q)+'.png',bbox_inches='tight',dpi=100)
		figt.clf()

	return avg

seasonraceno = {'2007':17,'2008':18,'2009':17,'2010':19,'2011':19,'2012':20,'2013':19,'2014':19,'2015':19,'2016':21,'2017':20}

vetric = avgqualigap('mercfer/vetric.csv',m=2.,seasons=['2014'])
hamros = avgqualigap('mercfer/hamros.csv',m=2.,seasons=['2014','2015','2016'])
hamros13 = avgqualigap('mercfer/hamros13.csv',m=2.5,seasons=['2013','2014','2015','2016'])

hambut = avgqualigap('mercfer/hambut.csv',m=3.5,seasons=['2010','2011','2012'])
alobutq1 = avgqualigap('mercfer/alobut.csv',q=1,m=3.,seasons=['2015','2016'])
alobutq2 = avgqualigap('mercfer/alobut.csv',q=2,m=.2,seasons=['2015','2016'])
alohamq2 = avgqualigap('mercfer/aloham.csv',q=2,m=3,seasons=['2007'])
alohamq3 = avgqualigap('mercfer/aloham.csv',q=3,m=4.,seasons=['2007'])
aloham = np.mean([np.mean([alohamq2,alohamq3]),np.mean([alobutq1,alobutq2])-hambut])

alorai = avgqualigap('mercfer/alorai.csv',m=2.,seasons=['2014'])
# vetrai = avgqualigap('mercfer/vetrai.csv',m=2.2,seasons=['2015','2016'])
vetrai = avgqualigap('mercfer/vetrai17.csv',m=3.,seasons=['2015','2016','2017'])
alovet = alorai-vetrai

hamvet = -(aloham - alovet)
hamrai = -(aloham - alorai)

alomas = avgqualigap('mercfer/alomas.csv',m=2.,seasons=['2010','2011','2012','2013'])
masbot = avgqualigap('mercfer/masbot.csv',m=2.1,seasons=['2014','2015','2016'])
# masrai = avgqualigap('masrai.csv',m=2.)
masrai = -(alomas - alorai)
botrai = -(masbot - masrai)
masvet = masrai - vetrai
botvet = -(masbot - masvet)

gaps = np.array([hamvet,hamrai,botvet,botrai])


m17 = np.array([82.188,91.678,88.769,93.289,79.149,72.223,71.459,100.593,64.251,86.600,76.530])
f17 = np.array([82.456,91.864,89.247,93.194,79.200,72.178,71.789,101.693,64.293,87.147,76.276])
num = len(m17)
whichgap = np.array([hamvet,hamvet,botvet,botvet,hamvet,botrai,hamvet,hamrai,botvet,hamrai,botvet])
diff = m17 - f17
pdiff = diff/m17*100
difftomerc = (pdiff + whichgap)*m17/100
race = ('AUS','CHI','BAH','RUS','SPA','MON','CAN','AZE','AUT','GBR','HUN','BEL','ITA','SIN','MAL','JAP','USA','MEX','BRA','ABU')
racenum = np.arange(1,num+1,1)

fig = plt.figure(2,figsize=[num,5])
ax = fig.add_subplot(1,1,1)
fig.suptitle('2017 F1 car performance difference between Mercedes and Ferrari in Q3',y=1.02,fontsize=16)
ax.axhline(y=0,color='#999999')
bm1 = np.ma.masked_where(difftomerc <= 0,difftomerc)
bm2 = np.ma.masked_where(difftomerc > 0,difftomerc)
ax.bar(racenum,bm1,align='center',color='#ff7f7f',ec='None',width=0.7)
ax.bar(racenum,bm2,align='center',color='#7fdede',ec='None',width=0.7)

for i, v in enumerate(difftomerc):
	ax.text(i + 1, v + np.sign(v)*0.1, str.format('{0:+.3f}s',v),
		color=('r' if np.sign(v)==1 else 'c'),ha='center',va='center')
	ax.text(i + 1, v + np.sign(v)*0.2, str.format('({0:+.3f}s)',diff[i]),
		color='#999999',ha='center',va='center')

majyticks = np.arange(-1.5,1.5+0.5,0.5)
minyticks = np.arange(-1.5,1.5+0.1,0.1)
ax.set_yticks(majyticks)
ax.set_yticks(minyticks,minor=True)
ax.set_yticklabels(['{0:+.1f}s'.format(x) for x in ax.get_yticks().tolist()])
# ax.set_yticklabels(['' for x in ax.get_yticks().tolist()])
ax.yaxis.set_ticks_position('none')
ax.grid(which='major',axis='y',alpha=0.5)
ax.grid(which='minor',alpha=0.25)
ax.set_axisbelow(True)
ax.set_xticks(np.arange(1,num+1,1))
ax.set_xticklabels(race)
ax.axis([0,num+1,-1.25,1.25])
ax.spines['left'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.tick_params(top='off',bottom='off',right='off',labelsize=11)
ax.text(0.35,1.,'Ferrari\nfaster',ha='left',va='center',color='#999999')
ax.text(0.35,-1.,'Mercedes\nfaster',ha='left',va='center',color='#999999')
ax.annotate('',xytext=(0.25,0.25),xy=(0.25,1.),
	xycoords='data',arrowprops=dict(arrowstyle="->",connectionstyle="arc3",color='#999999'),annotation_clip=False)
ax.annotate('',xytext=(0.25,-0.25),xy=(0.25,-1.),
	xycoords='data',arrowprops=dict(arrowstyle="->",connectionstyle="arc3",color='#999999'),annotation_clip=False)

signs = {-1:'- ',1:'+ '}
t = 1.1
box = patches.FancyBboxPatch((num-1.275,t-0.5),2.2,0.6,fc='white',ec='#666666',boxstyle='round,pad=0.005',mutation_scale=5.)
ax.add_patch(box)
ax.text(num-0.175,t,'Driver raw pace % gaps\n(-ve if 1st driver is faster)',color='#666666',fontsize=10,ha='center',va='center')
ax.text(num-0.175,t-0.16,'HAM v VET:',color='#666666',fontsize=10,ha='right',va='center')
ax.text(num-0.,t-0.16,str.format('{0:=+7.3f}%',-hamvet),color='#666666',fontsize=10,ha='left',va='center')
ax.text(num-0.175,t-0.26,'HAM v RAI:',color='#666666',fontsize=10,ha='right',va='center')
ax.text(num-0.,t-0.26,str.format('{0:=+7.3f}%',-hamrai),color='#666666',fontsize=10,ha='left',va='center')
ax.text(num-0.175,t-0.36,'BOT v VET:',color='#666666',fontsize=10,ha='right',va='center')
ax.text(num-0.,t-0.36,str.format('{0:=+6.3f}%',-botvet),color='#666666',fontsize=10,ha='left',va='center')
ax.text(num-0.175,t-0.46,'BOT v RAI:',color='#666666',fontsize=10,ha='right',va='center')
ax.text(num-0.,t-0.46,str.format('{0:=+7.3f}%',-botrai),color='#666666',fontsize=10,ha='left',va='center')

ax.text(num+1,-1.15,'Actual delta in brackets.',color='#999999',ha='right',va='center',fontsize=10)

plt.tight_layout()
plt.show()
fig.savefig('mercfer/mercfer.png',bbox_inches='tight',dpi=200)