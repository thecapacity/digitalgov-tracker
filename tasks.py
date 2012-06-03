import webapp2
import logging
logging.getLogger().setLevel(logging.DEBUG)

from data_shim import *

app = webapp2.WSGIApplication([
            ('/tasks/update', update_agencies),
        ], debug=True)
