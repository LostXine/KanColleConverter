# coding=utf-8

import win32gui
import win32con
import win32com.client
import win32ui
import numpy
import cv2
import traceback
import ConfigManager as Config
import mss


class BitbltCapture:
    def __init__(self):
        self.window_handle = 0
        self.window_name = Config.main_config['window']['name']
        self.frame_scale = Config.main_config['window']['frame_scale']
        self.frame_roi = Config.main_config['window']['flash_position']
        # windows api截屏相关
        self.handle_dc = None
        self.mfc_dc = None
        self.save_dc = None
        self.save_bitmap = None

    def update_dcs(self, old_handle, new_handle):
        self.clean_dcs(old_handle)
        self.window_handle = new_handle
        self.init_dcs()

    def update(self, oh, nh):
        self.update_dcs(oh, nh)

    def clean(self):
        self.clean_dcs(self.window_handle)

    def clean_dcs(self, old_handle):
        if self.mfc_dc is not None:
            try:
                self.mfc_dc.DeleteDC()
            except:
                traceback.print_exc()
            self.mfc_dc = None
        if self.save_dc is not None:
            try:
                self.save_dc.DeleteDC()
            except:
                traceback.print_exc()
            self.save_dc = None
        if self.handle_dc is not None:
            try:
                win32gui.ReleaseDC(old_handle, self.handle_dc)
            except:
                traceback.print_exc()
            self.handle_dc = None
        if self.save_bitmap is not None:
            try:
                win32gui.DeleteObject(self.save_bitmap.GetHandle())
            except:
                traceback.print_exc()
            self.save_bitmap = None

    def init_dcs(self):
        self.handle_dc = win32gui.GetWindowDC(self.window_handle)
        self.mfc_dc = win32ui.CreateDCFromHandle(self.handle_dc)
        self.save_dc = self.mfc_dc.CreateCompatibleDC()
        self.save_bitmap = win32ui.CreateBitmap()
        # MoniterDev = win32api.EnumDisplayMonitors(None, None)
        w = self.frame_roi[2] - self.frame_roi[0]
        h = self.frame_roi[3] - self.frame_roi[1]
        self.save_bitmap.CreateCompatibleBitmap(self.mfc_dc, w, h)
        self.save_dc.SelectObject(self.save_bitmap)

    def get_dc_frame(self):
        w = self.frame_roi[2] - self.frame_roi[0]
        h = self.frame_roi[3] - self.frame_roi[1]
        # bitblt: dst左上角(0,0) 右下角(w,h) src句柄 src左上角
        try:
            self.save_dc.BitBlt((0, 0), (w, h), self.mfc_dc, (self.frame_roi[0], self.frame_roi[1]), win32con.SRCCOPY)
            img_array = self.save_bitmap.GetBitmapBits(True)
            img = numpy.fromstring(img_array, dtype=numpy.uint8)
            img.shape = (h, w, 4)
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        except:
            traceback.print_exc()
            return None

    def get_screen_frame(self):
        return self.get_dc_frame()


class MssCapture:
    def __init__(self):
        self.frame_scale = Config.main_config['window']['frame_scale']
        self.frame_roi = Config.main_config['window']['flash_position']
        self.window_handle = 0
        self.window_rect = ()
        self.window_dict = {'width': (self.frame_roi[2] - self.frame_roi[0]),
                            'height': (self.frame_roi[3] - self.frame_roi[1])}
        self.m = mss.mss()
        self.m.__enter__()

    def get_screen_frame(self):
        self.update(None, self.window_handle)
        img = numpy.array(self.m.grab(self.window_dict))
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    def update(self, old_handle, new_handle):
        self.window_handle = new_handle
        self.window_rect = win32gui.GetWindowRect(self.window_handle)
        self.window_dict['left'] = self.window_rect[0] + self.frame_roi[0]
        self.window_dict['top'] = self.window_rect[1] + self.frame_roi[1]

    def clean(self):
        self.m.__exit__()


class ScreenManager:
    def __init__(self):
        # 窗口相关
        self.window_name = Config.main_config['window']['name']
        self.frame_scale = Config.main_config['window']['frame_scale']
        self.frame_roi = Config.main_config['window']['flash_position']
        self.frame_size = (round((self.frame_roi[3] - self.frame_roi[1]) * self.frame_scale),
                           round((self.frame_roi[2] - self.frame_roi[0]) * self.frame_scale), 3)
        self.window_handle = 0
        self.window_rect = ()
        # 按键
        self.shell = win32com.client.Dispatch("WScript.Shell")
        # 选择截屏器
        self.window_capture = BitbltCapture() if Config.main_config['flag']['flag_use_bitblt'] else MssCapture()

    def stop_loop(self):
        self.window_capture.clean()

    def get_screen_frame_roi(self):
        img = None
        try:
            while img is None:
                self.refresh_handle()
                img = self.window_capture.get_screen_frame()
            img = cv2.resize(img, (self.frame_size[1], self.frame_size[0]))
            return img
        except:
            return numpy.zeros(self.frame_size, numpy.uint8)

    def refresh_handle(self):
        old_handle = self.window_handle
        self.window_handle = win32gui.FindWindow(0, self.window_name)
        if self.window_handle:
            # print window_name + ' handle:' + unicode(window_handle)
            # force to show window
            # win32gui.ShowWindow(window_handle, win32con.SW_MAXIMIZE)
            # if self.frame_inv > 100:
            #    # force to focus
            #    win32gui.SetForegroundWindow(self.window_handle)
            #    self.frame_inv = 0
            # self.frame_inv += 1
            w_p = Config.main_config['window']['whole_position']
            # 正常化窗口
            # win32gui.ShowWindow(self.window_handle, 1)
            self.window_rect = win32gui.GetWindowRect(self.window_handle)
            # 固定宽高
            if Config.main_config['flag']['flag_fix_window']:
                win32gui.MoveWindow(self.window_handle, w_p[0], w_p[1], w_p[2], w_p[3], True)
            else:
                win32gui.MoveWindow(self.window_handle, self.window_rect[0], self.window_rect[1], w_p[2], w_p[3], True)
        else:
            self.window_handle = win32gui.GetDesktopWindow()
            self.window_rect = win32gui.GetWindowRect(self.window_handle)
        self.window_capture.update(old_handle, self.window_handle)
