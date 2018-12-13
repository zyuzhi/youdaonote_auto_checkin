import requests
import logging
import time
import os
from configparser import ConfigParser
from datetime import datetime

checkin_url = 'https://note.youdao.com/yws/mapi/user?method=checkin'
ad_url = 'https://note.youdao.com/yws/mapi/user?method=adPrompt&keyfrom=%6E%6F%74%65%2E%36%2E%38%2E%31%2E%69%50%68%6F%6E%65&vendor=%41%70%70%53%74%6F%72%65&imei=%32%46%34%39%30%36%33%41%2D%46%45%41%30%2D%34%38%42%43%2D%39%38%41%39%2D%41%33%33%32%43%32%46%36%32%45%32%31&mid=%31%32%2E%31&model=%69%50%68%6F%6E%65%38,%31&phoneVersion=%69%50%68%6F%6E%65&level=user&login=wechat&net=wifi&os=iOS&os_ver=12.1&device_name=z.yuzhi&device_model=iPhone&device_id=iPhone8,1-2F49063A-FEA0-48BC-98A9-A332C2F62E21&device_type=iPhone&client_ver=6.8.1&IDFA=13FD2136-1F51-45DA-A30A-0A3A339CA5F4'

headers = {
    'User-Agent': 'you dao yun bi ji/6.8.1 (iPhone; iOS 12.1; Scale/2.00)',
}


def parse_cookie(cookies_data:str):
    each_lines = [x.split('=') for x in cookies_data.split(';')]
    return { x.strip(): y.strip() for x, y in each_lines }


def yd_post(url: str, cookies: dict):
    """

    :param url:
    :rtype: requests.Response
    :return:
    """
    return requests.post(url=url,
                         headers=headers,
                         cookies=cookies)


def check_in(cookies: dict):
    """

    :param cookies:
    :rtype: bool
    :return:
    """
    try:
        logging.info('check in...')
        res = yd_post(checkin_url, cookies)
        logging.debug('check in result: ' + res.text)
        res_json = res.json()
        if res_json is not None and 'success' in res_json and res_json['success']:
            logging.info('check in success')
            return True
        logging.info('check in fail')
    except Exception as e:
        logging.exception(e)
    return False


def ad_watch(cookies: dict):
    """

    :param cookies:
    :rtype: bool
    :return:
    """
    try:
        logging.info('ad watch...')
        res = yd_post(ad_url, cookies)
        logging.debug('ad watch result: ' + res.text)
        res_json = res.json()
        if res_json is not None and 'success' in res_json and res_json['success']:
            logging.info('ad watch success')
            return True
        logging.info('ad watch fail')
    except Exception as e:
        logging.exception(e)
    return False


def checkin_daily(cookies: dict):
    if not check_in(cookies):
        return
    time.sleep(3)

    for _ in range(3):
        if not ad_watch(cookies):
            return
        time.sleep(34)


def auto_checkin(cfg_file: str):
    cfg = ConfigParser()
    with open(cfg_file, 'r') as f:
        cfg.read_file(f)
    cookies_str = cfg.get('ydnote_checkin', 'cookie')
    daily_checkin_time = cfg.get('ydnote_checkin', 'daily_checkin_time')
    last_checkin_date = cfg.get('ydnote_checkin', 'last_checkin_date')
    cookies = parse_cookie(cookies_str)

    while True:
        try:
            now = datetime.now()
            now_date_str = now.strftime('%Y-%m-%d')
            if last_checkin_date == now_date_str:
                continue

            today_checkin_time_str = now_date_str + " " + daily_checkin_time
            today_checkin_time = datetime.strptime(today_checkin_time_str, '%Y-%m-%d %H:%M:%S')
            if now < today_checkin_time:
                continue
            checkin_daily(cookies)
            cfg.set('ydnote_checkin', 'last_checkin_date', now_date_str)
            with open(cfg_file, 'w') as f:
                cfg.write(f)
            last_checkin_date = now_date_str
        except Exception as e:
            logging.exception(e)
        finally:
            time.sleep(60)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(levelname)s\t] %(asctime)s - %(filename)s[line:%(lineno)d]: %(message)s')
    cfg_file = os.path.join(os.path.dirname(__file__), 'ydnote_checkin.cfg')
    auto_checkin(cfg_file)
