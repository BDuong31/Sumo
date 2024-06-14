from machine import Pin, I2C
from lib.l298n import L298N
from lib.line_sensor import LineSensor
from lib.hcsr04 import HCSR04
from lib.vl53l0x import VL53L0X, TimeoutError
import utime

# === CẤU HÌNH CHÂN GPIO ===
PIN_LINE_LEFT = 26       # Chân GPIO cho cảm biến dò line trái
PIN_LINE_RIGHT = 27      # Chân GPIO cho cảm biến dò line phải

PIN_TRIG_FRONT = 14      # Chân Trigger cho cảm biến siêu âm phía trước
PIN_ECHO_FRONT = 15      # Chân Echo cho cảm biến siêu âm phía trước
PIN_TRIG_LEFT = 16       # Chân Trigger cho cảm biến siêu âm bên trái
PIN_ECHO_LEFT = 17       # Chân Echo cho cảm biến siêu âm bên trái
PIN_TRIG_RIGHT = 18      # Chân Trigger cho cảm biến siêu âm bên phải
PIN_ECHO_RIGHT = 19      # Chân Echo cho cảm biến siêu âm bên phải

PIN_MOTOR_LEFT_EN = 12   # Chân Enable cho động cơ trái
PIN_MOTOR_LEFT_IN1 = 10  # Chân IN1 cho động cơ trái
PIN_MOTOR_LEFT_IN2 = 11  # Chân IN2 cho động cơ trái
PIN_MOTOR_RIGHT_EN = 13  # Chân Enable cho động cơ phải
PIN_MOTOR_RIGHT_IN1 = 8   # Chân IN1 cho động cơ phải
PIN_MOTOR_RIGHT_IN2 = 9   # Chân IN2 cho động cơ phải

# === CẤU HÌNH I2C CHO CẢM BIẾN VL53L0X ===
i2c0 = I2C(0, scl=Pin(1), sda=Pin(0))     # Bus I2C 0
i2c1 = I2C(1, scl=Pin(22), sda=Pin(23))  # Bus I2C 1

# Khởi tạo cảm biến VL53L0X trên các bus I2C với địa chỉ mặc định 0x29
laser_left = VL53L0X(i2c0, address=0x29)  
laser_right = VL53L0X(i2c1, address=0x29) 

# === KHỞI TẠO CÁC CẢM BIẾN VÀ ĐỘNG CƠ ===
line_left = LineSensor(PIN_LINE_LEFT)
line_right = LineSensor(PIN_LINE_RIGHT)

tof_front = HCSR04(PIN_TRIG_FRONT, PIN_ECHO_FRONT)
tof_left = HCSR04(PIN_TRIG_LEFT, PIN_ECHO_LEFT)
tof_right = HCSR04(PIN_TRIG_RIGHT, PIN_ECHO_RIGHT)

motor_left = L298N(PIN_MOTOR_LEFT_EN, PIN_MOTOR_LEFT_IN1, PIN_MOTOR_LEFT_IN2)
motor_right = L298N(PIN_MOTOR_RIGHT_EN, PIN_MOTOR_RIGHT_IN1, PIN_MOTOR_RIGHT_IN2)

# === CÁC NGƯỠNG VÀ THAM SỐ ĐIỀU KHIỂN ===
DISTANCE_THRESHOLD_ATTACK = 100  # (mm)
DISTANCE_THRESHOLD_DETECT = 300  # (mm)
LINE_THRESHOLD = 0.5             
FORWARD_SPEED = 0.6              
BACKWARD_SPEED = 0.4             
TURN_SPEED = 0.5                 
SEARCH_TIME = 5                  
ATTACK_TIME = 3                  
TIMEOUT_DURATION = 200 # ms       # Thời gian tối đa để chờ một cảm biến

def main():
    print("Robot khởi động, chờ 5 giây...")
    utime.sleep(5)  

    state = "search"              
    search_start_time = utime.ticks_ms()  
    attack_start_time = utime.ticks_ms() 

    while True:
        # === ĐỌC GIÁ TRỊ TỪ CÁC CẢM BIẾN === (CÓ XỬ LÝ LỖI)

        line_left_value = line_left.read()      
        line_right_value = line_right.read()    

        # Đọc cảm biến siêu âm, giới hạn thời gian chờ
        start_time = utime.ticks_ms()
        while utime.ticks_diff(utime.ticks_ms(), start_time) < TIMEOUT_DURATION:
            try: 
                distance_front = tof_front.distance_mm()
                break
            except OSError:
                pass # tiếp tục nếu có lỗi đọc
        else:
            distance_front = 1000 # thiết lập giá trị mặc định khi timeout
 
        start_time = utime.ticks_ms()  
        while utime.ticks_diff(utime.ticks_ms(), start_time) < TIMEOUT_DURATION:
            try:
                distance_left = tof_left.distance_mm()
                break
            except OSError:
                pass # tiếp tục nếu có lỗi đọc
        else:
            distance_left = 1000  # thiết lập giá trị mặc định khi timeout

        start_time = utime.ticks_ms()  
        while utime.ticks_diff(utime.ticks_ms(), start_time) < TIMEOUT_DURATION:
            try:
                distance_right = tof_right.distance_mm()
                break
            except OSError:
                pass
        else:
            distance_right = 1000


        # Đọc cảm biến laser, giới hạn thời gian chờ
        start_time = utime.ticks_ms()  
        while utime.ticks_diff(utime.ticks_ms(), start_time) < TIMEOUT_DURATION:
            try:
                laser_left_value = laser_left.read()
                break
            except TimeoutError:
                pass
        else:
            laser_left_value = 1000 
        
        start_time = utime.ticks_ms()  
        while utime.ticks_diff(utime.ticks_ms(), start_time) < TIMEOUT_DURATION:
            try:
                laser_right_value = laser_right.read()
                break
            except TimeoutError:
                pass
        else:
            laser_right_value = 1000 
        
        # === XỬ LÝ LOGIC DÒ LINE ===
        if line_left_value < LINE_THRESHOLD and line_right_value < LINE_THRESHOLD:
            # Cả hai cảm biến trên vạch đen => Tiến
            motor_left.forward(FORWARD_SPEED)
            motor_right.forward(FORWARD_SPEED)
        elif line_left_value > LINE_THRESHOLD and line_right_value > LINE_THRESHOLD:
            # Cả hai cảm biến trên vạch trắng => Lùi
            motor_left.backward(BACKWARD_SPEED)
            motor_right.backward(BACKWARD_SPEED)
        else:
            # Một cảm biến trên vạch đen, một cảm biến trên vạch trắng => Xoay
            if line_left_value < LINE_THRESHOLD:
                motor_left.backward(TURN_SPEED)
                motor_right.forward(TURN_SPEED)
            else:
                motor_left.forward(TURN_SPEED)
                motor_right.backward(TURN_SPEED)
        
        # === XỬ LÝ LOGIC TRẠNG THÁI ===
        if state == "search":
            # Trạng thái tìm kiếm đối thủ
            if utime.ticks_diff(utime.ticks_ms(), search_start_time) > SEARCH_TIME * 1000:
                state = "attack" # Chuyển sang trạng thái tấn công nếu quá thời gian tìm kiếm
                attack_start_time = utime.ticks_ms()
            else:
                # Xoay để tìm kiếm đối thủ
                motor_left.forward(TURN_SPEED)
                motor_right.backward(TURN_SPEED)  

        elif state == "attack":
            # Trạng thái tấn công
            if utime.ticks_diff(utime.ticks_ms(), attack_start_time) > ATTACK_TIME * 1000:
                state = "search" # Chuyển sang trạng thái tìm kiếm nếu quá thời gian tấn công
                search_start_time = utime.ticks_ms()
            else:
                 if (distance_front < DISTANCE_THRESHOLD_ATTACK or distance_left < DISTANCE_THRESHOLD_ATTACK or distance_right < DISTANCE_THRESHOLD_ATTACK or laser_left_value < DISTANCE_THRESHOLD_ATTACK or laser_right_value < DISTANCE_THRESHOLD_ATTACK):
                    # Tấn công trực diện nếu đối thủ ở gần
                    motor_left.forward(FORWARD_SPEED)
                    motor_right.forward(FORWARD_SPEED)
                 elif (distance_front < DISTANCE_THRESHOLD_DETECT or distance_left < DISTANCE_THRESHOLD_DETECT or distance_right < DISTANCE_THRESHOLD_DETECT or laser_left_value < DISTANCE_THRESHOLD_DETECT or laser_right_value < DISTANCE_THRESHOLD_DETECT):
                    # Tiếp cận đối thủ nếu đối thủ ở xa hơn 
                    if distance_left < distance_right:
                        motor_left.forward(TURN_SPEED)
                        motor_right.backward(TURN_SPEED)
                    else:
                        motor_left.backward(TURN_SPEED)
                        motor_right.forward(TURN_SPEED)
                 else:
                    # Không thấy đối thủ, quay lại trạng thái tìm kiếm
                    state = "search"
                    search_start_time = utime.ticks_ms()

if __name__ == "__main__":
    main()