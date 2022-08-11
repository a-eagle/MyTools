function clearNone() {
	var _w = $('.dl-main.ng-isolate-scope');
	var _cc = _w.find('.dl-item.ng-scope');
	_cc.each(function() {
		var t = $(this);
		var hasCtx = t.find('.text').length > 0;
		if (! hasCtx) {
			t.hide();
		} else {
			t.find('label').click();
		}
	});
}
$('.replace-word').after('&nbsp;&nbsp;&nbsp;&nbsp;<button onclick="clearNone()" class="btn-search"> Clear </button>');
