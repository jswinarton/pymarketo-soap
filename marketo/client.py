from datetime import datetime
import hmac
import hashlib

from suds.client import Client as SudsClient


DEFAULT_WSDL = 'http://app.marketo.com/soap/mktows/2_1?WSDL'
DEFAULT_TIMEOUT = 15


class Client(object):
    '''
    Instantiates a suds client with default parameters. Can be used as a
    base client (no auth) to create Marketo factory objects.
    '''

    def __init__(self, *args, **kwargs):
        self.wsdl = kwargs.get('wsdl', DEFAULT_WSDL)
        self.timeout = kwargs.get('timeout', DEFAULT_TIMEOUT)
        self.suds_client = SudsClient(
            url=self.wsdl,
            timeout=self.timeout
        )

    def auth(self, user_id, location, encryption_key):
        auth = self.create('AuthenticationHeaderInfo')
        auth.mktowsUserId = user_id
        auth.requestTimestamp = datetime.now().isoformat()
        auth.requestSignature = hmac.new(
            encryption_key,
            auth.requestTimestamp + user_id,
            hashlib.sha1
        ).hexdigest().lower()
        self.suds_client.set_options(location=location, soapheaders=auth)
        return self

    def create(self, *args, **kwargs):
        return self.suds_client.factory.create(*args, **kwargs)

    def get_lead(self, lead_key):
        return self.suds_client.service.getLead(lead_key._to_soap())

    def request_campaign(self, campaign_id, leads):
        return self.suds_client.service.requestCampaign('MKTOWS', str(campaign_id), leads._to_soap())

    def sync_lead(self, lead, return_lead=False):
        return self.suds_client.service.syncLead(
            lead._to_soap(),
            return_lead,
            lead.get('cookie')
        )
