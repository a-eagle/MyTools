proc_info = {
	scores: null,
	scoreRefreshTime : 0,
	scoreWindowId: null,
	scoreTabId : null,

    readedLinks : {}, // {title: true}
    readinglinks: [], // {type: '', title: '', clickItem: Element, date: '' } type = Video, Article
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

function getNextReadingLink(type) {
    console.log(type);
    for (let i = 0; i < proc_info.readinglinks.length; i++) {
        let lk = proc_info.readinglinks[i];
        if (lk.type != type) {
            continue;
        }
        if (! proc_info.readedLinks[lk.ttitle]) {
            proc_info.readedLinks[lk.ttitle] = true;
            return lk;
        }
    }
    return null;
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

function refreshScorePage() {
	getScoreWindowTabId(function() {
        let url = 'https://pc.xuexi.cn/points/my-points.html';
        chrome.tabs.update(proc_info.scoreTabId, {selected : true, active: true, url: url}, function() {
        });
    });
}


class ArticleTask extends Task {
    constructor() {
        super('ArticleTask', 3000);
        this.curTab = null;
    }

    exec(resole) {
        let thiz = this;
        let lnk = getNextReadingLink('Article');
        console.log(lnk);
        if (lnk) {
            lnk.clickItem.click();
        }
        for (let i = 0; i < 10; i++) {
            setTimeout(function() {callNative("pressDownArrow()");}, (0.8 * i + 5) * 1000);
        }
        function end() {
            // chrome.tabs.remove(thiz.curTab.id);
            resole();
        }
        setTimeout(end, 70 * 1000);
    }
}

class VideoTask extends Task {
    constructor() {
        super('VideoTask', 3000);
    }
    exec(resole) {
        this.url = this.getUrl();
        let prop = {url: this.url, active: true};
        if (proc_info.scoreWindowId) {
            prop.windowId = proc_info.scoreWindowId;
        }
        let thiz = this;
        function try_move_mouse() {
            chrome.runtime.sendMessage({cmd: 'CALL_NATIVE', data: "for i in range(10) :\n\tpressDownArrow()\n\twait(0.8)"});
        }
        function cb(tab) {
            let details = {code: funcToString(try_move_mouse), runAt: 'document_idle' };
            chrome.tabs.executeScript(tab.id, details, function(any) {
            });
        }
        chrome.tabs.create(prop, function(tab) {
            thiz.curTab = tab;
            cb(tab);
        });

        function end() {
            chrome.tabs.remove(thiz.curTab.id);
            resole();
        }
        setTimeout(end, 7 * 60 * 1000);
    }
    getUrl() {
        return 'https://www.xuexi.cn/8e35a343fca20ee32c79d67e35dfca90/7f9f27c65e84e71e1b7189b7132b4710.html';
    }
}

class InitTask extends Task {
    constructor() {
        super('InitTask', 0);
        this.curTab = null;
        // 重要新闻
        this.url = 'https://www.xuexi.cn/98d5ae483720f701144e4dabf99a4a34/5957f69bffab66811b99940516ec8784.html';
    }

    exec(resole) {
        console.log('InitTask.exec() begin');
        let prop = {url: this.url, active: true};
        if (proc_info.scoreWindowId) {
            prop.windowId = proc_info.scoreWindowId;
        }
        let thiz = this;
        function try_move_keydown() {
            setInterval(function() {
                chrome.runtime.sendMessage({cmd: 'CALL_NATIVE', data: "keyPress(34)"}); // press page down
            }, 1500);
        }
        function cb(tab) {
            let details = {code: funcToString(try_move_keydown), runAt: 'document_idle' };
            chrome.tabs.executeScript(tab.id, details, function(any) {
            });
        }
        chrome.tabs.create(prop, function(tab) {
            thiz.curTab = tab;
            // cb(tab);
        });

        function get_links() {
            let links = $('.text-link-item-title');
            let rs = [];
            for (let i = 0; i < links.length; i++) {
                let clickItem = links.eq(i).find('div.text-wrap');
                let dateItem = links.eq(i).find('div.extra-wrap');
                let item = {title: clickItem.text(), clickItem: clickItem, date: dateItem.text(), type: 'Article'};
                rs.push(item);
            }
            return rs;
        }
        function get_links_a() {
            let details = {code: get_links.toString() + '; _a_ = get_links(); _a_; ', runAt: 'document_idle' };
            chrome.tabs.executeScript(thiz.curTab.id, details, function(any) {
                console.log('get_links: ', any);
                proc_info.readinglinks = any[0];
            });
        }
        setTimeout(get_links_a, 7 * 1000);

        function end() {
            // chrome.tabs.remove(thiz.curTab.id);
            resole();
        }
        setTimeout(end, 10 * 1000);
    }
}

class RefreshScorePageTask extends Task {
    constructor() {
        super('RefreshScorePageTask', 1000);
    }

    exec(resole) {
        console.log('RefreshScorePageTask.exec() begin');
        let thiz = this;
        refreshScorePage();
        function end() {
            resole();
        }
        setTimeout(end, 5 * 1000);
    }
}

function callNative(action) {
	console.log('Send native message: ', action);
	nativePort.postMessage(action);
}

// 监听消息
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
	let cmd = request['cmd'];
    let data = request['data'];
	let rspData = '';
	if (cmd == 'START_XUE_XI') {
		startXueXi();
	} else if (cmd == 'STOP_XUE_XI') {
		thread.stop();
	} else if (cmd == 'CALL_NATIVE') {
		callNative(data);
	} else if (cmd == 'SET_SCORE') {
		proc_info.scores = data;
	}

	if (sendResponse) {
		sendResponse(rspData);
	}
});

var nativePort = null;
function openNativeApp() {
	let host = 'my.xuexi.app';
	nativePort = chrome.runtime.connectNative(host);
	nativePort.onMessage.addListener(function(msg) {
		// console.log('Receive Native Callback Message:', msg);
	});
	nativePort.onDisconnect.addListener(function() {
		console.log('Disconnect Native App');
		nativePort = null;
	});
}

openNativeApp();

thread = new Thread();

function startXueXi() {
    thread.addTask(new InitTask());
    thread.addTask(new ArticleTask());
    thread.addTask(new RefreshScorePageTask());
    thread.addTask(new ArticleTask());
    thread.addTask(new RefreshScorePageTask());
    thread.addTask(new ArticleTask());
    thread.addTask(new RefreshScorePageTask());
    thread.addTask(new ArticleTask());
    thread.addTask(new RefreshScorePageTask());
    thread.addTask(new ArticleTask());
    thread.addTask(new RefreshScorePageTask());
    thread.addTask(new ArticleTask());
    thread.addTask(new RefreshScorePageTask());
    thread.addTask(new VideoTask());
    thread.start();
}

