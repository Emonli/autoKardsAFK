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

# 拖动鼠标操作
def drag_mouse(start_x, start_y, drag_x, drag_y, duration=0.6):
    pyautogui.moveTo(start_x, start_y)
    pyautogui.mouseDown()
    pyautogui.move(drag_x, drag_y, duration=duration)  # 按住左键并拖动，duration 参数控制滑动速度
    time.sleep(0.3)
    pyautogui.mouseUp()

def move_to_setting(setting_image_path):
    button_pos = detect_button(setting_image_path)
    if button_pos:
        center_x, center_y = button_pos
        # 移动鼠标至 setting 图标中央
        pyautogui.moveTo(center_x, center_y)
    else:
        print("Setting button not found.")

# 检测并处理 Setting 图标操作
def handle_setting_and_drag(setting_image_path):
    x_locate = -680
    for i in range(3):  # 重复3次拖动操作
        button_pos = detect_button(setting_image_path)
        if button_pos:
            center_x, center_y = button_pos
            # 移动鼠标至 setting 图标中央
            pyautogui.moveTo(center_x, center_y)
            time.sleep(0.5)  # 稍作等待

            # 向左移动400像素，向下移动400像素
            pyautogui.move(x_locate, 630)
            x_locate += 100
            time.sleep(0.5)  # 稍作等待

            # 按住左键向上移动100像素后松开
            drag_mouse(pyautogui.position()[0], pyautogui.position()[1], 0, -165)
            time.sleep(0.5)
            drag_mouse(pyautogui.position()[0], pyautogui.position()[1], 0, -165)
            #time.sleep(1)
            #drag_mouse(pyautogui.position()[0], pyautogui.position()[1], 0, -165)
        else:
            print("Setting button not found.")
        time.sleep(1)  # 每次操作后等待1秒
    
    

def find_all_template_positions(template_path, threshold=0.8, min_dist=20):
    screenshot = take_screenshot()
    img_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    points = list(zip(*loc[::-1]))
    filtered = []
    for p in points:
        if all(np.linalg.norm(np.array(p)-np.array(q)) > min_dist for q in filtered):
            filtered.append(p)
    return filtered

#遍历拖拽
def traversal_drag(units, target_x, target_y):
    for ux, uy in units:
        print(f"drag unit({ux},{uy})to Enemy HQ({target_x},{target_y})")
        drag_mouse(ux, uy, target_x-ux, target_y-uy, duration=0.5)
        time.sleep(0.5)

# 拖拽所有unit到敌方HQ
def drag_all_units_to_enemy_HQ(unit_image_path, HQ_image_path,setting_image_path,veteran_image_path):
    move_to_setting(setting_image_path)
    time.sleep(1)
    units = find_all_template_positions(unit_image_path, threshold=0.92, min_dist=30)
    veteran_units = find_all_template_positions(veteran_image_path, threshold=0.9, min_dist=50)
    HQs = find_all_template_positions(HQ_image_path, threshold=0.8, min_dist=200)
    if len(HQs) < 2 or not units:
        print("do not find HQ or unit")
        return
    # HQ按y坐标排序，y大的是我方，y小的是敌方
    HQs_sorted = sorted(HQs, key=lambda p: p[1])
    enemy_HQ = HQs_sorted[0]
    # 攻击总部时，鼠标移动的终点相对于总部坐标偏移(x+50, y-60)
    target_x = enemy_HQ[0] + 50
    target_y = enemy_HQ[1] - 60
    #单位坐标偏移,并依次托向总部
    units = [(ux + 25, uy - 50) for ux, uy in units]
    veteran_units = [(ux - 55, uy + 50) for ux, uy in veteran_units]
    traversal_drag(units, target_x, target_y)
    traversal_drag(veteran_units, target_x, target_y)



def do_chat(chat_image_path): #随机发送消息
    chat_pos = detect_button(chat_image_path)
    if chat_pos:
        print("you are trying to send message")
        chat_random = random.randint(1,2)
        if chat_random == 1:
            print("send!")
            detect_and_click_button(chat_image_path)
            random_y = random.randint(90, 230)
            pyautogui.move(-60, -random_y)
            time.sleep(1)
            pyautogui.click()
        else:
            print("next time")
    else:
        print("not find chat button")
            
        
    
# 主程序
def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))  
    start_image_path = os.path.join(current_dir, 'start.png')  
    confirm_image_path = os.path.join(current_dir, 'confirm.png')  
    endturn_image_path = os.path.join(current_dir, 'endturn.png')
    endturn2_image_path = os.path.join(current_dir, 'endturn2.png') 
    setting_image_path = os.path.join(current_dir, 'setting.png')  # Setting 图标路径
    continue_image_path = os.path.join(current_dir, 'continue.png')  # Continue 按钮路径
    surrender_image_path = os.path.join(current_dir, 'surrender.png')
    No_image_path = os.path.join(current_dir, 'No.png')
    chat_image_path = os.path.join(current_dir, 'chat.png')
    HQ_image_path = os.path.join(current_dir, 'HQ.png')
    unit_image_path = os.path.join(current_dir, 'unit.png')
    unit_image_path = os.path.join(current_dir, 'unit.png')
    HQ_image_path = os.path.join(current_dir, 'HQ.png')
    veteran_image_path = os.path.join(current_dir, 'veteran.png')



    pyautogui.click()
    time.sleep(2)
    pyautogui.click()
    pyautogui.click()
    time.sleep(2)
    pyautogui.click()

    # 检测并点击 Start 按钮
    #detect_and_click_button(No_image_path)
    #detect_and_click_button(start_image_path)
    detect_button(start_image_path)
    print("detect start button")
    while True:
        if detect_and_click_button(start_image_path):
            print("Start button clicked, waiting for 10 seconds...")
            time.sleep(2)
            break
    
    # 检测并点击 Confirm 按钮
    while True:
        if detect_and_click_button(confirm_image_path):
            print("Confirm button clicked, starting 4-minute countdown...")
            break
        time.sleep(1)
        pyautogui.click()

    # 进入4分钟倒计时
    if random.choice([True,False]):
        print("will surrender this time")
        countdown_time = 4 * 62  # 4分钟
    else:
        print("will not surrender")
        countdown_time = 360
    start_time = time.time()

    while time.time() - start_time < countdown_time:
        print("Checking for Endturn or Continue button...")
        
        endturn_pos = detect_button(endturn_image_path)
        if not endturn_pos: # 如果没找到第一个按钮
            endturn_pos = detect_button(endturn2_image_path)
        continue_pos = detect_button(continue_image_path)

        if continue_pos:
            while True:
                if detect_and_click_button(continue_image_path):
                    time.sleep(3)
                    detect_and_click_button(continue_image_path)
                    time.sleep(3)
                    detect_and_click_button(continue_image_path)
                    time.sleep(3)
                    detect_and_click_button(continue_image_path)
                    time.sleep(3)
                    detect_and_click_button(continue_image_path)
                    time.sleep(3)
                    pyautogui.move(-550, 0)
                    break

            print("Restarting main process...")
            return  # 结束当前循环并重新开始程序
        
        if endturn_pos:
            print("Endturn button detected, waiting 5 seconds...")
            time.sleep(3)  # 探测到endturn按钮后等待5秒
            do_chat(chat_image_path)
            
            # 检测setting按钮并执行操作
            handle_setting_and_drag(setting_image_path)
            # 将所有单位拖向敌方总部
            drag_all_units_to_enemy_HQ(unit_image_path, HQ_image_path,setting_image_path,veteran_image_path)

            # 等待5-20秒后点击endturn按钮
            time_random = random.randint(5,20)
            print("Waiting %d seconds before clicking Endturn..." % time_random)
            time.sleep(time_random)  # 等待5-20秒

            # 点击endturn按钮
            detect_and_click_button(endturn_image_path)
            print("Endturn button clicked after Setting operations.")
            pyautogui.move(-580, 0)

        time.sleep(1)  # 每秒检测一次endturn按钮
    detect_and_click_button(setting_image_path)
    time.sleep(2)  # 等待2秒
    detect_and_click_button(surrender_image_path)
    pyautogui.move(-580, 0)
    time.sleep(6)  # 等待10秒
    while True:
        if detect_and_click_button(continue_image_path):
            time.sleep(3)
            detect_and_click_button(continue_image_path)
            time.sleep(3)
            detect_and_click_button(continue_image_path)
            time.sleep(3)
            detect_and_click_button(continue_image_path)
            time.sleep(3)
            detect_and_click_button(continue_image_path)
            time.sleep(3)
            pyautogui.move(-550, 0)
            break
if __name__ == '__main__':
    while True:
        main()

