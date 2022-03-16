

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

function adjustCols(cols) {
	cols = cols.trim();
	if (cols.charAt(0) == '"') {
		cols = cols.substring(1, cols.length);
	}
	if (cols.charAt(cols.length - 1) == '"') {
		cols = cols.substring(0, cols.length - 1);
	}
	var re = new RegExp('\\s+');
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
	let addOp = $('<input type="text" id = "_ADD_OP_" /> ');
	let opBtn = $('<input type="button" class="submit" id="_MY_ADD_BTN" value="MyAdd" />');
	$('#infoName').after(addOp);
	addOp.after(opBtn);
	addOp.css({backgroundColor: 'bisque'});
	opBtn.click(function() {
		let txt = $('#_ADD_OP_').val();
		let ts = txt.split('\t');
		if (ts.length == 2) {
			$('#_ADD_OP_').val(ts[1]);
			txt = ts[1];
			$('#infoName').focus();
			$('#infoName').val(ts[0]);
			$('#infoName').blur();
		}
		adjustCols(txt);
		window.parent.$('html,body').animate({scrollTop: '1000px'}, 300);
	});
	addOp.focus();
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

