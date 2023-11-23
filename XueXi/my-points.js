temp = document.createElement('script');
temp.setAttribute('type','text/javascript');
temp.src = chrome.extension.getURL('jquery-3.6.min.js');
temp.async = false;
// document.documentElement.appendChild(temp);

let enableStyle = {'color': 'rgb(209, 0, 0)', 'cursor': 'pointer', 'border': '1px solid rgb(203, 30, 30)', 'background': '#fff', "pointer-events": "auto" };
let disableStyle = {'color': 'rgb(191, 191, 191)', 'background': 'rgb(238, 238, 238)', 'cursor': 'not-allowed', 'border': '0px solid', "pointer-events": "none"};

function buildUI() {
	// $('.my-points-card-footer > .buttonbox').hide();
	
	var div = $('.my-points-content');
	var px = $('<div class="my-points-card" style="display: flex; justify-content:center;  align-items: center;" /> ');
	let url = window.location.href;
	let wrap = $('<div> </div>');
	var op = $('<div class="big" id="st_xx_"> 开始学习 </div>');
	var op2 = $('<div class="big" id="pu_xx_" > 停止学习 </div>');
	op.css(enableStyle);
	op2.css(enableStyle);
	// checkTaskStatus(op, op2);
	op.click(function() { start_xuexi(); });
	op2.click(function() { stop_xuexi(); } );
	
	wrap.append(op);
	wrap.append('<div style="height: 20px; width: 60px; display: block;" />');
	wrap.append(op2);
	px.append(wrap);
	div.append(px);
	
	$('.layout-header').hide();
	$('.layout-footer').hide();
}

function _init_view() {
	if (! window['$']) {
		setTimeout(_init_view, 500);
		return;
	}
	let v = $('.my-points-content > .my-points-card');
	if (v.length < 4) {
		setTimeout(_init_view, 300);
		return;
	}
	loadScore();
	buildUI();
}
_init_view();


function loadScore() {
	let r = [];
	let cards = $('.my-points-content > .my-points-card');
	for (let i = 0; i < cards.length; i++) {
		let card = cards.eq(i);
		let title = card.find('.my-points-card-title').text();
		let progress = card.find('.my-points-card-text').text();
		let sp = progress.split('/');

		let obj = {};
		obj.title = title;
		obj.currentScore = parseInt(sp[0]);
		obj.dayMaxScore = parseInt(sp[1]);
		r.push(obj);
	}
	console.log('Get Score =', r);
	chrome.runtime.sendMessage({cmd: 'SET_SCORE', data: r});
}

function start_xuexi() {
	//content_scripts——>background
	console.log('start_xuexi now');
	chrome.runtime.sendMessage( {cmd : 'START_XUE_XI'},
		function(response) {
			// console.log('收到来自后台的回复：' + response);
		}
	);
}

function stop_xuexi() {
	chrome.runtime.sendMessage( {cmd : 'STOP_XUE_XI'},
		function(response) {
			// console.log('收到来自后台的回复：' + response);
		}
	);
}

window.addEventListener("message", function(evt) {
	console.log(evt);
	chrome.runtime.sendMessage({cmd: evt.data.cmd, data: evt.data.data});
}, false);

console.log('In My Points Page');