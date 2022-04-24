/*
	Author: Dalvan Griebler (dalvangriebler@gmail.com)
	Adapted from: http://docs.opencv.org/2.4/doc/tutorials/highgui/video-write/video-write.html
	Description: This is a simple video streaming application  
	Version-data: 02/11/2016

*/
#include <iostream> 
#include <string>   
#include <opencv2/core/core.hpp>        // Basic OpenCV structures (cv::Mat)
#include <opencv2/highgui/highgui.hpp>  // Video write
#include <opencv2/opencv.hpp>

using namespace std;
using namespace cv;

static void help(){
	cout
		<< "------------------------------------------------------------------------------" << endl
		<< "This program shows how to write video files."                                   << endl
		<< "You can extract the R or G or B color channel of the input video."              << endl
		<< "Usage:"                                                                         << endl
		<< "./video-write inputvideoName [ R | G | B] [Y | N]"                              << endl
		<< "------------------------------------------------------------------------------" << endl
		<< endl;
}
VideoCapture inputVideo;
VideoWriter outputVideo;
int channel;
Size S;
int total_frames=0;
int main(int argc, char *argv[]){
	setNumThreads(0);
	help();
	if (argc < 2){
		cout << "Not enough parameters" << endl;
		return -1;
	}
	const string source      = argv[1];
	inputVideo.open(source);               
	if (!inputVideo.isOpened()){
		cout  << "Could not open the input video: " << source << endl;
		return -1;
	}
	string::size_type pAt = source.find_last_of('.');                  // Find extension point
	const string NAME = source.substr(0, pAt) + argv[2][0] + ".avi";   // Form the new name with container
	int ex = static_cast<int>(inputVideo.get(CV_CAP_PROP_FOURCC));     // Get Codec Type- Int form

	// Transform from int to char via Bitwise operators
	char EXT[] = {(char)(ex & 0XFF) , (char)((ex & 0XFF00) >> 8),(char)((ex & 0XFF0000) >> 16),(char)((ex & 0XFF000000) >> 24), 0};

	S = Size((int) inputVideo.get(CV_CAP_PROP_FRAME_WIDTH),    // Acquire input size
				  (int) inputVideo.get(CV_CAP_PROP_FRAME_HEIGHT));

	outputVideo.open(NAME, ex, 30, S, true);

	if (!outputVideo.isOpened()){
		cout  << "Could not open the output video for write: " << source << endl;
		return -1;
	}

	cout << "Input frame resolution: Width=" << S.width << "  Height=" << S.height
		 << " of nr#: " << inputVideo.get(CV_CAP_PROP_FRAME_COUNT) << endl;
	cout << "Input codec type: " << EXT << endl;

	channel = 2; // Select the channel to save
	switch(argv[2][0]){
		case 'R' : channel = 2; break;
		case 'G' : channel = 1; break;
		case 'B' : channel = 0; break;
	}
	[[spar::ToStream]]while(1){       
		Mat src, res;
		total_frames++;
		inputVideo >> src;              // read frame
		if (src.empty()) break;         // check if end of video
		vector<Mat> spl;
		split(src, spl);                // process - extract only the correct channel
		for (int i =0; i < 3; ++i){
			if (i != channel){
				spl[i] = Mat::zeros(S, spl[0].type());
			}
		}
		merge(spl, res);
		[[spar::Stage,spar::Input(res),spar::Output(res), spar::Replicate(6)]]{
			cv::GaussianBlur(res, res, cv::Size(0, 0), 3);
			cv::addWeighted(res, 1.5, res, -0.5, 0, res);
			Sobel(res,res,-1,1,0,3);
		}
		[[spar::Stage,spar::Input(res)]]{
			outputVideo << res;	//write frame		
		}
	}
	cout << "Finished writing" << endl;
	std::cout << "Total Frames: " << total_frames << std::endl;
	return 0;
}

