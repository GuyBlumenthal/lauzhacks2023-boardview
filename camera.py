import cv2
import time

calib = {
    'phase': 0,
    'coord': [
        [0, 0],
        [0, 0],
    ],
    'delay': 0
}

# 2 #cv2.CAP_DSHOW
def OpenCamera(devPort, delay) -> cv2.VideoCapture:
    calib['delay'] = delay

    #Initiallizes camera stream
    return Start_Cam(devPort)

def InitializeStream(camera):
    # Add mouse listener to video stream
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', select_point)

def WaitForNextFrame(camera):
    cv2.waitKey(calib['delay'])
    return Take_Photo(camera)

def ShowFrame(img):
    cv2.imshow('image', img)

def IsInitalized():
    return calib['phase'] == 2

def GetSize():
    return [
        calib['coord'][1][0] - calib['coord'][0][0],
        calib['coord'][1][1] - calib['coord'][0][1],
    ]

def Main():
    #Sets port to avaliable external camers
    DevPort = 2 #cv2.CAP_DSHOW
    #Initiallizes camera stream
    Device = Start_Cam(DevPort)

    # Add mouse listener to video stream
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', select_point)

    while True:
        img = Take_Photo(Device)
        cv2.imshow('image',img)
        cv2.waitKey(100)

def Start_Cam(DevPort):
    #Initiate Device at DevPort
    cam = cv2.VideoCapture(DevPort)
    return cam

def Take_Photo(cam):
    #Take photo with device cam and reutrn image frame
    ret,frame=cam.read()
    if ret:
        if calib['phase'] == 2:
            frame = crop(frame)
        return frame
    else:
        print("image has error")
        cam.release()
        return False

def select_point(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONUP:
        if calib['phase'] == 0:
            calib['coord'][0][0] = x
            calib['coord'][0][1] = y
            calib['phase'] = calib['phase'] + 1
        elif calib['phase'] == 1:
            calib['coord'][1][0] = x
            calib['coord'][1][1] = y
            calib['phase'] = calib['phase'] + 1

def crop(img):
    x1 = calib['coord'][0][0]
    y1 = calib['coord'][0][1]
    x2 = calib['coord'][1][0]
    y2 = calib['coord'][1][1]
    crop_img = img[y1:y2, x1:x2]
    return crop_img

if __name__ == "__main__":
    Main()
