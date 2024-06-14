from machine import Pin, PWM

class L298N:
    """
    Thư viện điều khiển động cơ DC sử dụng mạch L298N.

    Args:
        en (int): Chân GPIO điều khiển Enable/PWM (tốc độ) của động cơ.
        in1 (int): Chân GPIO điều khiển hướng 1 của động cơ.
        in2 (int): Chân GPIO điều khiển hướng 2 của động cơ.
        freq (int, optional): Tần số PWM (mặc định là 1000Hz).
    """
    def __init__(self, en, in1, in2, freq=1000):
        self.en_pin = PWM(Pin(en))
        self.en_pin.freq(freq)  # Đặt tần số PWM
        self.in1_pin = Pin(in1, Pin.OUT)
        self.in2_pin = Pin(in2, Pin.OUT)

    def forward(self, speed):
        """
        Điều khiển động cơ quay về phía trước.

        Args:
            speed (float): Tốc độ từ 0.0 (dừng) đến 1.0 (tốc độ tối đa).
        """
        self.en_pin.duty_u16(int(speed * 65535))  # Điều chỉnh tốc độ bằng PWM
        self.in1_pin.value(1)  # IN1 cao, IN2 thấp để quay về phía trước
        self.in2_pin.value(0)

    def backward(self, speed):
        """
        Điều khiển động cơ quay về phía sau.

        Args:
            speed (float): Tốc độ từ 0.0 (dừng) đến 1.0 (tốc độ tối đa).
        """
        self.en_pin.duty_u16(int(speed * 65535))
        self.in1_pin.value(0)  # IN1 thấp, IN2 cao để quay về phía sau
        self.in2_pin.value(1)

    def stop(self):
        """Dừng động cơ."""
        self.en_pin.duty_u16(0)  # Tắt PWM để dừng động cơ

    def coast(self):
        """Cho phép động cơ chạy tự do (không cấp nguồn)."""
        self.en_pin.duty_u16(0)
        self.in1_pin.value(0)
        self.in2_pin.value(0)  # IN1 và IN2 đều thấp để không cấp nguồn

    def brake(self):
        """Phanh động cơ (ngắn mạch hai đầu cực động cơ)."""
        self.en_pin.duty_u16(65535)  # PWM ở mức cao nhất
        self.in1_pin.value(1)
        self.in2_pin.value(1)  # IN1 và IN2 đều cao để ngắn mạch

    def set_speed(self, speed):
        """
        Đặt tốc độ động cơ, cho phép cả tiến và lùi.

        Args:
            speed (float): Tốc độ từ -1.0 (lùi hết tốc lực) đến 1.0 (tiến hết tốc lực).
        """
        if speed >= 0:
            self.forward(speed)
        else:
            self.backward(-speed)

    def __del__(self):
        """Hàm hủy: Dừng động cơ khi đối tượng bị hủy."""
        self.stop()  # Đảm bảo động cơ dừng khi không sử dụng nữa
