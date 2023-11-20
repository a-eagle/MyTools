function $(id) {
	return document.getElementById(id);
}

// $('resourceName').value = '查询';

$('serviceUrl_disabled').value = 'http://10.119.81.36:8058/RestService/rest/api/';

$('serviceVersion').value = '1.0';

$('callFrequency').value = '50';

$('suppotUnit').value = '德安信息办';
$('supportUnitContact').value = '高炎';
$('supportUnitPhone').value = '18879269788';

// $('desc').value = '返回全部数据';

var cur = document.getElementsByName('interfaceType')[0];
cur.value = 'REST';
cur.previousElementSibling.previousElementSibling.value =  'REST';

cur = document.getElementsByName('openType')[0];
cur.value = '0';
cur.previousElementSibling.previousElementSibling.value =  '0';

cur = document.getElementsByName('procotol')[0];
cur.value = '1';
cur.previousElementSibling.previousElementSibling.value =  '1';


cur = document.getElementsByName('authOrizattionMode')[0];
cur.value = '2';
cur.previousElementSibling.previousElementSibling.value =  '2';


var cur = $('infoName');
cur.addEventListener('blur', function() {
	var t = cur;
	$('resourceName').value = '查询' + t.value;
});


