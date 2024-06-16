from app import app

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 8000, app)
    httpd.serve_forever()