// OA收文人员
function getOA_Users() {
    let txt = '中国共产党德安县委员会办公室	冷艳玲	[15170913919];中共德安县委巡察工作领导小组办公室	袁属铱	[17379218873];德安县科学技术协会	阙晓东	[13517929628];德安县文化广电新闻出版旅游局	胡文菁	[19379211275];中国共产党德安县委员会信访局	曹力	[13755207657];德安县人民政府办公室	满令祥	[17368666286];国家税务总局德安县税务局	徐杰	[18720177269];中国共产主义青年团德安县委员会	马雯	[18379250338];德安县水利局	周蕾	[18720203572];德安县工商联	曹哲铭	[15007929900];德安县人力资源和社会保障局	赵昕怡	[17879385760];德安县委员会党校	方婉婷	[15797983593];德安县档案馆	汪光凯	[18170236865];德安县林业局	刘琴	[18879258069];德安县妇女联合会	宋欣怡	[18979260160];德安县红十字会	曾繁宏	[15779231741];德安县气象局	陈超晴	[13030583363];德安县人民代表大会常务委员会办公室	陈佳丽	[18370233923];德安县人民法院	万政	[18879239502];德安县卫生健康委员会	郭金枝	[18770222012];德安县机关事务中心	张馨	[18379249896];德安县医疗保障局	鄢芸靓	[15979957962];德安县消防救援大队	张颖	[17770264119];德安县行政审批局	申婧颖	[17746606255];德安县住房和城乡建设局	黄芳	[18720189316];德安县营商办	吴梦宇	[15270298259];德安县发展和改革委员会	晏茹月	[18370215650];德安县民政局	饶雨昕	[18370112699];中共德安县委机构编制委员会办公室	欧阳敏	[13907029985];德安县司法局	周锦秀	[15270173371];德安县城市管理局	王涵玥	[15107919417];德安县委政法委员会	郭则堃	[18897922929];德安县总工会	桑佩	[18000221801];德安县统计局	蔡玉玲	[17854120408];德安县教育体育局	张熳琦	[19318600730];德安县农业农村局	卢明河	[13879232898];德安县委统战部	钟紫来	[18770233889];德安县退役军人事务局	陈劲	[13370875244];德安县物资公司	戴琳婕	[15170969928];德安县应急管理局	张婉盈	[15170931746];九江市德安生态环境局	杨红	[13767251112];德安县融媒体中心	欧阳雪	[15079245196];江西德安高新技术产业园区管理委员会	吴毓	[19107061607];德安县纪委监委	沈殿宏	[13907025617];德安县人民检察院	彭政	[17679220427];德安县市场监督管理局	闵敏	[18270285618];德安县委社会工作部	桂媛芳	[18779227055];德安县残疾人联合会	郑蒙	[18172923005];德安县审计局	闵燕	[15070241202];德安县供销合作社联合社	陈桂娥	[15779240616];德安县商务局	蒋自慧	[13207025522];德安县自然资源局	李应江	[13672259969];德安县交通运输局	程桂玲	[18160725662];德安县委组织部	曾伟轩	[15779210235];德安县财政局	陈勇	[13979277066];德安县科学技术和工业信息化局	戴幸儿	[19979626917];德安县公安局	黄少敏	[15170298897];德安县委宣传部	万谦	[15279266805]';
    let rows = txt.split(';');
    let data = [];
    for (let row of rows) {
        let item = row.split('\t');
        data.push({dept: item[0], user: item[1], tel: item[2]});
    }
    return data;
}

// 综合协同办公系统 OA
function config_OA() {
    initTableCss_OA();
    let pwds = [
		{title:"德安高新区管委会管理员", user: '吴毓'},
        {title:"德安县编办管理员", user: '欧阳敏/胡楠'},
        {title:"德安县财政局管理员", user: '陈勇'},
        {title:"德安县残联管理员", user: '黄平生/郑蒙'},
        {title:"德安县城管局管理员", user: '黄桐/王涵玥'},
        {title:"德安县发改委管理员", user: '晏茹月'},
        {title:"德安县法院管理员", user: '万政'},
        {title:"德安县妇联管理员", user: '刘娜/宋欣怡'},
        {title:"德安县工商联管理员", user: '曹哲铭'},
        {title:"德安县工业和信息化局管理员", user: '戴幸儿/曾令贵'},
        {title:"德安县公路局管理员", user: '刘梅/周思佳'},
        {title:"德安县公路中心管理员", user: ''},
        {title:"德安县供销社管理员", user: '陈桂娥'},
        {title:"德安县红十字会管理员", user: '肖成梅'},
        {title:"德安县交通运输局管理员", user: '程桂玲/蒋慧'},
        {title:"德安县教体局管理员", user: '谢德阳/张熳琦'},
        {title:"德安县民政局管理员", user: '王玲玲/饶雨昕'},
        {title:"德安县农业农村局管理员", user: '卢明河'},
        {title:"德安县人大管理员", user: '熊夏梓/黄雪松'},
        {title:"德安县人民检察院管理员", user: '彭政'},
        {title:"德安县人社局管理员", user: '黄煜鑫'},
        {title:"德安县融媒体中心管理员", user: '欧阳雪/余文明'},
        {title:"德安县商务局管理员", user: '姜玲/曹思勤'},
        {title:"德安县生态环境局管理员", user: '杨红'},
        {title:"德安县史志办公室管理员", user: '李依'},
        {title:"德安县市场监督管理局管理员", user: '江慧芳'},
        {title:"德安县司法局管理员", user: '周锦秀'},
        {title:"德安县统计局管理员", user: '孙锦珍/蔡玉玲'},
        {title:"德安县团县委管理员", user: '邹紫璇'},
        {title:"德安县退役军人事务局管理员", user: '郭巧缘'},
        {title:"德安县委办管理员", user: '冷艳玲'},
        {title:"德安县委党校管理员", user: '方婉婷/胡珊珊'},
        {title:"德安县委统战部管理员", user: '钟紫来'},
        {title:"德安县委信访局管理员", user: '曹力/陶凤'},
        {title:"德安县委宣传部管理员", user: '郑彤/万谦'},
        {title:"德安县委组织部管理员", user: '曾伟轩'},
        {title:"德安县卫健委管理员", user: '叶俊杰'},
        {title:"德安县文广新旅局管理员", user: '胡文菁/刘维康'},
        {title:"德安县物资公司管理员", user: ''},
        {title:"德安县行政审批局管理员", user: '邹铭/申婧颖'},
        {title:"德安县医疗保障局管理员", user: '张立权/鄢芸靓'},
        {title:"德安县应急管理局管理员", user: '刘依红'},
        {title:"德安县营商办管理员", user: '吴梦宇/袁玲丽'},
        {title:"德安县政法委管理员", user: '苏冰'},
        {title:"德安县政府办管理员", user: '满令祥'},
        {title:"德安县政协办管理员", user: '袁为强'},
        {title:"德安县住建局管理员", user: '黄芳/熊伟'},
        {title:"德安县总工会管理员", user: '刘钊/桑佩'},
        {title:"德安县爱民乡人民政府管理员", user: ''},
        {title:"德安县宝塔乡人民政府管理员", user: ''},
        {title:"德安县车桥镇人民政府管理员", user: ''},
        {title:"德安县丰林镇管理员", user: ''},
        {title:"德安县高塘乡管理员", user: ''},
        {title:"德安县河东乡人民政府管理员", user: ''},
        {title:"德安县林泉乡人民政府管理员", user: ''},
        {title:"德安县磨溪乡人民政府管理员", user: ''},
        {title:"德安县聂桥镇人民政府管理员", user: ''},
        {title:"德安县彭山公益林场管理员", user: ''},
        {title:"德安县蒲亭镇人民政府管理员", user: ''},
        {title:"德安县吴山镇人民政府管理员", user: ''},
        {title:"德安县向阳山生态林场管理员", user: ''},
        {title:"德安县塘山乡管理员", user: ''},
        {title:"德安县邹桥乡人民政府管理员", user: ''},
	];
	let wrap = $('<div style="min-width:300px; background-color: #ffffff; min-height:200px; position:absolute; left: 0; top: 0; z-index: 999999; over-flow:auto;"> </div>');
	let table = $('<table class="my-pwd-table"> </table>');
	for (let i = 0; i < pwds.length; i += 3) {
		let tr = $('<tr height=30> </tr>');
        for (let j = 0; j < 3 && i + j < pwds.length; j++) {
            let title = pwds[i + j].title.replace('管理员', '');
            if (title == '德安县委办')
                title = title.replace('德安', '');
            else
                title = title.replace('德安县', '').replace('德安', '');
            let user = pwds[i + j].user || '';
            if (user) user =  '（' + user + '）';
            let td = $(`<td width=240> ${title}${user} </td>`);
            td.data('info', pwds[i + j]);
            tr.append(td);
        }
		table.append(tr);
	}
	wrap.append(table);
	table.find('td').click(function() {
		table.find('td').removeClass('select');
		$(this).addClass('select');
		let inputs = $('input');
        if (inputs.length < 3)
            return;
		let info = $(this).data('info');
        simulateKeyPress(inputs.get(0), info.title);
        simulateKeyPress(inputs.get(1), 'JJoa@7386');
        if (! inputs.eq(2).val()) {
            // loadDataImageOcr($('form img').get(0), inputs.get(2));
        }
	});
	$(document.body).append(wrap);
    window['WRAP_LOGIN_PWD'] = wrap;
}

function initTableCss_OA() {
	let css = '.my-pwd-table {border: 2px solid #888; border-collapse: collapse; font-size: 16px;} \
			.my-pwd-table td {border: 1px solid #000; padding-left: 10px;} \
			.my-pwd-table .select {background-color: #cfadef; } \
	';
	let style = $("<style>" + css + " </style>");
	$(document.head).append(style);
}

function simulateKeyPress(elem, text) {
    let event = new InputEvent('input', {inputType: 'insertText', data: '', dataTransfer: null, isComposing: false});
    elem.value = text;
    elem.dispatchEvent(event);
}

(function() {
    setInterval(function() {
        let url = window.location.href;
        if (url.indexOf('http://10.100.66.38:2080/?#/login') >= 0) {
            if (window['WRAP_LOGIN_PWD']) {
                window['WRAP_LOGIN_PWD'].show();
            } else {
                config_OA();
            }
        } else {
            if (window['WRAP_LOGIN_PWD']) {
                window['WRAP_LOGIN_PWD'].hide();
            }
        }
    }, 1000);
})();