import json
import peewee as pw
import orm

def main():
    qr = orm.Person.select()
    idx = 0
    for it in qr:
        if not it.suggest_2:
            continue
        if it.suggest_5 and it.addr in it.suggest_5:
            continue
        build(it)
        idx += 1

def build(p):
    if not p.info:
        return
    records = json.loads(p.info)['records']
    result = {'region_xz': p.xz, 'region_cun': p.addr, 'idcard': p.suggest_2, 'name': p.name, 'phone': ''}
    result['regist_xz'] = p.xz
    result['regist_cun'] = p.addr
    for r in records:
        if r.get('phone', None):
            result['phone'] = r['phone']
        rcun = result.get('regist_cun', None)
        if not rcun:
            result['regist_xz'] = r['residenceAddressCommunity']
            result['regist_cun'] = r['residenceAddressVillage']
        elif '居委会' in rcun and '村委会' in r.get('residenceAddressVillage', ''):
            result['regist_xz'] = r['residenceAddressCommunity']
            result['regist_cun'] = r['residenceAddressVillage']
    if '村委会' in result['regist_cun']:
        result['hukou'] = '农村'
    else:
        result['hukou'] = '城镇'
    print(p.id, result)
    p.result = json.dumps(result)
    p.save()

def write():
    f = open('result.txt', 'w')
    qr = orm.Person.select().where(orm.Person.result.is_null(False))
    for idx, q in enumerate(qr):
        it = json.loads(q.result)
        hj = f"江西省>九江市>德安县>{it['regist_xz']}>{it['regist_cun']}"
        rs = ['德安县', it['region_xz'], it['region_cun'], it['idcard'], it['name'], '', '', '', it['hukou'], it['phone'], hj]
        f.write('\t'.join(rs))
        f.write('\n')
    f.close()

#main()
write()