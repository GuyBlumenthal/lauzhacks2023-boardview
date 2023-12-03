import matplotlib.pyplot as plt
import numpy as np
import cv2

from pathlib import Path

from dataclasses import dataclass
import typing

# (x, y)
Point = typing.Tuple[int, int]

# (Top Left, Bottom Right)
Rectangle = typing.Tuple[Point, Point]

size = (2048, 2048)
blur = (5, ) * 2
HALO_SIZE = size[0] * 0.05 # px
BORDER_SIZE = int(size[0] * 0.02)
MIN_SEG_AREA = (size[0] * size[1]) * 0.005
MERGE_PASSES = 3

VIZ = True
OUT_PREFIX = ""

class SegmentationContext:
    def __init__(self):
        self.alives = []

    def feed_img(self, img) -> typing.Dict[int, Rectangle]:
        rects = img2rects(img)

        self.alives = tag_segments(self.alives, rects)

        segments = rects2segs(img, self.alives.values())

        alive_segments = {k:v for k,v in zip(self.alives.keys(), segments)}

        for seg_id, segment in alive_segments.items():
            cv2.imwrite(img_out_dir(f"segments/segment_{seg_id}.jpg"), segment)

        return alive_segments

    def get_segmented_img(self, img):
        mask = np.zeros(size, np.uint8)
        img = cv2.resize(img, size)

        rects = []

        for rect in self.alives.values():
            l = min(max(rect[0][1] - BORDER_SIZE, 0), size[0])
            r = min(max(rect[1][1] + BORDER_SIZE, 0), size[0])
            t = min(max(rect[0][0] - BORDER_SIZE, 0), size[0])
            b = min(max(rect[1][0] + BORDER_SIZE, 0), size[0])

            rects.append([
                [t,l],
                [b,r]
            ])

        for rect in rects:
            mask = cv2.rectangle(mask, rect[0], rect[1], 255, -1)

        dst = cv2.bitwise_and(img, img, mask=mask)
        return cv2.cvtColor(dst, cv2.COLOR_BGR2RGB)


id_count = 0
def next_id():
    global id_count
    id_count = id_count + 1
    return id_count

def img_dir(path):
    path = f"segmentation/img/{path}"
    Path(path).parent.mkdir( parents=True, exist_ok=True )
    return path

def img_out_dir(path):
    return img_dir(f"out/{OUT_PREFIX}{path}")

def ex_img(index):
    return f"examples/manual_demo/img{index}.jpg"

def dist(p1, p2):
    return np.sqrt(pow(p2[0] - p1[0], 2) + pow(p2[1] - p1[1], 2))

def rect_area(rect):
    return (rect[1][0] - rect[0][0]) * (rect[1][1] - rect[0][1])

def get_rect_dist(rect1, rect2):
    (t1, l1), (b1, r1) = rect1
    (t2, l2), (b2, r2) = rect2

    left = r2 < l1
    right = r1 < l2
    bottom = b2 < t1
    top = b1 < t2

    if top and left:
        return dist((l1, b1), (r2, t2))
    elif left and bottom:
        return dist((l1, t1), (r2, b2))
    elif bottom and right:
        return dist((r1, t1), (l2, b2))
    elif right and top:
        return dist((r1, b1), (l2, t2))
    elif left:
        return l1 - r2
    elif right:
        return l2 - r1
    elif bottom:
        return t1 - b2
    elif top:
        return t2 - b1
    else:             # rectangles intersect
        return 0.


def merge_collocated_rects(rects: list[np.ndarray[list[int, int]]]):
    new_rects = []

    for rect in rects:
        merged = False

        # Check for overlap with existing rects
        for compare_i in range(len(new_rects)):
            new_rects[compare_i]
            compare_dist = get_rect_dist(rect, new_rects[compare_i])

            if compare_dist < HALO_SIZE:
                # Found overlap. Merge rectangles
                (t1, l1), (b1, r1) = rect
                (t2, l2), (b2, r2) = new_rects[compare_i]

                new_rects[compare_i] = np.array([
                    [min(t1, t2), min(l1, l2)],
                    [max(b1, b2), max(r1, r2)]
                ])

                merged = True
                break
            # What is the distance between them. Is it less than threshold
            pass

        if not merged:
            new_rects.append(rect)

    return new_rects

## Turn a list of rectangles into an image mask
## A rectangle is [[top, left], [bottom, right]]
def rect_mask(rects, index):
    mask = np.zeros(size, np.uint8)
    outline_mask = np.zeros(size, np.uint8)
    radi = []

    for rect in rects:
        mask = cv2.rectangle(mask, rect[0], rect[1], 255, -1)

        radi.append(np.array([
            [int(rect[0][0] - HALO_SIZE), int(rect[0][1] - HALO_SIZE)],
            [int(rect[1][0] + HALO_SIZE), int(rect[1][1] + HALO_SIZE)],
        ]))


    if VIZ:
        masked = np.zeros(size, np.uint8)
        for rect, radius in zip(rects, radi):
            masked = cv2.rectangle(masked, rect[0], rect[1], 255, -1)
            masked = cv2.rectangle(masked, radius[0], radius[1], 255, 1)

        cv2.imwrite(img_out_dir(f"masked_{index}.jpg"), masked)

    return mask

def normalize_img(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, size)

    return img


def img2cnt(img):
    blurred = cv2.blur(img, blur)

    gray = cv2.cvtColor(blurred, cv2.COLOR_RGB2GRAY)
    # _, thresh = cv2.threshold(gray, np.mean(gray), 255, cv2.THRESH_BINARY_INV)
    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

    edges = cv2.Canny(thresh, 0, 255)
    edges = cv2.dilate(edges, None)

    if VIZ:
        cv2.imwrite(img_out_dir("blurred.jpg"), blurred)
        cv2.imwrite(img_out_dir("gray.jpg"), gray)
        cv2.imwrite(img_out_dir("thresh.jpg"), thresh)
        cv2.imwrite(img_out_dir("edges.jpg"), edges)

    # Lead with largest contour area to increase collocation effectivity
    return sorted(cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2], key=cv2.contourArea)[::-1]

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

def rects2segs(img, rects):
    img = normalize_img(img)

    # Create a cropped segment image for each rectangle
    segments = []

    for rect in rects:
        t = min(max(rect[0][1] - BORDER_SIZE, 0), size[0])
        b = min(max(rect[1][1] + BORDER_SIZE, 0), size[0])
        l = min(max(rect[0][0] - BORDER_SIZE, 0), size[0])
        r = min(max(rect[1][0] + BORDER_SIZE, 0), size[0])

        segments.append(img[
            t:b,
            l:r
        ])

    return segments

def img2rects(img):
    img = normalize_img(img)

    # Edge and contour mapping
    cnts = img2cnt(img)

    # Define contours as large rectangle sections
    rects = cnts2rects(cnts)

    # Merge collocated rectangles in XX passes
    mask = rect_mask(rects, 0)

    for i in range(MERGE_PASSES):
        rects = merge_collocated_rects(rects)
        mask = rect_mask(rects, i + 1)

    dst = cv2.bitwise_and(img, img, mask=mask)
    segmented = cv2.cvtColor(dst, cv2.COLOR_BGR2RGB)

    cv2.imwrite(img_out_dir("img.jpg"), img)

    if VIZ:
        cv2.imwrite(img_out_dir(f"segmented.jpg"), segmented)

    return rects

def combine_rect(rect1, rect2):
    (t1, l1), (b1, r1) = rect1
    (t2, l2), (b2, r2) = rect2

    return np.array([
        [min(t1, t2), min(l1, l2)],
        [max(b1, b2), max(r1, r2)]
    ])


def tag_segments(alive_segments, segments):
    # Remove any segments with areas too small
    segments = [segment for segment in segments if (rect_area(segment) > MIN_SEG_AREA)]

    id2seg = {next_id(): segment for segment in segments}
    mapping = {}

    for segment_id, segment in id2seg.items():
        mapping[segment_id] = []

        for alive_id in alive_segments:
            if get_rect_dist(segment, alive_segments[alive_id]) < HALO_SIZE * 0.1:
                mapping[segment_id].append(alive_id)

    new_alive = {}

    multi = {}
    consume_mapping = {}
    for new_id, overlap_ids in mapping.items():
        n = len(overlap_ids)

        # If a new segment doesn't overlap, its a segment alone
        if n == 0:
            new_alive[new_id] = id2seg[new_id]
        # If a new segment only overlaps 1, it should be consumed by the original
        elif n == 1:
            overlap_id = overlap_ids[0]
            if overlap_id not in consume_mapping:
                consume_mapping[overlap_id] = [new_id]
            else:
                consume_mapping[overlap_id].append(new_id)
        # Otherwise, the new segment is consuming two old segments at a later stage
        elif n > 2:
            multi[new_id] = overlap_ids

    # Let the old regions consume the mappings
    for owner_id, consume_ids in consume_mapping.items():
        new_seg = id2seg[consume_ids[0]]
        for consume_id in consume_ids:
            new_seg = combine_rect(new_seg, id2seg[consume_id])

        new_alive[owner_id] = new_seg

    return new_alive

def WhiteboardEx():
    global OUT_PREFIX
    OUT_PREFIX = "manual/"
    # sample_img = cv2.imread(img_dir("whiteboard.jpg"))
    sample_img = cv2.imread("examples/size_chart.jpg")

    rects = img2rects(sample_img)
    alives = tag_segments([], rects)

    segments = rects2segs(sample_img, alives.values())

    for i, rect, segment in zip(alives.keys(), alives.values(), segments):
        cv2.imwrite(img_out_dir(f"segments/segment_{i}.jpg"), segment)


def RunManualDemo():
    # Load the demo images in order
    EXAMPLE_IMGS = 9
    example_imgs = [cv2.imread(ex_img(i + 1)) for i in range(EXAMPLE_IMGS)]

    segContext = SegmentationContext()

    for i, img in enumerate(example_imgs):
        global OUT_PREFIX
        OUT_PREFIX = f"src{i}/"

        alive_segments = segContext.feed_img(img)

        for seg_id, segment in alive_segments:
            cv2.imwrite(img_out_dir(f"segments/segment_{seg_id}.jpg"), segment)


def Main():
    RunManualDemo()

if __name__ == "__main__":
    Main()
