// 下载表格中的数据
function loadTable() {
	let trs = $($0).find('tr');
	let datas = [];
	for (let tr of trs) {
		let tds = $(tr).find('td'); 
		let row = [];
		let tdsIdx = [0, 1, 3, 9, 11];
		for (let idx of tdsIdx) { 
			let colTxt = $(tds[idx]).text().trim(); 
			colTxt = colTxt.replace('"', '');
			row.push(colTxt); 
		}
		datas.push(row.join('\t')); 
	};
	console.log(datas.join('\n'));
}