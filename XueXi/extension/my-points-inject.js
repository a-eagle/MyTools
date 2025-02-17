// import {proxy, unProxy} from "ajax-hook";
function formatTime(d) {
	let h = d.getHours();
	let m = d.getMinutes();
	let v = '';
	v += h > 9 ? h : '0' + h;
	v += ':';
	v += m > 9 ? m : '0' + m;
	return v;
}

function doScore(response) {
	let tasks = null;
	let userId = 0;
	try {
		let rsp = eval('(' + response.response + ')');
		tasks = rsp.data.taskProgress;
		userId = rsp.data.userId;
	} catch (e) {
		console.log(e);
		return;
	}
	
	let r = [];
	for (i in tasks) {
		let task = tasks[i];
		let obj = {};
		if (task.title == '我要选读文章' || task.title == '视听学习' || task.title == '视听学习时长' || task.title == '专项答题' || task.title == '每日答题' || task.title == '每周答题') {
			obj.title = task.title;
			obj.currentScore = task.currentScore;
			obj.dayMaxScore = task.dayMaxScore;
			r.push(obj);
		}
	}
	console.log(formatTime(new Date()), 'Get Score=', r);
	window.postMessage({cmd: 'GET_SCORE', data: r}, window.location.href);
	
	let userName = '';
	if (userId == 564647023) {
		userName = '高标';
	} else if (userId == 151146733393) {
		userName = '刘萍';
	}
	let userInfo = {userId : userId, userName : userName};
	window.postMessage({cmd: 'SET_USER_INFO', data: userInfo}, window.location.href);
}

function hook_proxy() {
	if (! window['ah']) {
		setTimeout(hook_proxy, 50);
		return;
	}
	ah.proxy({
		onRequest:  function(config, handler) {
			// console.log('my proxy request = ', config)
			handler.next(config)
		},
		
		onError: function(err, handler) {
			handler.next(err);
		},
		
		onResponse:function(response, handler) {
			let url = response.config.url;
			// console.log('my proxy response = ', response);
			if (url && url.indexOf('/delegate/score/days/listScoreProgress?sence=score') >= 0) {
				console.log(formatTime(new Date()), ' my proxy response A = ', response);
				doScore(response);
			}
			handler.next(response)
		},
	});
}

hook_proxy();


