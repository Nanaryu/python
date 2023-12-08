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
from traceback import print_exc

if cv.ocl.haveOpenCL():
    cv.ocl.setUseOpenCL(True)
    print("OpenCL is enabled")
else:
    print("OpenCL is not available")

hwnd = win32gui.FindWindowEx(None, None, None, 'NoxPlayer')

def c(x, y, delay=0.1):
    global hwnd
    screen_x, screen_y = win32gui.ClientToScreen(hwnd, (x, y))
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, screen_y * 0x10000 + screen_x)
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, screen_y * 0x10000 + screen_x)
    sleep(delay)

# Change the working directory to the folder this script is in.
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# before capturing the window get it focused or else it will throw CreateCompatibleDC failed
# Window Name, i recommend NoxPlayer because the program was made and tested on it
emulator = "Steam"
wincap = WindowCapture(emulator)

# filter that allows program to only see black and white
blackwhite = HsvFilter(0, 0, 237, 0, 153, 255, 0, 0, 0, 0)

while True:
    try:
        # get an updated image of the game
        screenshot = wincap.get_screenshot()
        cv.imshow("a",screenshot)
        # press 'q' with the output window focused to exit.
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            break

    # catch errors because if ran from external application the window will immediately close without showing the error
    except Exception as e:
        print_exc()
        input("Press Enter to continue...")