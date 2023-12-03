import cv2

def Main():
    for i in range(9):
        n = f"examples/size_chart.jpg"
        srcimg = cv2.imread(n)

        # From full size goodnotes image
        rect = [
            [50, 200],
            [1225, 900]
        ]

        # rect = [
        #     [0, 50],
        #     [1175, 700]
        # ]

        cv2.imwrite(
            # n,
            "test.jpg",
            srcimg[rect[0][1]:rect[1][1], rect[0][0]:rect[1][0]]
            # cv2.rectangle(srcimg, rect[0], rect[1], 0, -1)
            # srcimg
        )


if __name__ == "__main__":
    Main()