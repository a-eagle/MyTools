_depts = """政府办
发改委
教体局
科技局
工信局
公安局
民政局
司法局
财政局
人社局
自然资源局
生态局
住建局
交运局
水利局
农业农村局
商务局
文广新旅局
卫健委
审计局
应急管理局
退役军人事务局
统计局
林业局
市监局
乡村振兴局
医保局
城管局
高新区
政务服务中心
税务局
气象局
蒲亭镇
宝塔乡
河东乡
丰林镇
高塘乡
林泉乡
聂桥镇
磨溪乡
吴山镇
爱民乡
邹桥乡
车桥镇
塘山乡
彭山公益林场
向阳山生态林场
信息办
"""

depts = _depts.splitlines()
depts_bm = depts[0: 32]
depts_xz = depts[32: ]
#行政执法
depts_xzzf = "政府办 发改委 教体局 工信局 公安局 民政局 司法局 财政局 人社局 自然资源局 生态局 住建局 交运局 水利局 农业农村局 文广新旅局 卫健委 审计局 应急管理局 统计局 林业局 市监局 乡村振兴局 城管局 气象局".split()