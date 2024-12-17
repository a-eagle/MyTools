__filter_hosts__ = [
    "10.8.52.17:8088",
    "10.97.10.42:8082",
    "10.16.130.57:19005",
    "10.119.81.36:8059"
]

LOCAL_HOST_SERVER_PORT = "5585"

function _accepFiltertHost_(host) {
	if (! host) {
		return false;
	}
	for (let i = 0; i < __filter_hosts__.length; i++) {
		if (__filter_hosts__[i] == host) {
			return true;
		}
	}
	return false;
}

function sendToLocalServer_XHR(resp) {
	let req = resp.config;
	let url = req.url.trim();
	let curPage = new URL(window.location.href);
	let newUrl = new URL(url, curPage);
	if (!_accepFiltertHost_(newUrl.host) && !_accepFiltertHost_(curPage.host)) {
		return;
	}
	url = newUrl.href;

	let ct = resp.headers['content-type'] || resp.headers['Content-Type']
	let data = {'method': req.method, 'headers': JSON.stringify(req.headers), 'url': url, 'type': 'xhr',
				'body': req.body, 'response': resp.response, 'contentType': ct, 'respHeaders': JSON.stringify(resp.headers)};
	$.post({url: 'http://127.0.0.1:' + LOCAL_HOST_SERVER_PORT + '/save-xhr', contentType: "application/json", data: JSON.stringify(data),
		success: function(response) {
			// console.log('Success, ',data, response);
		}, error: function(response) {
			console.log('Error: ', data, response);
		}
	});
}

function sendToLocalServer_File(details) {
	let type = details.type;
	if (details.type == 'main_frame' || details.type == 'sub_frame') {
		type = 'frame'
	} else if (details.type == 'stylesheet' || details.type == 'script'  || details.type == 'image' || details.type == 'font') {
		type = 'static'
	} else {
		return
	}
	let data = {'method': details.method, 'headers': JSON.stringify(details.requestHeaders), 'url': details.url, 'type': type, 'body': ''};
	$.post({url: 'http://127.0.0.1:' + LOCAL_HOST_SERVER_PORT + '/download-file', contentType: "application/json", data: JSON.stringify(data),
		success: function(response) {
			// console.log('Success, ',data, response);
		}, error: function(response) {
			console.log('Error: ', data, response);
		}
	});
}

function sendToLocalServer_File_s(links) {
    if (! links) {
        return;
    }
    let cookie = document.cookie;
    let hds = {};
    if (cookie) {
        hds['Cookie'] = cookie;
    }
	let data = {'method': 'GET', 'headers': hds, 'urls': links, 'type': 'static', 'body': ''};
	$.post({url: 'http://127.0.0.1:' + LOCAL_HOST_SERVER_PORT + '/download-file-s', contentType: "application/json", data: JSON.stringify(data),
		success: function(response) {
			// console.log('Success, ',data, response);
		}, error: function(response) {
			console.log('Error: ', data, response);
		}
	});
}