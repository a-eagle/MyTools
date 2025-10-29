// 江西干部网络学院
// 需要启动server-ui.py服务器

function check_login() {
    let url = window.location.href;
    if (url.indexOf('https://study.jxgbwlxy.gov.cn/index') < 0) {
        return;
    }
    let inputs = $('form input');
    // check image is ready
    let imgSrc = $('form img').attr('src');
    let imgReady = imgSrc && imgSrc.length > 50;
    if (inputs.length != 3 || !imgReady) {
        setTimeout(check_login, 1000);
        return;
    }
    simulateKeyPress(inputs.get(0), '18879269788');
    simulateKeyPress(inputs.get(1), 'GaoYan2012');
    // 涂发旺  密码：tf332411W
    loadDataImageOcr($('form img').get(0), inputs.get(2));
}

function studyCourseFirst() {
    let url = window.location.href;
    if (url.indexOf('https://study.jxgbwlxy.gov.cn/study/courseMine?id=') < 0) {
        return;
    }
    let cols = $('.myCol4');
    if (cols.length > 0) {
        cols[0].click();
    }
}

function addTaskUI() {
    let url = window.location.href;
    if (url.indexOf('https://study.jxgbwlxy.gov.cn/courseDetailsNew?') < 0) {
        return;
    }
    let btn = $('<span style="float: right; border: solid 1px #00ff00; height: 30px; background-color: #5aaf5a; color: #000; font-size:16px; padding: 3px 8px;"> 已添加到任务队列 </span>');
    $('.contentCtr > .header').append(btn);
    window.postMessage({cmd: 'ADD_TASK', data: {url: url}}, '*');
}

function myCourseUI() {
    let url = window.location.href;
    if (url.indexOf('https://study.jxgbwlxy.gov.cn/study/courseMine') < 0) {
        return;
    }
    let div = $('<div style="background-color:#aaaa00; border:solid 2px #444; position:absolute; left: 0; top:0; width:150px; height: 300px; z-index: 100000; text-align:center;"> </div>');
    let sbtn = $('<button style="border: solid 1px #00ff00; height: 30px; background-color: #5aaf5a; color: #000; font-size:16px; padding: 3px 8px;"> 开始学习 </button>');
    let ebtn = $('<button style="border: solid 1px #00ff00; height: 30px; background-color: #5aaf5a; color: #000; font-size:16px; padding: 3px 8px;"> 结束学习 </button>');
    div.append('<br/><br/>').append(sbtn).append('<br/><br/>').append(ebtn);
    $(document.body).append(div);
    sbtn.click(function(){window.postMessage({cmd: 'START_STUDY'}, '*')});
    ebtn.click(function(){window.postMessage({cmd: 'STOP_STUDY'}, '*')});
}

function startStudyVideo() {
    console.log('[startStudyVideo]');
    let url = window.location.href;
    if (url.indexOf('https://study.jxgbwlxy.gov.cn/video?') < 0) {
        console.log('is not video; ', url);
        return;
    }
    let cc = $('.video_cover');
    // console.log('video cover is visible: ', cc.is(":visible"));
    if (cc.is(":visible")) {
        $.get('http://localhost:9000/click?x=600&y=600', function(resp) {console.log(resp)});
        // $('.video_cover').click();
    }
    // check timeout
    let nd = false;
    var currentTime = new Date().getTime();
    if (! window._saveTime || currentTime - window._saveTime >= 60 * 1000) {
        nd = true;
    }
    let saveBtn = $('.video_bottom button');
    if (saveBtn.length == 2 && nd) {
        saveBtn[0].click();
        window._saveTime = new Date().getTime();
    }
}

function checkVoice() {
    let cc = $('.custom-video-control-item.custom-video-voice');
    if (cc.length == 0)
        return;
    let vc = $('.custom-video-voice-current');
    if (vc.length == 0) {
        return;
    }
    let imgCtrs = cc.children('img:visible');
    imgCtrs.click();
    console.log('[checkVoice]');
}

setTimeout(function() {
    let url = window.location.href;
    check_login();
    addTaskUI();
    myCourseUI();
}, 1000);

setInterval(startStudyVideo, 5000);
setInterval(checkVoice, 5000);