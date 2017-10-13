
document.getElementById('lan_cn').addEventListener('click', function(event){
	event.preventDefault();
	window.location.href = '/?lang=zh';
}, false)


document.getElementById('lan_us').addEventListener('click', function(event){
	event.preventDefault();
	window.location.href = '/?lang=en';
}, false)


document.getElementById('lan_jp').addEventListener('click', function(event){
	event.preventDefault();
	window.location.href = '/?lang=ja';
}, false)