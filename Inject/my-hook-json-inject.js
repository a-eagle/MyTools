
function _doHook(response) {
	let data = response.response;
	console.log('response ->', response)
}

function hook_proxy() {
	ah.proxy({
		onRequest:  function(config, handler) {
			// console.log('request ->', config);
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
_can2DProto.fillText = function(txt, x, y) {
	_old_can2d_ft.call(this, txt, x, y);
	console.log(txt);
}
