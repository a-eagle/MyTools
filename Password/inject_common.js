function simulateKeyPress(elem, text) {
    let event = new InputEvent('input', {inputType: 'insertText', data: '', dataTransfer: null, isComposing: false});
    elem.value = text;
    elem.dispatchEvent(event);
}

function loadDataImageOcr(imgElem, codeInputElem) {
	let img = $(imgElem).attr('src');
	if (! img) {
		return;
	}
	if (img.substring(0, 11) != 'data:image/') {
		img = getBase64_Image(imgElem);
	}
	let url = 'https://api.vitphp.cn/Yzcode/?img=' + encodeURIComponent(img);
	$.get(url, function(resp) {
		// console.log(resp);
		if (! resp || resp.code != 1) {
			return;
		}
		let code = resp.captcha;
		simulateKeyPress(codeInputElem, code);
	});
}

function getBase64_Image(img) {
	// 创建一个空的Canvas元素
	var canvas = document.createElement("canvas");
	canvas.width = img.width;
	canvas.height = img.height;
	
	// 将图片绘制到Canvas上
	var ctx = canvas.getContext("2d");
	ctx.drawImage(img, 0, 0);
	
	// 获取图片的Base64编码
	var dataURL = canvas.toDataURL("image/png");
	return dataURL;
}