from robocorp.tasks import task
from robocorp import workitems
from logs_handler import logger
from selenium_site_handler import ApNewsSite
from excel_handler import ExcelHandler


@task
def task_handler():
    """ This task will get the news from the AP News site and save it to an excel file"""
    info = handle_parametres()
    ap = ApNewsSite()
    news = ap.get_news(info['news'], category=info['category'], months_to_download=info['months_to_download'])
    excel = ExcelHandler()
    excel.save_news_to_excel(news)
    logger.info('Finished')


def handle_parametres():
    """This method will handle the parameters received from the input of the task"""
    return_info = {}
    try:
        item = workitems.inputs.current
        print("Received payload:", item.payload)
        logger.info(f"Received payload: {item.payload}")
        dict_parametres = dict(item.payload)
        return_info['news'] = dict_parametres.get('news') if dict_parametres.get('news') is not None else 'Covid'
        return_info['category'] = dict_parametres.get('category') if dict_parametres.get('category') is not None\
            else "Health"
        return_info['months_to_download'] = dict_parametres.get('months_to_download') if \
            dict_parametres.get('months_to_download') is not None else 2

    except ValueError as e:
        logger.error(f"Error handling the parameters, probably empty parameter : {e}")
        return_info['news'] = 'Covid'
        return_info['category'] = "Health"
        return_info['months_to_download'] = 2

    except Exception as e:
        logger.error(f"Error handling the parameters, not treat: {e}")
    return return_info

# if __name__ == '__main__':
#     task_handler()
#     ap = ApNewsSite()
#     news = ap.get_news("Covid", category="Health", months_to_download=10)
#     excel = ExcelHandler()
#     excel.save_news_to_excel(news)
#     logger.info('Finished')
