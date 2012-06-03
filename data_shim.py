from google.appengine.ext import db
from google.appengine.api import urlfetch

import logging
logging.getLogger().setLevel(logging.DEBUG)
#using "print" and "logging" so that output shows up on the web console with;
#       http://localhost:8080/_ah/admin/interactive?debug

import datetime

class Agency(db.Model):
    """Models an individual Agency entry."""
    acronym = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    homepage = db.StringProperty(required=True)

    digitalurl_status = db.StringProperty(required=True, default="unknown", choices=set(["available", "unknown", "doubtful"]))
    developerurl_status = db.StringProperty(required=True, default="unknown", choices=set(["available", "unknown", "doubtful"]))
    
    last_checked = db.DateTimeProperty() #set with datetime.datetime.now().date()

def create_agencies():
    agencies_info = [
        ("DOAG", "http://www.usda.gov", "Department of Agriculture"),
        ("DOC", "http://www.commerce.gov", "Department of Commerce"),
        ("DOD", "http://www.defense.gov", "Department of Defense"),
        ("DOED", "http://www.ed.gov", "Department of Education"),
        ("DOE", "http://www.energy.gov", "Department of Energy"),
        ("HHS", "http://www.hhs.gov", "Department of Health and Human Services"),
        ("DHS", "http://www.dhs.gov", "Department of Homeland Security"),
        ("HUD", "http://www.hud.gov", "Department of Housing and Urban Development"),
        ("DOJ", "http://www.justice.gov", "Department of Justice"),
        ("DOL", "http://www.dol.gov", "Department of Labor"),
        ("DOS", "http://www.state.gov", "Department of State"),
        ("DOT", "http://www.dot.gov", "Department of Transportation"),
        ("VA", "http://www.va.gov", "Department of Veterans Affairs"),
        ("DOI", "http://www.doi.gov", "Department of Interior"),
        ("DOT", "http://www.treasury.gov", "Department of Treasury"),
        ("EPA", "http://www.epa.gov", "Environmental Protection Agency"),
        ("GSA", "http://www.gsa.gov", "General Services Administration"),
        ("NASA", "http://www.nasa.gov", "National Aeronautics and Space Administration"),
        ("NSF", "http://www.nsf.gov", "National Science Foundation"),
        ("NRC", "http://www.nrc.gov", "Nuclear Regulatory Commission"),
        ("OPM", "http://www.opm.gov", "Office of Personnel Management"),
        ("SBA", "http://www.sba.gov", "Small Business Administration"),
        ("SSA", "http://www.ssa.gov", "Social Security Administration"),
        ("USAID", "http://www.usaid.gov", "U.S. Agency for International Development")
    ]

    agencies = []
    for agency in agencies_info:
        a = Agency(acronym=agency[0], name=agency[2], homepage=agency[1])
        agencies.append(a)

    db.put(agencies)

def delete_agencies():
    agencies = Agency.all()
    if agencies.count() > 0:
        map(lambda x: x.delete(), agencies)

def update_agencies(request = None, *args, **kwargs):

    agencies = Agency.all()
    if agencies.count() <= 0:
        logging.debug("Updating Agencies, loading first")
        print ("Updating Agencies, loading first")
        create_agencies()
        agencies = Agency.all()

    for agency in agencies:
        agency.last_checked = datetime.datetime.now()

        for url in ["%s%s" % (agency.homepage,"/digitalstrategy"), "%s%s" % (agency.homepage,"/developer")]:
            logging.debug("Checking: %s" % (url))
            print ("Checking: %s" % (url))
            try:
                result = urlfetch.fetch(url, deadline=5, allow_truncated=True)
                        #, follow_redirects=False) -- varrient behavior causes problems
                logging.debug("\t Resp. Status Code: %s" % (result.status_code))
                print ("\t Resp. Status Code: %s" % (result.status_code))
            except:
                logging.debug("\tException thrown during fetch")
                print ("\tException thrown during fetch")
                if "/digitalstrategy" in url: agency.digitalurl_status = "unknown"
                elif "/developer" in url: agency.developerurl_status = "unknown"
                else: logging.error("Unknown URL1: %s" % (url))
                agency.put()
                continue

            if result.status_code == 200: #unfortunately an unfound page w/ a 302 redirect causes us to end up here w/ a 200 (i.e. we can't see the chain from google's fetch
                if "/digitalstrategy" in url: agency.digitalurl_status = "available"
                elif "/developer" in url: agency.developerurl_status = "available"
                else: logging.error("Unknown URL2: %s" % (url))
            else:
                if "/digitalstrategy" in url: agency.digitalurl_status = "doubtful"
                elif "/developer" in url: agency.developerurl_status = "doubtful"
                else: logging.error("Unknown URL3: %s" % (url))

        agency.put()
