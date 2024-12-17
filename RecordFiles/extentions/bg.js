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
	{urls: ['*://*/*']},
	['responseHeaders','blocking', 'extraHeaders']
);


// 监听发送请求 
//    '*://*/*'  所有地址
function filterHeaders(details) {
	for (var i = 0; i < details.requestHeaders.length; ++i) {
		if (details.requestHeaders[i].name === 'User-Agent') {
			details.requestHeaders.splice(i, 1);
			break;
		}
	}
	return {requestHeaders: details.requestHeaders};
}

// types: ["main_frame", "sub_frame", "stylesheet", "script", "image", "font", "xmlhttprequest", "websocket", "other"]
/*
chrome.webRequest.onBeforeRequest.addListener(
	function(details) {
		// console.log(details);
		// redirectUrl 只能在onBeforeRequest中使用
		//return {redirectUrl: chrome.extension.getURL("returnjs.js")};
	},
	{
		urls: [
			"<all_urls>"
		],
		types: ["main_frame", "sub_frame", "stylesheet", "script", "image", "font"]
	},
	["blocking"]
);
*/

// only "websocket"
chrome.webRequest.onBeforeRequest.addListener(
	function(details) {
		console.log('websocket:', details);
	},
	{
		urls: [
			"<all_urls>"
		],
		types: ["websocket"]
	},
	["blocking"]
);

resourcs = {}

function buildUrls() {
	let urls = [];
	for (let i = 0; i < __filter_hosts__.length; i++) {
		urls.push('http://' + __filter_hosts__[i] + '/*');
		urls.push('https://' + __filter_hosts__[i] + '/*');
	}
	console.log('filter-urls:', urls);
	return urls;
}

chrome.webRequest.onBeforeSendHeaders.addListener(
	function(details) {
		console.log(details);
		if (details.url && details.url.indexOf('chrome://') == 0) {
			return;
		}
		resourcs[details.url] = details;
		sendToLocalServer_File(details);
		// console.log(details);
		//return {redirectUrl: chrome.extension.getURL("returnjs.js")};
	},
	{
		//配置拦截匹配的url，数组里域名下的资源都将被拦截
		urls: buildUrls(), //"<all_urls>"
		types: ["main_frame", "sub_frame", "stylesheet", "script", "image", "font"]
	},
	//要执行的操作，这里配置为阻断
	["blocking", "requestHeaders"]
);

// $.get('http://10.8.52.17:8088/html-ledger-fe/dist/index.html#/datamart/exchange')