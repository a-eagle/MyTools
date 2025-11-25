<script setup>
import {computed, onMounted, ref} from 'vue'
import {strToHex} from '../common'
import {SERVER_URL} from '/src/config.js'

const allDatas = [];
const mainDepts = ['组织部', '政法委', '农业农村局', '宣传部', '民政局', '应急管理局', '卫健委', '残联', '医保局', '住建局', 
                    '文旅局', '行政审批局', '水利局', '林业局', '人社局', '营商办'];
const changed = ref(1);
const deptsAll_g = ref([]); // 全部
const deptsXQ_g = ref([]); // 县区级
const curSelDept = ref('')

async function loadBiaoDanDatas() {
  const filters = [{col: 'isDelete', op: '==', val: '0'}, {col: 'fbcj', op: '==', val: '县区级'}]; // 
  const fs = strToHex(JSON.stringify(filters));
  const resp = await fetch(`${SERVER_URL}/api/list/JcbdModel?filters=${fs}`);
  const js = await resp.json();
  let deptsAll = {}; // 全部
  let deptsXQ = {}; // 县区级

  for (let it of js) {
    allDatas.push(it);
    if (! deptsAll[it.bm]) {
      deptsAll[it.bm] = {};
    }
    let cur = deptsAll[it.bm];
    cur[it.gxpl] = cur[it.gxpl] ? cur[it.gxpl] + 1 : 1;

    if (it.fbcj != '县区级')
      continue;
    if (! deptsXQ[it.bm]) {
      deptsXQ[it.bm] = {};
    }
    cur = deptsXQ[it.bm];
    cur[it.gxpl] = cur[it.gxpl] ? cur[it.gxpl] + 1 : 1;
  }
  buildDeptSum(deptsAll);
  buildDeptSum(deptsXQ);
  sortDept(deptsAll_g.value, deptsAll);
  sortDept(deptsXQ_g.value, deptsXQ);
}

function isMainDept(deptName) {
  for (let d of mainDepts) {
    if (d.indexOf(deptName) >= 0 || deptName.indexOf(d) >= 0)
      return true;
  }
  return false;
}

function buildDeptSum(depts) {
  let dps = Object.keys(depts);
  for (let k of dps) {
    let d = depts[k];
    d.sum = buildDeptSumList(d);
    d.name = k;
    d.main = isMainDept(k);
  }
}

const getDeptCss = computed(() => function(item) {
      let css = item.main ? 'main-dept' : 'not-main-dept';
      if (item.name == curSelDept.value)
        css += ' cur-sel';
      return css;
    });

function buildDeptSumList(info) {
    let val = [];
    let keys = Object.keys(info);
    let SS = ['年报', '半年报', '季报', '月报', '阶段性', '临时性', '实时更新']
    for (let s of SS) {
      let d = info[s];
      if (d) {
        if (s == '实时更新')
          val.push('实时' + d);
        else
          val.push(s + d);
        keys.splice(keys.indexOf(s), 1)
      }
    }
    for (let i = 0; i < keys.length; i++) {
      val.push(keys[i] + '-' +  info[keys[i]]);
    }
    return val.join('<br/>');
}

function sortDept(dest, src) {
  for (let k in src) {
    if (isMainDept(k))
      dest.push(src[k]);
  }
  for (let k in src) {
    if (! isMainDept(k))
      dest.push(src[k]);
  }
}

onMounted(loadBiaoDanDatas);

function openQinDan(deptName, type) {
  let fbcj = type == 1 ? '' : '县区级';
  if (fbcj) fbcj = '&fbcj=' + strToHex(fbcj);
  window.open(`/#/?bm=${strToHex(deptName)}${fbcj}`, '_blank');
}

function onSelDept(evt, item) {
  // console.log(evt, item)
  curSelDept.value = item.name;
}

</script>

<template>
<div>
  <div class="header"> 全 部 </div>
  <table>
    <thead>
      <tr >
        <th v-for="(item, index) in deptsAll_g" :key="index" 
            :class="item.main ? 'main-dept' : 'not-main-dept' " 
            style="height: 30px;"> {{index + 1}} </th>
    </tr>
    <tr>
      <th v-for="item in deptsAll_g" :key="item.name" @click="onSelDept($event, item)"
          :class="getDeptCss(item)"
          @dblclick="openQinDan(item.name, 1)"> {{item.name}} </th>
    </tr>
    </thead>
    <tbody>
      <tr>
        <td v-for="item in deptsAll_g" :key="'z_' + item.name" v-html="item.sum">  </td>
      </tr>
    </tbody>
  </table>

  <div style="" class="header"> 县区级 </div>
  <table>
    <thead>
      <tr >
        <th v-for="(item, index) in deptsXQ_g" :key="index" style="height: 30px;" 
            :class="item.main ? 'main-dept' : 'not-main-dept' " > {{index + 1}} </th>
    </tr>
    <tr>
      <th v-for="item in deptsXQ_g" :key="item.name" @click="onSelDept($event, item)"
      :class="getDeptCss(item)"  @dblclick="openQinDan(item.name, 2)"> {{item.name}} </th>
    </tr>
    </thead>
    <tbody>
      <tr>
        <td v-for="item in deptsXQ_g" :key="'z_' + item.name" v-html="item.sum">  </td>
      </tr>
    </tbody>
  </table>
</div>
</template>

<style scoped>
table {
  border-collapse: collapse;
  width_: 1300px;
}
th {
  border: solid 1px #000;
  height: 50px;
  width: 80px;
  font-weight: normal;
}
th.cur-sel {
  color: blueviolet;
}
td {
  border: solid 1px #000;
}
th.main-dept {
  background-color: #ACB9CA;
}
th.not-main-dept {
  background-color: #FDEAAE;
}
div.header {
  font-size: 20px;
  margin-top: 30px;
  width: 100%;
  background-color: #ACB9CA;
}
</style>