var proc_info = {
	isLogined : false,
	lastTime : 0,
	windowId : null,
};

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
	let cmd = request['cmd'];
    let data = request['data'];
	let rspData = '';
	if (cmd == 'CHECK_LOGINED') {
		proc_info.isLogined = data.logined;
		proc_info.lastTime = new Date().getTime();
		getWindowId();
		console.log('CHECK_LOGINED :', new Date());
	}
	if (sendResponse) {
		sendResponse(rspData);
	}
});

function getWindowId(cb) {
	proc_info.windowId = null;
	chrome.windows.getAll({populate : true}, function(windows) {
		for (i in windows) {
			let win = windows[i];
			let winId = win.id;
			let tabs = win.tabs;
			for (j in tabs) {
				if (tabs[j].url.indexOf('://10.97.10.42:8082/') >= 0) {
					proc_info.windowId = winId;
					if (cb) cb();
					return;
				}
			}
		}
	});
}

function checkTime() {
	if (proc_info.lastTime == 0 || !proc_info.isLogined) {
		return;
	}
	let curTime = new Date().getTime();
	if (curTime - proc_info.lastTime < 5 * 60 * 1000) { // 5 minuts
		return;
	}
	
	let prop = {url: 'http://10.97.10.42:8082/govportal/zyNav/resourcecat!getInfo.action', active: false};
	if (proc_info.windowId) {
		prop.windowId = proc_info.windowId;
	}
	chrome.tabs.create(prop, function(tab) {
		console.log('open tab :', new Date());
		setTimeout(function() {
			chrome.tabs.remove(tab.id);
			console.log('close tab :', new Date());
		}, 10 * 1000);
	});
}

setInterval(checkTime, 1 * 60 * 1000);