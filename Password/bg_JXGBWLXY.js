// 江西干部网络学院

// chrome.webRequest.onHeadersReceived.addListener(
//     function(details) {
//         let hds = details.responseHeaders;
//         updateHeaders(hds, 'Access-Control-Allow-Origin', '*');
//         updateHeaders(hds, 'Access-Control-Allow-Credentials', 'true');
//         updateHeaders(hds, 'Access-Control-Allow-Methods', '*');
//         return {responseHeaders : hds};
//     },
//     {urls: ['https://study.jxgbwlxy.gov.cn/*']},
//     ['responseHeaders','blocking', 'extraHeaders']
// );

var proc_info_干部学院 = {
    requests: {},
    tasks: {},
    urlTasks: {},
    thread : 0,
}

function addRequest(type, details) {
    if (! details.initiator || details.initiator.indexOf('chrome-extension://') >= 0) {
        return;
    }
    if (details.tabId <= 0) {
        return;
    }
    // console.log(type, details);

    let req = proc_info_干部学院.requests[details.requestId];
    if (! req) {
        req = {method: details.method, requestBody: null, url: details.url, requestHeaders: null};
        proc_info_干部学院.requests[details.requestId] = req;
    }
    if (details.requestBody) {
        req.requestBody = details.requestBody;
    }
    if (details.requestHeaders) {
        req.requestHeaders = details.requestHeaders;
    }
    if (type == 'onBeforeSendHeaders') {
        // setTimeout(sendRequest, 1000, req);
    }
}

function sendRequest(req) {
    let headers = {};
    for (let it of req.requestHeaders) {
        if (it.name.indexOf('sec-') >= 0 || it.name.toLowerCase() == 'user-agent')
            continue;
        headers[it.name] = it.value;
    }
    let data = '';
    let buffer = req.requestBody.raw[0].bytes;
    if (req.requestBody) {
        let decoder = new TextDecoder('utf-8');
        data = decoder.decode(buffer);
    }
    $.ajax({
        url: req.url,
        method: req.method,
        dataType: 'json',
        headers: headers,
        data: data,
        success: function(resp) {
            addTasks(resp, req);
        },
        error: function(xhr, status, error) {
            console.error(error);
        }
    });
}

function getTaskUrl(task) {
    return `https://study.jxgbwlxy.gov.cn/courseDetailsNew?id=${task.coursewareId}&coursewareType=${task.resourceType}`
}

function addTasks(resp, req) {
    if (resp.code != 0)
        return;
    let data = resp.data.records;
    for (let d of data) {
        proc_info_干部学院.tasks[d.id] = d;
    }
}

// 监听发送请求
chrome.webRequest.onBeforeSendHeaders.addListener( //  onBeforeRequest  onBeforeSendHeaders
    function(details) {
        // console.log('[onBeforeSendHeaders]', details);
        addRequest('onBeforeSendHeaders', details);
        //拦截到执行资源后，为资源进行重定向
        //也就是是只要请求的资源匹配拦截规则，就转而执行returnjs.js
        //return {redirectUrl: chrome.extension.getURL("returnjs.js")};
    },
    {
        //配置拦截匹配的url，数组里域名下的资源都将被拦截
        urls: [
            'https://study.jxgbwlxy.gov.cn/api/study/years/yearsCourseware/annualPortalCourseListNew', // 必修课程
            'https://study.jxgbwlxy.gov.cn/api/study/my/elective/myElectivesNew', //选修课程
        ],
        //拦截的资源类型，在这里只拦截script脚本，也可以拦截image等其他静态资源
        types: ["xmlhttprequest"]
    },
    //要执行的操作，这里配置为阻断
    ['requestHeaders']
);

chrome.webRequest.onBeforeRequest.addListener(
    function(details) {
        // console.log('onBeforeRequest', details);
        addRequest('onBeforeRequest', details);
        //拦截到执行资源后，为资源进行重定向
        //也就是是只要请求的资源匹配拦截规则，就转而执行returnjs.js
        //return {redirectUrl: chrome.extension.getURL("returnjs.js")};
    },
    {
        //配置拦截匹配的url，数组里域名下的资源都将被拦截
        urls: [
            'https://study.jxgbwlxy.gov.cn/api/study/years/yearsCourseware/annualPortalCourseListNew', // 必修课程
            'https://study.jxgbwlxy.gov.cn/api/study/my/elective/myElectivesNew', //选修课程
        ],
        //拦截的资源类型，在这里只拦截script脚本，也可以拦截image等其他静态资源
        types: ["xmlhttprequest"]
    },
    //要执行的操作，这里配置为阻断
    ['requestBody'] // blocking | extraHeaders | requestBody  
);

// 监听消息
chrome.runtime.onMessage.addListener(
    function (request, sender, sendResponse) {
	    let cmd = request['cmd'];
        let data = request['data'];
        if (cmd == 'ADD_TASK') {
            proc_info_干部学院.urlTasks[data.url] = data;
        } else if (cmd == 'START_STUDY') {
            if (! proc_info_干部学院.thread) {
                proc_info_干部学院.thread = setInterval(loopStudy, 1000 * 60);
            }
        } else if (cmd == 'STOP_STUDY') {
            if (proc_info_干部学院.thread) {
                clearInterval(proc_info_干部学院.thread);
                proc_info_干部学院.thread = 0;
            }
        }
    }
);

function listTabs(cb) {
	chrome.windows.getAll({populate : true}, function(windows) {
        let rs = [];
		for (let i in windows) {
			let win = windows[i];
			let winId = win.id;
			let tabs = win.tabs;
            for (let t of tabs) rs.push(t);
		}
        cb(rs);
	});
}

function checkIsStudyEnd(tab) {
    if (!tab || tab.url.indexOf('https://study.jxgbwlxy.gov.cn/video?') < 0)
        return;
    function _isEndStudy() {
        let lis = document.querySelectorAll('ul.kc_list > li');
        for (let i = 0; i < lis.length; i++) {
            if (lis[i].textContent.indexOf('100.00%已完成') < 0) {
                return false;
            }
        }
        window.close();
        return true;
    }
    let details = {code: 'var _ssx = (' + _isEndStudy.toString() + ')(); _ssx;', runAt: 'document_idle' };
    chrome.tabs.executeScript(tab.id, details, function(end) {
        if (Array.isArray(end) && end[0])
            chrome.tabs.remove(tab.id);
    });
}

function checkIsStudy(cb) {
    let rt = false;
    function isStudy(tabs) {
        for (let tab of tabs) {
            if (tab.url && tab.url.indexOf('https://study.jxgbwlxy.gov.cn/video?') >= 0) {
                rt = true;
                checkIsStudyEnd(tab);
            }
        }
        cb(rt);
    }
    listTabs(isStudy);
}

function beginStudy() {
    let k = null;
    let data = null;
    for (let url in proc_info_干部学院.urlTasks) {
        k = url;
        break;
    }
    if (! k) return;
    data = proc_info_干部学院.urlTasks[k];
    delete proc_info_干部学院.urlTasks[k];
    listTabs(function(tabs) {
        let winId = chrome.windows.WINDOW_ID_CURRENT;
        for (let tab of tabs) {
            if (tab.url.indexOf('https://study.jxgbwlxy.gov.cn/') >= 0) {
                winId = tab.windowId;
                break;
            }
        }
        let prop = {url: k, active: true, windowId: winId};
        chrome.tabs.create(prop, function(tab) {
            let details = {code: 'setTimeout(function() {document.querySelector(".courseCtr button").click();}, 5000);'};
            chrome.tabs.executeScript(tab.id, details, function(any) {
            });
        });
    })
    
}

function loopStudy() {
    checkIsStudy(function(isStudy) {
        if (isStudy)
            return;
        beginStudy();
    });
}