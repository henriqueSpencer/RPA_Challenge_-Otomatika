from RPA.Excel.Files import Files
from logs_handler import logger


class ExcelHandler:
    def __init__(self):
        self.lib = Files()
        self.lib.create_workbook(path="output/news.xlsx", fmt="xlsx", sheet_name="news")

    def save_news_to_excel(self, excel_lines: list[dict]):
        """
        This method will save the news to an excel file
        :param excel_lines: list of dictionaries with the news information
        :return:
        """
        try:
            logger.info('saving news to excel')
            columns_order_excel = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
            columns = list(excel_lines[0].keys())

            # fill the header
            index_col = 0
            for column in columns:
                self.lib.set_cell_value(1, columns_order_excel[index_col], column)
                index_col += 1

            # fill the lines
            for index_line, line in enumerate(excel_lines):
                index_col = 0
                index_line += 2
                for column in columns:
                    self.lib.set_cell_value(index_line, columns_order_excel[index_col], line[column])
                    index_col += 1
        except Exception as e:
            logger.error('Error saving news to excel: %s', e)
        finally:
            self.lib.save_workbook()
            self.lib.close_workbook()
