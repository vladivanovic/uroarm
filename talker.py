import serial
import time

class TalkerError(Exception):
    pass

class SerialPortError(TalkerError):
    pass

class Talker:
    TERMINATOR = '\r'.encode('UTF8')

    def __init__(self, port='/dev/tty.usbmodem2101', timeout=1):
        try:
            self.serial = serial.Serial(port, 115200, timeout=timeout)
            time.sleep(2)
            self.serial.write(b'\x03')
        except serial.serialutil.SerialException:
            raise SerialPortError(f'The specified serial port does not exist: {port}')

    def send(self, text: str):
        line = '%s\r\f' % text
        self.serial.write(line.encode('utf-8'))
        time.sleep(1)  # Give some time for the device to process the command
        reply = self.receive()
        if text not in reply:  # the line should be echoed, so the result should match
            raise TalkerError(f'expected {text} got {reply}')
        return reply

    def receive(self) -> str:
        reply = self.serial.read_all().decode('utf-8').strip()
        # Filter out escape sequences and irrelevant output
        filtered_reply = []
        for line in reply.split('\n'):
            if not any(unwanted in line for unwanted in ["\x1b[", ">>>", "None"]):
                filtered_reply.append(line)
        return '\n'.join(filtered_reply)

    def close(self):
        self.serial.close()
