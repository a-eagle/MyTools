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

function sendToServer(details) {
	let type = details.type;
	if (details.type == 'main_frame' || details.type == 'sub_frame') {
		type = 'frame'
	} else if (details.type == 'stylesheet' || details.type == 'script'  || details.type == 'image' || details.type == 'font') {
		type = 'static'
	} else if (details.type == 'xmlhttprequest') {
		type = 'xhr'
	} else {
		return
	}
	let data = {'method': details.method, 'headers': JSON.stringify(details.requestHeaders), 'url': details.url, 'type': type, 'body': ''};
	$.post({url: 'http://127.0.0.1:5585/download-file', contentType: "application/json", data: JSON.stringify(data), 
		success: function(response) {
			// console.log('Success, ',data, response);
		}, error: function(response) {
			console.log('Error: ', data, response);
		}
	});
}

chrome.webRequest.onBeforeSendHeaders.addListener(
	function(details) {
		if (! details.initiator || details.initiator.indexOf('chrome://') == 0) {
			console.log(details);
			return;
		}
		resourcs[details.url] = details;
		sendToServer(details);
		// console.log(details);
		//return {redirectUrl: chrome.extension.getURL("returnjs.js")};
	},
	{
		//配置拦截匹配的url，数组里域名下的资源都将被拦截
		urls: [
			"http://10.8.52.17:8088/*"
			//"<all_urls>"
		],
		types: ["main_frame", "sub_frame", "stylesheet", "script", "image", "font"]
	},
	//要执行的操作，这里配置为阻断
	["blocking", "requestHeaders"]
);

// $.get('http://10.8.52.17:8088/html-ledger-fe/dist/index.html#/datamart/exchange')