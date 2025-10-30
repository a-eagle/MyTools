<script setup>
import { onMounted, ref, inject } from "vue";
import QinDan from "./components/QinDan.vue";
import QinDanDialog from "./components/QinDanDialog.vue";

const qinDanRef = ref();
const qinDanHeight = ref(400);
const newDialogRef = ref();

onMounted(function() {
    qinDanHeight.value = qinDanRef.value.$el.offsetHeight;
});

const isAdmin = inject('is-admin', false);
function addBiaoDan(evt) {
    newDialogRef.value.newData();
}
</script>

<template>
<el-container style="width:100vw; height:100vh;">
    <el-header height='45px' style="background-color:#ccc; font-size:30px;">
        <el-row :gutter="20"> 
            <el-col :span="18">基层报表底数初步清单（县区级） &nbsp;&nbsp;&nbsp; {{ isAdmin ? '(Admin)' : ''}}</el-col>
            <el-col :span="6">
                <el-button type="primary" @click="addBiaoDan" v-if="isAdmin" style="float:right;"> 添加表单 </el-button>
            </el-col>
        </el-row>
    </el-header>
    <el-main style="background-color:#dfdfdf; padding: 0 10px;">
        <QinDan style="width:100%; height:100%" ref="qinDanRef" :height="qinDanHeight"> </QinDan>
    </el-main>
    <el-footer height='10px'>
    </el-footer>
</el-container>
<QinDanDialog ref="newDialogRef"/>
</template>

<style scoped>

</style>
