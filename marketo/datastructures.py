import collections
import json

from suds import WebFault

from client import Client
from exceptions import MarketoFault
from mixins import IterableMethodMixin


BARE_CLIENT = Client()


class SoapBase(object):
    _mkto_type = None
    connection = None

    @property
    def _soap_obj(self):
        if not self._mkto_type:
            raise TypeError('_mkto_type is not defined')

        return BARE_CLIENT.create(self._mkto_type)

    def _from_soap(self, obj):
        if obj.__class__.__name__ != self._mkto_type:
            raise TypeError('{} cannot be parsed into {}'.format(
                obj, self.__class__.__name__
            ))

    def _validate(self):
        pass

    def json(self):
        raise NotImplementedError


class MarketoKeyBase(SoapBase):
    @property
    def data(self):
        return (self.key_name, self.key_value)

    def __init__(self, key_name=None, key_value=None):
        self.key_name = key_name
        self.key_value = key_value

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return self.__str__()

    def json(self):
        return json.dumps(self.data)


class MarketoListBase(IterableMethodMixin, collections.MutableSequence, SoapBase):
    def __init__(self, *args):
        self._store = list()
        self.extend(args)

    def __contains__(self, key):
        return key in self._store

    def insert(self, key, value):
        self._store.insert(key, value)


class MarketoDictBase(IterableMethodMixin, collections.MutableMapping, SoapBase):
    def __init__(self, **kwargs):
        self._store = dict()
        self.update(kwargs)

    def json(self):
        return json.dumps(self._store)


class MarketoLeadKey(MarketoKeyBase):
    _mkto_type = 'LeadKey'

    REFERENCES = (
        ('cookie', 'COOKIE'),
        ('Email', 'EMAIL'),
        ('Id', 'IDNUM'),
    )

    def _to_soap(self):
        obj = self._soap_obj
        obj.keyType = self.key_name
        obj.keyValue = self.key_value
        return obj

    def _from_soap(self):
        pass

    def generate_from_lead(self, lead):
        for i in self.REFERENCES:
            if i[0] in lead:
                self.key_name = i[1]
                self.key_value = lead[i[0]]
                return self
        raise Exception('not enough lead info to generate lead key')


class MarketoLeadKeyList(MarketoListBase):
    _mkto_type = 'ArrayOfLeadKey'

    def __setitem__(self, key, value):
        if not isinstance(value, MarketoLeadKey):
            raise Exception()
        super(MarketoLeadKeyList, self).insert(key, value)

    def insert(self, key, value):
        if not isinstance(value, MarketoLeadKey):
            raise Exception()
        super(MarketoLeadKeyList, self).insert(key, value)

    def _to_soap(self):
        obj = self._soap_obj
        obj.leadKey.extend([i._to_soap() for i in self])
        return obj

    def _from_soap(self):
        pass


class MarketoAttribute(MarketoKeyBase):
    _mkto_type = 'Attribute'

    def _to_soap(self):
        obj = self._soap_obj
        obj.attrName = self.key_name
        obj.attrValue = self.key_value
        return obj

    def _from_soap(self):
        pass


class MarketoAttributeSet(MarketoDictBase):
    _mkto_type = 'ArrayOfAttribute'

    def _to_soap(self):
        obj = self._soap_obj
        for key, value in self.iteritems():
            obj.attribute.append(MarketoAttribute(key, value)._to_soap())
        return obj

    def _from_soap(self, obj):
        super(MarketoAttributeSet, self)._from_soap(obj)
        for i in obj.attribute:
            self[i.attrName] = i.attrValue
        return self


class MarketoLead(MarketoDictBase):
    MAGIC_KEYS = ('id', 'cookie', 'email')
    _mkto_type = 'LeadRecord'

    def _to_soap(self):
        obj = self._soap_obj
        obj.Id = self.get('Id')
        obj.Email = self.get('Email')
        attr_set = {key: value for key, value in self.iteritems() if key not in self.MAGIC_KEYS}
        obj.leadAttributeList = MarketoAttributeSet(**attr_set)._to_soap()
        return obj

    def _from_soap(self, obj):
        super(MarketoLead, self)._from_soap(obj)

        self['Id'] = obj.Id
        self['Email'] = obj.Email
        self.update(
            MarketoAttributeSet()._from_soap(obj.leadAttributeList)
        )
        return self

    def generate_lead_key(self):
        return MarketoLeadKey().generate_from_lead(self)

    def pull(self):
        try:
            lead_key = self.generate_lead_key()
            raw_lead = self.connection.client.get_lead(lead_key)
        except WebFault as e:
            MarketoFault(e).raise_error(lead_key)

        self._from_soap(raw_lead.leadRecordList.leadRecord[0])
        return self

    def push(self):
        return self.connection.client.sync_lead(self)
