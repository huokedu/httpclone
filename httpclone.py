#!/usr/bin/env python

import argparse
import tornado
import tornado.httpclient
import tornado.ioloop
import tornado.web
from tornado.httpclient import HTTPRequest, HTTPError


parser = argparse.ArgumentParser(description='Start an HTTP server that clones (proxies) HTTP requests to other web servers')

parser.add_argument('-b', '--bind', help='Bind address', default='0.0.0.0')
parser.add_argument('-p', '--port', help='Port to listen to', default=8080, type=int)
parser.add_argument('-f', '--forward', help='Forward traffic to (host:port)', action='append', required=True)
parser.add_argument('-c', '--clone', help='Clone traffic to (host:port) disregarding output', action='append')

args = parser.parse_args()

client = tornado.httpclient.AsyncHTTPClient()
hosts = args.forward


class ForwardHandler(tornado.web.RequestHandler):
    def get_requests(self, method, hosts):
        requests = []
        for host in hosts:
            url = 'http://%s%s' % (host, self.request.path)
            if method in ["POST", "PUT"]:
                req = HTTPRequest(url, method=method, body=self.request.body)
            else:
                req = HTTPRequest(url, method=method)

            requests.append(req)

        return requests

    def forward(self, method):
        self.replied = 0
        self.replied_ok = False
        for req in self.get_requests(method, args.forward):
            client.fetch(req, self.handle_response)
        for req in self.get_requests(method, args.clone):
            client.fetch(req)

    def handle_response(self, response):
        if self.replied_ok:
            return

        self.replied += 1

        # check if we got a non-HTTP error or a connection refused error
        if response.error and type(response.error) != HTTPError or \
           response.error and type(response.error) == HTTPError and response.code == 599:
            if self.replied == len(args.forward):
                self.write(response.error.message)
                self.set_status(500)
                self.finish()
            return

        self.set_status(response.code)
        if response.body:
            self.write(response.body)
        else:
            self.write(response.error.message)

        self.replied_ok = True

        self.finish()

    @tornado.web.asynchronous
    def get(self):
        self.forward('GET')

    @tornado.web.asynchronous
    def post(self):
        self.forward('POST')

    @tornado.web.asynchronous
    def put(self):
        self.forward('PUT')

    @tornado.web.asynchronous
    def delete(self):
        self.forward('DELETE')

    @tornado.web.asynchronous
    def options(self):
        self.forward('OPTIONS')

    @tornado.web.asynchronous
    def head(self):
        self.forward('HEAD')



application = tornado.web.Application([
    (r'/.*', ForwardHandler),
])


# I have used synchronous one (you can use async one with callback)


if __name__ == '__main__':
    application.listen(args.port, address=args.bind)
    tornado.ioloop.IOLoop.instance().start()

