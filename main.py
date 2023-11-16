import machine
import time
import urequests

# Telegram bot configuration
BOT_TOKEN = "6328941060:AAGmkPxoo900Xf1Z542jcjfoXpajRFljMVc"
CHAT_ID = "187740907"

# Define GPIO pins for trigger and echo of ultrasonic sensor
trigger_pin = machine.Pin(2, machine.Pin.OUT)
echo_pin = machine.Pin(3, machine.Pin.IN)

# Define the GPIO pin connected to the OUT pin of the PIR sensor
pir_sensor_pin = machine.Pin(7, machine.Pin.IN)


def connect():
    import network
 
    ssid = "Staff KML" 
    password = "stafkml@15" 
 
    station = network.WLAN(network.STA_IF)
 
    if station.isconnected() == True:
        print("Already connected")
        return
 
    station.active(True)
    station.connect(ssid, password)
 
    while station.isconnected() == False:
        pass
 
    print("Connection successful")
    print(station.ifconfig())
    
connect()


def get_distance():
    # Triggering the ultrasonic sensor
    trigger_pin.off()
    time.sleep_us(2)
    trigger_pin.on()
    time.sleep_us(10)
    trigger_pin.off()
    
    # Measuring the time for the echo
    while echo_pin.value() == 0:
        pulse_time = time.ticks_us()
    
    while echo_pin.value() == 1:
        end_time = time.ticks_us()
    
    # Calculating distance in centimeters
    pulse_duration = end_time - pulse_time
    distance_cm = (pulse_duration * 0.0343) / 2
    
    return distance_cm

def motion_detected(pin):
    print("Motion detected!")
    send_telegram_message("Motion detected!")

def send_telegram_message(message):
    url = "https://api.telegram.org/bot{}/sendMessage".format(BOT_TOKEN)
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        response = urequests.post(url, json=data)
        print("Message sent to Telegram")
        response.close()
    except Exception as e:
        print("Failed to send message:", e)

# Set up an interrupt on the GPIO pin for detecting motion
pir_sensor_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=motion_detected)

try:
    while True:
        distance = get_distance()
        motion_status = "Motion detected!" if pir_sensor_pin.value() else "Motion Detected"
        message = f"Distance: {distance} cm\n{motion_status}"
        print(message)
        send_telegram_message(message)
        time.sleep(1)
        
except KeyboardInterrupt:
    pir_sensor_pin.irq(trigger=0)  # Disable the PIR sensor interrupt
    print("Measurement stopped by user")


