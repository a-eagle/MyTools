
function updateDocText(win, orgText, replaceText) {
	console.log(win, orgText, replaceText);
	let iframe = win.document.getElementById('ueditor_0');
	let bd = iframe.contentDocument.body;
	let cnt = bd.innerHTML;
	let idx = cnt.indexOf(orgText);
	console.log('updateDocText.idx=', idx);
	if (idx > 0) {
		cnt = cnt.replace(orgText, replaceText);
		bd.innerHTML = cnt;
		console.log('修改成功: [',orgText, '] --> [', replaceText, ']');
	} else {
		console.log('修改失败，未找到敏感词：[', orgText, ']');
	}
}

function onSuccess(json, orgText, replaceText) {
	console.log('resp=', json);
	window.DD = json;
	let data = json.DATA.DATA[0];
	let url = 'https://mis.jiujiang.gov.cn/govapp/#/govopendata?Modal=1&channelid=' + data.CHNLID + '&viewid=3&DocId=' + data.DOCID + '&ObjectId=' + data.DOCID +
		'&RecId=' + data.RECID + '&DocType=' + data.DOCTYPE + '&siteid=333&docstatus=yifa&titleField=DOCTITLE&host=https:%252F%252Fmis.jiujiang.gov.cn&metaview=%252Fapp%252Fapplication%252F3%252Fmetaviewdata_addedit.html&dynamicword=true&currrecid=' + data.ORIGINRECID
	console.log('url=', url);
	win = window.open(url, '_blank');
	setTimeout(function() {
		updateDocText(win, orgText, replaceText)
	}, 5000);
}

function searchByDocId(docId, orgText, replaceText) {
	$.ajax({
		url: 'https://mis.jiujiang.gov.cn/gov/gov.do',
		data: 'serviceid=gov_webdocument&methodname=queryDocumentsInQuanbu&OperTime=&DocType=&OnlyMy=1&SiteId=333&SearchFields=%E6%96%87%E6%A1%A3ID&SearchValue=' + docId + '&OrderBy=&PageSize=20&PageIndex=1&TimeField=&FLAGTYPE=0',
		headers: {
			Accept: "application/json, text/plain, */*",
			"content-type": "application/x-www-form-urlencoded",
			formdata: "1"
		},
		type: "POST",
		success: function(rsp) {
			onSuccess(rsp, orgText, replaceText);
		}
	});
}

searchByDocId('6601879', '《义务教育法》', '《中华人民共和国义务教育法》');