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
    console.log(details);
    //拦截到执行资源后，为资源进行重定向
    //也就是是只要请求的资源匹配拦截规则，就转而执行returnjs.js
    //return {redirectUrl: chrome.extension.getURL("returnjs.js")};
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
