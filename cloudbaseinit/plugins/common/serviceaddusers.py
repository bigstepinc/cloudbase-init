from oslo_config import cfg
from oslo_log import log as oslo_logging

from cloudbaseinit.osutils import factory as osutils_factory
from cloudbaseinit.plugins.common import base
from cloudbaseinit.plugins.common import createuser

CONF = cfg.CONF

LOG = oslo_logging.getLogger(__name__)


class ServiceAddUsers(base.BasePlugin):
    def execute(self, service, shared_data):
        osutils = osutils_factory.get_os_utils()
        if service.get_additional_users() is not None:
            users = service.get_additional_users()
            for user_information in users:
                if "username" in user_information:
                    username = user_information["username"]
                    if osutils.user_exists(username):
                        LOG.info("User with id %s already exists" % username)
                    else:
                        baseplugin = createuser.BaseCreateUserPlugin
                        password = baseplugin._get_password(osutils)
                        osutils.create_user(username, password)
                        try:
                            # Create a user profile in order for other plugins
                            # to access the user home, etc
                            token = osutils.create_user_logon_session(username,
                                                                      password,
                                                                      True)
                            osutils.close_user_logon_session(token)
                        except Exception:
                            LOG.exception('Cannot create a logon session for' +
                                          'user: %s', username)
                        service.post_additional_user_password(username,
                                                              password)
                    if "hide" in user_information:
                        if user_information["hide"]:
                            osutils.hide_user(username)
                    if "groups" in user_information:
                        groups = user_information["groups"]
                        for groupname in groups:
                            try:
                                osutils.add_user_to_local_group(username,
                                                                groupname)
                            except Exception:
                                LOG.exception('Cannot add user to group "%s"',
                                              groupname)
        return base.PLUGIN_EXECUTION_DONE, False
