<script setup>
import {ref, onMounted, computed, inject} from 'vue'
import {strToHex} from '/src/common.js'
import QinDanDialog from './QinDanDialog.vue'
import HistoryDialog from './HistoryDialog.vue'

let props = defineProps(['url', 'filters', 'pageSize']);
const datas = ref([]);
const curRowData = ref();
const editDialogRef = ref();
const historyDialogRef = ref();
const isAdmin = inject('is-admin', false);

async function loadData() {
    datas.value.length = 0;
    let sp = [];
    sp.push('filters=' + strToHex(JSON.stringify(props.filters)));
    sp.push('pageSize=' + props.pageSize);
    let sps = sp.join('&');
    const resp = await fetch(`http://localhost:8010/${props.url}?${sps}`);
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

const headerCellStyle = function(data) {
    return {
        border: 'solid 1px #000',
        color:'#000',
        'background-color': '#DBEBD4'
    }
}

const cellStyle = function(data) {
    return {
        'border-right': 'solid 1px #333',
        'border-bottom': 'solid 1px #333',
        color:'#000',
    }
}

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
    let rs = filterClumn('ybtx_zh', true);
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


const handleEdit = (rowData) => {
    // console.log(rowData.row);
    curRowData.value = rowData.row;
    editDialogRef.value.editData(curRowData, loadData);
}

const handleHistory = (rowData) => {
    curRowData.value = rowData.row;
    historyDialogRef.value.setData(curRowData.value.history, curRowData.value.sureTime);
}

const cellRender = ref((scope) => {
    let col = scope.column.property;
    let rowData = scope.row;
    if (rowData._changedInfo[col]) {
        return `<span style="color:#f00;"> ${rowData[col]} </span>`;
    }
    return rowData[col];
});
</script>

<template>
    <ElTable :data = 'datas' border  :cell-style="cellStyle" size='default' :header-cell-style='headerCellStyle' style="border:solid 0px #000;" v-bind="$attrs">
        <el-table-column type="index" width="50" label="序号"/>
        <el-table-column property="bbnc" label="报表名称" width="200"  >
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <el-table-column property="fbcj" label="发表层级" width="90" >
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <el-table-column property="ssbm" label="所属部门" width="100"  :filters="deptFilter" :filter-method="filterHandler">
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <el-table-column property="sjx" label="数据项（字段)" width="100" show-overflow-tooltip >
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <!--el-table-column property="sjxgs" label="数据项个数" width="120" /-->
        <el-table-column property="tbcj" label="填报层级" width="100" >
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <el-table-column property="bsfs" label="报送方式" width="100" >
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <!--el-table-column property="ywxtmc" label="业务系统名称" width="120" /-->
        <el-table-column property="gxpl" label="更新频率" width="80" >
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <el-table-column property="bz" label="备注" width="200" >
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <el-table-column property="lxr" label="联系人" width="120" >
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <el-table-column property="jbr" label="经办人" width="120" >
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <el-table-column property="ybtx_zh" label="是否有一表同享账号" width="80"  :filters="ybtx_zhFilter" :filter-method="filterHandler">
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <el-table-column property="ybtx_in" label="是否在一表同享系统中" width="80" >
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <el-table-column property="ybtx_mb" label="一表同享系统中模板名称" width="120" >
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <el-table-column property="fk" label="反馈" width="120" >
            <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
        <el-table-column property="op" label="操作" width="100"  fixed="right" >
            <template #default="scope">
                <el-button link type="primary" size="small" @click="handleEdit(scope)">编辑</el-button>
                <el-button link type="primary" size="small" @click="handleHistory(scope)" v-if="isAdmin">历史</el-button>
            </template>
        </el-table-column>
    </ElTable>

    <QinDanDialog ref="editDialogRef" > </QinDanDialog>
    <HistoryDialog ref="historyDialogRef" > </HistoryDialog>
</template>

<style scoped> 
.el-table--default .cell {
    padding: 0 2px;
}
.red {
    color: #f00;
}
</style>
