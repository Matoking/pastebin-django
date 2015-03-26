/**
 *  This script is responsible for displaying the comments as well as uploading any comments submitted by
 *  the user
 */
if (typeof pastebin === 'undefined') {
	var pastebin = {};
}

pastebin.loadComments = function() {
	// We need to send a CSRF token with POST requests, so make sure it's included
	// with every request
	$.ajaxSetup({
	    beforeSend: function(xhr) {
	        xhr.setRequestHeader('X-CSRFToken', pastebin_csrf_token);
	    }
	});
	
	pastebin.updateFavoriteButton();
};

//Delay execution until the page and jQuery have loaded
if (window.attachEvent) {
	window.attachEvent("onload", pastebin.loadComments);
} else {
	if (window.onload) {
        var currentOnLoad = window.onload;
        var newOnLoad = function() {
            currentOnLoad();
            pastebin.loadComments();
        };
        window.onload = newOnLoad;
    } else {
        window.onload = pastebin.loadComments;
    }
};