logined = document.querySelector('#loginbtn1').textContent != '用户登录';

chrome.runtime.sendMessage({cmd: 'CHECK_LOGINED', data: {logined : logined}});