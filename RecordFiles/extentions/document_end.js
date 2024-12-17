console.log('document-end, hook inject content .......');
console.log('可以在此处拦截并替换<script>');

let links = $('link');
let slinks = [];
for (let i = 0; i < links.length; i++) {
	let ln = links.eq(i);
    let href = ln.attr('href');
    let rel = ln.attr('rel').toLowerCase().trim();
    if (rel == 'prefetch' || rel == 'preload') {
        let u = new URL(href, window.location.href);
        slinks.push(u.href);
    }
}

sendToLocalServer_File_s(slinks);
