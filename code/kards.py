import pyautogui
import cv2
import numpy as np
import time
import os
import random
pyautogui.MINIMUM_DURATION = 0.01
pyautogui.MINIMUM_SLEEP = 0.005

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
def drag_mouse(start_x, start_y, drag_x, drag_y, duration=0.5):
    pyautogui.moveTo(start_x, start_y)
    pyautogui.mouseDown()
    pyautogui.move(drag_x, drag_y, duration=duration)  # 按住左键并拖动，duration 参数控制滑动速度
    time.sleep(0.3)
    pyautogui.mouseUp()

def move_to_setting(setting_image_path):
    button_pos = detect_button(setting_image_path,threshold=0.7)
    if button_pos:
        center_x, center_y = button_pos
        # 移动鼠标至 setting 图标中央
        pyautogui.moveTo(center_x, center_y)
    else:
        print("Setting button not found.")

# 检测并处理 Setting 图标操作(已弃用)
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
    
    

def find_all_template_positions(template_path, threshold, min_dist):
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
        print(f"drag unit({ux},{uy})to target({target_x},{target_y})")
        if detect_button(continue_image_path):
            break
        drag_mouse(ux, uy, target_x-ux, target_y-uy, duration=0.2)
        time.sleep(0.2)

#对比颜色相似度
def color_similar(c1, c2, threshold=50):
    # c1, c2: (B, G, R)
    return np.linalg.norm(np.array(c1) - np.array(c2)) < threshold

#拖拽可用手牌
def drag_available_kards_from_hand():
    template_color = cv2.imread(k_image_path, cv2.IMREAD_COLOR)
    h, w = template_color.shape[:2]
    main_color = np.array([56, 148, 208])  # K黄色 (BGR)
    try_times = 0
    x_offset = 0
    while True:
        if try_times == 8:
            break
        filtered = find_all_template_positions(k_image_path, threshold=0.85, min_dist=40)
        screenshot = take_screenshot()
        found = False
        for (x, y) in filtered:
            left_y = y + h // 2
            if 0 <= left_y < screenshot.shape[0]:
                # 遍历 x-10 到 x-5 之间的像素
                for left_x in range(x - 10, x - 4):
                    if left_x >= 0:
                        left_color = screenshot[left_y, left_x]
                        if color_similar(left_color, main_color):
                            print(f"dragging available kard at ({x},{y})")
                            drag_mouse(x, y, x_offset-30, -120, duration=0.2)
                            if (try_times%2) == 0:
                                x_offset += 150
                            else:
                                x_offset -= 180
                            time.sleep(1)
                            found = True
                            break
                if found:
                    try_times += 1
                    break  # 拖拽一张后立刻重新识别

        if not found:
            print("all kards not available")
            break


#尝试拖拽支援阵线的坦克和步兵到前线
def drag_supportline_unit_to_frontline():
    move_to_setting(setting_image_path)
    time.sleep(2)

    setting_loc = detect_button(setting_image_path, threshold=0.8)
    if setting_loc is None:
        print("Setting do not find")
        return
    
    setting_x, setting_y = setting_loc
    target_x = setting_x - 550
    target_y = setting_y + 300
    for i in range(2):
        flitered_infantry = find_all_template_positions(infantry_image_path, threshold=0.8, min_dist=40)
        if not flitered_infantry:
            print("do not find infantry in support line")
        else:
            infantry_sorted = sorted(
                [p for p in flitered_infantry if setting_y+500 <= p[1] <= setting_y+580],
                key=lambda p: p[0]
            )
            traversal_drag(infantry_sorted, target_x, target_y)
            time.sleep(0.5)

    move_to_setting(setting_image_path)
    time.sleep(1)
    flitered_tank = find_all_template_positions(tank_image_path, threshold=0.8, min_dist=40)
    if not flitered_tank:
        print("do not find tank in support line")
    else:
        tank_sorted = sorted(
            [p for p in flitered_tank if setting_y+500 <= p[1] <= setting_y+580],
            key=lambda p: p[0]
        )
        traversal_drag(tank_sorted, target_x, target_y)

    
# 拖拽所有unit到敌方HQ
def drag_all_units_to_enemy_HQ():
    move_to_setting(setting_image_path)
    time.sleep(1)
    units = find_all_template_positions(unit_image_path, threshold=0.92, min_dist=30)
    veteran_units = find_all_template_positions(veteran_image_path, threshold=0.9, min_dist=50)
    gold_units = find_all_template_positions(gold_unit_image_path, threshold=0.8, min_dist=50)
    HQs = find_all_template_positions(HQ_image_path, threshold=0.7, min_dist=200)
    be_guards = find_all_template_positions(be_guard_image_path, threshold=0.9, min_dist=50)
    guards = find_all_template_positions(guard_image_path, threshold=0.9, min_dist=50)
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
    gold_units = [(ux + 25, uy - 50) for ux, uy in gold_units]

    #剔除敌方单位
    cutoff_Y = enemy_HQ[1] + 100
    units = [(ux, uy) for ux, uy in units if uy >= cutoff_Y]
    veteran_units = [(ux, uy) for ux, uy in veteran_units if uy >= cutoff_Y]
    gold_units = [(ux, uy) for ux, uy in gold_units if uy >= cutoff_Y]

    #检测敌方总部是否被守护
    print(be_guards)
    print(guards)
    print(enemy_HQ)
    if any((enemy_HQ[0] < ux < enemy_HQ[0]+130) and (uy < enemy_HQ[1]) for ux, uy in be_guards):
        print("enemy HQ is been guard")
        guards_pos = [(ux, uy) for ux, uy in guards if (uy < enemy_HQ[1]) and (enemy_HQ[0] - 180 < ux < enemy_HQ[0] + 300)]
        if guards_pos:
            guard = min(guards_pos, key=lambda p: p[0])
            target_x, target_y = guard[0] - 55, guard[1] + 50  # 转成只包含一个元素的列表(x min)
            traversal_drag(units, target_x, target_y)
            traversal_drag(veteran_units, target_x, target_y)
            traversal_drag(gold_units, target_x, target_y) 
    else:
        traversal_drag(units, target_x, target_y)
        traversal_drag(veteran_units, target_x, target_y)
        traversal_drag(gold_units, target_x, target_y)



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

#记录胜负功能       
def init_record(path="record.txt"):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("0 win\n")
            f.write("0 lose\n")
            f.write("0 unknow\n")

def read_record(path="record.txt"):
    record = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            num, label = line.strip().split()
            record[label] = int(num)
    return record

def update_record(label, delta, path="record.txt"):
    record = read_record(path)
    if label in record:
        record[label] += delta
    with open(path, "w", encoding="utf-8") as f:
        for key, value in record.items():
            f.write(f"{value} {key}\n")

def do_continue():
    for i in range(5):
        time.sleep(2)
        if not detect_and_click_button(continue_image_path):
            detect_and_click_button(receive_image_path)
        pyautogui.move(-100, 0)

#路径定义
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)                  # 上一级目录
icon_dir = os.path.join(parent_dir, "icon")
CN_dir = os.path.join(parent_dir, "CN")
continue_image_path = os.path.join(current_dir, 'continue.png')  # Continue 按钮路径
start_image_path = os.path.join(current_dir, 'start.png')  
confirm_image_path = os.path.join(current_dir, 'confirm.png')  
endturn_image_path = os.path.join(current_dir, 'endturn.png')
endturn2_image_path = os.path.join(current_dir, 'endturn2.png') 
setting_image_path = os.path.join(current_dir, 'setting.png')  # Setting 图标路径
surrender_image_path = os.path.join(current_dir, 'surrender.png')
No_image_path = os.path.join(current_dir, 'No.png')
chat_image_path = os.path.join(current_dir, 'chat.png')
HQ_image_path = os.path.join(current_dir, 'HQ.png')
unit_image_path = os.path.join(current_dir, 'unit.png')
unit_image_path = os.path.join(current_dir, 'unit.png')
HQ_image_path = os.path.join(current_dir, 'HQ.png')
veteran_image_path = os.path.join(current_dir, 'veteran.png')
gold_unit_image_path = os.path.join(icon_dir, 'gold_unit.png')
k_image_path = os.path.join(current_dir, 'k.png')
infantry_image_path = os.path.join(current_dir, 'infantry.png')
tank_image_path = os.path.join(current_dir, 'tank.png')
defeated_image_path = os.path.join(current_dir, 'defeated.png')
victory_image_path = os.path.join(current_dir, 'victory.png')
guard_image_path = os.path.join(icon_dir, 'guard.png')
be_guard_image_path = os.path.join(icon_dir, 'be_guard.png')
receive_image_path = os.path.join(CN_dir, 'receive.png')
# 主程序
def main():
    pyautogui.click()
    time.sleep(2)
    pyautogui.click()
    pyautogui.click()
    time.sleep(2)
    pyautogui.click()
    init_record(path="record.txt")
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
        countdown_time = 60 * 9 # 9分钟
    else:
        print("will not surrender")
        countdown_time = 900 #15分钟
    start_time = time.time()

    while time.time() - start_time < countdown_time:
        print("Checking for Endturn or Continue button...")
        
        endturn_pos = detect_button(endturn_image_path, threshold=0.7)
        if not endturn_pos: # 如果没找到第一个按钮
            endturn_pos = detect_button(endturn2_image_path, threshold=0.7)
        continue_pos = detect_button(continue_image_path)

        if continue_pos:
            while True:
                if detect_button(victory_image_path):
                    update_record("win", 1)
                elif detect_button(defeated_image_path):
                    update_record("lose", 1)
                else:
                    update_record("unknow", 1) 
                if detect_and_click_button(continue_image_path):
                    do_continue()
                    break

            print("Restarting main process...")
            return  # 结束当前循环并重新开始程序
        
        if endturn_pos:
            print("Endturn button detected, waiting 5 seconds...")
            time.sleep(3)  # 探测到endturn按钮后等待5秒
            do_chat(chat_image_path)
            
            # 检测setting按钮并执行操作
            #handle_setting_and_drag(setting_image_path)
            # 拖拽可用手牌
            drag_available_kards_from_hand()
            # 拖拽支援阵线坦克和步兵
            drag_supportline_unit_to_frontline()
            # 将所有单位拖向敌方总部
            drag_all_units_to_enemy_HQ()

            # 等待5-20秒后点击endturn按钮
            if countdown_time == 900:
                time_random = 1
            else:
                time_random = random.randint(1,2)# 如有需要可以设置为等待5-20秒
            print("Waiting %d seconds before clicking Endturn..." % time_random)
            time.sleep(time_random)  

            # 点击endturn按钮
            detect_and_click_button(endturn_image_path)
            print("Endturn button clicked after Setting operations.")
            pyautogui.move(-580, 0)

        time.sleep(1)  # 每秒检测一次endturn按钮
    detect_and_click_button(setting_image_path)
    time.sleep(2)  # 等待2秒
    detect_and_click_button(surrender_image_path)
    update_record("lose", 1)
    pyautogui.move(-580, 0)
    time.sleep(6)  # 等待10秒
    while True:

        if detect_and_click_button(continue_image_path):
            do_continue()
            break
if __name__ == '__main__':
    while True:
        main()

