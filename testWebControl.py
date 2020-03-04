import RPi.GPIO as GPIO
import os
from time import sleep
from http.server import BaseHTTPRequestHandler, HTTPServer
import motorFunctions


host_name = '137.82.226.231'    # Change this to Raspberry Pi IP address
host_port = 8000


class MyServer(BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _redirect(self, path):
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', path)
        self.end_headers()

    def do_GET(self):
        #generate the html web with four buttons to control the robot to move forward, backward, left and right
        html = '''
            <html>
            <body style="width:960px; margin: 20px auto;">
            <h1>CPEN291 Project 1 Raspberry Pi web robot control</h1>
            <p>Current temperature is {}</p>
            <form action="/" method="POST">
                Robot control: <br />
                <input type="submit" name="submit" value="Forward"> <br />
                <input type="submit" name="submit" value="Left">
                <input type="submit" name="submit" value="Right"><br />
                <input type="submit" name="submit" value="Backward"> 
            </form>
            </body>
            </html>
        '''
        temp = os.popen("/opt/vc/bin/vcgencmd measure_temp").read()
        self.do_HEAD()
        self.wfile.write(html.format(temp[5:]).encode("utf-8"))

    def do_POST(self):
        #we get the request from the user
        #call the specific function in motor functions to handle the request
        content_length = int(self.headers['Content-Length'])    # Get the size of data
        post_data = self.rfile.read(content_length).decode("utf-8")   # Get the data
        post_data = post_data.split("=")[1]    # Only keep the value

        if post_data == 'Forward':
            motorFunctions.moveForward(1)
            print("car is moving forward")
        elif post_data == 'Backward':
            motorFunctions.moveBackward(1)
            print("car is moving backward")
        if post_data =='Left':
            motorFunctions.rotateLeft()
            print("car is rotating left")
        elif post_data == 'Right':
            motorFunctions.rotateRight()
            print("car is rotating right")
        
        self._redirect('/')    # finished handling request, redirect back to the root url


# setup the server
http_server = HTTPServer((host_name, host_port), MyServer)
print("server open")
try:
    #handle request until the controller exit the web
    http_server.serve_forever()
except KeyboardInterrupt:
    print("server exception")
    http_server.server_close()