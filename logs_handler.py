import logging

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
}



logger = logging.getLogger(__name__)
logging.basicConfig(filename='output/logs_my_aplication.log', level=logging.INFO)

