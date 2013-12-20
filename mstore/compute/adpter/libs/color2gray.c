#include <cv.h>
#include <cxcore.h>
#include <highgui.h>

void color2gray(char *srcImagePath, char *destImagePath){

    if(srcImagePath==NULL || destImagePath==NULL){
        return;
    }

    IplImage* srcImage = cvLoadImage(srcImagePath, -1);
    IplImage* dstImage = cvCreateImage( cvSize(srcImage->width, srcImage->height), srcImage->depth, 1);

    cvCvtColor(srcImage, dstImage, CV_BGR2GRAY);
    cvSaveImage(destImagePath, dstImage, 0);

    cvReleaseImage(&srcImage);
    cvReleaseImage(&dstImage);
    
    return;
}

