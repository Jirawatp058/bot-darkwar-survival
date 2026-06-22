import pyautogui
import time
import cv2
import numpy as np
from pywinauto import Desktop

# 1. ฐานข้อมูลรถของเรา (ใส่ระดับเป้าหมายเริ่มต้นที่อยากให้แต่ละคันไปตี)
# 💡 ต้องกะค่า region (X, Y, กว้าง, สูง) ให้ครอบคลุมกรอบวงกลมฮีโร่แต่ละคันให้พอดีนะครับ
TRUCK_CONFIG = [
    {"name": "รถคันที่ 1", "target_level": 70, "region": (870, 510, 55, 55)},
    {"name": "รถคันที่ 2", "target_level": 35, "region": (870, 570, 55, 55)},
    {"name": "รถคันที่ 3", "target_level": 30, "region": (870, 625, 55, 55)},
    {"name": "รถคันที่ 4", "target_level": 25, "region": (870, 680, 55, 55)}
]



# ==========================================
# ระบบจัดการหน้าต่างเกม (ล็อคขนาด/ตำแหน่ง)
# ==========================================
def setup_game_window(window_title):
    print(f"[*] กำลังค้นหาหน้าต่างโปรแกรม: '{window_title}' ...")
    try:
        # 💡 แก้ไขตรงนี้: เปลี่ยนจาก backend="uia" เป็น backend="win32"
        windows = Desktop(backend="win32").windows(title_re=f".*{window_title}.*", visible_only=True)
        
        if not windows:
            print(f"[-] หาหน้าต่าง '{window_title}' ไม่เจอ โปรดเปิดเกมก่อนครับ")
            return False
            
        app_window = windows[0]
        app_window.set_focus()
        time.sleep(1) 
        
        # ตอนนี้จะสามารถใช้ move_window ได้แล้วครับ
        app_window.move_window(x=0, y=0, width=945, height=1045)
        print("[+] ล็อคขนาดและตำแหน่งหน้าต่างเกมเรียบร้อย!")
        return True
    except Exception as e:
        print(f"[!] เกิดข้อผิดพลาดตอนจัดการหน้าต่าง: {e}")
        return False


# ====================================================
# 2. ฟังก์ชันช่วยเหลือ (ตรวจสอบรถว่าง, หาพื้นที่, หาปุ่ม, คลิก)
# ====================================================
def get_best_available_truck():
    """ เช็ครถจากบนลงล่าง คันไหนว่างก่อน (ลำดับน้อยสุด) เอาคันนั้น! """
    print("\n[-] ตรวจสอบสถานะคิวรถหน้าแผนที่...")
    
    for truck in TRUCK_CONFIG:
        # ด่านที่ 1: เช็คว่าเป็นเครื่องหมาย + ไหม
        try:
            is_locked = pyautogui.locateOnScreen('images/plus_slot_icon.png', region=truck['region'], confidence=0.8)
        except pyautogui.ImageNotFoundException:
            is_locked = None

        if is_locked:
            continue # ข้ามคันนี้ไปเลย

        # ด่านที่ 2: เช็คว่ากำลังทำงาน (เก็บเกี่ยว) ไหม
        try:
            is_gather = pyautogui.locateOnScreen('images/gather_icon.png', region=truck['region'], confidence=0.6)
        except pyautogui.ImageNotFoundException:
            is_gather = None

        if is_gather:
            continue # ข้ามคันนี้ไปเลย

        # ด่านที่ 3: เช็คว่ากำลังทำงาน (โจมตี) ไหม
        try:
            is_attack = pyautogui.locateOnScreen('images/attack_icon.png', region=truck['region'], confidence=0.6)
        except pyautogui.ImageNotFoundException:
            is_attack = None

        if is_attack:
            continue # ข้ามคันนี้ไปเลย

        # ด่านที่ 4: เช็คว่ากำลังทำงาน (แรลลี่) ไหม
        try:
            is_rally = pyautogui.locateOnScreen('images/rally_icon.png', region=truck['region'], confidence=0.6)
        except pyautogui.ImageNotFoundException:
            is_rally = None

        if is_rally:
            continue # ข้ามคันนี้ไปเลย

        # ด่านที่ 5: เช็คว่ากำลังทำงาน (กลับ) ไหม
        try:
            is_back = pyautogui.locateOnScreen('images/back_icon.png', region=truck['region'], confidence=0.6)
        except pyautogui.ImageNotFoundException:
            is_back = None

        if is_back:
            continue # ข้ามคันนี้ไปเลย

        # ด่านที่ 6: เช็คว่ากำลังทำงาน (dead) ไหม
        try:
            is_dead = pyautogui.locateOnScreen('images/dead_icon.png', region=truck['region'], confidence=0.6)
        except pyautogui.ImageNotFoundException:
            is_dead = None

        if is_dead:
            continue # ข้ามคันนี้ไปเลย

        # ด่านที่ 7: เช็คว่ากำลังทำงาน (busy) ไหม
        try:
            is_busy = pyautogui.locateOnScreen('images/busy_icon.png', region=truck['region'], confidence=0.6)
        except pyautogui.ImageNotFoundException:
            is_busy = None

        if is_busy:
            continue # ข้ามคันนี้ไปเลย

        # ด่านที่ 4: ถ้าไม่ติด + และ ไม่ติด busy แสดงว่าว่าง!
        print(f"[+] เลือก {truck['name']}! (เป้าหมายปัจจุบัน: Lv.{truck['target_level']})")
        return truck # รีเทิร์นค่ารถคันบนสุดที่ว่างทันที

    print("[!] รถถูกส่งออกไปหมดแล้ว (หรือยังไม่ปลดล็อค)")
    return None

def click_safe_ground():
    print("[?] กำลังสแกนหาพื้นที่สีเขียวว่างๆ บนจอ...")
    try:
        screen = pyautogui.screenshot()
        screen_np = np.array(screen)
        frame_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest_contour) > 5000:
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    center_x = int(M["m10"] / M["m00"])
                    center_y = int(M["m01"] / M["m00"])
                    pyautogui.click(center_x, center_y)
                    print(f"[+] เจอพื้นที่สีเขียวขนาดใหญ่ คลิกเคลียร์จอที่ (X:{center_x}, Y:{center_y})")
                    time.sleep(1)
                    return True
            else:
                print("[-] เจอสีเขียว แต่พื้นที่เล็กเกินไป เสี่ยงโดนของอื่น")
                return False
        else:
            print("[-] ไม่พบสีเขียวบนหน้าจอเลย")
            return False
    except Exception as e:
        print(f"[!] เกิดข้อผิดพลาด: {e}")
        return False

def find_and_click(image_path, confidence=0.8, wait_time=1.25):
    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        if location:
            pyautogui.moveTo(location)
            pyautogui.click()
            print(f"[+] คลิกสำเร็จ: {image_path}")
            time.sleep(wait_time) 
            return True
        else:
            print(f"[-] หาไม่เจอ: {image_path}")
            return False
    except Exception as e:
        return False

def find(image_path, confidence=0.8, wait_time=0.05):
    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        if location:
            # print(f"[+] หาเจอ: {image_path}")
            time.sleep(wait_time) 
            return True
        else:
            return False
    except Exception as e:
        return False

# ==========================================
# ลอจิกหลัก: ลุยซูโม่
# ==========================================
def hunt_smart_sumo():
    # 1. หารถคันที่ว่างที่สุดตามเงื่อนไข
    active_truck = get_best_available_truck()
    
    if not active_truck:
        return "NO_TRUCK_AVAILABLE"
        
    target_level = active_truck['target_level']
    print(f"=========================================================")
    print(f"[*] เริ่มลูป: ส่ง {active_truck['name']} ไปลุย Lv.{target_level}")
    
    # 2. เปิดหน้าค้นหาซูโม่
    if find_and_click('images/zoom.png'):

        if find_and_click('images/join.png') or find_and_click('images/joininactive.png'):
            find_and_click('images/sumo_icon.png')
        
            # 3. ดันหลอดไปที่เลเวลสูงสุดของเกมก่อน (สมมติว่าคือ 71 ตามในรูป)
            max_game_sumo_level = 85 
            print("[*] ดันหลอดเลเวลไปที่จุดสูงสุด (กด + รัวๆ)")
            is_max_level = find('images/plus_btn.png')
            while is_max_level:
                loc = pyautogui.locateCenterOnScreen('images/plus_btn.png', confidence=0.8)
                if loc: pyautogui.click(loc)
                time.sleep(0.05)
                is_max_level = find('images/plus_btn.png')
                
            # 4. ลบเลเวลลงมาให้ตรงกับรถคันนี้
            clicks_needed = max_game_sumo_level - target_level
            if clicks_needed > 0:
                print(f"[*] กดลดเลเวล [-] ลงมา {clicks_needed} ครั้ง...")
                loc_minus = pyautogui.locateCenterOnScreen('images/minus_btn.png', confidence=0.8)
                if loc_minus:
                    for _ in range(clicks_needed):
                        pyautogui.click(loc_minus)
                        time.sleep(0.1)
                        
            # 5. กดยืนยันค้นหา 
            if find_and_click('images/find.png', wait_time=3.0):
                if find_and_click('images/rally.png'):
                    print("[+] กดรวมพล รออ่านค่าพลัง VS ...")
                    
                    # 6. เช็คพลังก่อนตี (สีขาว = ไหว, สีแดง = ไม่ไหว)
                    can_attack = find('images/good_enermy.png')
                    
                    if can_attack:
                        print(f"[+] ศัตรูพลังน้อยกว่า (สีขาว) ลุยเลย!")
                        
                        if find_and_click('images/start-rally.png'):
                            if find_and_click('images/cancle.png'):
                                click_safe_ground()
                                print("[-] ซูโม่โดนแย่งตี ยกเลิก!")
                                return False
                            else:
                                print(f">>> ส่ง {active_truck['name']} สำเร็จ! <<<")
                                return True
                    else:
                        # 🚨 ไฮไลต์: ถ้ารถคันนี้สู้ไม่ไหว ให้จำและลดเลเวลเป้าหมายของมันลง 1
                        print(f"[-] ศัตรูพลังเยอะกว่า (สีแดง) {active_truck['name']} สู้ไม่ไหว!")
                        
                        # active_truck['target_level'] -= 1
                        # print(f"[*] ปรับเป้าหมายของ {active_truck['name']} ลงเหลือ Lv.{active_truck['target_level']} สำหรับรอบหน้า!")
                        
                        # click_safe_ground() 
                        # time.sleep(1)
                        click_safe_ground()
                        return False
                    
    return False

# ==========================================
# ควบคุมการทำงานของบอท
# ==========================================
if __name__ == "__main__":
    GAME_NAME = "DarkWar"
    setup_game_window(GAME_NAME)
    
    while True:
        result = hunt_smart_sumo()
        
        if result == "NO_TRUCK_AVAILABLE":
            print("\n[!!!] รถทำงานครบทุกคันแล้ว พัก 2 นาที... [!!!]")
            time.sleep(120) 
            
        elif result == True: # ตีสำเร็จ
            print("พัก 5 วินาที แล้วหาคันต่อไปทันที...")
            time.sleep(5)
            
        else: # ตีล้มเหลว หรือหาปุ่มไม่เจอ
            # (ใส่ Error Handling ของคุณตรงนี้ เช่น กด back.png, เติมพลังงาน ฯลฯ)
            if find_and_click('images/back.png'): 
                print("[+] ออกจากหน้าต่าง ลองใหม่ใน 2 วินาที...")
                time.sleep(2)
            elif find_and_click("images/world.png"):
                print("[+] อยู่ในบ้าน (กดออกแผนที่โลก) ลองใหม่ใน 3 วินาที...")
                time.sleep(3)
            elif find_and_click("images/add-energy.png"):
                find_and_click("images/energy20.png")
                print("[+] พลังงานหมด กำลังเติมพลังงาน...")
                time.sleep(3)
            elif not find("images/good_enermy.png"): # ปรับ logic เช็ครูปให้เขียนสั้นลง
                click_safe_ground()
                print("[-] ศัตรูพลังเยอะกว่า (หรือหาปุ่มไม่เจอ) ลองใหม่ใน 3 วินาที...")
                time.sleep(3)
            else:
                click_safe_ground()
                print("[-] ปัญหาอื่นๆ เคลียร์หน้าจอแล้วลองใหม่ใน 3 วินาที...")
                time.sleep(3)