
/**
 * columns = [{
 *      key: str of data's attr key, or '_index_',
 *      title: str, title of table header
 *      sortable ?: boolean, default is false
 *      cellRender ?: function(h, rowData, column)
 *      sorter? : function(a, b, tag)  tag = 'asc' | 'desc' return -1, 0, 1
 *      
 *  }, ...]
 */

import {deepCopy, extendObject} from './utils.js'

let BasicTable = {
    props: {
        columns: {type: Array, default: () => []},
        datas: {type: Array, default: () => []},
    },
    data() {
        return {
            tableCss: 'basic-table',
            filterDatas: this.datas.slice(),
            curSelRow: null,
        }
    },
    methods : {
        getDefaultSorter(key, _sort) {
            return function(a, b) {
                a = a[key], b = b[key];
                if (a == undefined) a = null;
                if (b == undefined) b = null;
                if (a == null && b == null)
                    return 0;
                if (a == null) {
                    return -1;
                }
                if (b == null) {
                    return 1;
                }
                if (typeof(a) != typeof(b)) {
                    // TODO:
                }
                if (typeof(a) == 'string') {
                    if (_sort == 'asc')
                        return a.localeCompare(b);
                    return b.localeCompare(a);
                } else if (typeof(a) == 'number' || typeof(a) == 'boolean') {
                    if (_sort == 'asc')
                        return a - b;
                    return b - a;
                }
                return 0;
            }
        },
        changeSort(column) {
            if (! column.sortable)
                return;
            if (! column._sort) column._sort = 'asc';
            else if (column._sort == 'asc') column._sort = 'desc';
            else if (column._sort == 'desc') column._sort = '';
            for (let h of this.columns) {
                if (h != column && h.sortable) h._sort = '';
            }
            if (! column._sort) {
                this.filterDatas = this.datas.slice();
                return;
            }
            let sorter = column.sorter ? function(a, b) {return column.sorter(a, b, column._sort);} : this.getDefaultSorter(column.key, column._sort);
            this.filterDatas.sort(sorter);
        },
        clearSort() {
            for (let h of this.columns) {
                if ( h.sortable) h._sort = '';
            }
        },
        onClickCell(rowData, column) {
            this.$emit('click-cell', rowData, column, this);
        },
        onDblclickCell(rowData, column) {
            this.$emit('dblclick-cell', rowData, column, this);
        },
        onClickRow(rowData) {
            if (this.curSelRow != rowData)
                this.curSelRow = rowData;
            this.$emit('click-row', rowData, this);
        },
        onDblclickRow(rowData) {
            this.$emit('dblclick-row', rowData, this);
        },
        filter(text) {
            if (! this.datas) {
                return;
            }
            let rs = this._searchText(text);
            this.filterDatas = rs;
            this.clearSort();
        },
        _searchText(text) {
            let rs = [];
            let qs, cond, qrs = new Set();
            if (!text || !text.trim()) {
                return this.datas.slice();
            }
            text = text.trim().toUpperCase();
            if (text.indexOf('|') >= 0) {
                qs = text.split('|')
                cond = 'OR'
            } else {
                qs = text.split(' ')
                cond = 'AND'
            }
            for (let q of qs) {
                q = q.trim();
                if (q && !qrs.has(q))
                    qrs.add(q);
            }
            
            for (let d of this.datas) {
                if (this.match(d, qrs, cond))
                    rs.push(d)
            }
            return rs;
        },
        getSearchData(data) {
            let rs = {};
            for (let hd of this.columns) {
                rs[hd.key] = data[hd.key] || '';
            }
            return rs;
        },
        match(data, qrs, cond) {
            for (let q of qrs) {
                let fd = false;
                let sd = this.getSearchData(data);
                for (let k in sd) {
                    let v = sd[k];
                    if (typeof(v) == 'string') {
                        if (v.toUpperCase().indexOf(q) >= 0) {
                            fd = true;
                            break;
                        }
                    }
                }

                if (cond == 'AND' && !fd)
                    return false;
                if (cond == 'OR' && fd)
                    return true;
            }
            if (cond == 'AND')
                return true;
            return false;
        }
    },
    render() {
        console.log('BaseTable.render');
        const {h} = Vue;
        let hds = [];
        for (let column of this.columns) {
            let hdText = column.title + ' ' + (column.sortable ? (column._sort == 'asc' ? '&#8593;' : column._sort == 'desc' ? '&#8595;' : '&#9830;') : '');
            let a = {onClick: (evt) => {this.changeSort(column);}, innerHTML: hdText};
            for (let k in column) {
                if (typeof(column[k]) != 'function')
                    a[k] = column[k];
            }
            hds.push(h('th', a));
        }
        let theader = h('thead', h('tr', hds));
        let trs = [];
        for (let i = 0; i < this.filterDatas.length; i++) {
            let tds = [];
            let rowData = this.filterDatas[i];
            rowData._index_ = i + 1;
            for (let column of this.columns) {
                let cellVal = null;
                if (column.cellRender) cellVal = column.cellRender(h, rowData, column);
                else cellVal = rowData[column.key];
                tds.push(h('td', {
                    onclick: () => this.onClickCell(rowData, column),
                    ondblclick: () => this.onDblclickCell(rowData, column)
                }, cellVal));
            }
            let tr = h('tr', {
                class: {sel: this.curSelRow == rowData},
                onClick: () => this.onClickRow(rowData),
                ondblclick: () => this.onDblclickRow(rowData),
            }, tds);
            trs.push(tr);
        }
        let tbody = h('tbody', trs);
        return h('table', {class: this.tableCss}, [theader, tbody]); // this.$slots.default()
    },
}

let StockTable = deepCopy(BasicTable);
extendObject(StockTable, {
    props: {
        day: {type: String, default: () => ''},
    },
    data() {
        return {
            tableCss: ['basic-table', 'stock-table'],
            filterDatas: this.datas.slice(),
            curSelRow: null,
        }
    },
    methods: {
        getSearchData(data) {
            let rs = {};
            for (let hd of this.columns) {
                rs[hd.key] = data[hd.key] || '';
            }
            rs['code'] = data['code'] || '';
            rs['name'] = data['name'] || '';
            return rs;
        },
        getCodeList() {
            if (! this.filterDatas)
                return [];
            let rs = [];
            for (let k of this.filterDatas) {
                if (k.code && k.code.length == 6)
                    rs.push(k.code);
            }
            return rs;
        },
        openKLineDialog(rowData) {
            let code = rowData.code;
            //console.log('[openKLineDialog]', code);
            let rdatas = { codes: this.getCodeList(), day: this.day};
            // this.notify({name: 'BeforeOpenKLine', src: this, data: rdatas, rowData});
            let data = JSON.stringify(rdatas);
            $.post({
                url: '/openui/kline/' + code,
                contentType: "application/json",
                data: data
            });
        },
        defaults: {
            codeNameRender(h, rowData, column) {
                let code = rowData.code;
                let html = `<a href="https://www.cls.cn/stock?code='${code}' target=_blank> 
                            <span style="color:#383838; font-weight:bold;" >${rowData.name}</span> </a> <br/>
                            <span style="color:#666;font-size:12px;"> ${code}</span>`;
                return h('span', {innerHTML: html});
            },
            // 热度
            hotsRender(h, rowData, column) {
                let val = '';
                if (rowData[column.key]) val =  String(rowData[column.key]) + '°';
                return h('span', val);
            },
            // 涨幅
            zfRender(h, rowData, column) {
                let zf = rowData[column.key];
                let val = '';
                let attrs = {};
                if (typeof(zf) == 'number') {
                    val = (zf * 100).toFixed(1) + '%';
                    if (zf >= 0) attrs.style = 'color: #de0422';
                    else attrs.style = 'color: #52C2A3';
                }
                return h('span', attrs, val);
            },
            // 元 -> 亿元
            yRender(h, rowData, column) {
                let z = rowData[column.key];
                if (typeof(z) == 'number') {
                    z = parseInt(z / 100000000) + '亿';
                }
                return h('span', z);
            },
            // 亿元 -> 亿元
            y2Render(h, rowData, column) {
                let z = rowData[column.key];
                if (typeof(z) == 'number') {
                    if (z < 1) z = z.toFixed(1);
                    else z = parseInt(z);
                }
                return h('span', `${z}亿`);
            },
            // 涨停原因
            ztReasonRender(h, rowData, column) {
                const ELIPSE_NUM = 60;
                let val = rowData[column.key] || '';
                let elipse = val;
                if (val && val.length > ELIPSE_NUM) {
                    elipse = val.substring(0, ELIPSE_NUM) + '...';
                }
                let idx = elipse.indexOf('|');
                if (idx > 0 && idx < 20) {
                    let cur = h('span', {class: 'zt-reason'}, s.substring(0, idx));
                    let tail = h('span', {title: val.substring(idx + 1)}, `&nbsp;&nbsp;${elipse.substring(idx + 1)}`);
                    return h('span', [cur, tail]);
                }
                if (val != elipse || val.length > 30) {
                    return h('span', {title: val}, elipse);
                }
                return h('span', {class: 'zt-reason'}, val);
            },
            // 涨速
            zsRender(h, rowData, column) {
                let val = rowData[column.key];
                if (typeof(val) == 'number' && val) {
                    val = '↑&nbsp;' + val.toFixed(1);
                }
                return h('span', {innerHTML: val});
            },
            // 连板
            lbRender(h, rowData, column) {
                let val = rowData[column.key];
                if (typeof(val) == 'number' && val) {
                    val = `${val}板`;
                }
                return h('span', val);
            },

        }
    }
});

export {
    BasicTable,
    StockTable,
}