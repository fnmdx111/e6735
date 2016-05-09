video.py -- extract features from videos
Two method:

generateFeature(filename, time_length, segmentNum, framePerSegment, binX, binY, binZ, HistType = 1):
	
	this method is used to calculate the color histogram of the video, it returns a [segmentNum x (binX*binY*binZ)] matrix  to represent the video.
	
	filename			----	Filename of the video
	time_length			----	The length of the video to load, start from 0 seconds (seconds)
	segmentNum			----	Segment number of the video (the video will be segmented, and each segment will be extract histogram separately.)
	framePerSegment		----	The number of frames per segment
	binX, binY, binZ	----	Number of bins 
	HistType			----	0 : RGB colospace; 1 : HSV colorspace
	
	
	
generateFeature2(filename, time_length, segmentNum, framePerSegment, beta = 2, k = 64, binX =18, binY =3, binZ =3):
	
	this method is used to calculate the soft coding of the video, it returns a [segmentNum x k] matrix  to represent the video.
	
	returns a segmentNum x (binX*binY*binZ) matrix  to represent the video
	filename			----	Filename of the video
	time_length			----	The length of the video to load, start from 0 seconds (seconds)
	segmentNum			----	Segment number of the video (the video will be segmented, and each segment will be extract histogram separately.)
	framePerSegment		----	The number of frames per segment
	beta				----	parameter of soft coding (default = 2)
	k					----	feature  dimension (default = 64)
	binX, binY, binZ	----	Number of bins (default = 18, 3, 3)
	
cluster.py -- clustering histogram features
Two method:

histExtract(videodir = './', binX =18, binY =3, binZ =3, time_length = 0, segmentNum = 400, framePerSegment = 5):
	
	this method is used to extract histogram features of all videos in the database.
	
	videodir			----	Video directory address of all mp4 videos
	binX, binY, binZ	----	Number of bins (default = 18, 3, 3) ####SHOULD BE SAME AS generateFeature2####
	time_length			----	The length of the video to load, start from 0 seconds (default the whole video: default = 0)
	segmentNum			----	Segment number of the video (default = 0)
	framePerSegment		----	The number of frames per segment (default = 5)
	
histClustering(k = 64):
	
	this method is used to clustering histogram features.
	
	returns a segmentNum x (binX*binY*binZ) matrix  to represent the video
	k					----	cluster numbers (default = 64) ####SHOULD BE SAME AS generateFeature2####