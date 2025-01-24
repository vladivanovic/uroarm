import serial
import time

# Open the serial port
ser = serial.Serial('/dev/tty.usbmodem2101', 115200, timeout=1)

# Function to send data
def send_command(command):
    print(f"Sending: {command}")
    ser.write((command + '\n').encode('utf-8'))
    time.sleep(0.5)

# Send the command "import main"
send_command("import main")

# Allow some time for the device to respond
time.sleep(1)

# Read and print any incoming data
try:
    while True:
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8').rstrip()
            print(f"Received: {response}")
        else:
            break
except Exception as e:
    print(f"An error occurred: {e}")

# Close the serial port when done (optional)
ser.close()
