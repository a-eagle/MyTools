function buildView() {
	// $('.action-row').prepend('<button type="button" class="ant-btn" style="width: 100px; height:40px; margin-left: 300px;" onclick="autoAnswer()" style="margin-right: 40px; height: 30px;" >自动答题</button> ');
	$('.layout-header').hide();
	$('.layout-footer').hide();
}

var _questions = null;
var _qsIdx = 0;

function checkMask() {
	console.log('checkMask IN');
	var mask = $('#nc_mask');
	if (mask.length != 1) {
		console.log('checkMask A ', mask.length);
		setTimeout(checkMask, 3000);
		return;
	}
	if (! mask.hasClass('nc-mask-display')) {
		console.log('checkMask B ', mask);
		setTimeout(checkMask, 3000);
		return;
	}
	
	var box = $('#nc_1_n1z');
	if (box.length == 0) {
		console.log('checkMask C ', box);
		setTimeout(checkMask, 3000);
		return;
	}
	var boxRect = box.get(0).getBoundingClientRect();
	var bg = $('#nc_1_n1t');
	var bgRect = bg.get(0).getBoundingClientRect();
	var dstRect = 'MOVE_MASK ' + parseInt(boxRect.left) + ' ' + parseInt(boxRect.top) + ' ' + parseInt(boxRect.width) + ' ' + parseInt(boxRect.height) + ' ' + parseInt(bgRect.width) + " ";
	var msg = {cmd: 'CALL_NATIVE', data: dstRect};
	console.log(dstRect);
	window.postMessage(msg);
	
	// setTimeout(checkMask, 8000);
}

$(document).ready( function() {
	setTimeout(function() {
		buildView();
	}, 1500);

	setTimeout(function () {
		window.postMessage({ cmd: 'CALL_NATIVE', data: 'CLICK  100 300' });
	}, 2500);

	setTimeout(function () {
		autoAnswer();
	}, 4000);
	
	setTimeout(checkMask, 5000);
});

function _closeWin() {
	setTimeout(function() {
			/* window.close();*/
		}, 120 * 1000);
}


function autoAnswer() {
	if (! _questions) {
		setTimeout(autoAnswer, 300);
		return;
	}
	console.log('autoAnswer ', _qsIdx);
	if (_qsIdx >= _questions.length) {
		console.log('close window');
		_closeWin();
		return;
	}
	let q = _questions[_qsIdx];
	if (! q['correct']) {
		autoAnswer_1(q);
		return;
	}

	let answer = q.correct;
	
	if (q.questionDisplay == 1 || q.questionDisplay == 2) {
		// 1:单选  2:多选
		let ans = $('.q-answers .q-answer');
		for (i in answer) {
			let v = answer[i].value;
			let idx = "ABCDEFG".indexOf(v);
			if (idx >= 0) {
				randMoveMouse();
				ans.eq(idx).trigger('click');
			}
		}
		tryClickNextWait();
	} else if (q.questionDisplay == 4) {
		// 填空
		let input = $('.q-body input');
		for (let i = 0; i < input.length; ++i) {
			function rrm() {
				input.eq(i).focus();
				input.eq(i).val(answer[i].value);
				randMoveMouse();
				triggerInput(input.get(i));
			}
			setTimeout(rrm, 2000 * i);
		}
		
		tryClickNextWait();
	}
}

function tryClickNextWait() {
	let ttm = 3000 + Math.random() * 3000;
	setTimeout(tryClickNext, ttm);
}

function tryClickNext() {
	var btn = $('.action-row > button:eq(0)');
	if (btn.attr('disabled')) {
		let fn = $('.action-row > button:eq(1)');
		if (fn.length == 1) {
			fn.click();
			_closeWin();
		} else {
			setTimeout("tryClickNext()", 1500);
		}
	} else {
		++_qsIdx;
		setTimeout(function() {$('.action-row > button:eq(0)').click();}, 1500);
		setTimeout("autoAnswer()", 5500);
	}
}

function tq(str) {
	if (! str)
		return str;
	return str.replaceAll(/[、,.;。（）()；：:！!【】\[\]？?"“”'\s]/g, '');
}

function getAnswers(desc) {
	let val = [];
	let re = /\<font\s+color="red"\>([^<]+)\<\/font\>/ig
	while (r = re.exec(desc)) {
		val.push(r[1]);
	}
	return val;
}

function autoAnswer_1(question) {
	let desc = question.questionDesc;
	let body = question.body;
	let opts = question.answers;
	// _qsIdx
	
	//  questionDisplay 1: 单选 2:多选 4:填空
	if (question.questionDisplay == 4) {
		// 填空
		let input = $('.q-body  input');
		input.focus();
		let ans = getAnswers(desc);
		input.val(ans[0]);
		if (! input.val()) {
			// 没找到答案，随便填一答案
			input.val('Hello');
		}
		randMoveMouse();
		triggerInput(input.get(0));
		tryClickNextWait();
	} else if (question.questionDisplay == 1 || question.questionDisplay == 2) {
		// 单选  // 多选
		let ans = getAnswers(desc);
		let foreSelAll = ans.length >= opts.length;
		let clickNum = 0;
		for (let i = 0; i < opts.length; ++i) {
			if (foreSelAll) {
				randMoveMouse();
				$('.q-answers .q-answer').eq(i).trigger('click');
				clickNum++;
			} else {
				if (ans.indexOf(opts[i].content) >= 0) {
					randMoveMouse();
					$('.q-answers .q-answer').eq(i).trigger('click');
					clickNum++;
				}
			}
		}
		if (clickNum == 0) {
			// 没找到答案，随便选择一答案
			randMoveMouse();
			$('.q-answers .q-answer').eq(0).trigger('click');
		}
		tryClickNextWait();
	}
}


function triggerInput(elem, data) {
	window.postMessage({cmd: 'CALL_NATIVE', data: 'PRESS_SPACE' });
}

function randMoveMouse() {
	window.postMessage({cmd: 'CALL_NATIVE', data: 'RAND_MOUSE_MOVE' });
}

function doZuoTi_A(res) {
	let txt = res.response;
	let obj = eval('(' + txt + ')');
	let data_str = MyBase64.decode(obj.data_str);
	// console.log('data_str = ', data_str);
	let qs = eval('(' + data_str + ')');
	// console.log('qs = ', qs);
	_questions = qs.questions;
	for (i in qs.questions) {
		let q = qs.questions[i];
		// questionDisplay 1: 单选 2:多选 4:填空
	}
	console.log('questions = ', _questions);
	data_str = MyBase64.encode(JSON.stringify(_questions));
	obj.data_str = data_str;
	txt = JSON.stringify(obj);
	// res.response = txt;
	// console.log('after response = ', txt);
}


function hook_ajax() {
	if (! window['ah']) {
		setTimeout(hook_ajax, 100);
		return;
	}
	ah.proxy({
		onRequest:  function(config, handler) {
			// console.log('my proxy request = ', config)
			handler.next(config)
		},
		
		onError: function(err, handler) {
			handler.next(err);
		},
		
		onResponse:function(response, handler) {
			let url = response.config.url;
			// console.log('my proxy response = ', response);
			us = [
				'https://pc-proxy-api.xuexi.cn/api/exam/service/common/deduplicateRandomSearchV3', // 每日答题
				"https://pc-proxy-api.xuexi.cn/api/exam/service/detail/queryV3", // 每周答题  专项答题
			];
			for (i in us) {
				if (url.indexOf(us[i]) >= 0) {
					console.log('my proxy response A = ', response);
					doZuoTi_A(response);
				}
			}
			handler.next(response)
		},
	});
}

hook_ajax();


