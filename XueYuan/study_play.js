
function check() {
	let html = $(document.body).html();
	if (html < 500) {
		window.location.reload();
		// server load page error
		return;
	}
}

setInterval(check, 10 * 1000);