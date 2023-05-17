
function _doHook(response) {
	let data = response.response;
	let len = response.headers['content-length'];
	if (! len) {
		return;
	}
	// len = parseInt(len);
	// if (len > 500) {
	console.log('Hook response ->', response)
	// }
}

function hook_proxy() {
	ah.proxy({
		onRequest:  function(config, handler) {
			console.log('Hook request ->', config);
			handler.next(config)
		},
		
		onError: function(err, handler) {
			handler.next(err);
		},
		
		onResponse:function(response, handler) {
			// _loadTiMu(response);
			_doHook(response);
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
