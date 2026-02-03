/**
 * @returns string | boolean | undefined | number | function | array | object
 */
function getTypeOf(obj) {
    let tp = typeof(obj);
    if (tp != 'object')
        return tp;
    if (Array.isArray(obj))
        return 'array';
    // let name = obj.constructor.name;
    // if (name == 'Date' || name == 'Set')
    //     return name;
    return 'object';
}

function isObject(obj) {
    if (obj == undefined || obj == null)
        return false;
    if (Object.prototype.toString.call(obj) == '[object Object]' && obj.constructor.name == 'Object') {
        return true;
    }
    return false;
}

// only suport Object | Array
function deepCopy(obj) {
    if (obj == undefined || obj == null)
        return obj;
    if (typeof(obj) == 'object') {
        if (Array.isArray(obj)) {
            let cc = [];
            for (let t of obj) cc.push(deepCopy(t));
            return cc;
        } else {
            let cc = {};
            for (let k in obj) {
                cc[k] = deepCopy(obj[k]);
            }
            return cc;
        }
    }
    return obj;
}

function extendObject(base, corver) {
    if (! isObject(corver)) {
        return;
    }
    for (let k in corver) {
        if (isObject(corver[k])) {
            if (! (k in base)) {
                base[k] = corver[k];
            } else if (! isObject(base[k])) {
                base[k] = corver[k];
            } else {
                extendObject(base[k], corver[k]);
            }
        } else {
            base[k] = corver[k];
        }
    }
}

function formatDate(date) {
    if (date instanceof Date) {
        let y = date.getFullYear();
        let m = date.getMonth() + 1;
        let d = date.getDate();
        if (m < 10) m = '0' + m;
        if (d < 10) d = '0' + d;
        return y + '-' + m + '-' + d;
    }
    date = String(date).trim();
    if (date.length == 8) {
        return date.substring(0, 4) + '-' + date.substring(4, 6) + '-' + date.substring(6, 8);
    }
    return date;
}

export {
    getTypeOf, isObject, deepCopy, extendObject, formatDate
}