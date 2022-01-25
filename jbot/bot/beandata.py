import requests
import datetime
import time
import json
import httpx
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


async def getbeans(ck, client):
    logger.info('即将从京东获取京豆数据')
    try:
        _7day = True
        page = 0
        headers = {
            "Host": "api.m.jd.com",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 9 Build/QKQ1.190825.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.62 XWEB/2797 MMWEBSDK/201201 Mobile Safari/537.36 MMWEBID/7986 MicroMessenger/8.0.1840(0x2800003B) Process/appbrand4 WeChat/arm64 Weixin NetType/4G Language/zh_CN ABI/arm64 MiniProgramEnv/android",
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
                logger.info(f'未能从京东获取到京豆数据，发生了错误{str(res)}')
                return {'code': 400, 'data': res}
        logger.info(f'获取到京豆数据')
        return {'code': 200, 'data': [beansin, beansout, _7days]}
    except Exception as e:
        logger.info(f'未能从京东获取到京豆数据，发生了错误{str(e)}')
        return {'code': 400, 'data': str(e)}


async def getTotal(ck, client):
    try:
        logger.info('即将从京东获取京豆总量')
        headers = {
            "Host": "wxapp.m.jd.com",
            "Connection": "keep-alive",
            "charset": "utf-8",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 9 Build/QKQ1.190825.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.62 XWEB/2797 MMWEBSDK/201201 Mobile Safari/537.36 MMWEBID/7986 MicroMessenger/8.0.1840(0x2800003B) Process/appbrand4 WeChat/arm64 Weixin NetType/4G Language/zh_CN ABI/arm64 MiniProgramEnv/android",
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
                beans_res = await getbeans(ck, client)
                beantotal = await getTotal(ck, client)
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
