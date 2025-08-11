import socket

ENTRIES = [ 'Guest1 was here' ]

def do_request(method, url, headers, body):
    out = "<!doctype html>"
    for entry in ENTRIES:
        out += "<p>" + entry + "</p>"
    return "200 OK", out

def handle_connection(conx):   
    # Reading request line
    req = conx.makefile("b")
    reqline = req.readline().decode('utf8')
    method, url, version = reqline.split(" ", 2)
    assert method in ["GET", "POST"]

    # Reading headers
    headers = {}
    while True:
        line = req.readline().decode('utf8')
        if line == '\r\n': break
        header, value = line.split(":", 1)
        headers[header.casefold()] = value.strip()

    # Reading the body (only when Content-Length header tells us how much to read)
    if 'content-length' in headers:
        length = int(headers['content-length'])
        body = req.read(length).decode('utf8')
    else:
        body = None
    
    # Server needs to generate a web page in response. 
    status, body = do_request(method, url, headers, body)

    # Server sends this page back to browser
    response = "HTTP/1.0 {}\r\n".format(status)
    response += "Content-Length: {}\r\n".format(
        len(body.encode("utf8")))
    response += "\r\n" + body
    conx.send(response.encode('utf8'))
    conx.close() 

if __name__ == "__main__":
    s = socket.socket(
        family=socket.AF_INET,
        type= socket.SOCK_STREAM,
        proto = socket.IPPROTO_TCP
    )
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 8000))
    s.listen()

    while True:
        conx, addr = s.accept()
        handle_connection(conx)

"""
setsockopt is optional. 
    if program has open socket and crashes, os temporary bans reusing the port for a while
    calling setsockopt with SO_REUSEADDR allows OS to immediately reuse the port

bind
    First argument - who is allowed to make connections "to" to server
    Empty string -> anyone can connect

    Second argument is the port otherrs must use to talk to our server
    all ports below 1024 require admin privileges

listen
    tells OS we're ready to accept conenctions

while 
    loop runs once per connection
    conx is both connection object, and socket corresponding to that one connection

    we read the contents and parse the HTTP message, 
    but server cant read from socket until connection is closed,
    browser is waiting for server and won't close connection. hence handle_connection reads from socket.
"""