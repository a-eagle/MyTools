
function loadNext() {
	let resp = $.ajax({url: 'http://localhost:5050/get-next', async : false});
	let js = resp.responseJSON;
	if (js.code == 0) {
		loadID(js.data);
	}
}


function loadID(data) {
	let id = data.suggest_2;
	$.ajax({
		url: '/ledger-be/ledger/residents/pageList', type:'post', headers: {authorization: 'Bearer 940fe9d712bd4dd38834a22349c0a072'},
		xhrFields: {withCredentials: true},
		contentType: 'application/json; charset=utf-8',
		data: JSON.stringify({body:{idCard: id},current:1,size:15,latestUpdateType:0,tagIds:[]}),
		success: function(resp) {
			console.log(resp);
			let diff = (Date.now() - startTime) / 1000;
			let mm = diff / 60;
			console.log('run time: ', mm, 'minutes');
			if (resp.code == 200) {
				if (resp.msg && resp.msg.indexOf('登录') >= 0) {
					clearInterval(IIV);
				} else {
					sendToServer(data, resp.data);
				}
			} else {
				clearInterval(IIV);
			}
		}
	});
}


function sendToServer(data, encData) {
	let ddx = window.my_decrypt(encData);
	if (ddx.indexOf('登录') >= 0) {
		clearInterval(IIV);
		return;
	}
	dd = JSON.parse(ddx);
	data.suggest_5 = '';
	console.log(data.id, data.suggest_2, '==>', dd);
	for (let i = 0; i < dd.records.length; i++) {
		let addr = dd.records[i].regionCodeVillage;
		console.log(addr);
		data.suggest_5 += addr + '  ';
	}
	data.info = ddx;
	if (dd.records.length == 0) {
		console.log('  Not Find');
	}
	$.ajax({
		contentType: 'application/json; charset=utf-8', type:'post',
		url: 'http://localhost:5050/save-data', data: JSON.stringify(data), 
		success: function (resp) {
			console.log(resp);
		}
	});
}

//loadNext();
IIV = setInterval(loadNext, 3500);
startTime = Date.now();