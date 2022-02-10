#!/usr/bin/env python3
# coding: utf-8
# Copyright 2022 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, Nathan Tang
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
# you may use urllib to encode data appropriately
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    # def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data.split()[1])

    def get_headers(self, data):
        return data.split('\r\n')[:-1]

    def get_body(self, data):
        return data.split('\r\n')[-1]

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def parse_url(self, url):
        '''
        Parse the url and return the hostname, port, and path

        Parameters
        ---
        url : str
            URL to be parsed

        Returns
        ---
        host : str
            The URL hostname
        port : int
            The URL port
        path : str
            The URL path
        '''
        parse_result = urllib.parse.urlparse(url)
        # Get the parsed path, and add query and fragment if they exist
        if parse_result.path:
            path = f"{parse_result.path}"
            if parse_result.query:
                path += f"?{parse_result.query}"
            if parse_result.fragment:
                path += f"#{parse_result.fragment}"
        else:
            path = "/"

        # If port is parsed, use parsed port. Else use 80 if HTTP and 443 if HTTPS
        if parse_result.port:
            port = parse_result.port
        elif parse_result.scheme == "http":
            port = 80
        elif parse_result.scheme == "https":
            port = 443

        host = parse_result.hostname

        return host, port, path

    def send_request(self, host, port, request):
        '''
        Send the request to the host and port

        Parameters
        ---
        host : str
            URL hostname
        port : int
            URL port
        request : str
            HTTP request string

        Returns
        ---
        code : int
            HTTP code
        body : str
            HTTP response
        '''
        # Send the HTTP request using socket and get data back
        self.connect(host, port)
        self.sendall(request)
        data = self.recvall(self.socket)
        self.close()

        # Parse the HTTP code and body from the response
        code = self.get_code(data)
        body = self.get_body(data)

        return code, body

    def GET(self, url, args=None):
        host, port, path = self.parse_url(url)

        # Build HTTP GET request
        request = f"GET {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += "User-Agent: nathanlytang/0.1\r\n"
        request += "Accept: */*\r\n"
        request += "Connection: close\r\n\r\n"
        code, body = self.send_request(host, port, request)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port, path = self.parse_url(url)

        # Add POST arguments to the request if they exist
        if args:
            args = urllib.parse.urlencode(args)
            request_content = "Content=Type: application/x-www-urlencoded\r\n"
            request_content += f"Content-Length: {len(args.encode('utf-8'))}\r\n"
        else:
            args = ""
            request_content = "Content-Length: 0\r\n"

        # Build HTTP POST request
        request = f"POST {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += "User-Agent: nathanlytang/0.1\r\n"
        request += "Accept: */*\r\n"
        request += request_content
        request += "Connection: close\r\n\r\n"
        request += args
        code, body = self.send_request(host, port, request)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
