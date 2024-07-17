# https://github.com/mCodingLLC/VideosSampleCode/blob/master/videos/135_modern_logging/logging_configs/2-stderr-json-file.json
import logging
logger = logging.getLogger(__name__) #Using my Iwn Logger
logging_config = {

    'version': 1,
    'disable_existing_loggers': False, #Desabilita qualquer outro logger que n esteja
    # 'filters': {},
    'formatters': {
        "simple": {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s' #'%(levelname)s - %(message)s'
        },
        "detailed": {
              "format": "[%(levelname)s|%(module)s|L%(lineno)d] %(asctime)s: %(message)s",
              "datefmt": "%Y-%m-%dT%H:%M:%S%z"
        },
        "json": {
              "()": "mylogger.MyJSONFormatter",
              "fmt_keys": {
                "level": "levelname",
                "message": "message",
                "timestamp": "timestamp",
                "logger": "name",
                "module": "module",
                "function": "funcName",
                "line": "lineno",
                "thread_name": "threadName"
              }
    },
    'handlers': {
        "stdout": {
            'class': 'logging.StreamHandler',
            'level': 'WARNING',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        },
        "file": {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
            'stream': 'logs/my_app.log',
            'maxBytes': 1024, #max per file
            'backupCount': 3 #max files, dps disso ele vai apagando os mais antigos
        }
    },
    'loggers': {
        'root': {'level': 'DEBUG', 'handlers': ['stdout']},
    },

}
# O logg pode ser droado pelo logger ou pelo Handler
# O Handle vai executar algo quando o log for chamado

def main():
    logging.basicConfig(filename='myapp.log', level=logging.INFO)

    logger.debug()

    logger.info('Started')
    logger.warning('This is a warning')
    logger.error('This is an error')
    logger.critical('This is a critical error')

    print('Hello, World!')
    logger.info('Finished')

if __name__ == '__main__':
    main()