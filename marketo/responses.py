class ResponsePullLead(MarketoDictBase):
    pass


class ResponseSyncLead(MarketoDictBase):
    _mkto_type = 'ResultSyncLead'

    def _from_soap(self, obj):
        super(ResponseSyncLead, self)._from_soap(obj)
        pass


class ResponseRequestCampaign(object):
    pass
