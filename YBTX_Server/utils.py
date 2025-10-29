import threading, sys, traceback, datetime, json, logging, copy, base64, urllib3, urllib.parse
import  peewee as pw
import orm

class OrmUtils:
    def findOrmClass(self, className):
        D = dir(orm)
        ds = [n.lower() for n in D]
        if className.lower() not in ds:
            return None
        idx = ds.index(className.lower())
        return getattr(orm, D[idx], None)
    
    def getColVal(self, col, val):
        if val is None:
            return None
        if ('INT' in col.field_type) or ('AUTO' in col.field_type):
            return int(val)
        if ('FLOAT' == col.field_type) or ('DOUBLE' == col.field_type) or ('DECIMAL' == col.field_type):
            return float(val)
        if ('CHAR' in col.field_type) or ('TEXT' in col.field_type) or ('DATE' in col.field_type) or ('TIME' in col.field_type):
            return str(val)
        return str(val)

    def getCondition(self, model, filters):
        if not filters:
            return []
        filters = json.loads(filters)
        cnds = []
        for f in filters:
            colName, op, val = f['col'], f['op'], f['val']
            if val == '':
                continue
            col = getattr(model, colName)
            val = self.getColVal(col, val)
            if op == 'like':
                cnds.append(col.contains(val))
            elif op == '==':
                cnds.append(col == val)
            elif op == '>':
                cnds.append(col > val)
            elif op == '>=':
                cnds.append(col >= val)
            elif op == '<':
                cnds.append(col < val)
            elif op == '<=':
                cnds.append(col <= val)
        return cnds

    def getCols(self, model, cols):
        if not cols:
            return []
        cc = cols.split(',')
        rs = []
        hasId = False
        for c in cc:
            c = c.strip()
            rs.append(getattr(model, c))
            if c == 'id':
                hasId = True
        if not hasId:
            rs.append(getattr(model, 'id'))
        return rs

class HexUtils:

    @staticmethod
    def strToHex(s : str):
        HEX = '0123456789ABCDEF'
        bs = s.encode()
        vals = []
        for b in bs:
            b = int(b)
            l, h = b & 0xf, (b >> 4) & 0xf
            vals.append(HEX[h])
            vals.append(HEX[l])
        return ''.join(vals)
    
    @staticmethod
    def strFromHex(hex : str):
        HEX = '0123456789ABCDEF'
        if not hex:
            return ''
        if len(hex) % 2 != 0:
            return False
        for h in hex:
            cnd = (h >= '0' and h <= '9') or (h >= 'A' and h <= 'F')
            if not cnd:
                return False
        bs = bytearray()
        for i in range(0, len(hex), 2):
            h, l = int(HEX.index(hex[i])), int(HEX.index(hex[i + 1]))
            b = (h << 4) | l
            bs.append(b)
        ss = bs.decode()
        return ss

if __name__ == '__main__':
    hex = HexUtils.strToHex('人好')
    vv = HexUtils.strFromHex(hex)
    print(hex)
    print(vv)