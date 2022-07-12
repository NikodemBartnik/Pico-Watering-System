from machine import Pin, ADC, Timer
import time, os

#constants
PIN_PUMP_1 = 15
PIN_PUMP_2 = 14
PIN_LED_R_1 = 2
PIN_LED_R_2 = 3
PIN_LED_R_3 = 4
PIN_LED_R_4 = 5
PIN_LED_G_1 = 18
PIN_LED_G_2 = 19
PIN_LED_G_3 = 20
PIN_LED_G_4 = 21

PIN_BUTTON_1 = 6
PIN_BUTTON_2 = 17

PIN_WATER_LEVEL_SENSOR_1 = 0
PIN_WATER_LEVEL_SENSOR_2 = 1

WATERING_CYCLE_TIMES_ARRAY = [2, 4, 6, 8] #time in minutes

#global variables
selectionActive = True
dailyWateringCycles = 3 
wateringCycleTime = 1 #choose from WATERING_CYCLE_TIMES
selectionTimer = Timer()
lastWatering = time.time()

pump1 = Pin(PIN_PUMP_1, Pin.OUT)
pump2 = Pin(PIN_PUMP_2, Pin.OUT)

ledR1 = Pin(PIN_LED_R_1, Pin.OUT)
ledR2 = Pin(PIN_LED_R_2, Pin.OUT)
ledR3 = Pin(PIN_LED_R_3, Pin.OUT)
ledR4 = Pin(PIN_LED_R_4, Pin.OUT)
ledG1 = Pin(PIN_LED_G_1, Pin.OUT)
ledG2 = Pin(PIN_LED_G_2, Pin.OUT)
ledG3 = Pin(PIN_LED_G_3, Pin.OUT)
ledG4 = Pin(PIN_LED_G_4, Pin.OUT)

button1 = Pin(PIN_BUTTON_1, Pin.IN, Pin.PULL_DOWN)
button2 = Pin(PIN_BUTTON_2, Pin.IN, Pin.PULL_DOWN)
wl1 = Pin(PIN_WATER_LEVEL_SENSOR_1, Pin.IN, Pin.PULL_UP)
wl2 = Pin(PIN_WATER_LEVEL_SENSOR_2, Pin.IN, Pin.PULL_UP)


def checkKeys():
    global selectionActive
    if(button1.value() or button2.value()):
        selectionActive = True
        selectionTimer.init(mode=Timer.ONE_SHOT, period=10000, callback=disableSelection)
        
def disableSelection(t):
    global selectionActive
    selectionActive = False
    ledR1.value(0)
    ledR2.value(0)
    ledR3.value(0)
    ledR4.value(0)
    ledG1.value(0)
    ledG2.value(0)
    ledG3.value(0)
    ledG4.value(0)
    saveSettings()
    selectionTimer.init(mode=Timer.PERIODIC, freq=0.1, callback=signOfLife)
    
    
def saveSettings():
    #saving settings
    try:
        os.remove('t.txt')
    except OSError:
        print("t.txt doesn't exists")
    try:
        os.remove('c.txt')
    except OSError:
        print("t.txt doesn't exists")
        
    f = open('t.txt', 'w+')
    f.write(str(wateringCycleTime))
    f.close()
    f = open('c.txt', 'w+')
    f.write(str(dailyWateringCycles))
    f.close()
    
def loadSettings():
    global wateringCycleTime, dailyWateringCycles
    try:
        f = open('t.txt')
        wateringCycleTime = int(f.read())
        print('wateringCycleTime', wateringCycleTime)
        f.close()
    except OSError:
        print("t.txt doesn't exists")
    try: 
        f = open('c.txt')
        dailyWateringCycles = int(f.read())
        print('dailyWateringCycles', dailyWateringCycles)
        f.close()
    except OSError:
        print("c.txt doesn't exists")

    
def displayWateringTimes():
    if(selectionActive):
        ledR4.value(1) if wateringCycleTime >= 0 else ledR4.value(0)
        ledR3.value(1) if wateringCycleTime >= 1 else ledR3.value(0)
        ledR2.value(1) if wateringCycleTime >= 2 else ledR2.value(0)
        ledR1.value(1) if wateringCycleTime >= 3 else ledR1.value(0)
        
        
def displayWateringCycles():
    if(selectionActive):
        ledG1.value(1) if dailyWateringCycles >= 0 else ledG1.value(0)
        ledG2.value(1) if dailyWateringCycles >= 1 else ledG2.value(0)
        ledG3.value(1) if dailyWateringCycles >= 2 else ledG3.value(0)
        ledG4.value(1) if dailyWateringCycles >= 3 else ledG4.value(0)
    

def checkAndModifySettings():
    global wateringCycleTime, dailyWateringCycles
    if(button1.value()):
        time.sleep_ms(50)
        if(button1.value()):
            wateringCycleTime = (wateringCycleTime+1) if wateringCycleTime < 3 else 0
            displayWateringTimes()
            time.sleep_ms(200)
    
    if(button2.value()):
        time.sleep_ms(50)
        if(button2.value()):
            dailyWateringCycles = (dailyWateringCycles+1) if dailyWateringCycles < 3 else 0
            displayWateringCycles()
            time.sleep_ms(200)
            
            

def checkWatering():
    global lastWatering
    if((time.time() - lastWatering) > (86400/(dailyWateringCycles + 1))):
        wateringStart = time.time()
        if(checkWaterLevel()):
            pump1.value(1)
            while(time.time() - wateringStart < (WATERING_CYCLE_TIMES_ARRAY[wateringCycleTime]*60)):
                ledG1.value(1)
                time.sleep_ms(200)
                ledG1.value(0)
                time.sleep_ms(200)
            pump1.value(0)
        lastWatering = time.time()
        
        
def signOfLife(t):
    ledR1.value(1)
    time.sleep_ms(10)
    ledR1.value(0)
    print('sign of life')
    
def checkWaterLevel():
    return 0 if wl1.value() else 1


def checkWaterAndAlarm():
    if(checkWaterLevel() == 0):
        ledR4.value(1)
        time.sleep_ms(500)
        ledR4.value(0)
        time.sleep_ms(500)
        

#loading the settings from flash before entering the loop
loadSettings()
#disable LEDs after 10 seconds
selectionTimer.init(mode=Timer.ONE_SHOT, period=10000, callback=disableSelection)

while(1):
    checkKeys()
    checkWatering()
    if(selectionActive):
        checkAndModifySettings()
        displayWateringTimes()
        displayWateringCycles()
    else:
        checkWaterAndAlarm()
        
    time.sleep_ms(50)
