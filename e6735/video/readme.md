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
	
	
	
generateFeature2(filename, time_length, segmentNum, framePerSegment, k = 64, binX =18, binY =3, binZ =3, beta = 50):
	
	this method is used to calculate the soft coding of the video, it returns a [segmentNum x k] matrix  to represent the video.
	
	returns a segmentNum x (binX*binY*binZ) matrix  to represent the video
	filename			----	Filename of the video
	time_length			----	The length of the video to load, start from 0 seconds (seconds)
	segmentNum			----	Segment number of the video (the video will be segmented, and each segment will be extract histogram separately.)
	framePerSegment		----	The number of frames per segment
	k					----	feature  dimension (default = 64)
	binX, binY, binZ	----	Number of bins 
	beta				----	parameter of soft coding (default = 40)