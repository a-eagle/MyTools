
/*
window.addEventListener("message", function(evt) {
	if (evt.data.cmd == 'CALL_NATIVE') {
		chrome.runtime.sendMessage({cmd: 'CALL_NATIVE', data: evt.data.data});
	}
}, false);

*/

setInterval(function() {
	window.location.reload();
	
}, 30 * 60 * 1000);

// http://www.jxgbwlxy.gov.cn/portal/study_play.do?id=151864364
// http://www.jxgbwlxy.gov.cn/portal/study_play.do?id=151864353

function findAllList() {
	let list = [];
	$('.hoz_course_row').each(function() {
		let time = $(this).find('span[title="课程时长"]').text();
		let ts = parseFloat(time.split(' ')[0]);
		if (time.indexOf('分钟') > 0) {
			ts *= 60;
		} else if (time.indexOf('小时') > 0) {
			ts *= 60 * 60
		}
		
		let w = $(this).find('input[value="我要学习"]');
		w = w.attr('onclick');
		w = w.substring(7, w.length - 1);
		
		let rate = $(this).find('.h_pro_percent').text();
		rate = rate.substring(0, rate.length - 1);
		rate = parseFloat(rate);
		ts = ts * (100 - rate) / 100;
		ts = parseInt(ts) + 60;
		list.push({sec: ts, id: w, url: 'http://www.jxgbwlxy.gov.cn/portal/study_play.do?id=' + w});
	});
	console.log(list);
	
	chrome.runtime.sendMessage({cmd: 'GET_WINDOW'});
	chrome.runtime.sendMessage({cmd: 'ADD_XUEXI_TASKS', data: list});
	
	if (list.length == 0) {
		if (window.location.href == 'http://www.jxgbwlxy.gov.cn/student/course_myrequired.do?searchType=1&menu=course') {
			window.location.href = "http://www.jxgbwlxy.gov.cn/student/course_myselect.do?searchType=2&menu=course";
		}
	}
}

findAllList();