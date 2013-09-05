import time
import logging
import traceback
from tlog.base.warning import Filter_warning
from tlog.logger import logger

def main():
    logger.set_logger('early_warning.log')
    while True:
        try:
            filters_to_check = Filter_warning.get_filters_to_check()
            Filter_warning.check_filter_warnings(filters_to_check)
        except Exception as e:
            logging.info(unicode(e))
        time.sleep(60)

if __name__ == '__main__':
    main()