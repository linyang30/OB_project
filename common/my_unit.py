import logging
import logging.config
from airtest.core.api import *
from common.base_unit import BaseUnit

CON_LOG = '../config/log.conf'
logging.config.fileConfig(CON_LOG)
logging = logging.getLogger()


class MyUnit(BaseUnit):

    def setUp(self):
        logging.info('setUp')
        start_app(self.param.package)
        sleep(5)
        self.param.skip_upgrade()
        self.param.skip_notice()
        sleep(30)

    def tearDown(self):
        logging.info('tearDown')
        self.param.exit_app()
        sleep(5)

