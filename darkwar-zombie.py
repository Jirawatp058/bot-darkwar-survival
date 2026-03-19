import pyautogui
import time
import cv2
import numpy as np
from pywinauto import Desktop

# ==========================================
# 1. ระบบจัดการหน้าต่างเกม (ล็อคขนาด/ตำแหน่ง)
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
        app_window.move_window(x=0, y=0, width=850, height=950)
        print("[+] ล็อคขนาดและตำแหน่งหน้าต่างเกมเรียบร้อย!")
        return True
    except Exception as e:
        print(f"[!] เกิดข้อผิดพลาดตอนจัดการหน้าต่าง: {e}")
        return False

# ==========================================
# 2. ฟังก์ชันช่วยเหลือ (หาพื้นที่, หาปุ่ม, คลิก)
# ==========================================
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

def find_and_click(image_path, confidence=0.8, wait_time=2):
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

def find(image_path, confidence=0.8, wait_time=1.25):
    try:
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        if location:
            print(f"[+] หาเจอ: {image_path}")
            time.sleep(wait_time) 
            return True
        else:
            return False
    except Exception as e:
        return False

# ==========================================
# 3. ลอจิกการทำงานหลัก (ตีซอมบี้)
# ==========================================
def attack_zombie_routine():
    print("======================== เริ่มลูปค้นหาและโจมตีซอมบี้ =================================")
    
    # 1. กดปุ่มค้นหา/เรดาร์
    if find_and_click('images/zoom.png'):
        
        # 2. เลือกแท็บซอมบี้
        if find_and_click('images/join.png') or find_and_click('images/joininactive.png'):
            
            # 3. กดยืนยันค้นหา 
            if find_and_click('images/find.png', wait_time=3):
                print("[+] พบซอมบี้")
                
                # 4. กดโจมตีซอมบี้บนแผนที่
                if find_and_click('images/rally.png'):
                    print("[+] กดรวมพล")
                    
                    # 5. เช็คว่าพลังศัตรูตีไหวไหม
                    if find('images/good_enermy.png'):
                        print("[+] ศัตรูพลังน้อยกว่า")
                        
                        # 6. กดปุ่มเตรียมส่งทัพ
                        if find_and_click('images/start-rally.png'):
                            
                            # เช็คว่ามีคนตีไปแล้วหรือยัง
                            if find_and_click('images/cancle.png'):
                                print("[-] ตีซอมบี้ซ้ำคนอื่น ยกเลิก!")
                                return False
                            else:
                                print(">>> ส่งทัพสำเร็จ! <<<")
                                return True
                    else:
                        print("[-] ศัตรูพลังเยอะกว่า (หรือหา good_enermy ไม่เจอ)")
                        return False
                        
    print("=== ลูปโจมตีล้มเหลว หรือ ไม่พบเป้าหมาย ===")
    return False

# ==========================================
# 4. ลูปควบคุมบอท
# ==========================================
if __name__ == "__main__":
    GAME_NAME = "DarkWar" # ชื่อหน้าต่างเกม
    
    print("*********************** โปรแกรมจะเริ่มทำงานใน 5 วินาที... *************************")
    time.sleep(5)
    
    # บังคับล็อคหน้าต่างก่อนเริ่มบอทเสมอ
    setup_game_window(GAME_NAME)
    
    is_attack = True
    success_count = 0
    energy_refill_count = 0
    
    while is_attack:
        if find("images/frank.png"):
            is_attack = False
        success = attack_zombie_routine()
        
        if success:
            success_count += 1
            print(f">>> ส่งทัพสำเร็จไปแล้ว {success_count} ครั้ง <<<")
            print(f">>> เติมพลังงานไปแล้ว {energy_refill_count} ครั้ง <<<")
            print("พักรอทัพกลับมา 3 นาที (180 วินาที)...")
            time.sleep(180) 
            
        else:
            # วิเคราะห์สาเหตุที่ล้มเหลวและแก้ไขสถานการณ์
            if find_and_click('images/back.png'): 
                print("[+] ออกจากหน้าต่าง ลองใหม่ใน 2 วินาที...")
                time.sleep(2)
            elif find_and_click("images/world.png"):
                print("[+] อยู่ในบ้าน (กดออกแผนที่โลก) ลองใหม่ใน 3 วินาที...")
                time.sleep(3)
            elif find_and_click("images/add-energy.png"):
                find_and_click("images/energy20.png")
                energy_refill_count += 1
                time.sleep(3)
            elif find("images/trucknotavailable.png"):
                click_safe_ground()
                print("[-] รถไม่ว่าง ลองใหม่ใน 60 วินาที...")
                time.sleep(60)
            elif not find("images/good_enermy.png"): # ปรับ logic เช็ครูปให้เขียนสั้นลง
                click_safe_ground()
                print("[-] ศัตรูพลังเยอะกว่า (หรือหาปุ่มไม่เจอ) ลองใหม่ใน 30 วินาที...")
                time.sleep(30)
            else:
                click_safe_ground()
                print("[-] ปัญหาอื่นๆ เคลียร์หน้าจอแล้วลองใหม่ใน 3 วินาที...")
                time.sleep(3)