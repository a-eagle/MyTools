function initTableCss_目录治理() {
	let css = '.my-pwd-table {border: 2px solid #888;} \
			.my-pwd-table td {border: 1px solid #000; padding-left: 10px;} \
			.my-pwd-table tr.select {background-color: #cfadef; } \
			b {color: #f00;} \
	';
	let style = $("<style>" + css + " </style>");
	$(document.head).append(style);
}

function config_目录治理(url) {
	if (url.indexOf('http://10.8.54.18/ebpm-web/frame/pages/login/login') < 0)
		return;
	initTableCss_目录治理();
	let pwds = [
		{title: '数据局（编制）', name: 'daxqzsj', pwd: 'Admin@12345', 'lxr': ''},
		// {title: '数据局（系统目录审核）', name: 'daxqzsjxtshy', pwd: 'Admin@1234', 'lxr': ''},
		// {title: '数据局（职责目录审核、数据目录审核、三清单审核）', name: 'daxqzsjmlshy', pwd: 'Admin@1234', 'lxr': ''},
		
		{title:'生态环境局', name:'jjsdasthjj', pwd:'Dean@4667668s', 'lxr': '李昱炜'},
		{title: '科工局', name: 'daxkxjshgyxxhj', pwd: 'Aa46665060@', 'lxr': '曾令贵'},
		{title:'市场监督管理局', name:'daxscjdglj', pwd:'Dasjj@4667701', 'lxr': '闵敏'},
		{title:'---药监局', name:'德安市监药品、医疗器械与化妆品监督管理股', pwd:'Sjj123456*', 'lxr': '闵敏'},
		{title:'农业农村局', name:'daxnyncj', pwd:'Daxnyncj@4332930', 'lxr': '冯智东'},
		{title:'自然资源局', name:'daxzrzyj', pwd:'Da123456@', 'lxr': '钟天乾'},
		{title:'财政局', name:'daxczgz', pwd:'Admin@1234', 'lxr': ''},
		{title:'--国有资产监督管理委员会', name:'daxgyzcjdglwyh', pwd:'Admin@12345', 'lxr': '蔡孝荣'},
		{title:'金融监管局', name:'gjjrjdglzjjjsfjdaxzj', pwd:'Admin@12345', 'lxr': '郝能全 / <b>吴彬</b>(183 7011 0029)'},
		{title:'医疗保障局', name:'daxylbzj', pwd:'Daxylbzj@1234', 'lxr': '闵雪梅(休产假)  / <b>夏淑琴</b>'},
		{title:'教育体育局', name:'daxjyhtyj', pwd:'Admin@12345', 'lxr': '谢德阳'},
		{title:'气象局', name:'daxqxj', pwd:'Daxqxj@1234', 'lxr': '陈超晴'},
		{title:'县委办', name:'daxwbgs', pwd:'Daxwb@1234', 'lxr': ''},
		{title:'--档案局', name:'daxdaj', pwd:'Dadaj@1234', 'lxr': '程燕'},
		{title:'消防救援大队', name:'daxxfjydd', pwd:'Daxf@2025', 'lxr': '彭小蜜'},
		
		{title:'', name:'', pwd:'', 'lxr': ''},
		{title:'编办', name:'zgjjsdaxwjgbzwyhbgs', pwd:'Bb@4332938', 'lxr': '易春宾'},
	];
	let wrap = $('<div style="min-width:300px; background-color: #fff; min-height:200px; position:absolute; left: 0; top: 0;"> </div>');
	let table = $('<table class="my-pwd-table"> </table>');
	for (let i = 0; i < pwds.length; i++) {
		let tr = $('<tr height=30> </tr>');
		tr.data('info', pwds[i]);
		tr.append($(`<td width=40> ${i + 1} </td>`));
		tr.append($(`<td width=140> ${pwds[i].title} </td>`));
		// tr.append($(`<td width=140> ${pwds[i].name} </td>`));
		tr.append($(`<td width=140> ${pwds[i].lxr} </td>`));
		table.append(tr);
	}
	wrap.append('初始密码为Admin@123<br/>');
	wrap.append(table);
	table.find('tr').click(function() {
		table.find('tr').removeClass('select');
		$(this).addClass('select');
		let inputs = $('#accountLogin input');
		let info = $(this).data('info');
		inputs[0].value = info.name;
		inputs[1].value = info.pwd;
	});
	$(document.body).append(wrap);
}

(function() {
	let url = window.location.href || '';
	let i = url.indexOf('?');
	if (i > 0) {
		url = url.substring(0, i);
	}
	config_目录治理(url);
})();