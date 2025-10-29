<script setup>
import {ref, onMounted, computed, reactive, inject} from 'vue'
import { ElNotification } from 'element-plus'
import {strToHex, copyDict} from '/src/common.js'

const dataModel = ref({});
const show = ref(false);
let ssd = null;
let callback = null;
const isAdmin = inject('is-admin', false);
// console.log('isAdmin', isAdmin.value);

function save() {
  // console.log(ssd);
  show.value = false;
  let dis = diff(dataModel.value, ssd.value);
  if (Object.keys(dis).length == 0) {
    return;
  }
  dis['id'] = dataModel.value.id;
  fetch(`http://localhost:8010/api/save/JcbdModel`, {
      method: 'post',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(dis)
    }).then(async function(resp) {
      let rs = await resp.json();
      if (rs.code == 0) {
        ElNotification({ title: '成功', message: '保存成功', type: 'success', });
        copyTo(dis, ssd.value);
        // callback();
      } else {
        ElNotification({ title: '失败', message: '保存失败', type: 'error', });
      }
    });
}

function diff(now, old) {
  let rs = {};
  let srcKS = Object.keys(now);
  for (let k of srcKS) {
    if (now[k] != old[k]) {
      rs[k] = now[k];
    }
  }
  return rs;
}

function copyTo(src, dest) {
    let ks = Object.keys(src);
    for (let a of ks) {
        dest[a] = src[a];
    }
}

function editData(srcData, cb) {
  callback = cb;
  ssd = srcData;
  let val = srcData.value;
  let skips = ['history', 'isDelete', 'createTime', 'updateTime', 'sureTime', ];
    let ks = Object.keys(val);
    for (let a of ks) {
        if (skips.indexOf(a) >= 0)
          continue;
        dataModel.value[a] = val[a];
    }
    show.value = true;
}

defineExpose({
    editData
});
</script>

<template>
<el-dialog v-model='show' title="编辑" width="600" style="" draggable>
 <el-form :model="dataModel" label-width="auto" style="width: 100%; height: 600px; overflow: auto;">
    <el-form-item label="报表名称">
      <el-input v-model="dataModel.bbnc" />
    </el-form-item>
    <el-form-item label="发表层级" v-if="isAdmin">
      <el-select v-model="dataModel.fbcj" placeholder="">
        <el-option label="国家级" value="国家级" />
        <el-option label="省级" value="省级" />
        <el-option label="市级" value="市级" />
        <el-option label="县区级" value="县区级" />
      </el-select>
    </el-form-item>
    <el-form-item label="所属部门">
      <span v-if="isAdmin">
        <el-input v-model="dataModel.ssbm"  />
      </span>
      <span v-else> {{ dataModel.ssbm }} </span>
    </el-form-item>
    <el-form-item label="数据项（字段)" >
      <el-input v-model="dataModel.sjx" type="textarea" :rows="3" />
    </el-form-item>
    <el-form-item label="数据项个数" v-if="isAdmin">
      <el-input v-model="dataModel.sjxgs" />
    </el-form-item>
    <el-form-item label="填报层级"  v-if="isAdmin">
      <span v-if="isAdmin">
        <el-input v-model="dataModel.tbcj"  />
      </span>
      <span v-else> {{ dataModel.tbcj }} </span>
    </el-form-item>
    <el-form-item label="报送方式"  v-if="isAdmin">
      <el-input v-model="dataModel.bsfs" />
    </el-form-item>
    <el-form-item label="业务系统名称"  v-if="isAdmin">
      <el-input v-model="dataModel.ywxtmc" />
    </el-form-item>
    <el-form-item label="更新频率">
      <el-select v-model="dataModel.gxpl" placeholder="">
        <el-option label="年报" value="年报" />
        <el-option label="季报" value="季报" />
        <el-option label="月报" value="月报" />
        <el-option label="实时更新" value="实时更新" />
        <el-option label="阶段性" value="阶段性" />
        <el-option label="临时性" value="临时性" />
        <el-option label="实时更新" value="实时更新" />
      </el-select>
    </el-form-item>
    <el-form-item label="备注">
      <el-input v-model.trim="dataModel.bz" type="textarea" :rows="2" />
    </el-form-item>
    <el-form-item label="联系人">
      <el-input v-model.trim="dataModel.lxr" type="textarea" :rows="2" />
    </el-form-item>
    <el-form-item label="经办人">
      <el-input v-model.trim ="dataModel.jbr"  type="textarea" :rows="2" />
    </el-form-item>
    <el-form-item label="(经办人)是否有一表同享账号" v-if="dataModel.jbr">
      <el-select v-model="dataModel.ybtx_zh"  >
        <el-option label="" value="" />
        <el-option label="是" value="是" />
        <el-option label="否" value="否" />
      </el-select>
    </el-form-item>
    <el-form-item label="(报表)是否在一表同享系统中">
      <el-select v-model="dataModel.ybtx_in"  >
        <el-option label="是" value="是" />
        <el-option label="否" value="否" />
      </el-select>
    </el-form-item>
    <el-form-item label="一表同享系统中模板名称">
      <el-input v-model.trim ="dataModel.ybtx_mb" />
    </el-form-item>
    <el-form-item label="反馈">
      <el-input v-model.trim ="dataModel.fk" type="textarea" :rows="3"/>
    </el-form-item>
 </el-form>
 <template #footer>
      <div class="dialog-footer">
        <el-button @click="show = false">取消</el-button>
        <el-button type="primary" @click="save">
          保存
        </el-button>
      </div>
    </template>
</el-dialog>
</template>


<style scoped>
.dialog-footer {
    background-color: #fafafa;
}
</style>