import cv2
import camera
import numpy as np
import segmentation.segmentation

class SegData:
    lastSegment: np.ndarray
    counter: int

    def __init__(self, lastSegment, counter):
        self.lastSegment = lastSegment
        self.counter = counter

LPF_TICKS = 4
class LPF:
    def __init__(self):
        self.stored_segs = {}
        self.update_q = []

    def update(self, segs):
        for seg_id, seg in segs.items():
            if seg_id not in self.stored_segs:
                # It's new, lets put it into the stored segments
                print(f"Registered id {seg_id} in the lpf")
                self.stored_segs[seg_id] = SegData(seg, LPF_TICKS)
            else:
                # Otherwise, we've seen this before.
                # Check for similarity. If all tests pass, decrement the ticker.
                # Otherwise, reset the ticker
                # At the end, we store this segment
                oldSegment = self.stored_segs[seg_id].lastSegment
                self.stored_segs[seg_id].lastSegment = seg

                ## Size Comparison ##
                dim_new = seg.shape
                dim_old = oldSegment.shape

                areaNew = dim_new[0] * dim_new[1]
                areaOld = dim_old[0] * dim_old[1]

                size_change = 100 * abs((areaNew - areaOld) / areaOld)

                if size_change > 20:
                    # Too much change
                    print(f"Seg id {seg_id} shape changed too much e={size_change:.3f}")
                    self.stored_segs[seg_id].counter = LPF_TICKS
                    next

                ## Abs Diff ##
                oldSegment = cv2.resize(oldSegment, seg.shape[:2])
                oldSegment = oldSegment.reshape(seg.shape)
                error, diff = mse(seg, oldSegment)

                if error > 50:
                    # Too much abs diff
                    print(f"Seg id {seg_id} content changed too much e={error:.3}")
                    self.stored_segs[seg_id].counter = LPF_TICKS
                    next

                # We've reached the end. We are a match. Decrement the counter
                if self.stored_segs[seg_id].counter > 0:
                    self.stored_segs[seg_id].counter = self.stored_segs[seg_id].counter - 1

                    if self.stored_segs[seg_id].counter == 0:
                        # We've reached 0, let's push it to the update queue to be handled
                        self.update_q.append(seg_id)

    def get_updates(self):
        segs = []

        for seg_id in self.update_q:
            segs.append(
                (seg_id, self.stored_segs[seg_id].lastSegment)
            )

        self.update_q = []
        return segs

def Main():

    print('main')


def mse(img1, img2):
   img1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
   img2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)

   h, w = img1.shape
   diff = cv2.subtract(img1, img2)
   err = np.sum(diff**2)
   mse = err/(float(h*w))
   return mse, diff

if __name__ == "__main__":
    Main()