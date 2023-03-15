

window.addEventListener("message", function(evt) {
	let info = evt.data;
	if (info.cmd == 'CALL_NATIVE') {
		chrome.runtime.sendMessage({cmd: 'CALL_NATIVE', data: info.data});
	} else if (info.cmd == 'EVAL') {
		chrome.runtime.sendMessage({cmd: 'EVAL', data: info.data});
	}
}, false);



function findAllList() {
	let list = [];
	$('.hoz_course_row').each(function() {
		let time = $(this).find('span[title="课程时长"]').text();
		let ts = parseFloat(time.split(' ')[0]);
		if (time.indexOf('分钟') > 0) {
			ts *= 60;
		} else if (time.indexOf('小时') > 0) {
			ts *= 60 * 60;
		}
		
		let w = $(this).find('input[value="我要学习"]');
		w = w.attr('onclick');
		w = w.substring(7, w.length - 1);
		
		let rate = $(this).find('.h_pro_percent').text();
		rate = rate.substring(0, rate.length - 1);
		rate = parseFloat(rate);
		ts = ts * (100 - rate) / 100;
		ts = parseInt(ts) + 120;
		
		let z = $(this).find('span[title="学时"]').text();
		let scores = parseFloat(z.split(' ')[0]);
		
		let idx = window.location.href.indexOf('/', 10);
		let domain = window.location.href.substring(0, idx);
		
		list.push({sec: ts, id: w, scores: scores, url: domain + '/portal/study_play.do?id=' + w});
	});
	console.log(list);
	
	chrome.runtime.sendMessage({cmd: 'GET_WINDOW', data: {url: window.location.href} });
	chrome.runtime.sendMessage({cmd: 'ADD_XUEXI_TASKS', data: list});
	
	/*
	if (list.length == 0) {
		if (window.location.href == 'https://www.jxgbwlxy.gov.cn/student/course_myrequired.do?searchType=1&menu=course') {
			window.location.href = "https://www.jxgbwlxy.gov.cn/student/course_myselect.do?searchType=2&menu=course";
		}
	}
	*/
}

function loadTaskList() {
	// 必修课
	let rowCount = 22;
	let params = "pageType=%24%7Btype%7D&searchType=1&rowCount=" + rowCount + "&menu=course&currentPage=1&pageSize=" + rowCount;
	$.post('https://www.jxgbwlxy.gov.cn/student/course_myrequired.do', params, function(data) {
		console.log(data);
	});
}

function evalBackground(code, fn) {
	console.log('Call evalBackground(): ', code);
	chrome.runtime.sendMessage({cmd: 'EVAL', data: code}, fn);
}

function checkBtn(startBtn, stopBtn) {
	evalBackground('threadId == 0', function(result) {
		console.log('result=', result);
		if (result) {
			stopBtn.attr('disabled', 'disabled');
			startBtn.removeAttr('disabled');
		} else {
			startBtn.attr('disabled', 'disabled');
			stopBtn.removeAttr('disabled');
		}
	});
}

function checkTodayStudy(elem) {
	$.ajax({
		url : "/portal/today_study.do",
		dataType : "text",
		type : "post",
		async : true,
		cache : false,
		success : function(data) {
			console.log('today_study=', data, typeof(data));
			if (data != '0') {
				elem.html('[今日已学完积分，再学习不记分]');
				evalBackground('setTodayCanStudy(false)');
			} else {
				elem.html('[正常工作]');
				evalBackground('setTodayCanStudy(true)');
			}
		}
	});
}

function checkTimeMsg(elem) {
	let startTime = new Date();
	setInterval(function() {
		let ts = String((new Date().getTime() - startTime) / 1000 / 60);
		if (ts.indexOf('.') >= 0) {
			ts = ts.substring(0, ts.indexOf('.') + 2);
		}
		elem.html('已刷新' + ts + '分钟');
	}, 60 * 1000);
}

function showTipInfo() {
	let div = $('<div style="position:fixed; width:600px; height: 90px;  background-color:#ff0; z-index: 11000; border: solid 2px #959551;"> </div>');
	div.append('<label>已加载学习插件，点击我的必修课、我的选修课里所有的页码以加载课程。</label> <br/> ');
	let msgLabel = $('<label> </label>');
	div.append(msgLabel);
	evalBackground('getProcInfo()', function(msg) {
		msgLabel.html(msg);
	});
	let msgLabel2 = $('<label style="color: red; padding-left: 96px;"> </label>');
	div.append(msgLabel2);
	checkTodayStudy(msgLabel2);
	let msgLabel3 = $('<label style="padding-left: 20px;"> </label>');
	div.append(msgLabel3);
	checkTimeMsg(msgLabel3);
	div.append('<br/>');
	
	let btn = $('<button style="margin-top : 10px; margin-left: 100px;"> 开始学习 </button>');
	div.append(btn);
	
	let btn2 = $('<button style="margin-top : 10px; margin-left: 100px;"> 停止学习 </button>');
	div.append(btn2);
	
	let btn3 = $('<button style="margin-top : 10px; margin-left: 100px;"> 清空任务 </button>');
	div.append(btn3);
	
	btn.click(function() {
		evalBackground('startThread()');
		checkBtn(btn, btn2);
	});
	btn2.click(function() {
		evalBackground('closeThread()');
		checkBtn(btn, btn2);
	});
	btn3.click(function() {
		evalBackground('clearTasks()');
	});
	checkBtn(btn, btn2);
	
	$(document.body).prepend(div);
}

showTipInfo();
findAllList();

console.log('Load Time:' + new Date().toString().split(' ')[4]);

setTimeout(function() {
	evalBackground('getTaskNum()', function(taskNum) {
		if (taskNum > 0) {
			evalBackground('refreshScorePage()');
		}
	});
	
}, 15 * 60 * 1000);

