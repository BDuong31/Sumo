from machine import Pin

class LineSensor:
    """
    Thư viện đơn giản để giao tiếp với cảm biến dò line kỹ thuật số trên Raspberry Pi Pico.

    Args:
        pin (int): Chân GPIO mà cảm biến dò line được kết nối.
    """
    def __init__(self, pin):
        """
        Khởi tạo đối tượng LineSensor.

        Args:
            pin (int): Chân GPIO mà cảm biến được kết nối.
        """
        self.pin = Pin(pin, Pin.IN)  # Cấu hình chân GPIO làm đầu vào

    def read(self):
        """
        Đọc giá trị từ cảm biến.

        Returns:
            int: 0 nếu phát hiện màu đen, 1 nếu phát hiện màu trắng.
        """
        return self.pin.value()  # Trả về giá trị đọc được từ chân GPIO

    def is_black(self):
        """
        Kiểm tra xem cảm biến có đang phát hiện màu đen không.

        Returns:
            bool: True nếu phát hiện màu đen, False nếu không.
        """
        return self.read() == 0  # Màu đen tương ứng với giá trị 0

    def is_white(self):
        """
        Kiểm tra xem cảm biến có đang phát hiện màu trắng không.

        Returns:
            bool: True nếu phát hiện màu trắng, False nếu không.
        """
        return self.read() == 1  # Màu trắng tương ứng với giá trị 1
