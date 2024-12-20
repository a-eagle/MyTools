
proc_info = {
	scoreWindowId: null,
	scoreTabId : null,

	lastTaskRunTime: 0,
	
	scoresOfStudy: 0, // 学习得分
	dayOfStudy: null, // 学习得分的日期
	todayCanStudy : true, // 今日能否继续学习
};

// type = TT_XUEXI TT_KEEP_BEAT  TT_REFRESH_SCORE_PAGE  TT_GET_WINDOW
function Task(type, url, sec, scores) {
	this.curTab = null;
	this.url = url;
	this.runTime = 0;
	this.sec = sec;
	this.type = type;
	this.scores = scores;
	this.onClose = null;
}
Task.prototype.exec = function() {
	this.runTime = Date.now();
	if (this.type == 'TT_XUEXI') {
		xuexi(this);
		this.close(true, this.sec * 1000 + 120 * 1000);
		return true;
	} else if (this.type == 'TT_KEEP_BEAT') {
		// readNext(this);
		this.close(true, 20 * 1000);
		return true;
	} else if (this.type == 'TT_GET_WINDOW') {
		getScoreWindowTabId(this);
		this.close(true, 4 * 1000);
		return true;
	} else if (this.type == 'TT_REFRESH_SCORE_PAGE') {
		refreshScorePage(this);
		this.close(true, 10 * 1000);
		return true;
	}

	// exec fail
	this.close(false, 0);
	return false;
}

Task.prototype.close = function(status, ms) {
	let thiz = this;
	setTimeout(function() {
		console.log('Task.close called ', status, thiz.type);
		try {
			if (thiz.curTab)
				chrome.tabs.remove(thiz.curTab.id);
		} catch (e) {
			console.log('Task.close error ', status, e);
		}
		// thiz.curTab = null;
		if (thiz.onClose) {
			thiz.onClose();
		}
		if (thiz.scores)
			proc_info.scoresOfStudy += thiz.scores;
	}, ms);
}

var taskMgr = {
	tasks : [],
	curTask : null,
	
	add : function(task) {
		this.tasks.push(task);
	},
	pop : function(flag) {
		if (this.tasks.length == 0) {
			return null;
		}
		if (flag == 'top') {
			let v = this.tasks[0];
			this.tasks.splice(0, 1);
			return v;
		}
		return null;
	},
	empty: function () {
		this.tasks.splice(0, this.tasks.length);
	},
	find: function(task) {
		for (let i = 0; i < this.tasks.length; ++i) {
			if (this.tasks[i].url == task.url) {
				return this.tasks[i];
			}
		}
		if (this.curTask && this.curTask.url == task.url) {
			return this.curTask;
		}
		return null;
	},
	// tasks is [{sec: , url: }, ]
	addXueXiTasks : function(tasks) {
		for (let j = 0; j < tasks.length; ++j) {
			let tsk = this.find(tasks[j]);
			if (! tsk) {
				this.add(new Task('TT_XUEXI', tasks[j].url, tasks[j].less, tasks[j].scores));
			} else {
				tsk.sec = tasks[j].less;
			}
		}
	},
	run : function() {
		if (this.curTask != null) {
			return false;
		}
		if (! this.checkStudy()) {
			return false;
		}
		this.curTask = this.pop('top');
		if (! this.curTask) {
			return false;
		}
		
		let tm = this;
		this.curTask.onClose = function() {
			tm.curTask = null;
		}
		let eo = this.curTask.exec();
		return true;
	},
	checkStudy : function() {
		let curDay = new Date().getDate();
		if (proc_info.dayOfStudy != curDay) {
			proc_info.dayOfStudy = curDay;
			proc_info.scoresOfStudy = 0;
			proc_info.todayCanStudy = true;
			return true;
		}
		if (! proc_info.todayCanStudy) {
			return false;
		}
		return true;
	}
};


function funcToString(func, waiteTime) {
	if (! waiteTime) {
		waiteTime = 5000;
	}
	let s = func.toString();
	s += ';\n';
	s += 'setTimeout("' + func.name + '()", ' + waiteTime + ');';
	return s;
}

function xuexi(task) {
	let prop = {url: task.url, active: true};
	if (proc_info.scoreWindowId) {
		prop.windowId = proc_info.scoreWindowId;
	}
	chrome.tabs.create(prop, function(tab) {
		task.curTab = tab;
	});
}

function getScoreWindowTabId(task, cb) {
	proc_info.scoreWindowId = null;
	proc_info.scoreTabId = null;
	chrome.windows.getAll({populate : true}, function(windows) {
		for (i in windows) {
			let win = windows[i];
			let winId = win.id;
			let tabs = win.tabs;
			for (j in tabs) {
				if (tabs[j].url == task.url) {
					proc_info.scoreWindowId = winId;
					proc_info.scoreTabId = tabs[j].id;
					if (cb) cb();
					return;
				}
			}
		}
	});
}

function log(...args) {
	let d = new Date();
	let wrap = function(v) {if (v < 10) return '0' + v; else return '' + v;}
	let ts = wrap(d.getHours()) + ':' + wrap(d.getMinutes()) + ':' + wrap(d.getSeconds());
	console.log('Log ' + ts, args);
}

function refreshScorePage(task) {
	log('refreshScorePage', proc_info.scoreWindowId, proc_info.scoreTabId);
	if ((! proc_info.scoreWindowId) || (! proc_info.scoreTabId) ) {
		return;
	}
	
	function reloadTab() {
		chrome.tabs.update(proc_info.scoreTabId, {active : true}, function(tab) {
			chrome.tabs.reload(proc_info.scoreTabId);
		});
	}
	chrome.windows.update(proc_info.scoreWindowId, {focused  : true}, reloadTab);
}

// 监听消息 request -> {cmd:   data:  }
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
	let cmd = request['cmd'];
	// console.log('Recive Msg: ', request);
	if (cmd == 'OPEN_TAB') {
		prop = {url: request.data, active: true};
		chrome.tabs.create(prop, function(tab) {
		});
	} else if (cmd == 'LOG') {
		console.log('Recive LOG: ', request['data']);
	} else if (cmd == 'GET_WINDOW') {
		let url = request['data'].url;
		let t = new Task('TT_GET_WINDOW', url, 10);
		t.exec();
	} else if (cmd == 'ADD_XUEXI_TASKS') {
		taskMgr.addXueXiTasks(request['data']);
	} else if (cmd == 'EVAL') {
		let v = eval(request['data']);
		if (sendResponse) {
			sendResponse(v);
		}
		log('Eval: ', request['data']);
	}
	
	/*
	if (sendResponse) {
		sendResponse('我已收到你的消息：' +JSON.stringify(request));
	}
	*/
});


function runThread() {
	taskMgr.run();
}

var threadId = 0;

function startThread() {
	if (threadId == 0)
		threadId = setInterval(runThread, 5 * 1000);
}

function closeThread() {
	clearInterval(threadId);
	threadId = 0;
	if (taskMgr.curTask) {
		taskMgr.curTask.close();
		taskMgr.curTask = null;
	}
}

function clearTasks() {
	taskMgr.empty();
}

function getProcInfo() {
	let num = getTaskNum();
	let msg = '任务数量：' + num;
	// msg += '，今日学分：' + proc_info.scoresOfStudy;
	return msg;
}

function getTaskNum() {
	let cur = taskMgr.curTask ? 1 : 0;
	let num = cur;
	for (let i = 0; i < taskMgr.tasks.length; i++) {
		if (taskMgr.tasks[i].type == 'TT_XUEXI') {
			num++;
		}
	}
	return num;
}

// flag = true | false
function setTodayCanStudy(flag) {
	proc_info.todayCanStudy = flag;
}




