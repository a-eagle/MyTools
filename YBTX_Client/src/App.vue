<script setup>
import { onMounted, ref, inject } from "vue";
import QinDan from "./components/QinDan.vue";
import QinDanDialog from "./components/QinDanDialog.vue";

const newDialogRef = ref();

const isAdmin = inject('is-admin', false);
function addBiaoDan(evt) {
    newDialogRef.value.newData();
}
</script>

<template>
<el-container style="width:100vw; height:100vh;">
    <el-header height='45px' style="background-color:#ccc; font-size:30px;">
        <el-row :gutter="20"> 
            <el-col :span="12">基层报表底数初步清单（县区级）{{ isAdmin ? '&nbsp;&nbsp;&nbsp;(Admin)' : ''}}</el-col>
            <el-col :span="6" v-show="isAdmin">
                <el-link href="/#/?admin=1"> Home </el-link>
                <el-link href="/#/dept?admin=1" style="margin-left: 50px;"> Dept </el-link>
                <el-link href="/#/del?admin=1" style="margin-left: 50px;"> Deleted </el-link>
            </el-col>
            <el-col :span="6">
                <el-button type="primary" @click="addBiaoDan" v-if="isAdmin" style="float:right;"> 添加表单 </el-button>
            </el-col>
        </el-row>
    </el-header>
    <el-main style="background-color-:#dfdfdf; padding: 0 10px;">
        <router-view />
    </el-main>
    <el-footer height='10px'>
    </el-footer>
</el-container>
<QinDanDialog ref="newDialogRef"/>
</template>

<style scoped>

</style>
