
proc_info = {
	scoreWindowId: null,
	scoreTabId : null,

	lastTaskRunTime: 0,
};

// type = TT_XUEXI TT_KEEP_BEAT
function Task(type, url, sec) {
	this.curTab = null;
	this.url = url;
	this.runTime = 0;
	this.sec = sec;
	this.type = type;
	this.onClose = null;
}
Task.prototype.exec = function() {
	this.runTime = Date.now();
	if (this.type == 'TT_XUEXI') {
		xuexi(this);
		this.close(true, this.sec * 1000);
		return true;
	} else if (this.type == 'TT_KEEP_BEAT') {
		// readNext(this);
		this.close(true, 20 * 1000);
		return true;
	} else if (this.type == 'TT_GET_WINDOW') {
		getScoreWindowTabId();
		this.close(true, 4 * 1000);
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
	}, ms);
}

var taskMgr = {
	tasks : [],
	curTask : null,
	
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
	exists: function(task) {
		for (let i = 0; i < this.tasks.length; ++i) {
			if (this.tasks[i].url == task.url) {
				return true;
			}
		}
		if (this.curTask && this.curTask.url == task.url) {
			return true;
		}
		return false;
	},
	addWindowTask : function() {
		let t = new Task('TT_GET_WINDOW', 'TT_GET_WINDOW', 10);
		if (! this.exists(t))
			this.add(t);
	},
	// tasks is [{sec: , url: }, ]
	addXueXiTasks : function(tasks) {
		for (let j = 0; j < tasks.length; ++j) {
			if (! this.exists(tasks[j])) {
				this.add(new Task('TT_XUEXI', tasks[j].url, tasks[j].sec));
			}
		}
	},
	run : function() {
		if (this.curTask != null) {
			return false;
		}
		this.curTask = this.pop();
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

function getScoreWindowTabId(cb) {
	proc_info.scoreWindowId = null;
	proc_info.scoreTabId = null;
	chrome.windows.getAll({populate : true}, function(windows) {
		for (i in windows) {
			let win = windows[i];
			let winId = win.id;
			let tabs = win.tabs;
			for (j in tabs) {
				if (tabs[j].url.indexOf('http://www.jxgbwlxy.gov.cn/') >= 0) {
					proc_info.scoreWindowId = winId;
					proc_info.scoreTabId = tabs[j].id;
					if (cb) cb();
					return;
				}
			}
		}
	});
}


// 监听消息 request -> {cmd:   data:  }
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
	let cmd = request['cmd'];
	console.log('Recive Msg: ', request);
	if (cmd == 'OPEN_TAB') {
		prop = {url: request.data, active: true};
		chrome.tabs.create(prop, function(tab) {
		});
	} else if (cmd == 'LOG') {
		console.log('Recive LOG: ', request['data']);
	} else if (cmd == 'GET_WINDOW') {
		taskMgr.addWindowTask();
	} else if (cmd == 'ADD_XUEXI_TASKS') {
		taskMgr.addXueXiTasks(request['data']);
	}
	
	if (sendResponse) {
		sendResponse('我已收到你的消息：' +JSON.stringify(request));
	}
});


function runThread() {
	taskMgr.run();
}

var threadId = 0;

function startThread() {
	threadId = setInterval(runThread, 5 * 1000);
}

function closeThread() {
	clearInterval(threadId);
	threadId = 0;
}

startThread();



