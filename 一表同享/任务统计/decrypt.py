N = 0
R = 16
O = [214, 144, 233, 254, 204, 225, 61, 183, 22, 182, 20, 194, 40, 251, 44, 5, 43, 103, 154, 118, 42, 190, 4, 195, 170, 68, 19, 38, 73, 134, 6, 153, 156, 66, 80, 244, 145, 239, 152, 122, 51, 84, 11, 67, 237, 207, 172, 98, 228, 179, 28, 169, 201, 8, 232, 149, 128, 223, 148, 250, 117, 143, 63, 166, 71, 7, 167, 252, 243, 115, 23, 186, 131, 89, 60, 25, 230, 133, 79, 168, 104, 107, 129, 178, 113, 100, 218, 139, 248, 235, 15, 75, 112, 86, 157, 53, 30, 36, 14, 94, 99, 88, 209, 162, 37, 34, 124, 59, 1, 33, 120, 135, 212, 0, 70, 87, 159, 211, 39, 82, 76, 54, 2, 231, 160, 196, 200, 158, 234, 191, 138, 210, 64, 199, 56, 181, 163, 247, 242, 206, 249, 97, 21, 161, 224, 174, 93, 164, 155, 52, 26, 85, 173, 147, 50, 48, 245, 140, 177, 227, 29, 246, 226, 46, 130, 102, 202, 96, 192, 41, 35, 171, 13, 83, 78, 111, 213, 219, 55, 69, 222, 253, 142, 47, 3, 255, 106, 114, 109, 108, 91, 81, 141, 27, 175, 146, 187, 221, 188, 127, 17, 217, 92, 65, 31, 16, 90, 216, 10, 193, 49, 136, 165, 205, 123, 189, 45, 116, 208, 18, 184, 229, 180, 176, 137, 105, 151, 74, 12, 150, 119, 126, 101, 185, 241, 9, 197, 110, 198, 132, 24, 240, 125, 236, 58, 220, 77, 32, 121, 238, 95, 62, 215, 203, 57, 72]
I = [462357, 472066609, 943670861, 1415275113, 1886879365, 2358483617, 2830087869, 3301692121, 3773296373, 4228057617, 404694573, 876298825, 1347903077, 1819507329, 2291111581, 2762715833, 3234320085, 3705924337, 4177462797, 337322537, 808926789, 1280531041, 1752135293, 2223739545, 2695343797, 3166948049, 3638552301, 4110090761, 269950501, 741554753, 1213159005, 1684763257]

def i32(v):
    return v & 0xffffffff

def u2i(x):
    x = x & 0xffffffff
    if x >> 31 == 1:
        sx = (1 << 32) - x
        return -sx
    return x

def urs(num, bits): # 无符号右移
    if num < 0:
        num += 1 << 32
    return num >> bits

def a(e):
    t = []
    nidx = 0
    rn = len(e)
    while nidx < rn:
        t.append(int(e[nidx : nidx + 2], 16))
        nidx += 2
    return t

def l(e, t):
    n = 31 & t
    return i32(e << n | urs(e, 32 - n))

def s(e):
    ax = (255 & O[urs(e, 24) & 255]) << 24 | (255 & O[urs(e, 16) & 255]) << 16 | (255 & O[urs(e, 8) & 255]) << 8 | 255 & O[255 & e]
    return i32(ax)

def c(e):
    return i32(e ^ l(e, 2) ^ l(e, 10) ^ l(e, 18) ^ l(e, 24))

def u(e):
    return i32(e ^ l(e, 13) ^ l(e, 23))

def p(e, t, n):
    r = [0, 0, 0, 0] #new Array(4)
    o = [0, 0, 0, 0] #new Array(4)
    for i in range(4):
    #for (let i = 0; i < 4; i++)
        o[0] = 255 & e[4 * i]
        o[1] = 255 & e[4 * i + 1]
        o[2] = 255 & e[4 * i + 2]
        o[3] = 255 & e[4 * i + 3]
        r[i] = u2i(o[0] << 24 | o[1] << 16 | o[2] << 8 | o[3])
    #for (let i, a = 0; a < 32; a += 4)
    for a in range(0, 32, 4):
        i = u2i(r[1] ^ r[2] ^ r[3] ^ n[a + 0])
        r[0] = u2i(r[0] ^ c(s(i)))
        i = u2i(r[2] ^ r[3] ^ r[0] ^ n[a + 1])
        r[1] = u2i(r[1] ^ c(s(i)))
        i = u2i(r[3] ^ r[0] ^ r[1] ^ n[a + 2])
        r[2] = u2i(r[2] ^ c(s(i)))
        i = u2i(r[0] ^ r[1] ^ r[2] ^ n[a + 3])
        r[3] = u2i(r[3] ^ c(s(i)))
    #for (let i = 0; i < 16; i += 4)
    for i in range(0, 16, 4):
        t[i] = urs(r[3 - i // 4], 24) & 255
        t[i + 1] = urs(r[3 - i // 4], 16) & 255
        t[i + 2] = urs(r[3 - i // 4], 8) & 255
        t[i + 3] = 255 & r[3 - i // 4]

def _decrypt(e, t, o):
    #{padding: l="pkcs#7", mode: c, iv: d=[], output: h="string"}={}
    l = "pkcs#7"
    d = []
    h = "string"
    
    t = a(t)
    if 16 != len(t):
        raise Exception("key is invalid")
    e = a(e)
    #const f = new Array(32)
    f = [0] * 32
    def fff(e, t, r):
        #const o = new Array(4) , a = new Array(4);
        o, a = [0] * 4, [0] * 4
        #for (let n = 0; n < 4; n++)
        for n in range(4):
            a[0] = 255 & e[0 + 4 * n]
            a[1] = 255 & e[1 + 4 * n]
            a[2] = 255 & e[2 + 4 * n]
            a[3] = 255 & e[3 + 4 * n]
            o[n] = u2i(a[0] << 24 | a[1] << 16 | a[2] << 8 | a[3])
        o[0] = u2i(o[0] ^ 2746333894)
        o[1] = u2i(o[1] ^ 1453994832)
        o[2] = u2i(o[2] ^ 1736282519)
        o[3] = u2i(o[3] ^ 2993693404)
        #for (let n, l = 0; l < 32; l += 4)
        for l in range(0, 32, 4):
            n = o[1] ^ o[2] ^ o[3] ^ I[l + 0]
            t[l + 0] = o[0] = u2i(o[0] ^ u(s(n)))
            n = o[2] ^ o[3] ^ o[0] ^ I[l + 1]
            t[l + 1] = o[1] = u2i(o[1] ^ u(s(n)))
            n = o[3] ^ o[0] ^ o[1] ^ I[l + 2]
            t[l + 2] = o[2] = u2i(o[2] ^ u(s(n)))
            n = o[0] ^ o[1] ^ o[2] ^ I[l + 3]
            t[l + 3] = o[3] = u2i(o[3] ^ u(s(n)))
        if r == N:
            for i in range(16):
            #for (let n, i = 0; i < 16; i++)
                n = t[i]
                t[i] = t[31 - i]
                t[31 - i] = n

    fff(t, f, o)
    m = []
    g = d
    y = len(e)
    b = 0
    #for (; y >= r; ) {
    while y >= R:
        #const t = e.slice(b, b + 16)
        _t = e[b : b + 16]
        i = [0] * 16 #new Array(16)
        p(_t, i, f)
        #for (let e = 0; e < r; e++)
        for _e in range(R):
            #m[b + _e] = i[_e]
            m.append(i[_e])
        y -= R
        b += R
    
    if "pkcs#7" == l and o == N:
        #const e = m.length
        _e = len(m)
        _t = m[_e - 1]
        #for (let n = 1; n <= t; n++)
        for _n in range(1, _t + 1):
            if m[_e - _n] != _t:
                raise Exception("padding is invalid")
        #m.splice(e - t, t)
        del m[_e - _t : _e]
    
    def kk(e):
        t = []
        r = len(e)
        #for (let n = 0, r = e.length; n < r; n++)
        n = 0
        while n < r:
            if e[n] >= 240 and e[n] <= 247:
                t.append(chr(((7 & e[n]) << 18) + ((63 & e[n + 1]) << 12) + ((63 & e[n + 2]) << 6) + (63 & e[n + 3])))
                n += 3
            elif e[n] >= 224 and e[n] <= 239:
                t.append(chr(((15 & e[n]) << 12) + ((63 & e[n + 1]) << 6) + (63 & e[n + 2])))
                n += 2
            elif e[n] >= 192 and e[n] <= 223:
                t.append(chr(((31 & e[n]) << 6) + (63 & e[n + 1])))
                n += 1
            else:
                t.append(chr(e[n]))
            n += 1
        return "".join(t)
    return kk(m)

# key = window.key4
def decrypt(text, key = '74473454703855456978456e46657476'):
    return _decrypt(text, key, 0)