import pyautogui
import cv2
import numpy as np
import time
import os
import random


    # 截图函数，捕捉指定区域的图像
def take_screenshot(region=None):
    screenshot = pyautogui.screenshot(region=region)
    screenshot = np.array(screenshot)
    return cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)


# 检测按钮并返回是否找到按钮（不点击）
def detect_button(image_path, threshold=0.8):
    screenshot = take_screenshot()
    template = cv2.imread(image_path, cv2.IMREAD_COLOR)
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        button_x, button_y = max_loc
        button_w, button_h = template.shape[1], template.shape[0]
        center_x, center_y = button_x + button_w // 2, button_y + button_h // 2
        print(f"\033[32mButton detected at ({center_x}, {center_y})\033[0m")
        return (center_x, center_y)
    return None

# 检测按钮并移动鼠标点击
def detect_and_click_button(image_path, threshold=0.8):
    button_pos = detect_button(image_path, threshold)
    if button_pos:
        pyautogui.moveTo(button_pos[0], button_pos[1])
        time.sleep(0.5)  # 稍作等待
        pyautogui.click()
        return True
    return False

def move_to_setting(setting_image_path):
    button_pos = detect_button(setting_image_path)
    if button_pos:
        center_x, center_y = button_pos
        # 移动鼠标至 setting 图标中央
        pyautogui.moveTo(center_x, center_y)
    else:
        print("Setting button not found.")

def drag_mouse(start_x, start_y, drag_x, drag_y, duration=0.5):
    pyautogui.moveTo(start_x, start_y)
    pyautogui.mouseDown()
    pyautogui.move(drag_x, drag_y, duration=duration)  # 按住左键并拖动，duration 参数控制滑动速度
    time.sleep(0.3)
    pyautogui.mouseUp()

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__)) 
    continue_image_path = os.path.join(current_dir, 'continue.png')
    k_image_path = os.path.join(current_dir, 'k.png')
    setting_image_path = os.path.join(current_dir, 'setting.png')

    move_to_setting(setting_image_path)
    pyautogui.move(0, 520)




if __name__ == '__main__':
    main()
