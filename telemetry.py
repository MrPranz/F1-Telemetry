import csv
import numpy as np

def processtelemetry(csvfile,thrcut=1,brkcut=1,tb=False):
	# inputs:
	# csvfile = csv file as string
	# thrcut = normalised cut off value for throttle data. Sets this value as the max instead of the true max.
	# brkcut = normalised cut off value for brake data. Sets this value as the max instead of the true max.
	# tb = True if csv file has throttle/brake data, boolean.

	# outputs: 
	# v = 1d array of velocity
	# f = 1d array of time
	# d = 1d array of distance
	# [dtb,thr,brk] = array of 3x1d arrays of distance, throttle, and brake

	# read csv file
	with open(csvfile,'r') as file:
		reader = csv.reader(file)
		v_ocr,t_ocr,thr_ocr,brk_ocr = list(reader)

	v_all = []
	t_all = []
	thr_all = []
	brk_all = []

	# since the raw output from ocr is not always numeric, its converted to floats here where possible
	for j in range(0,len(v_ocr),1):
		try:
			vj = [float(v_ocr[j])]
			tj = [float(t_ocr[j])]
		except ValueError:
			vj = [-1]
			tj = [t_ocr[j]]
		v_all = v_all + vj
		t_all = t_all + tj
		if tb == True:
			try:
				thr_all = thr_all + [thr_ocr[j]]
				brk_all = brk_all + [brk_ocr[j]]
			except IndexError:
				pass

	# find and remove odd speed values
	kidx = []
	for k in range(len(v_all)):
		if v_all[k] == -1 or v_all[k] > 400 or v_all[k] < 30:
			kidx = kidx + [k]
	vc1 = np.delete(v_all,kidx)
	tc1 = np.delete(t_all,kidx)
	thr = np.delete(thr_all,kidx).astype(float)
	brk = np.delete(brk_all,kidx).astype(float)
	v,t = vc1,tc1

	# create distance array for throttle and brake traces
	dtb = np.array([0])
	tc1 = tc1.astype(float)
	for s in range(0,len(vc1)-1):
		dtbi = (vc1[s]+vc1[s+1])*(tc1[s+1]-tc1[s])*0.5/3.6
		dtb = np.append(dtb,dtbi+dtb[s])

	# create distance array for velocity trace
	d = np.array([0])
	t = t.astype(float)
	for n in range(len(v)-1):
		di = (v[n]+v[n+1])*(t[n+1]-t[n])*0.5/3.6
		d = np.append(d,di+d[n]) 

	# Since the throttle and brake data is the pixel count, these are normalised and converted. 
	# Pixel counts can vary a lot so thrcut and brkcut serve to fix this. For thrcut, it also serves
	# to remove the DRS addition of green pixels. 
	if tb:
		thrmax = max(np.extract(thr < thrcut*max(thr),thr))
		brkmax = max(np.extract(brk < brkcut*max(brk),brk))

		for i in range(len(thr)):
			if thr[i] > thrmax:
				thr[i] = thrmax
			if brk[i] > brkmax:
				brk[i] = brkmax 
			if brk[i] < 0.75*brkmax:
				brk[i] = 0
		thr = thr*(100/max(thr))
		brk = brk*(1/max(brk))

		# this next bit transforms the throttle curve past 30% throttle to account for the white text in the graphic.
		l1,l2 = 30,30
		u1,u2 = 60,67
		v1,v2 = 100,100
		k1,k2 = u1,u2

		r = (k2-v1)/(k1-v1)
		s = (u2-l1)/(u1-l1)

		for i2 in range(len(thr)):
			if thr[i2] > l1 and thr[i2] < u1:
				thr[i2] = s*(thr[i2]-l1) + l1
			elif thr[i2] > k1:
				thr[i2] = r*(thr[i2]-v1) + v1
	else:
		pass

	dtot = str(max(d))
	print(csvfile[0:-4],"completed. Distance =",dtot[0:6]+'m',",Time =",max(t),'seconds')
	f = t

	return v,f,d,[dtb,thr,brk]

if __name__ == '__main__':
	main()

# dictionary of parameters for each lap
params = {
		'AUS':
			{},
		'CHI':
			{},
		'BAH':
			{},
		'RUS':
			{},
		'SPA':
			{'num':5,'length':4655,'title':'F1 2017 R05 Spain - Circuit de Catalunya',
			'HAM':{'thr':0.7,'brk':0.75,'tb':True,'label':'Hamilton: 01.19.149','colour':'c'},
			'BOT':{'thr':0.66,'brk':0.5,'tb':True,'label':'Bottas: 01.19.390','colour':'#005656'},
			'VET':{'thr':1,'brk':1,'tb':True,'label':'Vettel: 01.19.200','colour':'r'},
			'VER':{'thr':1,'brk':1,'tb':False,'label':'Verstappen: 01.19.706','colour':'#440044'},
			'ALO':{'thr':1,'brk':1,'tb':False,'label':'Alonso: 01.21.076','colour':'#ff8200'}},
		'MON':
			{'num':6,'length':3337,'title':'F1 2017 R06 Monaco - Circuit de Monaco',
			'RAI':{'thr':1,'brk':1,'tb':False,'label':'Raikkonen: 01.12.178','colour':'r'},
			'VET':{'thr':0.7,'brk':0.05,'tb':True,'label':'Vettel: 01.12.221','colour':'#960000'},
			'BOT':{'thr':0.925,'brk':0.1,'tb':True,'label':'Bottas: 01.12.559','colour':'c'},
			'VER':{'thr':1,'brk':1,'tb':False,'label':'Verstappen: 01.12.496','colour':'#690069'},
			'RIC':{'thr':1,'brk':1,'tb':False,'label':'Ricciardo: 01.13.094','colour':'#ec00ec'},
			'BUT':{'thr':1,'brk':1,'tb':False,'label':'Button: 01.13.613','colour':'#ff9500'}},
		'CAN':
			{'num':7,'length':4361,'title':'F1 2017 R07 Canada - Circuit Gilles Villeneuve',
			'HAM':{'thr':1,'brk':1,'pass':0,'tb':False,'label':'Hamilton: 01.11.459','colour':'c'},
			'VET':{'thr':1,'brk':1,'pass':0,'tb':False,'label':'Vettel: 01.11.789','colour':'r'},
			'VER':{'thr':1,'brk':1,'pass':0,'tb':False,'label':'Verstappen: 01.12.403','colour':'#690069'},
			'PER':{'thr':1,'brk':1,'pass':0,'tb':False,'label':'Perez: 01.13.018','colour':'#ff70ff'},
			'ALO':{'thr':1,'brk':1,'pass':0,'tb':False,'label':'Alonso: 01.13.693','colour':'#ff9500'}},
		'AZE':
			{'num':8,'length':6003,'title':'F1 2017 R08 Azerbaijan - Baku City Circuit',
			'HAM':{'thr':1,'brk':1,'pass':0,'tb':False,'label':'Hamilton: 01.40.593','colour':'c'},
			'BOT':{'thr':1,'brk':1,'pass':0,'tb':False,'label':'Bottas: 01.41.027','colour':'#005656'},
			'RAI':{'thr':1,'brk':1,'pass':0,'tb':False,'label':'Raikkonen: 01.41.693','colour':'r'},
			'VET':{'thr':1,'brk':1,'pass':0,'tb':False,'label':'Vettel: 01.41.841','colour':'#960000'},
			'VER':{'thr':1,'brk':1,'pass':0,'tb':False,'label':'Verstappen: 01.41.879','colour':'#690069'}},
		}