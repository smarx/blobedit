import tornado.ioloop
import tornado.web
import tornado.escape
import sys
import argparse
from winazurestorage import *

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        if not self.get_cookie("AccountName") or not self.get_cookie("AccountKey") or not self.get_cookie("ContainerName"):
            self.redirect("/login")
            return
        self.set_header("Cache-Control", "no-cache")
        blob_storage = BlobStorage(host = CLOUD_BLOB_HOST, account_name = self.get_cookie("AccountName"), secret_key = self.get_cookie("AccountKey"))
        blobs = [x[0] for x in blob_storage.list_blobs(self.get_cookie("ContainerName"))]
        self.render("index.html", blobs=blobs, account_name=self.get_cookie("AccountName"), container_name=self.get_cookie("ContainerName"))

class BlobHandler(tornado.web.RequestHandler):
    def get(self, blobname):
        self.set_header("Content-Type", "text/plain")
        self.set_header("Cache-Control", "no-cache")
        self.write(BlobStorage(host = CLOUD_BLOB_HOST, account_name = self.get_cookie("AccountName"), secret_key = self.get_cookie("AccountKey")).get_blob(self.get_cookie("ContainerName"), blobname))
    def post(self, blobname):
        BlobStorage(host = CLOUD_BLOB_HOST, account_name = self.get_cookie("AccountName"), secret_key = self.get_cookie("AccountKey")).put_blob(self.get_cookie("ContainerName"), blobname, self.request.body, "text/plain")

class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("login.html")
    def post(self):
        self.set_cookie("AccountName", self.get_argument("AccountName"))
        self.set_cookie("AccountKey", self.get_argument("AccountKey"))
        self.set_cookie("ContainerName", self.get_argument("ContainerName"))
        self.redirect("/")

class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.clear_cookie("AccountName")
        self.clear_cookie("AccountKey")
        self.clear_cookie("ContainerName")
        self.redirect("/")
        
settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
}
application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/blob/(.*)", BlobHandler),
    (r"/login", LoginHandler),
    (r"/logout", LogoutHandler),
], **settings)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-p', '--port', dest='port', type=int, action='store', default=8080, help='port to listen on (default: 8080)')
    args = parser.parse_known_args()[0]
    application.listen(args.port)
    tornado.ioloop.IOLoop.instance().start()