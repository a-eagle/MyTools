<script setup>
import {ref, onMounted, computed, reactive, inject} from 'vue'
import { ElNotification } from 'element-plus'
import {strToHex, copyDict} from '/src/common.js'

const datas = ref();
const show = ref(false);
const MAP = {
  bbnc: '报表名称', fbcj: '发表层级', ssbm: '所属部门', sjx: '数据项（字段）', sjxgs: '数据项个数',
  tbcj: '填报层级', bsfs: '报送方式', ywxtmc: '业务系统名称', gxpl: '更新频率', gxsj: '更新时间',
  lxr: '联系人', jbr: '经办人', bm: '县直部门', ybtx_zh: '(经办人)是否有一表同享账号',
  ybtx_in: '(报表)是否在一表同享系统中', ybtx_mb: '一表同享系统中模板名称', mark: '备注'
}

function setData(history, minTime) {
  if (! history) {
    datas.value = [];
  } else {
    let dd = JSON.parse(history);
    let rs = []
    let firstTime = dd[0].time;
    for (let i = dd.length - 1; i >= 0; i--) {
        dd[i].col = MAP[dd[i].col];
        dd[i]._isInitData = dd[i].time == firstTime;
        rs.push(dd[i]);
    }
    datas.value = rs;
  }
  show.value = true;
}

const cellRender = ref((scope) => {
    let col = scope.column.property;
    let rowData = scope.row;
    let m = rowData._isInitData ? "#006400" : "#f00";
    return `<span style="color:${m};"> ${rowData[col]} </span>`;
});

defineExpose({
    setData
});
</script>

<template>
<el-dialog v-model='show' title="查看历史" style="" draggable>
  <ElTable :data = 'datas' border  size='default' xstyle="border:solid 0px #000;" width="600" height="500">
      <el-table-column type="index" width="50" label="序号"/>
      <el-table-column property="time" label="修改时间" width="120" >
        <template #default="scope" >
                <span v-html="cellRender(scope)"> </span>
            </template>
        </el-table-column>
      <el-table-column property="col" label="列" width="120" />
      <el-table-column property="data" label="修改内容" />
  </ElTable>
</el-dialog>
</template>


<style scoped>
.dialog-footer {
    background-color: #fafafa;
}
</style>