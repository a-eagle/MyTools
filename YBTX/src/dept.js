function buildDeptUrl(deptName) {
	return 'http://localhost:8020/?bm=' + strToHex(deptName);
}
let depts = [
	'组织部', '教体局', '民政局', '自然资源局', '住建局', '水利局', '农业农村局', 
	'卫健委', '退役军人', '应急管理局', '医保局', '行政审批局', '妇联', '残联',
	'攻坚办', '宣传部', '发改委', '科工局', '司法局', '财政局', '人社局', '生态环境局', 
	'营商办', '交运局', '统计局', '消防', '总工会', '文广旅局', '商务局'
];
for (let dept of depts) {
	console.log(dept, '  ', buildDeptUrl(dept));
}
/*
组织部    http://localhost:8020/?bm=E7BB84E7BB87E983A8
教体局    http://localhost:8020/?bm=E69599E4BD93E5B180
民政局    http://localhost:8020/?bm=E6B091E694BFE5B180
自然资源局    http://localhost:8020/?bm=E887AAE784B6E8B584E6BA90E5B180
住建局    http://localhost:8020/?bm=E4BD8FE5BBBAE5B180
水利局    http://localhost:8020/?bm=E6B0B4E588A9E5B180
农业农村局    http://localhost:8020/?bm=E5869CE4B89AE5869CE69D91E5B180
卫健委    http://localhost:8020/?bm=E58DABE581A5E5A794
退役军人    http://localhost:8020/?bm=E98080E5BDB9E5869BE4BABA
应急管理局    http://localhost:8020/?bm=E5BA94E680A5E7AEA1E79086E5B180
医保局    http://localhost:8020/?bm=E58CBBE4BF9DE5B180
行政审批局    http://localhost:8020/?bm=E8A18CE694BFE5AEA1E689B9E5B180
妇联    http://localhost:8020/?bm=E5A687E88194
残联    http://localhost:8020/?bm=E6AE8BE88194
攻坚办    http://localhost:8020/?bm=E694BBE59D9AE58A9E
宣传部    http://localhost:8020/?bm=E5AEA3E4BCA0E983A8
发改委    http://localhost:8020/?bm=E58F91E694B9E5A794
科工局    http://localhost:8020/?bm=E7A791E5B7A5E5B180
司法局    http://localhost:8020/?bm=E58FB8E6B395E5B180
财政局    http://localhost:8020/?bm=E8B4A2E694BFE5B180
人社局    http://localhost:8020/?bm=E4BABAE7A4BEE5B180
生态环境局    http://localhost:8020/?bm=E7949FE68081E78EAFE5A283E5B180
营商办    http://localhost:8020/?bm=E890A5E59586E58A9E
交运局    http://localhost:8020/?bm=E4BAA4E8BF90E5B180
统计局    http://localhost:8020/?bm=E7BB9FE8AEA1E5B180
消防    http://localhost:8020/?bm=E6B688E998B2
总工会    http://localhost:8020/?bm=E680BBE5B7A5E4BC9A
文广旅局    http://localhost:8020/?bm=E69687E5B9BFE69785E5B180
商务局    http://localhost:8020/?bm=E59586E58AA1E5B180
*/