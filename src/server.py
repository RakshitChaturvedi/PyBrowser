import socket
import urllib.parse

def handle_connection(conx):   
    # Reading request line
    req = conx.makefile("b")
    reqline = req.readline().decode('utf8')
    if not reqline or reqline.isspace():
        conx.close()
        return
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

# Figure out which function to call for which request
def do_request(method, url, headers, body):
    if method == "GET" and url == "/":
        return "200 OK", show_comments()
    elif method == "POST" and url == "/add":
        params = form_decode(body)
        return "200 OK", add_entry(params)
    else:
        return "404 Not Found", not_found(url, method)

# Decode the request body
def form_decode(body):
    params = {}
    for field in body.split("&"):
        name, value = field.split("=", 1)
        name = urllib.parse.unquote_plus(name)      # unquote plus handles both "name" and +name+ because
        value = urllib.parse.unquote_plus(value)    # browsers also use plus sign to encode space
        params[name] = value
    return params

ENTRIES = [ 'Guest1 was here' ]

# Handle regular browsing
def show_comments():
    out = "<!doctype html>"
    out += "<form action=add method=post>"
    out += "<p><input name=guest></p>"
    out += "<p><button>Sign the book!</button></p>"
    out += "</form>"
    for entry in ENTRIES:
        out+= "<p>" + entry + "</p>"
    return out

# For page not found
def not_found(url, method):
    out = "<!doctype html>"
    out += "<h1>{} {} not found!</h1>".format(method, url)
    return out

# Looks up the guest parameter and adds its content as new guest book entry
def add_entry(params):
    if 'guest' in params:
        ENTRIES.append(params['guest'])
    return show_comments()

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