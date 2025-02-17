
proc_info = {
	fetch: {},
	fetchDocJsons: [],
	fetchVideoJsons: [],
	cache: null,
	cacheDocIdx : 0,
	cacheVideoIdx : 0,

	scores: null,
	scoreRefreshTime : 0,
	scoreWindowId: null,
	scoreTabId : null,

	lastTaskRunTime: Date.now(),
	idle_duration : 0, // seconds
	
	userInfo: null, // {userId, userName}
	
	startXueXiTime: '',
	startXueXiTime2: ''
};

// type = TT_READ_DOC TT_READ_VIDEO TT_DO_DAYLAY, TT_DO_WEEK, TT_DO_SPECIAL, TT_CHROME_TOP, TT_REFRESH_SCORE, TT_RESET_PROC_INFO, TT_KEEP_BEAT
function Task(type) {
	this.curTab = null;
	this.url = null;
	this.beginTime = Date.now();
	this.endTime = Date.now() + 1000 * 60 * 60;
	this.runTime = 0;
	this.type = type;
	this.onClose = [];
}
Task.prototype.exec = function() {
	this.runTime = Date.now();
	let okTime = (this.beginTime <= Date.now()) && (this.endTime > Date.now());
	if (! okTime) {
		this.close(false, 0);
		return false;
	}

	if (this.type == 'TT_CHROME_TOP') {
		showScorePage();
		this.close(true, 10 * 1000);
		return true;
	} else if (this.type == 'TT_REFRESH_SCORE') {
		refreshScorePage();
		this.close(true, 20 * 1000);
		return true;
	} else if (this.type == 'TT_RESET_PROC_INFO') {
		proc_info.scores = null;
		proc_info.scoreWindowId = null;
		proc_info.scoreTabId = null;
		this.close(true, 2 * 1000);
		return true;
	}
	
	if (! proc_info.scores) {
		this.close(false, 0);
		return false;
	}
	if (this.type == 'TT_READ_DOC') {
		let ww = proc_info.scores['我要选读文章'];
		if (ww && ww.currentScore < ww.dayMaxScore) {
			readNext(this);
			this.close(true, 80 * 1000);
			return true;
		}
	} else if (this.type == 'TT_READ_VIDEO') {
		let ww = proc_info.scores['视听学习'];
		if (ww && ww.currentScore < ww.dayMaxScore) {
			readNext(this);
			this.close(true, 80 * 1000);
			return true;
		}
	} else if (this.type == 'TT_DO_DAYLAY') {
		let ww = proc_info.scores['每日答题'];
		if (ww && ww.currentScore == 0 && ww.dayMaxScore > 0) {
			zuoti_day(this);
			this.close(true, 150 * 1000);
			return true;
		}
	} else if (this.type == 'TT_DO_WEEK') {
		let ww = proc_info.scores['每周答题'];
		if (ww && ww.currentScore == 0 && ww.dayMaxScore > 0) {
			zuoti_week(this);
			this.close(true, 250 * 1000);
			return true;
		}
	} else if (this.type == 'TT_DO_SPECIAL') {
		let ww = proc_info.scores['专项答题'];
		mlog('专项答题: ', ww)
		if (ww && ww.currentScore == 0 && ww.dayMaxScore > 0) {
			zuoti_special(this);
			this.close(true, 250 * 1000);
			return true;
		}
	} else if (this.type == 'TT_KEEP_BEAT') {
		readNext(this);
		this.close(true, 65 * 1000);
		return true;
	} else if (this.type == 'TT_KEEP_BEAT_NEW') {
		doKeepNew(this);
		this.close(true, 120 * 1000);
		return true;
	}

	// exec fail
	this.close(false, 0);
	return false;
}
Task.prototype.close = function(status, ms) {
	let thiz = this;
	setTimeout(function() {
		mlog('Task.close called ', status, thiz.type);
		try {
			if (thiz.curTab)
				chrome.tabs.remove(thiz.curTab.id);
		} catch (e) {
			mlog('Task.close error ', status, e);
		}
		// thiz.curTab = null;
		for (i in thiz.onClose) {
			thiz.onClose[i](thiz);
		}
	}, ms);
}

var taskMgr = {
	tasks : [],
	curTask : null,
	ready: false,
	
	add : function(task) {
		this.tasks.push(task);
	},
	pop : function() {
		if (this.tasks.length > 0) {
			let v = this.tasks[0];
			this.tasks.splice(0, 1);
			return v;
		}
		return null;
	},
	empty: function () {
		this.tasks.splice(0, this.tasks.length);
	},
	addAllTasks : function() {
		if (this.tasks.length != 0) {
			return;
		}
		this.add(new Task('TT_RESET_PROC_INFO'));
		this.add(new Task('TT_CHROME_TOP'));
		this.add(new Task('TT_REFRESH_SCORE'));
		for (let i = 0; i < 6; ++i) {
			this.add(new Task('TT_READ_DOC'));
		}
		for (let i = 0; i < 6; ++i) {
			this.add(new Task('TT_READ_VIDEO'));
		}
		this.add(new Task('TT_DO_DAYLAY'));
		// this.add(new Task('TT_DO_WEEK'));
		this.add(new Task('TT_DO_SPECIAL'));
		this.add(new Task('TT_CHROME_TOP'));
		this.add(new Task('TT_REFRESH_SCORE'));
	},
	run : function() {
		if (! this.ready || this.curTask != null) {
			return false;
		}
		this.curTask = this.pop();
		if (! this.curTask) {
			this.ready = false;
			return false;
		}

		let tm = this;
		this.curTask.onClose.push(function() {
			tm.curTask = null;
		});
		try {
			let eo = this.curTask.exec();
			if (eo) {
				proc_info.lastTaskRunTime = Date.now();
			}
		} catch (e) {
			mlog('Run error: ', e, tm);
		}
		return true;
	},
};

function formatDate(date) {
	let d = date;
	let m = d.getMonth() + 1;
	return '' + d.getFullYear() + '-' + (m > 9 ? m : '0' + m) + '-' + (d.getDate() > 9 ? d.getDate() : '0' + d.getDate());
}

function formatTime(d) {
	let h = d.getHours();
	let m = d.getMinutes();
	let v = '';
	v += h > 9 ? h : '0' + h;
	v += ':';
	v += m > 9 ? m : '0' + m;
	return v;
}

function formatDateTime(date) {
	let d = formatDate(date);
	let t = formatTime(date);
	return d + ' ' + t;
}

function funcToString(func, waiteTime) {
	if (! waiteTime) {
		waiteTime = 5000;
	}
	let s = func.toString();
	s += ';\n';
	s += 'setTimeout("' + func.name + '()", ' + waiteTime + ');';
	return s;
}

function mlog(...args) {
	console.log('[' + formatDateTime(new Date()) + '] ' ,...args);
}

function zuoti_day(task) {
	callNative('TOP_CHROME');
	let prop = {url: "https://pc.xuexi.cn/points/exam-practice.html", active: true};
	if (proc_info.scoreWindowId) {
		prop.windowId = proc_info.scoreWindowId;
	}
	chrome.tabs.create(prop, function(tab) {
		task.curTab = tab;
	});
}

function zuoti_special(task) {
	callNative('TOP_CHROME');
	let prop = {url: "https://pc.xuexi.cn/points/exam-paper-list.html", active: true};
	if (proc_info.scoreWindowId) {
		prop.windowId = proc_info.scoreWindowId;
	}
	function _injectSpecial(ndx) {
		let ws = $('.items > .item');
		let w = ws.find('button').not('.ant-btn-background-ghost');
		if (w.length > 0) {
			w.eq(0).click();
			return;
		}
		
		// goto next page
		let nextPage = $('ul[class="ant-pagination pager"] > .ant-pagination-next');
		if (nextPage.hasClass('ant-pagination-disabled')) {
			return;
		}
		nextPage.click();
		setTimeout(_injectSpecial, 10 * 1000);
	}
	
	chrome.tabs.create(prop, function(tab) {
		task.curTab = tab;
		let details = {code: funcToString(_injectSpecial, 10 * 1000), runAt: 'document_idle' };
		chrome.tabs.executeScript(tab.id, details, function(any) {
			// mlog(any);
		});
	});
}

function zuoti_week(task) {
	callNative('TOP_CHROME');
	let prop = {url: "https://pc.xuexi.cn/points/exam-weekly-list.html", active: true};
	if (proc_info.scoreWindowId) {
		prop.windowId = proc_info.scoreWindowId;
	}
	function _injectWeekly(ndx) {
		let ws = $('.weeks > .week');
		let w = ws.find('button').not('.ant-btn-background-ghost');
		if (w.length > 0) {
			w.eq(0).click();
			return;
		}
		
		// goto next page
		let nextPage = $('ul[class="ant-pagination pager"] > .ant-pagination-next');
		if (nextPage.hasClass('ant-pagination-disabled')) {
			return;
		}
		nextPage.click();
		setTimeout(_injectWeekly, 10 * 1000);
	}
	
	chrome.tabs.create(prop, function(tab) {
		task.curTab = tab;
		let details = {code: funcToString(_injectWeekly, 10 * 1000), runAt: 'document_idle' };
		chrome.tabs.executeScript(tab.id, details, function(any) {
			// mlog(any);
		});
	});
}

function doKeepNew(task) {
	callNative('TOP_CHROME');
	let prop = {url: "https://www.xuexi.cn/", active: true};
	if (proc_info.scoreWindowId) {
		prop.windowId = proc_info.scoreWindowId;
	}
	chrome.tabs.create(prop, function(tab) {
		task.curTab = tab;
		function try_move_mouse() {
			let a1 = document.querySelectorAll('a.login-icon').length > 0;
			let a2 = document.querySelectorAll('a.logged-link').length > 0;
			if (a1 || !a2) {
				// not login
				return;
			}
			
			chrome.runtime.sendMessage({cmd: 'CALL_NATIVE', data: "IN_PAGE_DOC"});
			setTimeout(function() {
				let ma = document.querySelectorAll('.text-wrap');
				let idx = parseInt(Math.random() * ma.length);
				console.log('do click link ', idx, ma[idx]);
				ma[idx].scrollIntoView();
				let tg = ma[idx];
				setTimeout(function() {tg.click();}, 1000);
			  }, 10 * 1000);
		}
		details = {code: funcToString(try_move_mouse), runAt: 'document_idle' };
		chrome.tabs.executeScript(tab.id, details, function(any) {
			// mlog(any);
		});
	});
	
	setTimeout(function() {
		callNative('IN_PAGE_DOC');
	}, 60 * 1000);
	
	task.onClose.push(function(task_) {
		let minId = task_.curTab.id;
		let params = {};
		if (proc_info.scoreWindowId) {
			params.windowId = proc_info.scoreWindowId;
		} else {
			params.windowId = chrome.windows.WINDOW_ID_CURRENT;
		}
		chrome.tabs.query(params, function(tabs) {
			for (i in tabs) {
				if (tabs[i].id > minId && tabs[i].url && tabs[i].url.indexOf('https://www.xuexi.cn/') >= 0) {
					chrome.tabs.remove(tabs[i].id);
				}
			}
		});
	});
}

function activeScoreWindow(cb) {
	if (! proc_info.scoreWindowId) {
		return;
	}
	chrome.windows.update(proc_info.scoreWindowId, {focused : true}, function () {
		if (cb) cb();
	});
}

function activeScoreTab(cb) {
	if (! proc_info.scoreTabId) {
		return;
	}
	chrome.tabs.update(proc_info.scoreTabId, {selected : true}, function() {
		if (cb) cb();
	});
}

function showScorePage() {
	function sst() {
		function randMouse() {
			callNative('TOP_CHROME');
			callNative('RAND_MOUSE_MOVE');
		}
		activeScoreTab(randMouse);
	}
	getScoreWindowTabId(function() {
		activeScoreWindow(sst);
	});
}

function refreshScorePage() {
	proc_info.scoreRefreshTime = Date.now();
	function ref_page() {
		let details = {code: "window.location.reload();", runAt: 'document_idle' };
		chrome.tabs.executeScript(proc_info.scoreTabId, details, function(any) {
			// mlog(any);
		});
	}
	getScoreWindowTabId(ref_page);
}

function getScoreWindowTabId(cb) {
	proc_info.scoreWindowId = null;
	proc_info.scoreTabId = null;
	chrome.windows.getAll({populate : true}, function(windows) {
		for (i in windows) {
			let win = windows[i];
			let winId = win.id;
			let tabs = win.tabs;
			for (j in tabs) {
				if (tabs[j].url == 'https://pc.xuexi.cn/points/my-points.html' ) {
					proc_info.scoreWindowId = winId;
					proc_info.scoreTabId = tabs[j].id;
					if (cb) cb();
					return;
				}
			}
		}
	});
}

function keepAlive() {
	if (taskMgr.ready) {
		return;
	}
	let tt = formatTime(new Date());
	if (tt >= '00:02' && tt < '00:04') {
		// set start-xue-xi time
		let mm = (Math.random() * 100) % 55;
		let mm1 = mm, mm2 = mm + 2;
		if (mm1 < 10) {
			mm1 = '0' + mm1;
		}
		if (mm2 < 10) {
			mm2 = '0' + mm2;
		}
		proc_info.startXueXiTime = '06:' + mm1;
		proc_info.startXueXiTime2 = '06:' + mm2;
	}
	if (tt >= proc_info.startXueXiTime && tt < proc_info.startXueXiTime2) {
		startXueXi();
	}

	let lst = (Date.now() - proc_info.lastTaskRunTime) / 1000 / 60; // minutes
	// if (tt >= '23:30' && tt <= '23:59' && lst > 60) {
	// 	taskMgr.add(new Task('TT_CHROME_TOP'));
	// 	taskMgr.add(new Task('TT_KEEP_BEAT_NEW'));
	// 	taskMgr.ready = true;
	// 	return;
	// }
	
	if (lst < 3 * 60) {
		// less 3 hours
		// callNative('GET_IDLE_DURATION');
		return;
	}
	
	taskMgr.add(new Task('TT_CHROME_TOP'));
	taskMgr.add(new Task('TT_REFRESH_SCORE'));
	taskMgr.add(new Task('TT_KEEP_BEAT_NEW'));
	taskMgr.ready = true;
}

function startXueXi() {
	mlog('start xue xi');
	taskMgr.empty();
	taskMgr.ready = true;
	taskMgr.addAllTasks();
}

function parseScores(scores) {
	proc_info.scoreRefreshTime = Date.now();
	proc_info.scores = {};
	for (let i = 0; i < scores.length; ++i) {
		proc_info.scores[ scores[i].title ] = scores[i];
	}

	it = proc_info.scores['视听学习'];
	let it2 = proc_info.scores['视听学习时长'];
	it.currentScore += it2.currentScore;
	it.dayMaxScore += it2.dayMaxScore;
	delete proc_info.scores['视听学习时长'];
	
	let cp = Object.assign({}, proc_info.scores);
	mlog('parseScores: ', cp);
}

// 监听消息
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
	let cmd = request['cmd'];
	let rspData = '';
	if (cmd == 'start-xuexi') {
		startXueXi();
	} else if (cmd == 'pause-xuexi') {
		taskMgr.ready = false;
		taskMgr.empty();
	} else if (cmd == 'open-tab') {
		prop = {url: request.url, active: true};
		chrome.tabs.create(prop, function(tab) {
		});
	} else if (cmd == 'GET_SCORE') {
		let s = request['data'];
		parseScores(s);
	} else if (cmd == 'GET_DOC_VIDEO_URLS') {
		let data = request['data'];
		for (i in data) {
			if (data[i].type == 'tuwen') {
				proc_info.fetchDocJsons.push(data[i]);
			} else if (data[i].type == 'shipin') {
				proc_info.fetchVideoJsons.push(data[i]);
			}
		}
	} else if (cmd == 'CALL_NATIVE') {
		let data = request['data'];
		callNative(data);
	} else if (cmd == 'DATI_WEEK') {
	} else if (cmd == 'DATI_SPECIAL') {
	} else if (cmd == 'LOG') {
		mlog('Recive LOG: ', request['data']);
	} else if (cmd == 'GET_TASK_STATUS') {
		let status = { ready: taskMgr.ready };
		rspData = status;
	} else if (cmd == 'SET_USER_INFO') {
		let userInfo = request['data'];
		proc_info.userInfo = userInfo;
	} else if (cmd == 'GET_USER_INFO') {
		rspData = proc_info.userInfo;
	}
	
	if (sendResponse) {
		sendResponse(rspData);
	}
});

function readNext(task) {
	let targetUrl = null;
	let jss = '';
	let type = task.type;
	if (type == 'TT_READ_DOC') {
		jss = proc_info.fetchDocJsons;
		if (proc_info.cacheDocIdx < jss.length) {
			jss = jss[jss.length - 1 - proc_info.cacheDocIdx];
			targetUrl = jss.url;
			proc_info.cacheDocIdx++;
			chrome.storage.local.set({ 'cacheDocIdx': proc_info.cacheDocIdx}, function() {});
		}
	} else if (type == 'TT_READ_VIDEO') {
		jss = proc_info.fetchVideoJsons;
		if (proc_info.cacheVideoIdx < jss.length) {
			jss = jss[jss.length - 1 - proc_info.cacheVideoIdx];
			targetUrl = jss.url;
			proc_info.cacheVideoIdx++;
			chrome.storage.local.set({ 'cacheVideoIdx': proc_info.cacheVideoIdx}, function() {});
		}
	} else if (type == 'TT_KEEP_BEAT') {
		let idx = parseInt(Math.random() * proc_info.cacheDocIdx);
		jss = proc_info.fetchDocJsons;
		if (idx < jss.length) {
			jss = jss[jss.length - 1 - idx];
			targetUrl = jss.url;
		}
	}
	
	// open tab url
	if (! targetUrl) {
		mlog('FAIL: readNext() target url is null');
		return;
	}
	// callNative('TOP_CHROME');
	mlog('open : ', targetUrl);
	callNative('TOP_CHROME');
	// task.url = targetUrl;
	
	prop = {url: targetUrl, active: true};
	if (proc_info.scoreWindowId) {
		prop.windowId = proc_info.scoreWindowId;
	}
	chrome.tabs.create(prop, function(tab) {
		task.curTab = tab;
		function try_move_mouse() {
			chrome.runtime.sendMessage({cmd: 'CALL_NATIVE', data: "IN_PAGE_DOC"});
			/*setTimeout(function() {$('.outter').click();}, 10 * 1000);*/
		}
		details = {code: funcToString(try_move_mouse), runAt: 'document_idle' };
		chrome.tabs.executeScript(tab.id, details, function(any) {
			// mlog(any);
		});
	});
}

function runThread() {
	taskMgr.run();
	keepAlive();
}

var threadId = 0;

function startThread() {
	threadId = setInterval(runThread, 3 * 1000);
}

function closeThread() {
	clearInterval(threadId);
	threadId = 0;
}

var nativePort = null;
function openNativeApp() {
	let host = 'my.xuexi.app';
	nativePort = chrome.runtime.connectNative(host);
	nativePort.onMessage.addListener(function(msg) {
		mlog('Receive Native Callback Message:', msg);
		msg = msg.toString();
		if (msg.indexOf('GET_IDLE_DURATION') >= 0) {
			msg = msg.substring(0, 18);
			try {
				proc_info.idle_duration = parseInt(msg);
			} catch(e) {}
		}
	});
	nativePort.onDisconnect.addListener(function() {
		mlog('Disconnect Native App');
		nativePort = null;
	});
}

openNativeApp();

function callNative(action) {
	// mlog('Now send native message: ', action);
	nativePort.postMessage(action);
}

function initAppData() {
	chrome.storage.local.get(null, function(val) {
			mlog('read cache end ', val);
			if (val['cacheDocIdx']) {
				proc_info.cacheDocIdx = val['cacheDocIdx'];
			}
			if (val['cacheVideoIdx']) {
				proc_info.cacheVideoIdx = val['cacheVideoIdx'];
			}
		});
	
	
	$.get(chrome.extension.getURL('tuwen.json')).then(function(data) {
		proc_info.fetchDocJsons = data;
	});
	
	$.get(chrome.extension.getURL('shipin.json')).then(function(data) {
		proc_info.fetchVideoJsons = data;
	});
}

initAppData();
startThread();



