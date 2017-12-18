import os
import xlrd
import configparser
import logging
from PIL import Image, ImageDraw

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='stat.log',
                filemode='w')

def to_log(mode, message):
    if mode == 'error':
        logging.error(message)
    if mode == 'debug':
        logging.debug(message)
    if mode == 'info':
        logging.info(message)



class ini_handle():
    def __init__(self, f=None):
        self.cf = configparser.ConfigParser()
        self.is_valid = False
        if f is None:
            self.ini_file = './static/config/setting.ini'
        else:
            self.ini_file = f
        if os.path.exists(self.ini_file):
            self.cf.read(self.ini_file)
            self.is_valid = True

    def read_db(self):
        if not self.is_valid:
            raise Exception(r'配置文件不存在！')
        if 'database' not in self.cf.sections():
            raise Exception(r'配置文件中不包含database！')
        try:
            _user = self.cf.get('database', 'user')
            _ip = self.cf.get('database', 'ip')
            _port = self.cf.getint('database', 'port')
            _pwd = self.cf.get('database', 'pwd')
            _db_name = self.cf.get('database', 'db')
            return _user, _ip, _port, _pwd, _db_name
        except Exception as e:
            to_log('error', repr(e))

    def read_sections(self):
        if not self.is_valid:
            raise Exception(r'配置文件不存在！')
        if 'all' not in self.cf.sections():
            raise Exception(r'配置文件中不包含all！')
        try:
            sections = self.cf.sections()
            _user = self.cf.get('database', 'user')
            _ip = self.cf.get('database', 'ip')
            _port = self.cf.getint('database', 'port')
            _pwd = self.cf.get('database', 'pwd')
            _db_name = self.cf.get('database', 'db')
            return _user, _ip, _port, _pwd, _db_name
        except Exception as e:
            to_log('error', repr(e))

def test_ini():
    ini = ini_handle()
    r = ini.read_db()
    print(r)

if __name__ == '__main__':
    test_ini()