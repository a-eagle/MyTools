let temp = document.createElement('script');
temp.setAttribute('type','text/javascript');
temp.src = chrome.extension.getURL('jquery-3.6.min.js');
temp.async = false;
document.documentElement.appendChild(temp);

temp = document.createElement('script');
temp.setAttribute('type','text/javascript');
temp.src = chrome.extension.getURL('ajax-hook.js');
temp.async = false;
document.documentElement.appendChild(temp);

temp = document.createElement('script');
temp.setAttribute('type','text/javascript');
temp.src = chrome.extension.getURL('mybase64.js');
temp.async = false;
document.documentElement.appendChild(temp);

temp = document.createElement('script');
temp.setAttribute('type','text/javascript');
temp.src = chrome.extension.getURL('answer-inject-cnt.js');
temp.async = false;
document.documentElement.appendChild(temp);

window.addEventListener("message", function(evt) {
	if (evt.data.cmd == 'CALL_NATIVE') {
		chrome.runtime.sendMessage({cmd: 'CALL_NATIVE', data: evt.data.data});
	}
}, false);