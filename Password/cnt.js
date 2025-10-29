url = window.location.href;

function loadScript(url) {
    let temp = document.createElement('script');
    temp.setAttribute('type','text/javascript');
    temp.src = chrome.extension.getURL(url);
    temp.async = false;
    document.documentElement.appendChild(temp);
}

if (url.indexOf('http://10.8.54.18/ebpm-web/') >= 0) { // 数据目录治理
    loadScript('inject_MLZL.js');
}
else if (url.indexOf('http://10.8.52.17:8088/') >= 0) { // 一表同享
    loadScript('jquery-3.6.min.js');
    loadScript('inject_YBTX.js');
}
else if (url.indexOf('http://10.100.66.38:2080/?#/login') >= 0) { // OA
    loadScript('jquery-3.6.min.js');
    loadScript('inject_common.js');
    loadScript('inject_OA.js');
}
else if (url.indexOf('https://study.jxgbwlxy.gov.cn/') >= 0) { // 江西干部网络学院学习平台
    loadScript('jquery-3.6.min.js');
    loadScript('inject_common.js');
    loadScript('inject_JXGBWLXY.js');
}

window.addEventListener("message", function(evt) {
	if (evt.data && evt.data.cmd) {
        console.log(evt.data);
		chrome.runtime.sendMessage(evt.data);
	}
}, false);