video.py -- extract features from videos
Two method:

generateFeature(filename, segmentNum, HistType, binX, binY, binZ):
	
	this method is used to calculate the color histogram of the video, it returns a [segmentNum x (binX*binY*binZ)] matrix  to represent the video.
	
	filename			----	Filename of the video
	segmentNum			----	Segment number of the video (the video will be segmented, and each segment will be extract histogram separately.)
	HistType			----	0 : RGB colospace; 1 : HSV colorspace
	binX, binY, binZ	----	Number of bins 
	
	
	
generateFeature2(filename, segmentNum, binX, binY, binZ, k, beta):
	
	this method is used to calculate the soft coding of the video, it returns a [segmentNum x k] matrix  to represent the video.
	
	returns a segmentNum x (binX*binY*binZ) matrix  to represent the video
	filename			----	Filename of the video
	segmentNum			----	Segment number of the video (the video will be segmented, and each segment will be extract histogram separately.)
	binX, binY, binZ	----	Number of bins 
	k					----	feature length (default = 64)
	beta				----	parameter of soft coding (default = 40)