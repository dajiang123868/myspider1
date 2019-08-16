#_*_coding:utf-8_*_
import datetime
import logging
import random
from concurrent import futures
from fake_useragent import UserAgent
import requests

ua = UserAgent(verify_ssl=False)

def get_one_proxy(proxies_list, check_proxy_url):
    while True:
        if len(proxies_list) == 0:  # 损耗殆尽
            logging.debug("在proxies_list列表中代理ip 代理【耗尽 或 初始】")
            return None
        index = random.randint(0, len(proxies_list) - 1)
        one_proxy_dict = proxies_list[index]
        if time_cmp(one_proxy_dict['expire_time']):  # 代理ip过期
            logging.debug('在proxies_list列表中代理ip【过期】:{}'.format(one_proxy_dict))
            proxies_list.pop(index)
            continue
        # if not test_proxy("{}:{}".format(one_proxy_dict['ip'], one_proxy_dict['port']), check_proxy_url):  # 不可访问
        #     logging.debug('在proxies_list列表中代理ip【不可访问】:{}'.format(one_proxy_dict))
        #     proxies_list.pop(index)
        #     continue
        logging.debug("在proxies_list列表中挑出一个【可用】的随机ip代理:{}".format(one_proxy_dict))
        return one_proxy_dict

def time_cmp(expire_time):
    '''
    判断代理ip是否过期
    :param expire_time:
    :return:
    '''
    time_now = datetime.datetime.now()
    expire_time_datetime = datetime.datetime.strptime(expire_time, "%Y-%m-%d %H:%M:%S")
    return time_now > expire_time_datetime

def get_valid_proxy_pool(check_proxy_url, request_per_domain=10):
    '''
    (线程池)获取可用的ip代理列表
    '''
    logging.info('---用线程池,并发检验代理有效性---')
    valid_proxy_pool = []  # 有效代理列表
    pool = futures.ThreadPoolExecutor(request_per_domain)
    future_list = []
    proxies_list_raw = raw_proxy_pool(request_per_domain)
    for proxy_dict in proxies_list_raw:
        proxy_host = "{}:{}".format(proxy_dict['ip'], proxy_dict['port'])
        future_list.append(pool.submit(test_proxy, proxy_host, check_proxy_url))
    logging.info('检验代理ip提交成功, 等待响应')

    for future in futures.as_completed(future_list):
        proxy_host = future.result()
        if proxy_host:  # 有效代理
            logging.debug('有效代理:{}:'.format(proxy_host))
            for proxy_dict in proxies_list_raw:
                if proxy_host == "{}:{}".format(proxy_dict['ip'], proxy_dict['port']):
                    valid_proxy_pool.append(proxy_dict)
    logging.info('获取可用ip:{}个, 可访问地址:{}'.format(len(valid_proxy_pool), check_proxy_url))
    return valid_proxy_pool

def raw_proxy_pool(request_per_domain=10):
    '''
    获取获取原始代理ip列表
    :return:
    '''
    VALID_STATUS_CODES = [200]
    # 根据并发值，获取代理ip的个数
    r = requests.get(
        "http://http.tiqu.alicdns.com/getip3?num={}&type=2&pro=&city=0&yys=0&port=1&pack=37377&ts=1&ys=0&cs=0&lb=1&sb=0&pb=45&mr=1&regions=&gm=4".format(
            request_per_domain)
        , timeout=10)
    if r.status_code in VALID_STATUS_CODES:
        logging.info("提取供验证的代理ip总共:{}个".format(len(r.json()['data'])))
        proxies_list_raw = r.json()['data']
        return proxies_list_raw

def test_proxy(proxy_host, check_proxy_url):
    '''
    测试代理质量
    :param proxy_host:
    :param check_proxy_url:
    :return:
    '''
    # 无效状态码:403服务器拒绝此请求
    VALID_STATUS_CODES = [200]
    headers = {
        'User-Agent': ua.chrome
    }
    proxies = {
        'http': 'http://' + proxy_host,
        'https': 'https://' + proxy_host,
    }
    try:
        r = requests.get(check_proxy_url, proxies=proxies, timeout=5, headers=headers)
        if r.status_code in VALID_STATUS_CODES:
            logging.debug("代理可用:HTTP状态码:{},目标网址: {},代理ip: {}".format(r.status_code, check_proxy_url, proxy_host))
            return proxy_host
        else:
            logging.debug("代理不可用:HTTP状态码:{},目标网址: {},代理ip: {}".format(r.status_code, check_proxy_url, proxy_host))
            return False
    except Exception as e:
        logging.debug("代理不可用:Exception:{},目标网址: {},代理ip: {}".format(e, check_proxy_url, proxy_host))
        return False

if __name__ == '__main__':
    # raw_proxy_pool(request_per_domain=1)
    get_valid_proxy_pool('https://www.baidu.com/',request_per_domain= 1)