'''
ESC204 Wildfire
Task: Desc.
'''

# Import libraries needed
import board
import analogio
import digitalio
import adafruit_am2320
import adafruit_bme680
import busio
import math
import time

# Set a control GPIO pin for power to thermistor
control_pin = digitalio.DigitalInOut(board.GP16)
control_pin.direction = digitalio.Direction.OUTPUT # sends 3.3V to power circuit if True
control_pin.value = False # start with the power off to avoid self-heating of thermistor

# Set up analog input using pin connected to thermistor
thermistor = analogio.AnalogIn(board.A1)

# Set up analog input using pin connected to gas sensor
gas_sensor = analogio.AnalogIn(board.A0)

# I2C for BME680 sensor
i2c_bme = busio.I2C(scl=board.GP19, sda=board.GP18) 
bme680_sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c_bme, address=0x76)
# I2C for AM2320 sensor
i2c_am = busio.I2C(scl=board.GP1, sda=board.GP0)
am2320_sensor = adafruit_am2320.AM2320(i2c_am)

# Set up digital input for PIR sensor
pir = digitalio.DigitalInOut(board.GP15)
pir.direction = digitalio.Direction.INPUT

def thermistor_temp_C(R0 = 10000.0, T0 = 25.0, B = 3950.0):
    '''
    Calculates the temperature in Celsius from the raw thermistor data
    using the B coefficient Steinhart-Hart equation
    '''
    control_pin.value = True # turn power on to read temperature
     
    thermistor_resistance = 10000 / (65535/thermistor.value - 1) # thermistor resistance in ohms
    steinhart = math.log(thermistor_resistance / R0) / B + 1.0/(T0 + 273.15) # find 1/T
    temp = (1.0 / steinhart) - 273.15 # find T in celcius
    
    control_pin.value = False # turn power off to save battery and prevent sefl heating
    return temp

while True:
    #print(thermistor_temp_C())

    #print(f'Humidity: {am2320_sensor.relative_humidity} %')
    
    #print(f'Temperature: {am2320_sensor.temperature} C')

    #print(pir.value)
    
    #print(gas_sensor.value)
    
    #print(f'Temperature (C): {bme680_sensor.temperature}')
    
    #print(f'Gas (ohms): {bme680_sensor.gas}')
    
    #print(f'Humidity (%): {bme680_sensor.humidity}')

    #print(f'Pressure (hPa): {bme680_sensor.pressure}')

    data = (f'Temperature: {thermistor_temp_C()} C',
            f'Humidity: {am2320_sensor.relative_humidity} %',
            f'PIR: {pir.value}',
            f'Gas: {gas_sensor.value} idk the units yet')
    

    print(data)
    time.sleep(1)  # wait 1 second between readings

#write down design decision somewhere: to avoid self heating,power the voltage divider from GPIO pin instead of 3.3V