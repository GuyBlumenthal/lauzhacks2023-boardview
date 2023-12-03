import camera
from segmentation.segmentation import SegmentationContext
from object_detector import detector
from whiteboard.whiteboard import WhiteBoard
from lpf import LPF
from texcompile import update_data_base, initialise_tex, get_data, get_tex_line, end_file

import numpy as np

import cv2

DELAY = 100

VIZ_RAW     = 1 << 0
VIZ_OBJDET  = 1 << 1
VIZ_SEGS    = 1 << 2
VIZ_WB      = 1 << 3

ENABLED_VIZ = sum([
    VIZ_RAW,
    VIZ_OBJDET,
    # VIZ_WB,
    VIZ_SEGS,
])

def IsEnabled(viz):
    return viz & ENABLED_VIZ

def DisplayCamera(cam):
    img = camera.WaitForNextFrame(cam)

    if not camera.IsInitalized() or IsEnabled(VIZ_RAW):
        camera.ShowFrame(img)

    return img

def hz10Loop(segContext, img, whiteboard, lpf):
    # Get the object mask of the whiteboard
    disp, mask = detector.get_rejection_mask(img)

    if IsEnabled(VIZ_OBJDET):
        cv2.imshow('objdet', mask)

    if np.mean(mask) > (100 * 90 / 255):
        return

    # Update the stored whiteboard image
    whiteboard.update_image(img, mask)
    img = whiteboard.board()

    if IsEnabled(VIZ_WB):
        cv2.imshow("wb", img)

    # Update the segmentation context
    alive_segments = segContext.feed_img(img)

    if IsEnabled(VIZ_SEGS):
        cv2.imshow('segs', cv2.resize(segContext.get_segmented_img(img), (512, 512)))

    lpf.update(alive_segments)
    updated_segments = lpf.get_updates()

    for update_id, update_img in updated_segments:
    #   pass the image to daniel. These are only stable segments as they become stable
        print(f"ID {update_id} has a new img")
        update_data_base(update_id, update_img)

        


# Pass the segments through the LPF
# updates = (ids, segments) = applyLPF(alive_segments)

# Register any updates from the LPF into the image registry
# for updated_id, updated_segment in updates:
#    imageRegistry.update(updated_id, updated_segment)

def hz2Loop():
    data_base = get_data()
    data = []
    for segment_id in sorted(data_base.keys()):
        data.append(get_tex_line(data_base[segment_id]))

    end_file(data)

def Main():
    cam = camera.OpenCamera(
        # 0,
        2,
        #cv2.CAP_DSHOW,
        DELAY
    )
    camera.InitializeStream(cam)
    initialise_tex()
    # Calibrate the camera to the whiteboard
    while not camera.IsInitalized():
        DisplayCamera(cam)

    segContext = SegmentationContext()
    whiteboard = WhiteBoard((1024, 1024))
    lpf = LPF()

    counter = 0
    while 1:
        # Block for the next image, should be 100ms (DELAY)
        img = DisplayCamera(cam)

        hz10Loop(segContext, img, whiteboard, lpf)

        counter = counter + 1
        if counter == 5:
            hz2Loop()
            counter = 0


if __name__ == "__main__":
    Main()