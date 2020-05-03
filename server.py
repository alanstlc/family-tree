import os

import tornado.ioloop
import tornado.web

from family_tree import run

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("template.html",
                    input_data=[],
                    message="")

    def post(self):
        print('muhehehe')
        input_data = self.get_argument("input_data")
        #self.render("template.html",
        #input_data=input_data,
        success, message = run(input_data)
        if success:
            with open('output.png.pdf', 'rb') as f:
               while True:
                  data = f.read()
                  if not data:
                     break
                  self.set_header("Content-Type", 'application/pdf; charset="utf-8"')
                  self.set_header("Content-Disposition", "attachment; filename=family-tree.pdf")
                  self.write(data)
            self.finish()
        else:
            self.render("template.html",
                        input_data=input_data,
                        message=message)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler)],
        template_path=os.path.dirname(__file__)
    )

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
