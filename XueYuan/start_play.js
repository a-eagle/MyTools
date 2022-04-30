flag = false;

function check() {
	if (flag) {
		return;
	}
	ch = $(document).find('.user_choise');
	console.log('ch: ', ch);
	if (ch.length > 0) {
		ch.click();
		flag = true;
	}
}

setInterval(check, 10 * 1000);