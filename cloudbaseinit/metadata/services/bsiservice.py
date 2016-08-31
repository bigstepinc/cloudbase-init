import json
import posixpath
import time

from oslo_config import cfg
from oslo_log import log as oslo_logging
from six.moves.urllib import error
from six.moves.urllib import request

from cloudbaseinit.metadata.services import base
from cloudbaseinit.utils import encoding

opts = [
]

CONF = cfg.CONF
CONF.register_opts(opts)

LOG = oslo_logging.getLogger(__name__)


class BSIService(base.BaseMetadataService):

    def __init__(self):
        base.BaseMetadataService.__init__(self)
        self.URL = None
        self.decoded_information = {}

    def load(self):
        super(BSIService, self).load()
        tries = 10
        while tries > 0:
            try:
                f = open('C:/URL.tmp', 'r')
                break
            except FileNotFoundError:
                tries = tries-1
                LOG.debug('Could not find file, %i retries remaining', tries)
                time.sleep(5)

        if tries == 0:
            raise base.NotExistingMetadataException()

        self.URL = f.read()
        f.close()
        LOG.debug('%s', self.URL)
        raw_information = encoding.get_as_string(self._get_data(self.URL))
        self.decoded_information = json.loads(raw_information)
        LOG.debug('%s', self.decoded_information)
        return True

    def get_instance_id(self):
        return str(self.decoded_information["metadata"]["instance-id"])

    def get_licensing_info(self):
        if "licensing-information" in self.decoded_information["metadata"]:
            metadata = self.decoded_information["metadata"]
            return metadata["licensing-information"]
        else:
            pass

    def get_host_name(self):
        return str(self.decoded_information["metadata"]["hostname"])

    def get_public_keys(self):
        if "public-keys" in self.decoded_information["metadata"]:
            return self.decoded_information["metadata"]["public-keys"]
        else:
            pass

    def get_admin_password(self):
        if "password-plaintext-unsafe" in self.decoded_information["metadata"]:
            metadata = self.decoded_information["metadata"]
            return str(metadata["password-plaintext-unsafe"])
        else:
            pass

    def get_user_data(self):
        if "userdata" in self.decoded_information["metadata"]:
            metadata = self.decoded_information["metadata"]
            return str(metadata["userdata"]).encode()
        else:
            pass

    def is_password_changed(self):
        return self.decoded_information["metadata"]["password-changed"]

    @property
    def can_update_password(self):
        return True

    def _get_response(self, req):
        try:
            return request.urlopen(req)
        except error.HTTPError as ex:
            if ex.code == 404:
                raise base.NotExistingMetadataException()
            else:
                raise

    def _get_data(self, path):
        req = request.Request(path)
        response = self._get_response(req)
        return response.read()
