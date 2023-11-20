

var curDay = new Date();
var m = curDay.getMonth() + 1;
var d = curDay.getDate();
curDay = '' + curDay.getFullYear() + '-' + (m < 10 ? '0' + m : m) + '-' + (d < 10 ? '0' + d : d);

// $('#div_foot').append('<p> <textarea id="mycols" style="width: 370px; height: 100px;"> </textarea>  <button type="button" class="submit" onclick="myAddVV()"> MY ADD </button> </p>');
$('#div_foot').css({margin: '0 auto'});

window.reset = function() {
	window.location.reload(true);
}

function myAddOneRow(col) {
	$('#col_datagrid').datagrid('appendRow', {
                                    resourceName: col,
                                    fieldType: '1',
                                    fieldLength: '100',
                                    description:'',
                                    fieldPrec: '',
                                    dateType: '',
                                    fieldOpen: '0',
                                    publishTime: curDay,
									publishTime: '',
                                });
}

function adjustCols(cols, sp) {
	cols = cols.trim();
	if (cols.charAt(0) == '"') {
		cols = cols.substring(1, cols.length);
	}
	if (cols.charAt(cols.length - 1) == '"') {
		cols = cols.substring(0, cols.length - 1);
	}
	var re = new RegExp(sp);
	var lines = cols.split(re);
	cols = lines.join('\n');
	
	for (var i = 0; lines && i < lines.length; ++i) {
		if (lines[i].trim() != '')
			myAddOneRow(lines[i].trim());
	}
	
	return cols;
}

function myAddVV() {
	console.log('call myAdd');
	var cols = $('#mycols').val();
	cols = adjustCols(cols);
	$('#mycols').val(cols);
}

(function() {
	let wrap = $('<div style="height: 60px; width: 100%; padding: 10px 30px; background-color: #adbfae;" >  </div>' );
	let addOp = $('<span>字段列表：</span><input type="text" id = "_ADD_OP_"  style="height: 35px; width: 200px; background-color: bisque;"  />  &nbsp;&nbsp; 分割符： <input type="text" id = "__ADD_OP_FG"  style="height: 35px; width: 40px; background-color: bisque;" value="\\s+|、"  />');
	let opBtn = $('<input type="button" class="submit" id="_MY_ADD_BTN" value="添加字段" />');
	addOp.after(opBtn);
	opBtn.click(function() {
		let txt = $('#_ADD_OP_').val();
		let sp = $('#__ADD_OP_FG').val();
		adjustCols(txt, sp);
		// window.parent.$('html,body').animate({scrollTop: '1000px'}, 300);
	});
	wrap.append(addOp).append(opBtn).append(' <br/> <hr style="color: #ff5523;"/>');
	$('#something_3').after(wrap);
})();


// 信息资源格式
// $('resFormat').parentNode.style.backgroundColor = 'bisque';
setTimeout(function() {
	$('#resFormat').combobox('setValue', '2');
}, 1500);
setTimeout(function() {
	$('#resFormatType').combobox('setValue', 'xlsx');
}, 2000);


//关键字
// $N('selfLable').value = $('infoName').value;

// 开放类型
// $('openType').parentNode.style.backgroundColor = 'bisque';
setTimeout(function() {
	$('#openType').combobox('setValue', '0');
}, 1500);

