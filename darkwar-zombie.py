import pyautogui
import time
import cv2
import numpy as np

def check_energy_portable():
    print("กำลังค้นหารูปโปรไฟล์อ้างอิง...")
    try:
        # 1. ค้นหารูปโปรไฟล์บนหน้าจอ
        anchor = pyautogui.locateOnScreen('profile_anchor.png', confidence=0.8)
        
        if anchor:
            # anchor จะคืนค่ากล่องสี่เหลี่ยม (left, top, width, height)
            # 2. คำนวณหาพิกัดของหลอดพลังงาน (Offset)
            # แกน X: เอาขอบซ้ายบวกครึ่งหนึ่งของความกว้าง (ให้อยู่ตรงกลางรูปโปรไฟล์พอดี)
            check_x = int(anchor.left + (anchor.width / 2))
            
            # แกน Y: เอาขอบบนบวกความสูงของรูปโปรไฟล์ แล้วบวกลงมาอีกนิดหน่อย (เช่น 15 พิกเซล) เพื่อให้ตรงกับหลอดสีเขียวพอดี
            check_y = int(anchor.top + anchor.height + 15) 
            
            # 3. ดึงค่าสีจากตำแหน่งที่คำนวณได้
            current_color = pyautogui.screenshot().getpixel((check_x, check_y))
            r, g, b = current_color
            
            # 4. เช็คว่าเป็นสีเขียวหรือไม่
            if g > 150 and r < 120 and b < 120: 
                print(f"[OK] พลังงานพอ (ตรวจพบสีเขียวที่ X:{check_x}, Y:{check_y})")
                return True
            else:
                print(f"[!] พลังงานไม่พอ (ไม่ใช่สีเขียวที่ X:{check_x}, Y:{check_y} | RGB: {current_color})")
                return False
        else:
            print("[-] หารูปโปรไฟล์อ้างอิงไม่เจอ (อาจจะเปิดหน้าต่างอื่นบังอยู่)")
            return False
            
    except Exception as e:
        print(f"[!] เกิดข้อผิดพลาดในการเช็คพลังงาน: {e}")
        return False

def check_enemy_power():
    print("[?] กำลังสแกนหาแถบพลัง VS...")
    try:
        vs_loc = pyautogui.locateOnScreen('vs_icon.png', confidence=0.8)
        
        if vs_loc:
            # ตีกรอบจับภาพฝั่งขวาเหมือนเดิม
            roi_x = int(vs_loc.left + vs_loc.width + 10)
            roi_y = int(vs_loc.top - 10)
            roi_w = 200 
            roi_h = int(vs_loc.height + 20)
            
            roi_screenshot = pyautogui.screenshot(region=(roi_x, roi_y, roi_w, roi_h))
            img_bgr = cv2.cvtColor(np.array(roi_screenshot), cv2.COLOR_RGB2BGR)
            hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
            
            # --- เปลี่ยนมาตรวจจับ "สีขาว" แทน ---
            # สีขาวใน HSV คือ: ค่า H(สี) อะไรก็ได้, ค่า S(ความสด) ต่ำมากๆ, ค่า V(ความสว่าง) สูงมากๆ
            lower_white = np.array([0, 0, 200]) 
            upper_white = np.array([180, 45, 255])
            
            # สร้าง Mask กรองเอาเฉพาะสีขาว
            white_mask = cv2.inRange(hsv, lower_white, upper_white)
            
            # นับจำนวนพิกเซลสีขาว
            white_pixels = cv2.countNonZero(white_mask)
            
            # --- ระบบ DEBUG (เปิดหน้าต่างโชว์สิ่งที่บอทเห็น) ---
            # หน้าต่างนี้จะโชว์ภาพขาวดำ ส่วนที่เป็นสีขาวคือสิ่งที่บอทจับได้
            # cv2.imshow("Bot Vision (White Mask)", white_mask)
            # cv2.waitKey(2000) # โชว์ค้างไว้ 2 วินาที (2000 ms) แล้วปิดอัตโนมัติ
            # cv2.destroyAllWindows()
            # ----------------------------------------------
            
            # ถ้าเจอสีขาวเยอะ (ตัวเลขเป็นสีขาว) แปลว่าตีไหว!
            if white_pixels > 4100: 
                print(f"[+] เจอตัวเลขสีขาว ({white_pixels} จุด) -> ตีไหว ลุยเลย!")
                return True
            else:
                print(f"[-] ไม่พบตัวเลขสีขาว ({white_pixels} จุด) น่าจะเป็นสีแดง -> ยกเลิกการตี")
                return False
                
        else:
            print("[-] หารูป VS ไม่เจอ (ตั้งค่า confidence หรือรูปภาพอาจยังไม่เป๊ะ)")
            return False

    except Exception as e:
        print(f"[!] เกิดข้อผิดพลาด: {e}")
        return False


def click_safe_ground():
    print("[?] กำลังสแกนหาพื้นที่สีเขียวว่างๆ บนจอ...")
    try:
        # 1. แคปหน้าจอและแปลงรูปแบบภาพสำหรับ OpenCV
        screen = pyautogui.screenshot()
        screen_np = np.array(screen)
        # แปลงจาก RGB เป็น BGR (มาตรฐานของ OpenCV)
        frame_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
        # แปลงจาก BGR เป็น HSV เพื่อให้แยกสีได้แม่นยำขึ้น
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

        # 2. กำหนดช่วงสี "เขียว" ของพื้นหญ้าในเกม (อาจต้องปรับจูนตัวเลขนี้)
        # ค่า H (Hue) สำหรับสีเขียวจะอยู่ราวๆ 35 ถึง 85
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])

        # 3. สร้าง Mask กรองเอาเฉพาะสีเขียวที่อยู่ในช่วงที่เรากำหนด
        mask = cv2.inRange(hsv, lower_green, upper_green)

        # 4. หา "รูปร่าง" (Contours) ของพื้นที่สีเขียวทั้งหมดที่เจอ
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # 5. หาพื้นที่สีเขียวที่ "ใหญ่ที่สุด" เพื่อความชัวร์ว่าจะไม่ไปโดนซอกเล็กๆ
            largest_contour = max(contours, key=cv2.contourArea)
            
            # เช็คว่าพื้นที่นั้นใหญ่พอที่จะเป็นที่ว่างจริงๆ ไหม (เช่น ขนาดพื้นที่ > 5000 พิกเซล)
            if cv2.contourArea(largest_contour) > 5000:
                # หาจุดกึ่งกลาง (Center) ของพื้นที่สีเขียวนั้น
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    center_x = int(M["m10"] / M["m00"])
                    center_y = int(M["m01"] / M["m00"])

                    # สั่งคลิกที่จุดกึ่งกลางของพื้นที่สีเขียว
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

# ฟังก์ชันหลักสำหรับหาภาพและคลิก
def find_and_click(image_path, confidence=0.8, wait_time=1.25):
    try:
        # ค้นหาจุดกึ่งกลางของภาพบนหน้าจอ
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        
        if location:
            # เลื่อนเมาส์ไปที่พิกัดนั้นแล้วคลิก
            pyautogui.moveTo(location)
            pyautogui.click()
            print(f"[+] คลิกสำเร็จ: {image_path}")
            
            # หน่วงเวลาให้แอนิเมชันเกมโหลดเสร็จก่อนทำขั้นตอนต่อไป
            time.sleep(wait_time) 
            return True
        else:
            print(f"[-] หาไม่เจอ: {image_path}")
            return False
            
    except pyautogui.ImageNotFoundException:
        print(f"[-] หาไม่เจอ: {image_path} (Exception)")
        return False
    except Exception as e:
        print(f"[!] ข้อผิดพลาดอื่นๆ: {e}")
        return False
# ฟังก์ชันหลักสำหรับหาภาพ
def find(image_path, confidence=0.8, wait_time=1.25):
    try:
        # ค้นหาจุดกึ่งกลางของภาพบนหน้าจอ
        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        
        if location:
            print(f"[+] หาเจอ: {image_path}")
            
            # หน่วงเวลาให้แอนิเมชันเกมโหลดเสร็จก่อนทำขั้นตอนต่อไป
            time.sleep(wait_time) 
            return True
        else:
            print(f"[-] หาไม่เจอ: {image_path}")
            return False
            
    except pyautogui.ImageNotFoundException:
        print(f"[-] หาไม่เจอ: {image_path} (Exception)")
        return False
    except Exception as e:
        print(f"[!] ข้อผิดพลาดอื่นๆ: {e}")
        return False

# ลำดับการทำงาน (State Machine อย่างง่าย)
def attack_zombie_routine():
    print("======================== เริ่มลูปค้นหาและโจมตีซอมบี้ =================================")
    
    # 1. กดปุ่มค้นหา/เรดาร์
    if find_and_click('zoom.png'):
        # # 2. เลือกแท็บซอมบี้
        if find_and_click('join.png') or find_and_click('joininactive.png'):
            
        #     # 3. กดยืนยันค้นหา (อาจจะหน่วงเวลาเพิ่มให้แผนที่เลื่อนไปหาเป้าหมาย)
            if find_and_click('find.png', wait_time=2.5):
                print("[+] พบซอมบี้")
                
                
        #         # 4. กดโจมตีซอมบี้บนแผนที่
                if find_and_click('rally.png'):
                    print("[+] กดรวมพล")
                    if find('good_enermy.png'):
                        print("[+] ศัตรูพลังน้อยกว่า")
                         # 5. จัดทัพ (ถ้าเกมไม่จัดให้อัตโนมัติ)
                        if find_and_click('start-rally.png'):
                            if find_and_click('cancle.png'):
                                click_safe_ground()
                                print("[+] ตีซอมบี้ซ้ำคนอื่น")
                                return False
                            else:
                                print("[+] ส่งทัพสำเร็จ! <<<")
                                return True
                    else:
                        print("[-] ศัตรูพลังเยอะกว่า")
                        return False
        #               
                        
        #             # 6. กดส่งทัพ (March)
        #             if find_and_click('march_btn.png'):
        #                 print(">>> ส่งทัพสำเร็จ! <<<")
        #                 return True
                        
    print("=== ลูปโจมตีล้มเหลว หรือ ไม่พบเป้าหมาย ===")
    return False

# รันลูปการทำงาน
if __name__ == "__main__":
    print("***********************โปรแกรมจะเริ่มทำงานใน 5 วินาที... (กรุณาเปิดหน้าจอเกมเตรียมไว้)*************************")
    time.sleep(5)
    
    success_count = 0
    
    while True:
        success = attack_zombie_routine()
        
        if success:
            success_count += 1
            print(f">>> ส่งทัพสำเร็จไปแล้ว {success_count} ครั้ง <<<")
            # สมมติว่าใช้เวลาเดินทัพไป-กลับ 3 นาที (180 วินาที)
            print("พักรอทัพกลับมา 3 นาที...")
            time.sleep(190) 
            # energy = check_energy_portable()
            
        else:
            # ถ้าเกิด Error หรือหาปุ่มไม่เจอ ให้พักแป๊บเดียวแล้วลองใหม่
            if find_and_click('back.png'): 
                print("[+] ออกจากหน้าต่าง ลองใหม่ใน 2 วินาที...")
                time.sleep(2)
            elif find_and_click("world.png"):
                print("[+] อยู่ในบ้าน ลองใหม่ใน 3 วินาที...")
                time.sleep(3)
            elif find_and_click("add-energy.png"):
                print("[+] add energy ลองใหม่ใน 3 วินาที...")
                find_and_click("energy20.png")
                time.sleep(3)
            elif find("trucknotavailable.png"):
                click_safe_ground()
                print("[-] รถไม่ว่าง ลองใหม่ใน 60 วินาที...")
                time.sleep(60)
            elif find("good_enermy.png") == False:
                click_safe_ground()
                print("[-] ศัตรูพลังเยอะกว่า ลองใหม่ใน 30 วินาที...")
                time.sleep(30)
            else:
                click_safe_ground()
                print("[-] ลองใหม่ใน 3 วินาที...")
                time.sleep(3)