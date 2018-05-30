import argparse
import json
import logging
import sys
from pathlib import Path

log_format = '%(asctime)s %(name)s[%(module)s] %(levelname)s: %(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)

Headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
Mobile_Headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Mobile Safari/537.36'}

class Config:
    def __init__(self):
        self.debug = False
        self.db_echo = False
        self.log_format = log_format

        self.site_info = {
            'site_name': '',
            'url': '',
            'table_name': ''
        }

        # sqlite基本设置
        self.db_info = {
            'name': '',
            'path': ''
        }

        self.proxies = {
            'http': 'http://127.0.0.1:1080',
            'https': 'http://127.0.0.1:1080'
        }

    @classmethod
    def load(cls, d):
        the_config = Config()

        the_config.debug = d.get('debug', False)
        the_config.db_echo = d.get('db_echo', False)
        the_config.site_info.update(d.get('site_info', {}))
        the_config.db_info.update(d.get('db_sqlite_info', {}))

        return the_config


# 读取配置文件与输入参数
def load_config():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='config file name')
    args = parser.parse_args()

    config_name = args.config or 'config.json'
    logging.info('使用配置文件 "{}".'.format(config_name))

    config_file = Path(__file__).parent.joinpath('../conf/', config_name)

    if not config_file.exists():
        config_name = 'config.default.json'
        logging.warning('配置文件不存在, 使用默认配置文件 "{}".'.format(config_name))
        config_file = config_file.parent.joinpath(config_name)

    try:
        # 略坑, Path.resolve() 在 3.5 和 3.6 上表现不一致... 若文件不存在 3.5 直接抛异常, 而 3.6
        # 只有 Path.resolve(strict=True) 才抛, 但 strict 默认为 False.
        # 感觉 3.6 的更合理些...
        config_file = config_file.resolve()
        config_dict = json.loads(config_file.read_text())
    except Exception as e:
        sys.exit('# 错误: 配置文件载入失败: {}'.format(e))

    #获得数据库路径
    db_path = Path(__file__).parent.joinpath('../../DB/')

    # 读取配置文件，进行配置赋值
    the_config = Config.load(config_dict)
    the_config.db_info['path'] = db_path

    return the_config


# 获得配置内容，并返回config
config = load_config()
