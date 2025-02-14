
function _doHook(response) {
	console.log('Hook response ==>>', response);
	let data = response.response;
	try {
		let js = JSON.parse(data);
		if (js.data && window['my_decrypt']) {
			let de = window['my_decrypt'](js.data);
			console.log(de);
		}
	} catch (error) {
	}
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