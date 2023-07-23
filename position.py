import pyautogui
import time

while True:
    print(pyautogui.position())
    time.sleep(0.5)  # 每0.5秒打印一次鼠标的位置
