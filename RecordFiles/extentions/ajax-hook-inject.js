
HOST_NAME = '10.8.52.17'


function sendToServer(resp) {
	let req = resp.config;
	let url = req.url.trim();
	let curPage = new URL(window.location.href);
	if (url.indexOf(curPage.host) < 0) {
		let newUrl = curPage.origin;
		if (url.charAt(0) == '/') { // root path
			newUrl += url;
		} else if (curPage.pathname == '/' || !curPage.pathname) { // cur page is root path
			newUrl += '/' + url;
		} else { // relative path
			let li = curPage.pathname.lastIndexOf('/');
			let pp = curPage.pathname.substring(0, li + 1);
			newUrl += pp;
			newUrl += url;
		}
		url = newUrl;
	}
	let um = new URL(url);
	if (um.hostname != HOST_NAME) {
		return;
	}

	let ct = resp.headers['content-type'] || resp.headers['Content-Type']
	let data = {'method': req.method, 'headers': JSON.stringify(req.headers), 'url': url, 'type': 'xhr', 'body': req.body, 'response': resp.response, 'contentType': ct};
	$.post({url: 'http://127.0.0.1:5585/save-xhr', contentType: "application/json", data: JSON.stringify(data),
		success: function(response) {
			// console.log('Success, ',data, response);
		}, error: function(response) {
			console.log('Error: ', data, response);
		}
	});
}

function _doHook(response) {
	let data = response.response;
	let len = response.headers['content-length'];
	console.log('Hook response ==>>', response);
	sendToServer(response);
}

function hook_proxy() {
	ah.proxy({
		onRequest:  function(config, handler) {
			if (config.url.indexOf('127.0.0.1') < 0 && config.url.indexOf('localhost') < 0) {
				console.log('Hook request ->', config);
			}
			handler.next(config);
		},
		
		onError: function(err, handler) {
			handler.next(err);
		},
		
		onResponse:function(response, handler) {
			// _loadTiMu(response);
			if (response.config.url.indexOf('127.0.0.1') < 0 && response.config.url.indexOf('localhost') < 0) {
				_doHook(response);
			}
			handler.next(response)
		},
	});
}

hook_proxy();
console.log('in hook :', window.location.href)

var _can2DProto = CanvasRenderingContext2D.prototype;
var _old_can2d_ft = _can2DProto.fillText;
let _txtAll = ''
let doTtt = false;
_can2DProto.fillText = function(txt, x, y) {
	_old_can2d_ft.call(this, txt, x, y);
	let v = txt.replace(/[\r\n]/g, '');
	// console.log(v);
	_txtAll += v;
	if (! doTtt) {
		doTtt = true;
		setTimeout(function() {
			console.log(_txtAll);
		}, 4000);
	}
}
