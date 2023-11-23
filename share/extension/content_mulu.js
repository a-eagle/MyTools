
console.log(window.location)

// 注册目录

function $(id) {
	return document.getElementById(id);
}

function $N(name) {
	return document.getElementsByName(name)[0];
}

// 信息资源名称
// $('infoName').style.backgroundColor = 'bisque';

// 信息资源摘要
$('infoName').addEventListener('blur', function() {
	let v = $('infoName').value;
	if (! v) return;
	v = v.trim();
	if (v.charAt(0) == '"') {
		v = v.substring(1, v.length);
	}
	if (v.charAt(v.length - 1) == '"') {
		v = v.substring(0, v.length - 1);
	}
	v = v.trim();
	
	// 信息资源摘要
	$('infoName').value = v;
	
	// 摘要
	$('description').value = v;
	// 关键字
	v = v.replace(/[、（）()]/g, '')
	$('selfLable').value = v.substring(0, 10);
});


// $N('openType').value = '0';
// $N('openType').previousElementSibling.previousElementSibling.value =  '不可对社会开放';

// 涉密
$N('security').value = '0';
$N('security').previousElementSibling.previousElementSibling.value =  '否';

// 共享类型
$N('shareClassId').value = '402882a75885fd150158860e3d170006';
$N('shareClassId').previousElementSibling.previousElementSibling.value =  '有条件共享';

//共享条件
$('shareCondition').value = '依申请';

//共享方式
$N('shareTypeName').value = '4028829d44f8223f0144f87555540001';
$N('shareTypeName').previousElementSibling.previousElementSibling.value =  '数据交换';


//更新周期
$('radio_4').checked = true;

// 所属系统
$N('systemId').value = '0';
$N('systemId').previousElementSibling.previousElementSibling.value =  '手工';



var temp = document.createElement('script');
temp.setAttribute('type','text/javascript');
// temp.src = chrome.extension.getURL('chrome-extension://eklpleaofjfknkhadfmiddbpmaigodpp/inject2.js');
temp.src = chrome.extension.getURL('inject_mulu.js');
document.head.appendChild(temp);





