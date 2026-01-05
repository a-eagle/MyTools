// 一表同享
function config_一表同享() {
    initTableCss__一表同享();
    let pwds = [
		{title: 'DeAn003', name: 'DeAn003', pwd: 'Deann@2024', 'desc': ''},
        {title: 'ME', name: '18879269788', pwd: 'GaoYan@2014', 'desc': ''},
		{title: '乡镇测试员', name: 'xz001', pwd: 'Ysjx@2024!@', 'desc': ''},
		{title: '默认密码', name: '', pwd: 'Ybtx2023!!@#', 'desc': ''},

		{title: '自定义', name: '', pwd: '', 'desc': ''},
	];
	let wrap = $('<div style="min-width:300px; background-color: #fff; min-height:200px; position:absolute; left: 0; top: 0; z-index: 999999;"> </div>');
	let table = $('<table class="my-pwd-table"> </table>');
	for (let i = 0; i < pwds.length; i++) {
		let tr = $('<tr height=30> </tr>');
		tr.data('info', pwds[i]);
		tr.append($(`<td width=40> ${i + 1} </td>`));
		tr.append($(`<td width=140> ${pwds[i].title} </td>`));
		if (pwds[i].title == '自定义') {
			tr.append($(`<td width=140> <input id='zdy_name' value='${pwds[i].name}'/>  </td>`));
			tr.append($(`<td width=140> <input id='zdy_pwd' value='${pwds[i].pwd}'/> </td>`));
		} else {
			tr.append($(`<td width=140> ${pwds[i].name} </td>`));
			tr.append($(`<td width=140>  </td>`));
		}
		table.append(tr);
	}
	wrap.append(table);
	table.find('tr').click(function() {
		table.find('tr').removeClass('select');
		$(this).addClass('select');
		let inputs = $('form input');
        if (inputs.length < 2)
            return;
		let info = $(this).data('info');
		// inputs[0].value = info.name;
		// inputs[1].value = info.pwd;
		if (info.title == '自定义') {
			simulateKeyPress(inputs.get(0), $('#zdy_name').val().trim());
			simulateKeyPress(inputs.get(1), $('#zdy_pwd').val().trim());
		} else {
			simulateKeyPress(inputs.get(0), info.name);
			simulateKeyPress(inputs.get(1), info.pwd);
		}
		loadImageOcr();
	});
	$(document.body).append(wrap);
    window['WRAP_LOGIN_PWD'] = wrap;
}

function initTableCss__一表同享() {
	let css = '.my-pwd-table {border: 2px solid #888; border-collapse: collapse; font-size: 16px;} \
			.my-pwd-table td {border: 1px solid #000; padding-left: 10px;} \
			.my-pwd-table tr.select {background-color: #cfadef; } \
	';
	let style = $("<style>" + css + " </style>");
	$(document.head).append(style);
}

function simulateKeyPress(elem, text) {
    let event = new InputEvent('input', {inputType: 'insertText', data: '', dataTransfer: null, isComposing: false});
    elem.value = text;
    elem.dispatchEvent(event);
}

function loadImageOcr() {
	let codeInput = $('form input').get(2);
	if (codeInput.value) {
		return;
	}
	let img = $('form img').attr('src');
	if (! img) {
		return;
	}
	console.log('Yzcode=', img);
	let url = 'http://localhost:8080/Yzcode?img=' + encodeURIComponent(img);
	$.get(url, function(resp) {
		// console.log(resp);
		if (! resp || resp.code != 0) {
			return;
		}
		let code = resp.captcha;
		simulateKeyPress(codeInput, code);
	});
}

(function() {
    setInterval(function() {
        let url = window.location.href;
        if (url.indexOf('http://10.8.52.17:8088/html-ledger-fe/dist/index.html#/login') >= 0) {
            if (window['WRAP_LOGIN_PWD']) {
                window['WRAP_LOGIN_PWD'].show();
            } else {
                config_一表同享();
            }
        } else {
            if (window['WRAP_LOGIN_PWD']) {
                window['WRAP_LOGIN_PWD'].hide();
            }
        }
		if (url.indexOf('http://10.8.52.17:8088/html-ledger-fe/dist/index.html#/lockScreen') >= 0) {
			let inputs = $('form input');
			if (inputs.length == 1)
				simulateKeyPress(inputs.get(0), 'Ysjx@2024!@');
		}
    }, 1000);
})();