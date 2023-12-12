import cv2 as cv
import os
from time import sleep
from windowcapture import WindowCapture
from vision import Vision
from pyautogui import getWindowsWithTitle
from hsvfilter import HsvFilter
from random import randint
import win32api
import win32con
import win32gui
import win32process
from traceback import print_exc
import ctypes

if cv.ocl.haveOpenCL(): cv.ocl.setUseOpenCL(True)

WINDOW_NAME = "repos"

hwnd = win32gui.FindWindowEx(None, None, None, WINDOW_NAME)

if hwnd == 0:
    raise Exception("Window not found.")

window_rect = win32gui.GetWindowRect(hwnd)

def c(x, y, repeat=1,delay=0.1):
    global hwnd
    window_x, window_y, _, _ = window_rect
    screen_x, screen_y = win32gui.ClientToScreen(hwnd, (x - window_x, y - window_y))
    for _ in range(repeat):
        print(f"Clicked on x:{x} y:{y}")
        win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, screen_y * 0x10000 + screen_x)
        win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, screen_y * 0x10000 + screen_x)
        sleep(delay)

def focus_window(window):
    win_handle = ctypes.windll.user32.FindWindowW(None, window)
    if win_handle != 0:
        # Bring the window to the foreground
        ctypes.windll.user32.ShowWindow(win_handle, 9)  # SW_RESTORE
        ctypes.windll.user32.SetForegroundWindow(win_handle)
    else:
        print(f"{window} not found.")

def get_c_pos():
    point = ctypes.wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
    return point.x, point.y

wincap = WindowCapture(WINDOW_NAME) 

# filter that allows program to only see black and white
blackwhite = HsvFilter(0, 0, 237, 0, 153, 255, 0, 0, 0, 0)

focus_window(WINDOW_NAME)
sleep(1) # delay because without it CreateCompatibleDC failed is thrown

c(391, 263, 2, 0.5)

while True:
    try:
        # update window position for fixed clicks calculation
        window_rect = win32gui.GetWindowRect(hwnd) 

        # get an updated image of the game
        screenshot = wincap.get_screenshot()

        x, y = win32gui.ClientToScreen(hwnd, (391 - window_rect[0], 263 - window_rect[1]))
        #print(x, y)
        cv.circle(screenshot, (x, y), 5, (0,233,0), -1)
        
        cv.imshow("a",screenshot)
        # press 'q' with the output window focused to exit.
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            break

    # catch errors because if ran from external application the window will immediately close without showing the error
    except Exception as e:
        print_exc()
        input("Press Enter to exit...")