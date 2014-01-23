import time
import logging
import traceback
from tlog.base.warning import Filter_warning, Filter_inactivity
from tlog.logger import logger

def main():
    logger.set_logger('early_warning.log')
    while True:
        try:
            filters_to_check = Filter_warning.get_filters_to_check()
            Filter_warning.check_filter_warnings(filters_to_check)

            Filter_inactivity.check()
        except Exception as e:
            logging.exception('Exception in early warning checker')
        time.sleep(60)

if __name__ == '__main__':
    main()