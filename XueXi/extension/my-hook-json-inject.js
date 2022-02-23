
function _doHook(response) {
	let data = response.response;
	console.log(response)
	if (! Array.isArray(data)) {
		return;
	}
	let r = [];
	for (i in data) {
		if (data[i]['type'] == 'tuwen' || data[i]['type'] == 'shipin') {
			r.push(data[i]);
		}
	}
	window.postMessage({cmd: 'GET_DOC_VIDEO_URLS', data: r}, window.location.href);
}

function _loadTiMu(response) {
	let url = response.config.url;
	// 每周答题
	if (url.indexOf('https://pc-proxy-api.xuexi.cn/api/exam/service/practice/pc/weekly/more') >= 0) {
		// https://pc-proxy-api.xuexi.cn/api/exam/service/practice/pc/weekly/more?pageSize=50&pageNo=1
		let data = response.response;
		data = eval('(' + data + ')');
		data = eval('(' + MyBase64.decode(data.data_str) + ')');
		data = data.list;
		let undoTM = []
		for (let i = 0; i < data.length; ++i) {
			let ms = data[i].practices;
			for (let j = 0; j < ms.length; ++j) {
				// 未答的题
				if (ms[j].status == 1) {
					undoTM.push('https://pc.xuexi.cn/points/exam-weekly-detail.html?id=' + ms[j].id);
				}
			}
		}
		
		window.postMessage({cmd: 'GET_WEEKLY_ZUOTI', data: undoTM});
		return;
	}
	
	// 专项答题
	if (url.indexOf("https://pc-proxy-api.xuexi.cn/api/exam/service/paper/pc/list") >= 0) {
		// "https://pc-proxy-api.xuexi.cn/api/exam/service/paper/pc/list?pageSize=50&pageNo=1"
		let data = response.response;
		data = eval('(' + data + ')');
		data = eval('(' + MyBase64.decode(data.data_str) + ')');
		data = data.list;
		let undoTM = [];
		for (let i = 0; i < data.length; ++i) {
			if (data[i].alreadyAnswerNum == 0) {
				undoTM.push('https://pc.xuexi.cn/points/exam-paper-detail.html?id=' + data[i].id);
			}
		}
		window.postMessage({cmd: 'GET_SPECIAL_ZUOTI', data: undoTM});
		return;
	}
	
}

function hook_proxy() {
	ah.proxy({
		onRequest:  function(config, handler) {
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