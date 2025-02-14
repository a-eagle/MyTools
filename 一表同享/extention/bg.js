// CORS
function updateHeaders(hds, name, value) {
	let sname = name.toLowerCase();
	for (let i = 0; i < hds.length; i++) {
		if (hds[i].name.toLowerCase() == sname) {
			hds[i].value = value;
			return;
		}
	}
	hds.push({'name': name, 'value': value});
}

chrome.webRequest.onHeadersReceived.addListener(function(details) {
		let hds = details.responseHeaders;
		updateHeaders(hds, 'Access-Control-Allow-Origin', '*');
		updateHeaders(hds, 'Access-Control-Allow-Credentials', 'true');
		updateHeaders(hds, 'Access-Control-Allow-Methods', '*');
		return {responseHeaders : hds};
	},
	{urls: ['http://10.16.130.57:19005/*', '*://*/*']},
	['responseHeaders','blocking', 'extraHeaders']
);


// 监听发送请求
chrome.webRequest.onBeforeRequest.addListener(
  function(details) {
    //console.log(details);
    //拦截到执行资源后，为资源进行重定向
    //也就是是只要请求的资源匹配拦截规则，就转而执行returnjs.js
    //return {redirectUrl: chrome.extension.getURL("returnjs.js")};
	if (details.url.indexOf('chunk.app.js') >= 0) {
		return {redirectUrl: chrome.extension.getURL("chunk.app.js")};
	}
	else if (details.url.indexOf('chunk.chunk-libs.js') >= 0) {
		return {redirectUrl: chrome.extension.getURL("chunk.libs.js")};
	}
  },
  {
    //配置拦截匹配的url，数组里域名下的资源都将被拦截
    urls: [
		'*://*/*'
    ],
    //拦截的资源类型，在这里只拦截script脚本，也可以拦截image等其他静态资源
    types: ["script"]
  },
  //要执行的操作，这里配置为阻断
  ["blocking"]
);

proc_info = {
	lastLoadTime : 0
};

function mis(tabs) {
	if (tabs.length == 0) {
		return;
	}
	let diff = new Date().getTime() - proc_info.lastLoadTime;
	if (diff <= 5 * 60 * 1000) {
		return;
	}
	let windowId = null;
	for (let i = 0; i < tabs.length; i++) {
		if (tabs[i].url.indexOf('/login') < 0) {
			windowId = tabs[i].windowId;
		}
	}
	proc_info.lastLoadTime = new Date().getTime();
	let url = 'http://10.8.52.17:8088/html-ledger-fe/dist/index.html#/index';
	chrome.tabs.create({url: url, windowId: windowId, active: true}, function(tab) {
		let tabId = tab.id;
		setTimeout(function() {
			chrome.tabs.remove(tabId);
		}, 8000);
	});
}

function work() {
	chrome.tabs.query({windowType: 'normal'}, function(tabs) {
		let ybs = [];
		for (let i = 0; i < tabs.length; i++) {
			if (tabs[i].url.indexOf('//10.8.52.17:8088/') > 0) {
				ybs.push(tabs[i]);
			}
		}
		mis(ybs);
	});
}

//setInterval(work, 1000 * 10);
