""" 
@ author: Kahoku
@ date: 2024/08
@ description: logging 日志文件生成器
@ version: 1.0
"""
import sys
import logging

class LogDriver:

    def __init__(self, file_path, logger_name="root"):
        
        self.logger = logging.Logger(logger_name)
        self.logger.setLevel(logging.INFO)

        self.fmts = "%(asctime)s--%(levelname)s: %(message)s"   # log输出格式
        self.dmt = "%Y/%m/%d %H:%M:%S"      # log时间格式

        self.log_path = file_path

        self.logger_init()  # 初始化 logger

    def logger_init(self):
        """ 配置 logger """
        self.handler = logging.FileHandler(self.log_path, 'a+')
        self.rf_handler = logging.StreamHandler(sys.stderr)      #默认是sys.stderr
        formatter = logging.Formatter(self.fmts, self.dmt)

        # 保存至本地文件
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)

        # 控制台打印日志
        self.rf_handler.setFormatter(formatter)
        self.logger.addHandler(self.rf_handler)

    def info(self, message):
        # self.logger_init()
        self.logger.info(message)
        # self.logger.removeHandler(self.handler)
        # self.logger.removeHandler(self.rf_handler)
        
    def error(self, message):

        # self.logger_init()
        self.logger.error(message)
        # self.logger.removeHandler(self.handler)
        # self.logger.removeHandler(self.rf_handler)