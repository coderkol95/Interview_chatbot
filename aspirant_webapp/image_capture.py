import cv2
import time
import datetime
from numpy import savetxt

time_delay = 40
test_is_on=True
intervieweeID = "1234"

def capture_image(intervieweeID):
    #Capture frame
    ret,frame = videoCaptureObject.read()
    #Capture timestamp
    timestamp = str(datetime.datetime.now().date())+"_"+str(datetime.datetime.now().hour)+"_"+str(datetime.datetime.now().minute)
    #Filename
    filename = intervieweeID+"@"+timestamp
    #Writing the image to disk
    cv2.imwrite(f".\{filename}.jpg",frame)
    #Writing the numpy array as csv to disk
    savetxt(f"{filename}.csv", frame, delimiter=',')
    #Release the webcam and close windows which captured the images
    videoCaptureObject.release()
    cv2.destroyAllWindows()

while(test_is_on):
    #Capturing images after time_delay
    time.sleep(time_delay)
    #Initiate process for capturing image
    videoCaptureObject = cv2.VideoCapture(0)
    #Capture image and store to drive
    capture_image(intervieweeID)


    
