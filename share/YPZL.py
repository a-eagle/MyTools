import requests, datetime, random, time

REST_BASE_URL = 'http://10.97.10.41:61001/baseifsys/thirdparty/restful/send?_orgid=001061042003034&appKey=YQCDPYY'

urlGroups = [
    # (_refuladdress, _token, _servicecode)
    [{'name': '环卫整体统计情况', 'url': ('e913885429c257812fb25ad8914f46b58', '2b7f3b223de6aaa83895eb2b7f655fce', '202309151619581608')},
    {'name': '环卫垃圾数月统计情况', 'url': ('e01a96701575b38c594fe681dc24af1ef', '48a35aa64ab42db63576af779326c062', '202309151619589649')},
    {'name': '环卫车辆日统计情况', 'url': ('efa921c1731b4f1a50bb3fd02e6fe1385', '743819bfc84816d9c73bb25e68bb044b', '202309151619582066')},
    {'name': '环卫作业量情况', 'url': ('ef4c4e9222fa50b2caa443029cb8b599f', '19f606492ef551fd3763cf76d3030afa', '202309151619585009')}],

    [{'name': '工伤待遇统计情况', 'url': ('e18b55519ff1a9791cabf97f7f602d064', '014b104c30ec041843c9588c52e1d461', '202309151019591772')},
    {'name': '居民养老统计情况', 'url': ('ee0928a36631aecb6d81c7530c8cd54e7', '6636f4dfb06c459a73e7ba6a479aaa87', '202309151019594549')}],
    
    [{'name': '森林资源调查数据', 'url': ('e403c60e2635ab29b08c067a3595d57da', '097d1bca971a6c06fc5601c72dadbfde', '202309151019598049')}],
    [{'name': '不停车系统测重统计清单', 'url': ('e80c39b434ad8ebe78a6b9c1162c96642', 'cdbdcf2e404f3e97949fbfebfe1b1827', '202309151014594934')}],
    [{'name': '12345市民热线工作情况', 'url': ('ec4fd304eab4c9fd7e936b149f0a4853b', 'e15e37d3eb0c947e690d31f198b8dd05', '202309151014593852')}]
]

outfile = open('call.txt', 'w')

def log(*args):
    dt = datetime.datetime.now()
    tag = dt.strftime('[%Y-%m-%d %H:%M:%S] ')
    print(tag, *args, file = outfile)
    outfile.flush()

def runOneGroup(idx):
    idx = idx % len(urlGroups)
    names = ('_refuladdress', '_token', '_servicecode')
    for item in urlGroups[idx]:
        params = ['&' + name + '=' + item['url'][i] for i, name in enumerate(names)]
        params = ''.join(params)
        url = REST_BASE_URL + params
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                log(f'Request OK: ({item["name"]})', resp.text)
                print('Request OK: ', resp.status_code, item["name"])
            else:
                log(f'Request Fail: {resp.status_code}({item["name"]})', resp.text)
                print('Request Fail: ', resp.status_code, item["name"])
        except Exception as e:
            log('Request Exception: ', item["name"], url, e)
            print('Request Exception: ', e)

def checkTime():
    global testTime
    dt = datetime.datetime.now()
    curTime = dt.strftime('%H:%S')
    if curTime <= '08:00':
        wt = random.randint(3600, 3600 * 3)
        time.sleep(wt)
        testTime += wt
        return False
    return True

def wait(runTimes, maxTimes):
    time.sleep(random.randint(20, 240) * 60)
 
if __name__ == '__main__':
    day = None
    runTimes = None
    maxTimes = 0
    while True:
        today = datetime.date.today()
        if day != today:
            day = today
            runTimes = 0
            maxTimes = 10 + random.randint(0, 20)
            if today.weekday() >= 5:
                maxTimes = 3
            testTime = time.time()
        if not checkTime():
            continue
        if runTimes <= maxTimes:
            runOneGroup(random.randint(0, 100))
            runTimes += 1
            log('runTimes=', runTimes, 'maxTimes=', maxTimes)
        wait(runTimes, maxTimes)