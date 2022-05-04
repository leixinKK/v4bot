import requests
import datetime
import time
import json
import httpx
import random
from datetime import timedelta
from datetime import timezone
from .utils import _ConfigFile, myck, logger
SHA_TZ = timezone(
    timedelta(hours=8),
    name='Asia/Shanghai',
)
requests.adapters.DEFAULT_RETRIES = 5
session = requests.session()
session.keep_alive = False

url = "https://api.m.jd.com/api"


async def getUA():
    """
    随机生成一个UA
    jdapp;iPhone;10.0.4;14.2;9fb54498b32e17dfc5717744b5eaecda8366223c;network/wifi;ADID/2CF597D0-10D8-4DF8-C5A2-61FD79AC8035;model/iPhone11,1;addressid/7785283669;appBuild/167707;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/null;supportJDSHWK/1
    :return: ua
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.15(0x18000f29) NetType/WIFI Language/zh_CN'

    """
    uuid = ''.join(random.sample('123456789abcdef123456789abcdef123456789abcdef123456789abcdef', 40))
    addressid = ''.join(random.sample('1234567898647', 10))
    iosVer = ''.join(random.sample(["14.5.1", "14.4", "14.3", "14.2", "14.1", "14.0.1", "13.7", "13.1.2", "13.1.1"], 1))
    iosV = iosVer.replace('.', '_')
    iPhone = ''.join(random.sample(["8", "9", "10", "11", "12", "13"], 1))
    ADID = ''.join(random.sample('0987654321ABCDEF', 8)) + '-' + ''.join(random.sample('0987654321ABCDEF', 4)) + '-' + ''.join(random.sample('0987654321ABCDEF', 4)) + '-' + ''.join(random.sample('0987654321ABCDEF', 4)) + '-' + ''.join(random.sample('0987654321ABCDEF', 12))
    return f'jdapp;iPhone;10.0.4;{iosVer};{uuid};network/wifi;ADID/{ADID};model/iPhone{iPhone},1;addressid/{addressid};appBuild/167707;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS {iosV} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/null;supportJDSHWK/1'


def getbody(page):
    body = {
        "beginDate": datetime.datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(SHA_TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "endDate": datetime.datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(SHA_TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "pageNo": page,
        "pageSize": 20,
    }
    return body


def getparams(page):
    body = getbody(page)
    params = {
        "functionId": "jposTradeQuery",
        "appid": "swat_miniprogram",
        "client": "tjj_m",
        "sdkName": "orderDetail",
        "sdkVersion": "1.0.0",
        "clientVersion": "3.1.3",
        "timestamp": int(round(time.time() * 1000)),
        "body": json.dumps(body)
    }
    return params


async def getbeans(ck, UA, client):
    logger.info('即将从京东获取京豆数据')
    try:
        _7day = True
        page = 0
        headers = {
            "Host": "api.m.jd.com",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": UA,
            "Content-Type": "application/x-www-form-urlencoded;",
            "Accept-Encoding": "gzip, compress, deflate, br",
            "Cookie": ck,
            "Referer": "https://servicewechat.com/wxa5bf5ee667d91626/141/page-frame.html",
        }
        _7days = []
        for i in range(0, 7):
            _7days.append(
                (datetime.date.today() - datetime.timedelta(days=i)).strftime("%Y-%m-%d"))
        beansin = {key: 0 for key in _7days}
        beansout = {key: 0 for key in _7days}
        while _7day:
            page = page + 1
            resp = await client.get(url, params=getparams(page), headers=headers, timeout=100)
            resp = resp.text
            res = json.loads(resp)
            if res['resultCode'] == 0:
                if (len(res['data']['list'])) != 0:
                    for i in res['data']['list']:
                        for date in _7days:
                            if str(date) in i['createDate'] and i['amount'] > 0:
                                beansin[str(date)] = beansin[str(
                                    date)] + i['amount']
                                break
                            elif str(date) in i['createDate'] and i['amount'] < 0:
                                beansout[str(date)] = beansout[str(
                                    date)] + i['amount']
                                break
                        if i['createDate'].split(' ')[0] not in str(_7days):
                            _7day = False
                else:
                    _7day = False
            else:
                logger.info(f'未能从京东获取到京豆数据，发生了错误{str(res)}')
                return {'code': 400, 'data': res}
        logger.info(f'获取到京豆数据')
        return {'code': 200, 'data': [beansin, beansout, _7days]}
    except Exception as e:
        logger.info(f'未能从京东获取到京豆数据，发生了错误{str(e)}')
        return {'code': 400, 'data': str(e)}


async def getTotal(ck, UA, client):
    try:
        logger.info('即将从京东获取京豆总量')
        headers = {
            "Host": "wxapp.m.jd.com",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": UA,
            "Content-Type": "application/x-www-form-urlencoded;",
            "Accept-Encoding": "gzip, compress, deflate, br",
            "Cookie": ck,
        }
        jurl = "https://wxapp.m.jd.com/kwxhome/myJd/home.json"
        resp = await client.get(jurl, headers=headers, timeout=100)
        resp = resp.text
        res = json.loads(resp)
        logger.info(f'从京东获取京豆总量{res["user"]["jingBean"]}')
        return res['user']['jingBean']
    except Exception as e:
        logger.error(str(e))


async def get_bean_data(i):
    try:
        async with httpx.AsyncClient(verify=False) as client:
            logger.info('开始执行京豆收支')
            cookies = myck(_ConfigFile)
            if cookies:
                logger.info(f'共获取到{len(cookies)},将获取第{i}个账户京豆数据')
                ck = cookies[i-1]
                theUA = await getUA()
                beans_res = await getbeans(ck, theUA, client)
                beantotal = await getTotal(ck, theUA, client)
                if beans_res['code'] != 200:
                    return beans_res
                else:
                    beansin, beansout = [], []
                    beanstotal = [int(beantotal), ]
                    for i in beans_res['data'][0]:
                        beantotal = int(
                            beantotal) - int(beans_res['data'][0][i]) - int(beans_res['data'][1][i])
                        beansin.append(int(beans_res['data'][0][i]))
                        beansout.append(int(str(beans_res['data'][1][i]).replace('-', '')))
                        beanstotal.append(beantotal)
                return {'code': 200, 'data': [beansin[::-1], beansout[::-1], beanstotal[::-1], beans_res['data'][2][::-1]]}
    except Exception as e:
        logger.error(str(e))
