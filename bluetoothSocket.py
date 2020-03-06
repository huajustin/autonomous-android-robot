# from https://circuitdigest.com/microcontroller-projects/controlling-raspberry-pi-gpio-using-android-app-over-bluetooth
import bluetooth
#import motorFunctions
 
server_socket=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
uuid = "bbcc40a1-adae-41d7-a13f-676f427c9c41"
 
port = 1
server_socket.bind(("",port))
server_socket.listen(1)

advertise_service( server_socket, "Bluetooth Server", service_id = uuid, 
                service_classes = [ uuid, bluetooth.SERIAL_PORT_CLASS ],profiles = [ bluetooth.SERIAL_PORT_PROFILE ]
                )
print("Currently looking for connections...")
client_socket,address = server_socket.accept()
print("Accepted connection from %s" %(address))
while 1: 
    data = client_socket.recv(1024)
    print(data)
    break
 
client_socket.close()
server_socket.close()

