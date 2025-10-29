<script setup>
import { onMounted, ref, inject } from "vue";
import QinDan from "./components/QinDan.vue";

const qinDanRef = ref();
const qinDanHeight = ref(400);
onMounted(function() {
    qinDanHeight.value = qinDanRef.value.$el.offsetHeight;
});

const isAdmin = inject('is-admin', false);

</script>

<template>
<el-container style="width:100vw; height:100vh;">
    <el-header height='45px' style="background-color:#ccc; font-size:30px;">
         基层报表底数初步清单（县区级）  &nbsp; &nbsp;  {{ isAdmin ? '(Admin)' : ''}}
    </el-header>
    <el-main style="background-color:#dfdfdf; padding: 0 10px;">
        <QinDan style="width:100%; height:100%" ref="qinDanRef" :height="qinDanHeight"> </QinDan>
    </el-main>
    <el-footer height='10px'>
    </el-footer>
</el-container>
</template>

<style scoped>

</style>
