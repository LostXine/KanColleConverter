# coding=utf-8

from utils import *
from ScreenManager import *
from collections import deque
import cv2
import win32gui
import time


def kancolle_converter():
    press_right = False
    frame_ui = True
    name = "KanColle Converter"
    console_output(name + " START")
    screen_manager = ScreenManager()
    img = screen_manager.get_screen_frame_roi()

    def on_mouse_callback(event, x, y, flags, para):
        if event == cv2.EVENT_LBUTTONUP:
            print('x:%d, y:%d (%0.3f, %0.3f)' % (x, y, float(x) / img.shape[1], float(y) / img.shape[0]))
        if event == cv2.EVENT_RBUTTONDOWN:
            nonlocal press_right
            press_right = True

    # 注册窗口
    frame_name = name
    cv2.namedWindow(frame_name)
    cv2.setMouseCallback(frame_name, on_mouse_callback)
    # 计算FPS
    fps_list = deque(maxlen=20)
    fps_list.append(0.1)
    while True:
        try:
            fps_start = time.perf_counter()
            img = screen_manager.get_screen_frame_roi()
            if win32gui.FindWindow(0, frame_name):
                fps = len(fps_list) / sum(fps_list)
                if frame_ui:
                    img = put_text_left_top(img, 'FPS:%0.1f' % fps)
                cv2.imshow(frame_name, img)
            else:
                break
            key = cv2.waitKey(20) & 0xff
            if key == 27 or chr(key) in 'Qq':
                break
            if press_right:
                press_right = False
            # if key > 0:
            #    console_output('Press key:%d' % key)
            fps_list.append(time.perf_counter() - fps_start)
        except KeyboardInterrupt:
            break
    console_output(name + " QUIT")
    screen_manager.stop_loop()
    cv2.destroyAllWindows()
    console_output(name + " DONE")


if __name__ == '__main__':
    Config.load_config()
    kancolle_converter()
