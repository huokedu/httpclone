httpclone
=========

httpclone is a simple HTTP request proxy that forwards HTTP requests to other web servers.

Usage example:

    ./httpclone.py -p 8080 -f 127.0.0.1:8001 -f 127.0.0.1:8002 -c 127.0.0.1:8003

This will execute an HTTP web server on port 8080, which forwards requests to both port 8001 and 8002 (at least one forward rule is required), and will reply with the first server to respond successfully. It will clone traffic to port 8003 and completely disregard the output.

httpclone will respond with the first successful HTTP request (non-5xx server error) it receives. If no successful responses are received, it will return the last server error it receives.

### TODOs:

* HTTP header forwarding
* Statistics
* HTTPS support