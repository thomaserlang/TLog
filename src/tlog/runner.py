import argparse
import sys
import os
import logging
import json
from tlog.config import Config
from tlog.logger import logger

parser = argparse.ArgumentParser()
parser.add_argument('init', help='foo help')

def main():
    logger.set_logger('tlog.log')
    try:
        if len(sys.argv) < 2:
            sys.exit(1)
        if sys.argv[1] == 'init':
            if len(sys.argv) <> 3:
                print 'Usage: init [path to config file].'
                sys.exit(1)
            if os.path.isfile(sys.argv[2]):
                print 'Config file does already exists, overwite? Y,N'
                if raw_input().lower() <> 'y':
                    sys.exit(1)
            with open(sys.argv[2], 'w') as f:
                json.dump(
                    Config.data,
                    f,
                    sort_keys=True,
                    indent=4, 
                    separators=(',', ': '),
                )            
            print 'Config written to: {}'.format(sys.argv[2])
            os.environ['TLOG_CONFIG'] = sys.argv[2]

        if sys.argv[1].split('=')[0] == '--config':
            config = sys.argv[1].split('=')[1]
            if not os.path.isfile(config):
                print 'Config "{}" could not be found.'.format(config)
                sys.exit(1)
            os.environ['TLOG_CONFIG'] = config
            sys.argv.pop(1)

        Config.load(os.environ.get('TLOG_CONFIG', './tlog.json'))

        arg = sys.argv[1]
        sys.argv.pop(1)
        if arg == 'web':   
            import tlog.web.app
            tlog.web.app.main()
        elif arg == 'receiver':
            import tlog.receiver.app
            tlog.receiver.app.main()
        elif arg == 'upgrade':
            logger.set_logger('upgrade.log')
            import tlog.migrate
            tlog.migrate.upgrade()
        elif arg == 'celery':
            import tlog.worker.app
            tlog.worker.app.main()
        elif arg == 'watchdog':
            import tlog.watchdog.app
            tlog.watchdog.app.main()
        elif arg == 'early_warning_checker':
            import tlog.early_warning_checker.app
            tlog.early_warning_checker.app.main()
        else:
            sys.exit(1)
    except Exception as e:
        logging.error(unicode(e))
        raise

if __name__ == "__main__":
    main()