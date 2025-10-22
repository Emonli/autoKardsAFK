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

#找到所有k字符
def find_all_k_positions(k_template_path, threshold=0.8, min_dist=20):
    screenshot = take_screenshot()
    img_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(k_template_path, cv2.IMREAD_GRAYSCALE)
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    points = list(zip(*loc[::-1]))
    filtered = []
    for p in points:
        if all(np.linalg.norm(np.array(p)-np.array(q)) > min_dist for q in filtered):
            filtered.append(p)
    return filtered

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__)) 
    continue_image_path = os.path.join(current_dir, 'continue.png')
    k_image_path = os.path.join(current_dir, 'k.png')



if __name__ == '__main__':
    main()
