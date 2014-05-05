from client import Client
from datastructures import MarketoLead
from datastructures import MarketoLeadKey
from datastructures import MarketoLeadKeyList


class MarketoConnection(object):

    def __init__(self, user_id, location, encryption_key):
        self.client = Client().auth(user_id, location, encryption_key)

    def new_lead(self, **kwargs):
        lead = MarketoLead(**kwargs)
        lead.connection = self
        return lead

    def pull_lead(self, **kwargs):
        lead = MarketoLead(**kwargs)
        lead.connection = self
        return lead.pull()

    def get_lead_activity(self):
        pass

    def push_lead(self, lead):
        return lead.push()

    def request_campaign(self, campaign_id, leads):
        if isinstance(leads, MarketoLeadKey):
            leads = MarketoLeadKeyList(leads)

        return self.client.request_campaign(campaign_id, leads)
