#ENG1013 Chemical Tank Monitoring System Project - Milestone 4
#Team B10
#By Harshath Muruganantham (33114064), Zander Cappello (33111073), Matthew Jay Davis (33116768) and Minh Hoang Nguyen (33051399)
#Last Updated: 15/10/2022

import matplotlib.pyplot as plt
import time
import random
import math
from pymata4 import pymata4

#Arduino and pn set up
myArduino = pymata4.Pymata4()
#motor definition
outPumpPin = 5
myArduino.set_pin_mode_pwm_output(outPumpPin)
# myArduino.set_pin_mode_pwm_output
inPumpPin = 6
myArduino.set_pin_mode_pwm_output(inPumpPin)

# 555 Timer setup
triggerPin = 7 
myArduino.set_pin_mode_digital_output(triggerPin)
inputPin = 3 
myArduino.set_pin_mode_analog_input(inputPin)

#LEDs Initialisation
yellow = 15
myArduino.set_pin_mode_digital_output(15) #Yellow
red = 16
myArduino.set_pin_mode_digital_output(16) #Red
blue = 4
myArduino.set_pin_mode_digital_output(4) #Blue


#seven-seg display definition
srclk = 8
myArduino.set_pin_mode_digital_output(srclk)
ser = 9
myArduino.set_pin_mode_digital_output(ser)
Digit1 = 10
myArduino.set_pin_mode_digital_output(Digit1)
Digit2 = 11
myArduino.set_pin_mode_digital_output(Digit2)
Digit3 = 12
myArduino.set_pin_mode_digital_output(Digit3)
Digit4 = 13
myArduino.set_pin_mode_digital_output(Digit4)

tuning = 0.0001

srPins = [8,9]
dPins = [10,11,12,13]

# reset the input pins
myArduino.digital_write(ser,0)
myArduino.digital_write(srclk,0)

for pin in dPins:  #Might need to do Manually
    myArduino.digital_write(pin,1)
# sleeptime = 1
characters = {
    "A": "1110111",
    "B": "1111100",
    "C": '0111001',
    "D": '1011110',
    "E": '1111001',
    "F": '1110001',
    "G": '0111101',
    "H": '1110110',
    "I": '0000110',
    "J": '0001110',
    "K": '1110101',
    "L": '0111000',
    "M": '1010101',
    "N": '1010100',
    "O": '1011100',
    "P": '1110011',
    "Q": '1100111',
    "R": '1010000',
    "S": '1101101',
    "T": '1111000',
    "U": '0011100',
    "V": '0111110',
    "W": '1101010',
    "X": '1110110',
    "Y": '1101110',
    "Z": '1001011',
}

trigPin = 3
#define HCSR04_PIN_ECHO	2
echoPin = 2
myArduino.set_pin_mode_sonar(trigPin, echoPin, timeout=200000)
#define LDR_PIN_SIG	A5
ldrPin = 5
myArduino.set_pin_mode_analog_input(ldrPin)
#define THERMISTOR_PIN_CON1	A4
thermPin = 4
myArduino.set_pin_mode_analog_input(thermPin)


#Pins for UltraSonicSensor

#Tank Length, Height and Width
lengthLower = 26.5          
height = 50.5
widthLower = 25
lengthUpper = 25
widthUpper = 25      

#Initialise Values for Water Level
wli = 0
wlMatrix = [0]
waterSum =[]

#Specifications of Thermistor
r1 = float(9960)       #this will depend on what we use
vin = float(1023.0)
a = float(1.009249522e-03)         
b = float(2.378405444e-04)         
c = float(2.019202697e-07)        
tempVar = 18

#Initialize Values for Temperature Sensor
tempMatrix = []
tpi = 0

#Initialize Values for LDR
lri = 0
LDRMatrix = []
ldrVar = 820

#Initialise Values for system settings function
pin = 1234
tries = 0
sleepTime = 2

#Water Volume Ranges
lowWaterVolumeMin = 3
lowWaterVolumeMax = 4
optimumWaterVolumeMax = 6
highWaterVolumeMax = 7
fullWaterVolumeMax = 10

#Change in waterlevel parameters
dvdtMax = 0.1
LEDflash = 14
myArduino.set_pin_mode_digital_output(LEDflash)

timeoutSystemSettings = 120

def system_menu():
    '''
    This is the function that the sysstem boots into. Allows to enter other functions such as Tank Operation Mode,
    Graphing Mode and System Settings

    Inputs: Integer between 1 and 4
    Outputs: Calls Other Function. None is outputted by this specificc fucnction
    '''
    while True:
        option1 = '1. Enter Tank Operation Mode' 
        option2 = '2. Enter Graphing Mode'
        option3 = '3. Enter System Settings'
        option4 = '4. Quit Program'
        while True:
            try:
                print(f'\n{option1}\n{option2}\n{option3}\n{option4}')
                option = input("Please enter the number corresponding to required mode: ")
                option = int(option)
                if option < 1 or option > 4:
                    raise ValueError
                if option == 1:
                    polling_loop_main()
                elif option == 2:
                    time = []
                    for sec in range(0,21):
                        time.append(sec)                        #time for graphing, m,aking sure there are enough values
                    if len(wlMatrix) ==  21 and len(tempMatrix) ==  21 and len(LDRMatrix) == 21:
                        graphing_mode(time,wlMatrix,tempMatrix,LDRMatrix)
                    else:
                        polling_loop_main('graphing')           #goes to graphing
                        graphing_mode(time,wlMatrix,tempMatrix,LDRMatrix)
                elif option == 3:                               #can change settings and values
                    system_settings()
                elif option == 4:
                    myArduino.pwm_write(inPumpPin, 0)
                    myArduino.pwm_write(outPumpPin, 0)
                    myArduino.shutdown()
                    quit()
            except ValueError:
                print("Invalid Number Entered, Please Try Again")
            except KeyboardInterrupt:
                quit()
        

def graphing_mode(timeData, waterVolume,tempMatrix,LDRMatrix):
    '''
    graphing_mode allows the user to create plots

    Inputs: Either 1 or 2
    Return:  Print statements denoting options
    '''
    graphing_function(timeData,waterVolume,tempMatrix,LDRMatrix)
    option1 = '1. Redraw graph with new data' 
    option2 = '2. Exit to System Menu'
    while True:
        print(f'\n{option1}\n{option2}')
        option = input("Please enter the number corresponding to required option: ")
        try:
            option = int(option)
            if option < 1 or option > 2:
                    raise ValueError
            elif option == 1:
                time = []
                for sec in range(0,21):
                    time.append(sec)
                polling_loop_main('graphing')
                graphing_function(time,wlMatrix,tempMatrix,LDRMatrix)
                print("Close Graphs To Continue")
            elif option == 2:
                return
        except ValueError:
                print("Invalid Number Entered, Please Try Again")


def graphing_function(timeData, waterVolume,tempMatrix,LDRMatrix):
    '''
    graphing_function plots data from the last 20 seconds

    Inputs: Data from LDR, Ultrasonic sensor and Thermistor
    Return: Plots of sensor data for past 20 seconds
    '''
    plt.figure(3)
    plt.plot(timeData, LDRMatrix)
    plt.xlabel('Time (s)')
    plt.ylabel('LDR Sensor Readings')
    plt.title('LDR Sensor Readings in tank for the past 20 seconds.')
    plt.savefig('Light_vs_Time.png')

    plt.figure(2)
    plt.plot(timeData, tempMatrix)
    plt.xlabel('Time (s)')
    plt.ylabel('Temperature (C)')
    plt.title('Temperature (C) in tank for the past 20 seconds.')
    plt.savefig('Temperature_vs_Time.png')

    plt.figure(1)
    plt.plot(timeData, waterVolume)
    plt.xlabel('Time (s)')
    plt.ylabel('Water Volume (L)')
    plt.title('Water Volume (L) in tank for the past 20 seconds.')
    plt.savefig('Volume_vs_time.png')

    
    print('3 Figures are shown, each with a different graph')
    print("Close Graphs To Continue")
    plt.show()
    return


def system_settings():
    '''
    system_settings is used to edit the parameters used by the program

    Inputs: PIN, option selection, new value for parameter
    Return: Print statement asking for PIN, print statement listing parameter options, confirmation of new value
    '''
    global sleepTime
    global lowWaterVolumeMin
    global lowWaterVolumeMax
    global optimumWaterVolumeMax
    global highWaterVolumeMax
    global fullWaterVolumeMax
    global pin
    global tries
    global ldrVar
    global tempVar
    global dvdtMax
    global timeoutSystemSettings
    option1 = '1. Enter System Settings'
    option2 = '2. Return to System Menu'

    while True:
        print(f'\n{option1}\n{option2}')
        option = input("Please enter the number corresponding to required option: ")
        try:
            option = int(option)
            if option < 1 or option > 2:
                    raise ValueError
            elif option == 1:
                startSystemSettings = time.time()
                endSystemSettings = time.time()
                break
            elif option == 2:
                return
        except ValueError:
                print("Invalid Number Entered, Please Try Again")

    while True:
        inputPin = input("Please enter the 4 digit Pincode: ")
        try:
            inputPin = int(inputPin)
            if pin != inputPin:
                raise ValueError
            else:
                option3 = '1. Change the time the Polling Loop runs each time'
                option4 = '2. Change Near Empty Water Volume'
                option5 = '3. Change Low Water Volume Range'
                option6 = '4. Change Optimum Water Volume Range'
                option7 = '5. Change High Water Volume Range'
                option8 = '6. Change Near Full Water Volume'
                option9 = '7. Change System pin'
                option10 = '8. Change Optimum Light Level'
                option11 = '9. Change Optimum Temperature Level'
                option12 = '10. Change dV/dT Optimum'
                option13 = '11. Change System Settings Timeout'
                option14 = '12. Return to System Menu'
                while True:
                    print(f'\n{option3}\n{option4}\n{option5}\n{option6}\n{option7}\n{option8}\n{option9}\n{option10}\n{option11}\n{option12}\n{option13}\n{option14}')
                    option = input("Please enter the number corresponding to required option: ")
                    try:
                        option = int(option)
                        if option < 1 or option > 12:
                                raise ValueError
                        elif option == 1:
                            endSystemSettings = time.time()
                            if endSystemSettings - startSystemSettings > timeoutSystemSettings:
                                print('System Settings Timeout')
                                return
                            print(f"Current time the polling loop runs each time is {sleepTime}s")
                            while True:
                                newSleeptime = input("Enter New Polling Loop Time: ")
                                try:
                                    newSleeptime = int(newSleeptime)
                                    if newSleeptime < 2 or newSleeptime > 5:
                                        raise ValueError
                                    else:
                                        sleepTime = newSleeptime
                                        print(f'New time the polling loop runs each time is {sleepTime}s')
                                        break
                                except ValueError:
                                    print("Invalid Number entered. Enter a Positive Integer between 2 and 5.")
                        elif option == 2:
                            endSystemSettings = time.time()
                            if endSystemSettings - startSystemSettings > timeoutSystemSettings:
                                print('System Settings Timeout')
                                return
                            print(f"Current near empty water volume is {lowWaterVolumeMin}")
                            print("Enter q to quit")
                            while True:
                                newEmptyWaterLevel = input("Enter New Near Empty Water Volume: ")
                                try:
                                    if newEmptyWaterLevel == 'q':
                                        break
                                    newEmptyWaterLevel = int(newEmptyWaterLevel)
                                    if newEmptyWaterLevel <= 0 or newEmptyWaterLevel > lowWaterVolumeMax:
                                        raise ValueError
                                    else:
                                        lowWaterVolumeMin = newEmptyWaterLevel
                                        print(f'New Near Empty Water Volume is {lowWaterVolumeMin}')
                                        break
                                except ValueError:
                                    print(f"Invalid Number entered. Enter a Positive Integer that is less than {lowWaterVolumeMax}")
                        elif option == 3:
                            endSystemSettings = time.time()
                            if endSystemSettings - startSystemSettings > timeoutSystemSettings:
                                print('System Settings Timeout')
                                return
                            print(f"Current low water volume range is between {lowWaterVolumeMin} and {lowWaterVolumeMax}")
                            print("To change the lower bound range, please change it through Option 2. Enter q to exit.")
                            while True:
                                newValue = input("Enter New Upper Bound for Low Water Volume range: ")
                                try:
                                    if newValue == 'q':
                                        break
                                    newValue = int(newValue)
                                    if newValue < 0 or newValue > optimumWaterVolumeMax or newValue < lowWaterVolumeMin:
                                        raise ValueError
                                    else:
                                        lowWaterVolumeMax = newValue
                                        print(f'New Upper Bound for Low Water Volume range is {lowWaterVolumeMax}')
                                        break
                                except ValueError:
                                    print(f"Invalid Number entered. Enter a Positive Integer that greater than {lowWaterVolumeMin} and is less than {optimumWaterVolumeMax}")
                        elif option == 4:
                            endSystemSettings = time.time()
                            if endSystemSettings - startSystemSettings > timeoutSystemSettings:
                                print('System Settings Timeout')
                                return
                            print(f"Current optimum water volume range is between {lowWaterVolumeMax} and {optimumWaterVolumeMax}")
                            print("To change the lower bound range, please change it through Option 3. Enter q to exit.")
                            while True:
                                newValue = input("Enter New Upper Bound for Optimum Water Volume range: ")
                                try:
                                    if newValue == 'q':
                                        break
                                    newValue = int(newValue)
                                    if newValue <= 0 or newValue > highWaterVolumeMax or newValue < lowWaterVolumeMax:
                                        raise ValueError
                                    else:
                                        optimumWaterVolumeMax = newValue
                                        print(f'New Upper Bound for Optimum Water Volume range is {optimumWaterVolumeMax}')                                      
                                        break
                                except ValueError:
                                    print(f"Invalid Number entered. Enter a Positive Integer that is greater than {lowWaterVolumeMax} and less than {highWaterVolumeMax}")
                        elif option == 5:
                            endSystemSettings = time.time()
                            if endSystemSettings - startSystemSettings > timeoutSystemSettings:
                                print('System Settings Timeout')
                                return
                            print(f"Current high water volume range is between {optimumWaterVolumeMax} and {highWaterVolumeMax}")
                            print("To change the lower bound range, please change it through Option 4. Enter q to exit.")
                            while True:
                                newValue = input("Enter New Upper Bound for High Water Volume range: ")
                                try:
                                    if newValue == 'q':
                                        break
                                    newValue = int(newValue)
                                    if newValue <= 0 or newValue > fullWaterVolumeMax or newValue < optimumWaterVolumeMax:
                                        raise ValueError
                                    else:
                                        highWaterVolumeMax = newValue
                                        print(f'New Upper Bound for High Water Volume range is {highWaterVolumeMax}')                                        
                                        break
                                except ValueError:
                                    print(f"Invalid Number entered. Enter a Positive Integer that is greater than {optimumWaterVolumeMax} and less than {fullWaterVolumeMax}")
                        elif option == 6:
                            endSystemSettings = time.time()
                            if endSystemSettings - startSystemSettings > timeoutSystemSettings:
                                print('System Settings Timeout')
                                return
                            print(f"Current full water volume range is between {highWaterVolumeMax} and {fullWaterVolumeMax}")
                            print("To change the lower bound range, please change it through Option 5. Enter q to exit.")
                            while True:
                                newValue = input("Enter New Upper Bound for High Water Volume range: ")
                                try:
                                    if newValue == 'q':
                                        break
                                    newValue = int(newValue)
                                    if newValue < highWaterVolumeMax:
                                        raise ValueError
                                    else:
                                        fullWaterVolumeMax = newValue
                                        print(f'New Upper Bound for Full Water Volume range is {fullWaterVolumeMax}')                                       
                                        break
                                except ValueError:
                                    print(f"Invalid Number entered. Enter a Positive Integer that is greater than {highWaterVolumeMax}")
                                    break
                        elif option == 7:
                            endSystemSettings = time.time()
                            if endSystemSettings - startSystemSettings > timeoutSystemSettings:
                                print('System Settings Timeout')
                                return
                            print(f"Current system pin is {pin}")
                            print("Enter q to exit.")
                            while True:
                                newValue = input("Enter New 4 digit System Pin: ")
                                try:
                                    if newValue == 'q':
                                        break
                                    if len(newValue) != 4:
                                        raise ValueError
                                    newValue = int(newValue)
                                    if newValue < 0:
                                        raise ValueError
                                    pin = newValue
                                    print(f'The New System pin is {pin}')
                                    break
                                except ValueError:
                                    print(f"Invalid Pin entered. Enter a 4 digit positive pin.")
                        elif option == 8:
                            endSystemSettings = time.time()
                            if endSystemSettings - startSystemSettings > timeoutSystemSettings:
                                print('System Settings Timeout')
                                return
                            print(f"Current Optimum Light is {ldrVar}")
                            print("Enter q to exit.")
                            while True:
                                newValue = input("Enter New Optimum Light: ")
                                try:
                                    if newValue == 'q':
                                        break
                                    newValue = int(newValue)
                                    if newValue < 0:
                                        raise ValueError
                                    ldrVar = newValue
                                    print(f'The New Optimum Light is {ldrVar}')
                                    break
                                except ValueError:
                                    print(f"Invalid Optimum Light entered. Enter a positive number.")
                        elif option == 9:
                            endSystemSettings = time.time()
                            if endSystemSettings - startSystemSettings > timeoutSystemSettings:
                                print('System Settings Timeout')
                                return
                            print(f"Current Optimum Temperature is {tempVar}")
                            print("Enter q to exit.")
                            while True:
                                newValue = input("Enter New Optimum Temperature: ")
                                try:
                                    if newValue == 'q':
                                        break
                                    newValue = int(newValue)
                                    if newValue < 0:
                                        raise ValueError
                                    tempVar = newValue
                                    print(f'The New Optimum Temperature is {tempVar}')
                                    break
                                except ValueError:
                                    print(f"Invalid Optimum Temperature entered. Enter a positive number.")
                        elif option == 10:
                            endSystemSettings = time.time()
                            if endSystemSettings - startSystemSettings > timeoutSystemSettings:
                                print('System Settings Timeout')
                                return
                            print(f"Current dV/dT Max is {dvdtMax}")
                            print("Enter q to exit.")
                            while True:
                                newValue = input("Enter New dV/dT Max: ")
                                try:
                                    if newValue == 'q':
                                        break
                                    newValue = float(newValue)
                                    dvdtMax = newValue
                                    print(f'The New dV/dT Max is {dvdtMax}')
                                    break
                                except ValueError:
                                    print(f"Invalid Optimum Temperature entered. Enter a positive number.")
                        elif option == 11:
                            endSystemSettings = time.time()
                            if endSystemSettings - startSystemSettings > timeoutSystemSettings:
                                print('System Settings Timeout')
                                return
                            print(f"Current System Timout Value is {timeoutSystemSettings}")
                            print("Enter q to exit.")
                            while True:
                                newValue = input("Enter New System Timout Value: ")
                                try:
                                    if newValue == 'q':
                                        break
                                    newValue = int(newValue)
                                    if newValue < 0:
                                        raise ValueError
                                    timeoutSystemSettings = newValue
                                    print(f'The New System Timout Value is {timeoutSystemSettings}')
                                    break
                                except ValueError:
                                    print(f"Invalid System Timout Value entered. Enter a positive integer.")
                        elif option == 12:
                            return
                    except ValueError:
                            endSystemSettings = time.time()
                            if endSystemSettings - startSystemSettings > timeoutSystemSettings:
                                print('System Settings Timeout')
                                return
                            print("Invalid Number Entered, Please Try Again")
        
        except ValueError:
            tries += 1
            if tries < 3:
                print(f"Incorrect Pin. Please try again. You have {3-tries} attempts left!")
            else:
                tries = 0
                print("Too many Failed Attempts. Wait 2 minutes before attempting again.")
                time.sleep(120)


def gen_random_number(sensor):
    '''
    gen_random_number is used to generate random values for use by other functions
    
    Inputs: sensor type
    Return: random value in range determined by sensor type
    '''
    if sensor == 'depth':
        return random.randint(5,50)
    elif sensor == 'ldr' or sensor == 'temp':
        return random.randint(200,1023)

def polling_loop_main(callFrom = None):
    '''
    polling_loop_main calls other sensor polling loop functions every 2 seconds

    Inputs: Graphing stat
    Return: None
    '''
    global start
    global end
    if callFrom == 'graphing':
        print("Collecting Live Values from Polling Loop. Please wait 20 seconds.")
        for _ in range(0,21):
            water_volume()
            tank_temp()
            tank_light()
    else:
        print('Press Ctrl+C To Exit Loop')
        myArduino.digital_write(7, 1)
        while True:
            start = time.time()
            waterPrint = "\n"
            try:
                water = water_volume()              #calls ultrasonic sensor

                for elem in water:
                    waterPrint += f"{elem}, "       #prints the outputs from the water level each time
                print(waterPrint[0:-2])
                motor_setting(waterMovement)        #gets the motors to go to what they are specified depending on volume
                if dvdt > dvdtMax:                  #will run if waterlevel increases or decreases too quickly
                    p=0
                    print(f'Water Level is Changing Rapidly at {dvdt}L/s.')
                    while p < 3:                    #this flashes LED 3 times at 2hz
                        myArduino.digital_pin_write(LEDflash, 1)
                        time.sleep(0.25)
                        myArduino.digital_pin_write(LEDflash, 0)
                        time.sleep(0.25)
                        p=p+1

                tp = tank_temp()                    #calls thermistor

                if tp != None:
                    print(tp)
                
                light = tank_light()                #calls ldr

                if light != None:
                    print(light)

                end1 = time.time()
                if end1 - start > 5:
                    if myArduino.analog_read(inputPin)[0] < 10:         #556 timer reset, if value drops when capaciter discharges then it will reset
                        print('555 Timer Reset')
                        myArduino.send_reset()
                        break

                end = time.time()
                print(f'It took {round(end - start, 3)}s for the polling loop to complete this cycle.')

                myArduino.digital_write(7, 0)
                myArduino.digital_write(7, 1)       #resets timer
            except KeyboardInterrupt:
                myArduino.pwm_write(inPumpPin, 0)
                myArduino.pwm_write(outPumpPin, 0)
                break

def water_volume(waterData=None):
    '''
    water_volume function processes inputed data from the sensor, converts it to a volume level and then 
    presents it with outputs in graphs and pump usage

    Inputs: Ultrasonic sensor input, distance from water
    Return: Print statement of water level movement and the volume status of the tank, whether in need of changing
    '''
    global wli
    global wlMatrix
    global waterMovement
    global waterSum
    global dvdt
    waterSum=[]
    output =[]
    while len(waterSum) < 5:                                #gets average of values for more accurate level or reading
        waterData = myArduino.sonar_read(3)                 #reads value
        while True:
            try:
                waterData = float(waterData[0])             #gets first value which is cm distance
                break
            except:
                return 'Error in Water Data Sensor'         #this checks everything
        waterSum.append(waterData)
        time.sleep(0.2)

    waterSum = sum(waterSum)/5
    current_height = height-waterSum
    if current_height < 35.5:
        waterVolume = (lengthLower*widthLower*(height-waterSum))/1000
    else:
        waterVolume = (lengthLower*widthLower*(35.5))/1000 + (lengthUpper*widthUpper*(15-waterSum))
    
    wlMatrix.append(round(waterVolume,2))                   #adds to matrix for graphing and printing water level

    dvdt = abs((wlMatrix[int(len(wlMatrix)-1)]-wlMatrix[int(len(wlMatrix))-2])/(5))     #calculates how quick water level rises
    if len(wlMatrix) > 21:                                  #will make sure to remove data to allow for regraphing new data
        wlMatrix.remove(wlMatrix[0])
    index = len(wlMatrix) - 1
    if index == 0:
        wli = 1
        output = ['Initialised Water Level']
    elif wli != 1 and wlMatrix[index] == wlMatrix[index-1]:
        wli = 1                                                     #set variable so that know if need to print again
        output = ['Water level Steady compared to Previous Value']
    elif wlMatrix[index] > wlMatrix[index-1]:
        wli = 2
        output = ['Water level is Increasing compared to Previous Value']
    elif wlMatrix[index] < wlMatrix[index-1]:
        wli = 3
        output = ['Water level is Decreasing compared to Previous Value']
    else:
        pass
    
    if lowWaterVolumeMin <= waterVolume < lowWaterVolumeMax:
        # low
        output.append(f'Water Volume is {waterVolume}L currently. Low Water Level In Tank, Turn on Input Pump')
        waterMovement = 1

        myArduino.digital_write(red, 0)                 #if near empty or full
        myArduino.digital_pin_write(blue, 0)            #if overflowing
        myArduino.digital_write(yellow, 1)              #if low or high

        return output
    elif waterVolume < lowWaterVolumeMin:
        #near empty
        output.append(f'Water Volume is {round(waterVolume, 3)}L currently. Tank Near Empty, Turn on Input Pump')
        waterMovement = 0

        myArduino.digital_pin_write(blue, 0)
        myArduino.digital_write(yellow, 0)
        myArduino.digital_write(red, 1)
        
        return output
    elif lowWaterVolumeMax <= waterVolume <= optimumWaterVolumeMax:
        #safe working range
        output.append(f'Water Volume is {waterVolume}L currently. Optimum Water Level in Tank. Do Nothing')
        waterMovement = 2
        
        myArduino.digital_pin_write(blue, 0)
        myArduino.digital_write(yellow, 0)
        myArduino.digital_write(red, 0)

        return output
    elif optimumWaterVolumeMax < waterVolume < highWaterVolumeMax:
        #high
        output.append(f'Water Volume is {waterVolume}L currently. Water Level High in Tank. Turn on Output Tap')
        waterMovement = 3

        myArduino.digital_write(red, 0)
        myArduino.digital_pin_write(blue, 0)
        myArduino.digital_write(yellow, 1)

        return output
    elif highWaterVolumeMax <= waterVolume < fullWaterVolumeMax:
        #nearfull
        output.append(f'Water Volume is {waterVolume}L currently. Tank Near Full. Turn on Output Tap')

        myArduino.digital_pin_write(blue, 0)
        myArduino.digital_write(yellow, 0)
        myArduino.digital_write(red, 1)

        waterMovement = 4
        return output
    elif fullWaterVolumeMax <= waterVolume:
        #overfull
        output.append(f'Water Volume is {waterVolume}L currently. Tank is Overflowing. Turn on Output Tap')
        waterMovement = 4

        myArduino.digital_write(yellow, 0)
        myArduino.digital_write(red, 0)
        myArduino.digital_pin_write(blue, 1)

        return output
    
        
def tank_temp(tempData=None):
    '''
    tank_temp function processes inputed data from the sensor, converts it to a tempurature in degrees celcius

    Inputs: Thermistor resistance ratio
    Return: Print statement of tempurature movement
    '''
    global tpi
    global tempMatrix
    global temp
    tempData = myArduino.analog_read(thermPin)
    while True:
        if tempData == None:
            tempData = gen_random_number('temp')            #this is where pseudorandom numbers are
            break
        else:
            try:
                tempData = float(tempData[0])
                break
            except ValueError:
                return 'Error in Temperature Sensor'                               #this checks everything
    r2 = r1*(vin/tempData - 1)
    temp = 1/(a+b*math.log(r2)+c*(math.log(r2))**3) - 273.15 - 5                   #calculates tempurature
    tempMatrix.append(temp)
    if temp > tempVar:                                                             #makes sure variation is not too high, this will allert user if too high
        print("WARNING! TEMPURATURE TOO HIGH")
    if len(tempMatrix) > 21:                                                       #will make sure to remove data to allow for regraphing new data
        tempMatrix.remove(tempMatrix[0])
    index = len(tempMatrix) - 1
    if index == 0:
        tpi = 1
        return 'Default Tempurature Initialised'
    elif tpi != 1 and tempMatrix[index] == tempMatrix[index-1]:
        tpi = 1                                             #set variable so that know if need to print again
        return 'Tempurature is Steady'
    elif tempMatrix[index] > tempMatrix[index-1]:
        tpi = 2
        return 'Tempurature is Increasing'
    elif tempMatrix[index] < tempMatrix[index-1]:
        tpi = 3
        return 'Tempurature is Decreasing'
    else:
        return

def tank_light(LDRData=None):
    '''
    temp_light function processes inputed data from the sensor, presents as a ratio of light

    Inputs: Light Dependent Resistance ratio
    Return: Print statement of light input movement
    '''
    global lri
    global LDRMatrix
    global ldrVar
    LDRData = myArduino.analog_read(ldrPin)
    while True:
        if LDRData == None:
            LDRData = gen_random_number('ldr')           #this is where pseudorandom numbers are
            break
        else:
            try:
                LDRData = float(LDRData[0])
                break
            except ValueError:
                assert False,'Invalid LDR Data'
    if LDRData > ldrVar + 20 or LDRData < ldrVar - 20:   #makes sure variation is not too high, this will allert user if too high
        print("WARNING! LIGHT LEVEL NOT NORMAL")
    LDRMatrix.append(LDRData)
    if len(LDRMatrix) > 21:
        LDRMatrix.remove(LDRMatrix[0])
    index = len(LDRMatrix) - 1
    if index == 0:
        lri = 1
        return "Initialised Light Levels"
    elif lri != 1 and LDRMatrix[index] == LDRMatrix[index-1]:
        lri = 1                             #set variable so that know if need to print again
        return 'Light Level is Steady'
    elif LDRMatrix[index] < LDRMatrix[index-1]:
        lri = 2
        return 'Light Level is Decreasing'
    elif LDRMatrix[index] > LDRMatrix[index-1]:
        lri = 3
        return 'Light Level is Increasing'
    else:
        return

def print_seven_seg_display(input):
    '''
    This function prints the input string onto the seven-seg-display
    This method is NOT user-facing.

    Inputs: Input string containing only alphabetical characters. The length of the string must be 4 and only 4.
    Outputs: None - Message is printed on seven-seg-display
    '''
    input = input.upper()
    start = time.time()
    while True:
        n = -1
        for j in range(4):
            for k in range(7):
                #Pushing 1 or 0 to shift register according to dictionary of characters
                if characters[input[j]][k] == '1':
                    myArduino.digital_write(9, 1)
                else:
                    myArduino.digital_write(9, 0)
                
                myArduino.digital_write(8, 1)
                myArduino.digital_write(8, 0)
            
            myArduino.digital_write(8, 1)
            myArduino.digital_write(8, 0)

            myArduino.digital_write(dPins[n], 0)
            time.sleep(0.005) 
            myArduino.digital_write(dPins[n], 1)
            n -= 1
            time.sleep(0.0001)

        end = time.time()
        if end - start > sleepTime:
            break
    
def motor_setting(waterMovement):
    if waterMovement == 0:
        myArduino.pwm_write(outPumpPin,0)
        myArduino.pwm_write(inPumpPin, 200)             #high speed to get rid of water
        print_seven_seg_display('llih')                 #will mean level low input high

    elif waterMovement == 1:
        myArduino.pwm_write(outPumpPin,0)
        myArduino.pwm_write(inPumpPin, 75)              #low speed to get rid of water
        print_seven_seg_display('llil')                 #will mean level low input low
        
    elif waterMovement == 2:
        myArduino.pwm_write(inPumpPin,0)
        myArduino.pwm_write(outPumpPin,0)
        print_seven_seg_display('lsao')                 #will mean level safe all off

    elif waterMovement == 3:
        myArduino.pwm_write(inPumpPin,0)
        myArduino.pwm_write(outPumpPin, 75)
        print_seven_seg_display('lhol')                 #will mean level high output low

    elif waterMovement == 4:
        myArduino.pwm_write(inPumpPin,0)
        myArduino.pwm_write(outPumpPin, 200)
        print_seven_seg_display('lhoh')                 #will mean level high output high                 

#Run Program              
system_menu()