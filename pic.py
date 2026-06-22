import cv2
import numpy as np
import pyautogui

# ใส่ TRUCK_CONFIG ที่คุณกำลังจะทดสอบลงไปตรงนี้
TRUCK_CONFIG = [
    {"name": "Truck 1", "region": (870, 510, 55, 55)},
    {"name": "Truck 2", "region": (870, 570, 55, 55)},
    {"name": "Truck 3", "region": (870, 625, 55, 55)},
    {"name": "Truck 4", "region": (870, 680, 55, 55)}
]

def show_debug_regions():
    print("[*] กำลังแคปหน้าจอเพื่อวาดกรอบ Debug...")
    
    # 1. แคปหน้าจอทั้งหมด
    screen = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)

    # 2. วนลูปวาดกรอบสี่เหลี่ยมตามค่า region ของรถแต่ละคัน
    for truck in TRUCK_CONFIG:
        # แยกค่า x, y, กว้าง(w), สูง(h) ออกมาจาก tuple
        x, y, w, h = truck['region']
        
        # วาดกรอบสี่เหลี่ยมสีเขียว (พิกัดมุมซ้ายบน ถึง พิกัดมุมขวาล่าง) ความหนาเส้น = 2
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # ใส่ตัวหนังสือชื่อรถกำกับไว้บนกล่อง (สีแดง)
        cv2.putText(img, truck['name'], (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    print("[+] วาดเสร็จแล้ว! กำลังเปิดหน้าต่างรูปภาพ...")
    print("💡 ปิดหน้าต่างโดยการ 'กดปุ่มอะไรก็ได้บนคีย์บอร์ด' 1 ครั้ง")
    
    # 3. โชว์รูปภาพที่วาดกรอบแล้ว
    cv2.imshow("Debug Regions Vision", img)
    
    # รอจนกว่าคุณจะกดคีย์บอร์ด ถึงจะปิดหน้าต่าง
    cv2.waitKey(0) 
    cv2.destroyAllWindows()

if __name__ == "__main__":
    show_debug_regions()