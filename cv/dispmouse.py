from pyautogui import displayMousePosition, getWindowsWithTitle
getWindowsWithTitle("repos")[0].moveTo(0,0)
displayMousePosition()