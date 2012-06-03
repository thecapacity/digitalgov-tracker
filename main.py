import webapp2
import logging
logging.getLogger().setLevel(logging.DEBUG)

import os
from google.appengine.ext.webapp import template

from data_shim import *

class MainHandler(webapp2.RequestHandler):
    def get(self):
        agencies = Agency.all().order("name")
        template_values = {'agency_list': agencies}

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

app = webapp2.WSGIApplication([
            ('/tasks/update', update_agencies),
            ('/', MainHandler)
        ], debug=True)
