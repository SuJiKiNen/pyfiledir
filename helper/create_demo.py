#!/usr/bin/env python
import os

import pyautogui

pyautogui.PAUSE = 1

DEMO_PATH = os.path.join(
    os.getcwd(),
    "demo.svg",
)
dirs = [
    '/tmp/demo',
    '/tmp/demo/视频剪辑',
    '/tmp/demo/视频素材',
    '/tmp/demo/音乐',
    '/tmp/demo/下载',
    '/tmp/demo/文档',
]

for d in dirs:
    os.makedirs(d, exist_ok=True)

pyautogui.typewrite('cd /tmp/demo')
pyautogui.press('enter')

pyautogui.typewrite("termtosvg {} -c '/bin/bash' -g 64x20".format(DEMO_PATH))
pyautogui.press('enter')
pyautogui.typewrite('ls', interval=0.25)
pyautogui.press('enter')
pyautogui.typewrite('cd yy', interval=0.25)
pyautogui.press('tab')
pyautogui.press('enter')

pyautogui.typewrite('cd -')
pyautogui.press('enter')

pyautogui.typewrite('cd sp')
pyautogui.press('tab')
pyautogui.typewrite('2')
pyautogui.press('tab')
pyautogui.press('enter')
pyautogui.hotkey('ctrl', 'd')
pyautogui.typewrite("cd -")
pyautogui.press('enter')
