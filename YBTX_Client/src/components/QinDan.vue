<script setup>
import {ref, onMounted, computed, inject} from 'vue'
import {strToHex, strFromHex, HashUrl} from '@/common'
import { ElNotification } from 'element-plus'
import QinDanDialog from './QinDanDialog.vue'
import HistoryDialog from './HistoryDialog.vue'
import {SERVER_URL} from '/src/config.js'

// let props = defineProps(['url', 'filters', 'pageSize']);
const datas = ref([]);
const curRowData = ref();
const editDialogRef = ref();
const historyDialogRef = ref();
const isAdmin = inject('is-admin', false);
const error = ref(false);

const qinDanRef = ref();
const qinDanHeight = ref(400);
onMounted(function() {
    qinDanHeight.value = qinDanRef.value.$el.offsetHeight;
});

async function loadData() {
    datas.value.length = 0;
    let sp = [];
    let url = new HashUrl();
    const filters = [
        {col: 'isDelete', op: '==', val: 0},
    ]
    let bm = strFromHex(url.getQueryParam('bm'));
    let fbcj = strFromHex(url.getQueryParam('fbcj'));
    if (bm === false || fbcj === false) {
        // error
        error.value = true;
        return;
    }
    if (bm) filters.push({col: 'bm', op: 'like', val: bm});
    if (fbcj) filters.push({col: 'fbcj', op: '==', val: fbcj});
    else filters.push({col: 'fbcj', op: '==', val: '县区级'});
    sp.push('filters=' + strToHex(JSON.stringify(filters)));
    // sp.push('pageSize=1000');
    let sps = sp.join('&');
    const resp = await fetch(`${SERVER_URL}/api/list/JcbdModel?${sps}`);
    const js = await resp.json();
    for (let it of js) {
        it._changedInfo = {};
        if (it.history && it.sureTime) {
            let hs = JSON.parse(it.history);
            for (let h of hs) if (h.time > it.sureTime) it._changedInfo[h.col] = true;
        }
        datas.value.push(it);
    }
}

onMounted(loadData);

function filterClumn(colName, hasIdx) {
    let rs = [];
    let ss = {};
    let idx = 1;
    for (let row of datas.value) {
        let colVal = row[colName];
        if (colVal && !ss[colVal]) {
            ss[colVal] = true;
            if (hasIdx)
                rs.push({text: `${idx++} ` + colVal, value: colVal });
            else
                rs.push({text: colVal, value: colVal });
        }
    }
    return rs;
}

const deptFilter = computed(() => {
    let rs = filterClumn('ssbm', true);
    return rs;
});

const ybtx_zhFilter = computed(() => {
    let rs = filterClumn('ybtx_zh', false);
    return rs;
});

const filterHandler = (value, row, column) => {
    const property = column['property'];
    return row[property] === value;
}
const fbcjFilter = computed(() => {
    let rs = filterClumn('fbcj', false);
    return rs;
});
const bmFilter = computed(() => {
    let rs = filterClumn('bm', true);
    return rs;
});

const handleEdit = (rowData) => {
    // console.log(rowData.row);
    curRowData.value = rowData.row;
    editDialogRef.value.editData(curRowData, loadData);
}

const handleHistory = (rowData) => {
    curRowData.value = rowData.row;
    historyDialogRef.value.setData(curRowData.value.history, curRowData.value.sureTime);
}

function handleSureTime(rowData) {
    let id = rowData.row.id;
    fetch(`${SERVER_URL}/api/update-sure-time/${id}`).then(async function(resp) {
        let rs = await resp.json();
        if (rs.code == 0) {
            ElNotification({ title: '成功', message: '更新成功', type: 'success', });
        } else {
            ElNotification({ title: '失败', message: '更新失败', type: 'error', });
        }
    });
}

function handleDelete(rowData) {
    let id = rowData.row.id;
    fetch(`${SERVER_URL}/api/markdel/JcbdModel/${id}`).then(async function(resp) {
        let rs = await resp.json();
        if (rs.code == 0) {
            ElNotification({ title: '成功', message: '删除成功', type: 'success', });
        } else {
            ElNotification({ title: '失败', message: '删除失败', type: 'error', });
        }
    });
}

function cellRender(scope) {
    let col = scope.column.property;
    let rowData = scope.row;
    if (rowData._changedInfo[col]) {
        return `<span style="color:#f00;"> ${rowData[col]} </span>`;
    }
    return rowData[col];
};
</script>

<template>
    <ElTable v-if="! error" :data = 'datas' border size='default' v-bind="$attrs"  ref="qinDanRef" :height="qinDanHeight" style="width:100%; height:100%">
        <el-table-column type="index" width="50" label="序号"/>
        <el-table-column property="bbnc" label="报表名称" width="300"  >
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <el-table-column property="fbcj" label="发表层级" width="100" :filters="fbcjFilter" :filter-method="filterHandler">
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <el-table-column property="ssbm" label="所属部门" width="100"  :filters="deptFilter" :filter-method="filterHandler">
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <!--el-table-column property="sjx" label="数据项（字段)" width="100" show-overflow-tooltip >
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column-->
        <!--el-table-column property="sjxgs" label="数据项个数" width="120" /-->
        <el-table-column property="tbcj" label="填报层级" width="90" >
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <!--el-table-column property="bsfs" label="报送方式" width="100" >
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column-->
        <!--el-table-column property="ywxtmc" label="业务系统名称" width="120" /-->
        <el-table-column property="gxpl" label="更新频率" width="110" sortable >
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <el-table-column property="gxsj" label="更新时间" width="200" >
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <el-table-column property="bm" label="县直部门" width="100" :filters="bmFilter" :filter-method="filterHandler">
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <el-table-column property="lxr" label="部门联系人" width="100" >
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <el-table-column property="jbr" label="经办人" width="100" sortable >
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <!--el-table-column property="ybtx_zh" label="(经办人)是否有一表同享账号" width="80"  :filters="ybtx_zhFilter" :filter-method="filterHandler">
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <el-table-column property="ybtx_in" label="(报表)是否在一表同享系统中" width="80" >
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column-->
        <el-table-column property="ybtx_mb" label="一表同享系统中模板名称" width="150" >
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <el-table-column property="mark" label="备注" width="200" >
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <el-table-column property="op" label="操作" width="200"  fixed="right" >
            <template #default="scope">
                <el-button link type="primary" size="small" @click="handleEdit(scope)">编辑</el-button>
                <el-button link type="primary" size="small" @click="handleHistory(scope)" v-if="isAdmin">历史</el-button>
                <el-button link type="primary" size="small" @click="handleSureTime(scope)" v-if="isAdmin">更新时间</el-button>
                <el-button link type="primary" size="small" @click="handleDelete(scope)" v-if="isAdmin">删除</el-button>
            </template>
        </el-table-column>
    </ElTable>

    <QinDanDialog ref="editDialogRef" > </QinDanDialog>
    <HistoryDialog ref="historyDialogRef" > </HistoryDialog>
    <el-alert title="链接地址错误，请检查！" type="error" effect="dark" :closable='false' v-if="error"/>
</template>

<style scoped > 
.red {
    color: #f00;
}

.el-table {
    --el-table-border-color: #333;
    --el-table-header-text-color: #000;
    --el-table-header-bg-color: #DBEBD4;
    --el-table-text-color: #000;
    --el-scrollbar-hover-bg-color: #333;
}

::v-deep .el-scrollbar {
    --el-scrollbar-opacity: 1;
    --el-scrollbar-bg-color: #444;
    --el-scrollbar-hover-opacity: 1;
}

</style>
