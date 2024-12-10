
HOST_NAME = '10.8.52.17' // 不需要带端口


function sendToServer(resp) {
	let req = resp.config;
	let url = req.url.trim();
	let curPage = new URL(window.location.href);
	let newUrl = new URL(url, curPage);
	if (newUrl.hostname != HOST_NAME) {
		return;
	}
	url = newUrl.href;

	let ct = resp.headers['content-type'] || resp.headers['Content-Type']
	let data = {'method': req.method, 'headers': JSON.stringify(req.headers), 'url': url, 'type': 'xhr',
				'body': req.body, 'response': resp.response, 'contentType': ct, 'respHeaders': JSON.stringify(resp.headers)};
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
