import motorFunctions as Motor
from gpiozero import MCP3008

mic = MCP3008(0)

try:
    while True:
        micValue = mic.value 

        if (1 / micValue <= 0.2):
            Motor.stop()
        else:
            Motor.moveForward(1 / micValue)

except KeyboardInterrupt:
    print("Stopping...")
        
