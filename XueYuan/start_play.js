var scheckid = 0, spid = 0;

function check() {
	let ch = $(document).find('.user_choise, .promp_continue');
	let visible = ch.is( ":visible" );
	if (ch.length == 0) {
		return;
	}
	if (visible) {
		ch.click();
	} else {
		// clearInterval(scheckid);
		// spid = setInterval(startPlayer, 5000);
	}
}

scheckid = setInterval(check, 3 * 1000);


function startPlayer() {
	let v = $('video');
	if (v.length != 1) {
		return;
	}
	v.get(0).play();
	clearInterval(spid);
}