""" 
@ author: Kahoku
@ date: 2024/08
@ description: logging 日志文件生成器
@ version: 1.0
"""
import sys
import logging

class LogDriver:

    def __init__(self, file_path, logger_name="root", console_printing=True):
        
        self.logger = logging.Logger(logger_name)
        self.logger.setLevel(logging.INFO)

        self.fmts = "%(asctime)s--%(levelname)s: %(message)s"   # log输出格式
        self.dmt = "%Y/%m/%d %H:%M:%S"      # log时间格式

        self.log_path = file_path

        self.console_printing = console_printing    # 是否输出到控制台

        self.logger_init()  # 初始化 logger

    def __getstate__(self):
        # 返回一个不包含logger的字典
        state = self.__dict__.copy()
        del state['logger']
        return state

    def __setstate__(self, state):
        # 重新创建logger并恢复其他状态
        self.__dict__ = state
        self.logger = logging.getLogger('MyLogger')

    def logger_init(self):
        """ 配置 logger """
        self.handler = logging.FileHandler(self.log_path, 'a+')
        self.rf_handler = logging.StreamHandler(sys.stderr)      #默认是sys.stderr
        formatter = logging.Formatter(self.fmts, self.dmt)

        # 保存至本地文件
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)

        # 控制台打印日志
        if self.console_printing:
            self.rf_handler.setFormatter(formatter)
            self.logger.addHandler(self.rf_handler)

    def info(self, message):

        self.logger.info(message)
        
    def error(self, message):

        self.logger.error(message)
