# from https://circuitdigest.com/microcontroller-projects/controlling-raspberry-pi-gpio-using-android-app-over-bluetooth
import bluetooth
#import motorFunctions
 
# get server socket and set UUID and port number
server_socket=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
uuid = "bbcc40a1-adae-41d7-a13f-676f427c9c41"
port = 10

# set up the server socket and listen in on the connection
server_socket.bind(("",port))
server_socket.listen(1)
bluetooth.advertise_service( server_socket, "Bluetooth Server", service_id = uuid, 
                service_classes = [ uuid, bluetooth.SERIAL_PORT_CLASS ],profiles = [ bluetooth.SERIAL_PORT_PROFILE ]
                )
print("Currently looking for connections...")

# blocking call, waits until a client connects to the socket
client_socket,address = server_socket.accept()
print("Accepted connection from {}".format(address))

# loop to receive communication from client
while 1: 
    data = client_socket.recv(1024)
    print(data)
    # if client sends an exit signal, then break this loop
    if (data == b'\x00'):
        break
    # if client unexpectedly disconnects, also break
    if not data:
        break
 

# close sockets
print("Client disconnected. Now quitting...")
client_socket.close()
server_socket.close()

