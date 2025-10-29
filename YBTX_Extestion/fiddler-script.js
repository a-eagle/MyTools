console.log('document-end, hook inject content .......');
console.log('可以在此处拦截并替换<script>');

console.log(document.scripts);
let ss = document.scripts;

for (let i = 0; i < ss.length; i++) {
	
}