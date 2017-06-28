from PIL import Image,ImageEnhance
import numpy as np
import pytesseract
import subprocess
import cv2
import csv

def get_timestamps(filename):
	cmnd = ['ffprobe', '-select_streams', 'v', '-show_entries', 'frame=pkt_pts_time', '-of', 'csv', filename]
	p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out,err =  p.communicate()
	tstr = str(out)[8:-7].replace('\\r\\nframe','').split(',')

	return tstr

def throttle_ocr(image,coords):
	img = image[coords[1]:coords[3],coords[0]:coords[2]]
	# lower and upper ranges for green pixels, format BGR
	lower = np.array([0,110,0])
	upper = np.array([90,200,90])
	res = cv2.inRange(img,lower,upper)
	count = np.count_nonzero(res)
	return count

def brake_ocr(image,coords):
	img = image[coords[1]:coords[3],coords[0]:coords[2]]
	# lower and upper ranges for red pixels, format BGR
	lower = np.array([0,0,100])
	upper = np.array([50,50,200])
	res = cv2.inRange(img,lower,upper)
	count = np.count_nonzero(res)
	return count

def velocity_ocr(image,coords,f1app):
	# crop and convert image to greyscale
	img = Image.fromarray(image).crop(coords).convert('L')
	img = img.resize([img.width*2,img.height*2])

	if f1app:
		# filters for video from the f1 app 
		img = ImageEnhance.Brightness(img).enhance(3.0)
		img = ImageEnhance.Contrast(img).enhance(2.0)
	else:
		# filters for onboard video graphic
		img = ImageEnhance.Brightness(img).enhance(0.1)
		img = ImageEnhance.Contrast(img).enhance(2.0)
		img = ImageEnhance.Contrast(img).enhance(4.0)
		img = ImageEnhance.Brightness(img).enhance(0.2)
		img = ImageEnhance.Contrast(img).enhance(16.0)
	
	try:
		# vel = pytesseract.image_to_string(img,config='digits')
		vel = pytesseract.image_to_string(img)
	except UnicodeDecodeError:
		vel = -1

	return vel

def vidocr_to_csv(video,vcoords,tbcoords,f1app=True):
	# inputs: 
	# video = video file as a string
	# vcoords = array of pixel coordinates [top left x, top left y, bottom right x, bottom right y] for velocity
	# tbcoords = array of pixel coordinates [top left x, top left y, bottom right x, bottom right y] for throttle/brake
	# f1app = boolean, default = True, use True for video from the F1 app, False for onboard video.
	# outputs .csv file with each line as a row of each extracted parameter. 

	# capture video via opencv
	vid = cv2.VideoCapture(video)
	s,frm = vid.read()

	v_all = []
	t_all = []
	thr_all = []
	brk_all = []

	step = 1
	total_frames = vid.get(cv2.CAP_PROP_FRAME_COUNT);
	print(total_frames)
	i = int(total_frames*0);
	vid.set(0,i)

	# go through each frame and extract data
	while s:
		if i >= int(total_frames):
			break
		s,frm = vid.read()
		if i%step == 0 or i == total_frames-1:
			v_temp = velocity_ocr(frm,vcoords,f1app)
			t_temp = vid.get(cv2.CAP_PROP_POS_MSEC)/1e3
			v_all += [v_temp]
			# thr_temp = throttle_ocr(frm,tbcoords)
			# brk_temp = brake_ocr(frm,tbcoords)
			# thr_all += [thr_temp]
			# brk_all += [brk_temp]
		if i%200 == 0:
			print(v_temp,t_temp,i)
		i += 1

	t_all = get_timestamps(video)
	# save data to .csv with same filename as videofile
	with open(video[0:-4]+'.csv', 'w', newline='') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(v_all)
		writer.writerow(t_all)
		# writer.writerow(thr_all)
		# writer.writerow(brk_all)
		writer.writerow([])
		writer.writerow([])

	print(video,"completed.")

vidocr_to_csv('.mp4',[],[])