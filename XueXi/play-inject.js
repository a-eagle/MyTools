_exply = false;
$(function() {
	if (_exply) {
		return;
	}
	$('.outter').click();
	console.log('=x==start run video=A===', $('.outter').get(0));
	_exply = true;
});

if (! _exply) {
	_exply = true;
	$('.outter').click();
	console.log('=x==start run video=B===', $('.outter').get(0));
}