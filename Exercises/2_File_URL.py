# To read files (text files) present in the local computer with the url file:///path/to/file.txt

import socket
import ssl

class URL:
    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https", "file"]

        if self.scheme == "file":
            self.host = None
            self.port = None
            self.path = url.lstrip("/")
        
        else:
            if "/" not in url:
                url = url + "/"
            self.host, url = url.split("/", 1)
            self.path = "/" + url

            if self.scheme == "http":
                self.port = 80
            elif self.scheme == "https":
                self.port = 443

            if ":" in self.host:
                self.host, port = self.host.split(":", 1)
                self.port = int(port)
    
    # Creating a socket (Request and Response)
    def request(self):
        if self.scheme == "file":
            with open(self.path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            s = socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM,
                proto=socket.IPPROTO_TCP,
            )
            s.connect((self.host, self.port))

            if self.scheme == "https":
                ctx = ssl.create_default_context()
                s = ctx.wrap_socket(s, server_hostname=self.host)
            
            headers = {
                "Host": self.host,
                "Connection": "close",
                "User-Agent": "MyBrowser",
            }

            # Sending the Request
            request = "GET {} HTTP/1.1\r\n".format(self.path) # \r\n: \r means go to the start of current line, \n means go to the next line.
            for header, value in headers.items():
                request += f"{header}: {value}\r\n" 
            request += "\r\n" # add blank line at end of request, if not, the other computer keeps waiting.
            s.send(request.encode("utf8"))

            # Recieving the Response
            response = s.makefile("r", encoding="utf8", newline="\r\n") # makefile returns file-like obj containing every byte we recieve from server

            statusline = response.readline()
            version, status, explanation = statusline.split(" ", 2)

            response_headers = {}
            while True:
                line = response.readline()
                if line == "\r\n": break
                header, value = line.split(":", 1)
                response_headers[header.casefold()] = value.strip()

            assert "transfer-encoding" not in response_headers
            assert "content-encoding" not in response_headers

            content = response.read() # Everything after the headers
            s.close()

            return content
    
def show(body):
    if "<html" in body.lower():
        in_tag = False
        for c in body:
            if c == "<":
                in_tag=True
            elif c == ">":
                in_tag=False
            elif not in_tag:
                print(c, end="")
    else:
        print(body)
def load(url):
    body = url.request()
    show(body)

if __name__ == "__main__":
    import sys
    load(URL(sys.argv[1]))