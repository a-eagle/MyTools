// image is base64 url data
function qrcode(img) {
	let di = img.indexOf(',');
	if (di > 0)
		img = img.substring(di + 1);
	let n = atob(img);
	let a = new Array(n.length);
	for (let i = 0; i < n.length; i++) {
		a[i] = n.charCodeAt(i);
	}
	let u8 = new Uint8Array(a);
	let png = UPNG.decode(u8.buffer);
	// console.log('png:', png);
	let rgba = UPNG.toRGBA8(png)[0];
	let qr = jsQR(new Uint8ClampedArray(rgba), png.width, png.height);
	let data = qr.data;
	return data;
}