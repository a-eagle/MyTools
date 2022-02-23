chrome.devtools.panels.create('MyPanel', 'images/icon.png', 'panel.html', function(panel) {
	
});

/*
// 与后台页面消息通信-长连接
const port = chrome.runtime.connect({name: 'devtools'});

// 监听后台页面消息
port.onMessage.addListener((message) => {
    
});


// 往后台页面发送消息
port.postMessage({
    name: 'original',
    tabId: chrome.devtools.inspectedWindow.tabId
});
*/

/*
chrome.devtools.network.onRequestFinished.addListener(function(request) {
	console.log(request);
	let url = request.request.url;
	if (! url) {
		return;
	}
	if (url.indexOf('www.xuexi.cn') < 0) {
		return;
	}
	request.getContent(function(content, encoding) {
		msg = {"cmd": "receive-request-data" ,"content": content, "encoding": encoding, "request": request};
		chrome.runtime.sendMessage(msg);
	});
});

*/