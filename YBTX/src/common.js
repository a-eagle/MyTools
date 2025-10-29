function strToHex(str) {
    const HEX = '0123456789ABCDEF';
    if (! str) {
        return '';
    }
    const encoder = new TextEncoder();
    const bs = encoder.encode(str); // Uint8Array(5)
    let vals = []
    for (let i = 0; i < bs.length; i++) {
        let b = bs[i];
        let l = b & 0xf, h = (b >> 4) & 0xf;
        vals.push(HEX[h])
        vals.push(HEX[l])
    }
    return vals.join('');
}

function strFromHex(hex) {
    const HEX = '0123456789ABCDEF';
    if (!hex)
        return ''
    if (hex.length % 2 != 0)
        return false;
    for (let h of hex) {
        let cnd = (h >= '0' && h <= '9') || (h >= 'A' && h <= 'F');
        if (! cnd)
            return false;
    }
    let bs = [];
    for (let i = 0; i < hex.length; i += 2) {
        let h = HEX.indexOf(hex[i]);
        let l = HEX.indexOf(hex[i + 1]);
        let b = (h << 4) | l;
        bs.push(b)
    }
    let byteArray = new Uint8Array(bs);
    let decoder = new TextDecoder("utf-8");
    let str = decoder.decode(byteArray);
    return str;
}

function copyDict(obj) {
    let rs = {};
    let ks = Object.keys(obj);
    for (let k of ks) {
        rs[k] = ks[k];
    }
    return rs;
}

function copy(obj) {
    return copyObject(obj);
}

export  {
    strToHex, strFromHex, copy, copyDict
}