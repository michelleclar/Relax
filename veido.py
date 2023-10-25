import mss
import cv2
import time
import numpy as np
from memory_profiler import profile


# 平均帧数 140 内存 74mb cpu 峰值1.2 平均 0.4
now = lambda: time.time()

@profile(precision=4, stream=open(f'./memory_profiler/memory_profiler.log','w+'))
def main():
    fpss = []
    with mss.mss() as sct:
        # Part of the screen to capture
        # monitor = {"top": 40, "left": 0, "width": 800, "height": 640}
        monitor = (40,0, 800, 640)
        static_time = now()
        while now() - static_time < 60:
            last_time = time.time()

            # Get raw pixels from the screen, save it to a Numpy array
            img = np.array(sct.grab(monitor))
            # Display the picture debug 才显示视频
            cv2.imshow("OpenCV/Numpy normal", img)

            # Display the picture in grayscale
            # cv2.imshow('OpenCV/Numpy grayscale',
            #            cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY))
            fps = 1 / (time.time() - last_time)
            fpss.append(fps)
            print(f"fps: {1 / (time.time() - last_time)}")

            # Press "q" to quit
            if cv2.waitKey(25) & 0xFF == ord("q"):
                cv2.destroyAllWindows()
                print(np.mean(fpss))
                break
    print(np.mean(fpss))


if __name__ == '__main__':
    main()
