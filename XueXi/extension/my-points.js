temp = document.createElement('script');
temp.setAttribute('type','text/javascript');
temp.src = chrome.extension.getURL('jquery-3.6.min.js');
temp.async = false;
document.documentElement.appendChild(temp);

temp = document.createElement('script');
temp.setAttribute('type','text/javascript');
temp.src = chrome.extension.getURL('ajax-hook.js');
temp.async = false;
document.documentElement.appendChild(temp);

temp = document.createElement('script');
temp.setAttribute('type','text/javascript');
temp.src = chrome.extension.getURL('my-points-inject.js');
temp.async = false;
document.documentElement.appendChild(temp);

let enableStyle = {'color': 'rgb(209, 0, 0)', 'cursor': 'pointer', 'border': '1px solid rgb(203, 30, 30)', 'background': '#fff', "pointer-events": "auto" };
let disableStyle = {'color': 'rgb(191, 191, 191)', 'background': 'rgb(238, 238, 238)', 'cursor': 'not-allowed', 'border': '0px solid', "pointer-events": "none"};

function buildUI() {
	$('.my-points-card-footer > .buttonbox').hide();
	
	var div = $('.my-points-content');
	var px = $('<div class="my-points-card" style="display: flex; justify-content:center;  align-items: center;" /> ');
	let url = window.location.href;
	let wrap = $('<div> </div>');
	var op = $('<div class="big" id="st_xx_" onclick="window.postMessage({cmd: 1}, \'' + url + '\');" > 开始学习 </div>');
	var op2 = $('<div class="big" id="pu_xx_" onclick="window.postMessage({cmd: 2}, \'' + url + '\');" > 暂停学习 </div>');
	var op3 = $('<div class="big" onclick="window.postMessage({cmd: 3}, \'' + url + '\');" > 每周答题 </div>');
	var op4 = $('<div class="big" onclick="window.postMessage({cmd: 4}, \'' + url + '\');" > 专项答题 </div>');
	op.css(enableStyle);
	op2.css(enableStyle);
	op3.css(enableStyle);
	op4.css(enableStyle);
	
	wrap.append(op);
	wrap.append('<div style="height: 20px; width: 60px; display: block;" />');
	wrap.append(op2);
	px.append(wrap);
	div.append(px);
	
	let mr = $('p.my-points-card-title:contains("每日答题")');
	mr.html("<a href='https://pc.xuexi.cn/points/exam-practice.html' target='_blank' > 每日答题 </a> ");
	
	mr = $('p.my-points-card-title:contains("每周答题")');
	mr.html("<a href='https://pc.xuexi.cn/points/exam-weekly-list.html' target='_blank' > 每周答题 </a> ");
	
	mr = $('p.my-points-card-title:contains("专项答题")');
	mr.html("<a href='https://pc.xuexi.cn/points/exam-paper-list.html' target='_blank' > 专项答题 </a> ");
	
	$('.layout-header').hide();
	$('.layout-footer').hide();
}

function _init_view() {
	if (! window['$']) {
		setTimeout(_init_view, 500);
		return;
	}
	let v = $('.my-points-content > .my-points-card');
	if (v.length < 7) {
		setTimeout(_init_view, 300);
		return;
	}
	buildUI();
}
_init_view();

function start_xuexi() {
	//content_scripts——>background
	// $('#st_xx_').css(disableStyle);
	// $('#pu_xx_').css(enableStyle);
	
	chrome.runtime.sendMessage(
		{cmd : 'start-xuexi'},
		function(response) {
			console.log('收到来自后台的回复：' + response);
		}
	);
}

function pause_xuexi() {
	//content_scripts——>background
	// $('#pu_xx_').css(disableStyle);
	// $('#st_xx_').css(enableStyle);
	
	chrome.runtime.sendMessage(
		{cmd : 'pause-xuexi'},
		function(response) {
			console.log('收到来自后台的回复：' + response);
		}
	);
}

window.addEventListener("message", function(evt) {
	console.log(evt);
	if (evt.data.cmd == 1) {
		// start xue xi
		start_xuexi();
	} else if (evt.data.cmd == 2) {
		pause_xuexi();
	} else if (evt.data.cmd == 'GET_SCORE') {
		chrome.runtime.sendMessage({cmd: 'GET_SCORE', data: evt.data.data});
	} else if (evt.data.cmd == 3) {
		chrome.runtime.sendMessage({cmd: 'DATI_WEEK', data: ''});
	} else if (evt.data.cmd == 4) {
		chrome.runtime.sendMessage({cmd: 'DATI_SPECIAL', data: ''});
	} else {
		chrome.runtime.sendMessage({cmd: evt.data.cmd, data: evt.data.data});
	}
}, false);

chrome.runtime.sendMessage({cmd: 'LOG', data: 'IN points page now'});

/**
popup页：
var bg = chrome.extension.getBackgroundPage();
bg.test();   //test()是background中的一个方法

*/

