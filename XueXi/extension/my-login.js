/* ,
{
    "matches": ["https://www.xuexi.cn/?login", "https://login.xuexi.cn/login/xuexiWeb?*"],
        "run_at": "document_start",
            "js": ["jquery-3.6.min.js", "my-login.js"],
                "all_frames": true
}
*/

console.log('my-login.js ==>', document.readyState, window.location.href);
var changeUITag = false;

function checkUIOK() {
    console.log('checkUIOK()...');
    let loggedElem = $('.logged-text > .logged-link');
    let loginEmel = $('.login > .login-icon');
    if (loggedElem.length == 0 && loginEmel.length == 0) {
        // not ready
        if (!changeUITag)
            setTimeout(checkUIOK, 100);
        return;
    }
    changeUITag = true;
    if (loggedElem.length > 0) {
        $(document.body).append(loggedElem);
        let style = "position:absolute; left: 50px; color: rgb(209, 0, 0); cursor: pointer; border: 1px solid rgb(203, 30, 30); background: rgb(255, 255, 255); pointer-events: auto; width: 130px; height: 32px; font-size: 14px; border-radius: 4px; line-height:30px; text-decoration: none; margin-top: 140px;";
        loggedElem[0].style = style;
    } else if (loginEmel.length > 0) {
        window.location.href = 'https://pc.xuexi.cn/points/login.html?a=b';
    }
    $(document.body).css('overflow', 'hidden');
    $(document.body).css('text-align', 'center');
}

if (window.location.href == 'https://www.xuexi.cn/?login') {
    document.onreadystatechange = function () {
        console.log('my-login.js ==>', document.readyState);
        $('#root').hide();
        setTimeout(checkUIOK, 100);
    };
} else if (window.location.href == 'https://pc.xuexi.cn/points/login.html?a=b') {
    
}

