import cv2
import numpy as np

from pathlib import Path

class WhiteBoard:
    def __init__(self, dims):
        self.dims = dims
        self.stored_board = np.ones(dims, np.uint8) * 255

    def update_image(self, img, mask):
        self.stored_board = img
        return
        # img = img.reshape(self.dims)
        # mask = mask.reshape(self.dims)

        self.stored_board = np.array(cv2.resize(self.stored_board, self.dims), np.uint8)
        img = cv2.resize(img, self.dims)
        mask = cv2.resize(img, self.dims)

        A = cv2.bitwise_and(
            self.stored_board,
            self.stored_board,
            mask=mask
        )

        B = cv2.bitwise_and(
            img,
            img,
            mask=(255-mask)
        )

        A = cv2.resize(A, self.dims)
        B = cv2.resize(B, self.dims)

        # print(A.shape)
        # print(B.shape)

        # self.stored_board = cv2.bitwise_or(A, B)
        self.stored_board = A

    def board(self):
        return self.stored_board

def Main():
    Path("whiteboard/out").mkdir( parents=True, exist_ok=True )

    wb = WhiteBoard((100, 100))
    cv2.imwrite("whiteboard/out/test0.jpg", wb.board())

    im1 = cv2.line(255 * np.ones(wb.dims, np.uint8), [20, 20], [40, 70], 127, 2)
    im2 = cv2.line(cv2.line(255 * np.ones(wb.dims, np.uint8), [20, 20], [40, 70], 127, 2), [40, 70], [70, 10], 127, 2)

    empty_mask = np.zeros(wb.dims, np.uint8)
    right_masked = cv2.rectangle(np.zeros(wb.dims, np.uint8), [50, 0], [100, 100], 255, -1)

    wb.update_image(im1, empty_mask)
    cv2.imwrite("whiteboard/out/test1.jpg", wb.board())

    wb.update_image(im2, right_masked)
    cv2.imwrite("whiteboard/out/test2.jpg", wb.board())

    wb.update_image(im2, empty_mask)
    cv2.imwrite("whiteboard/out/test3.jpg", wb.board())



if __name__ == "__main__":
    Main()
