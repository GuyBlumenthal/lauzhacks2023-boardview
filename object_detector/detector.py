import cv2
import numpy as np

size = (1024, 1024)
AREA = (1024 ** 2)

BORDER_SIZE = 5

def objetc_mask(img):
    pass

def Main():
    img = cv2.imread("examples/object_rejection.jpg")

    img = cv2.resize(img,size)

    gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    gray = cv2.rectangle(gray, [0, 0], [1024, 1024], 255, BORDER_SIZE)

    # _,thresh = cv2.threshold(gray, np.mean(gray), 255, cv2.THRESH_BINARY_INV)
    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        10
    )

    print(AREA)

    edges = cv2.dilate(cv2.Canny(thresh,0,255),None)
    edges = cv2.rectangle(edges, [0, 0], [1024, 1024], 0, 20)

    cnts = list(filter(
        lambda x: (cv2.contourArea(x) / AREA) > 0.04,
        # lambda x: print(f"{100 *cv2.contourArea(x) / AREA:.3}") == None,
        sorted(
            cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2],
            key=cv2.contourArea
    )))

    mask = np.zeros(size, np.uint8)
    masked = cv2.drawContours(mask, cnts,-1, 255, -1)

    cv2.imwrite("test.jpg", masked)

def rect_area(rect):
    return (rect[1][0] - rect[0][0]) * (rect[1][1] - rect[0][1])

def cnts2rects(cnts):
    rects = []

    for cnt in cnts:
        top = left = size[0]
        bottom = right = 0

        for pnt in cnt:
            y, x = pnt[0]
            top     = min(y, top)
            left    = min(x, left)

            bottom  = max(y, bottom)
            right   = max(x, right)

        rects.append(np.array([
            [top, left],
            [bottom, right],
        ]))

    return rects

def get_rejection_mask(img):
    img = cv2.resize(img, size)

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    #gray = cv2.fastNlMeansDenoising(gray)
    gray = cv2.fastNlMeansDenoising(gray)

    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        55,
        3
    )
    # _,thresh = cv2.threshold(thresh, np.mean(thresh), 255, cv2.THRESH_BINARY_INV)

    edges = cv2.dilate(cv2.Canny(thresh,0,255),None)

    contours = sorted(cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2], key=cv2.contourArea)

    cnt_rects = cnts2rects(contours)
    cnt_rects = filter(
        lambda rect: (rect_area(rect) / AREA) >  0.05,
        cnt_rects
    )

    mask = np.zeros(size, np.uint8)
    disp = img
    for rct in cnt_rects:
        disp = cv2.rectangle(disp, rct[0], rct[1], 255, 1)
        mask = cv2.rectangle(mask, rct[0], rct[1], 255, -1)

    return disp, mask

def Main():
    img = cv2.imread("examples/object_rejection.jpg")
    for i in range(1):
        disp, mask = get_rejection_mask(img)
        cv2.imwrite("test.jpg", disp)


if __name__ == "__main__":
    Main()