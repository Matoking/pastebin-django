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
	
	pastebin.updateComments();
};

/**
 * Get and update the comments for a specific page (first page if not defined)
 */
pastebin.getComments = function(page) {
	page = typeof page !== 'undefined' ? page : 0;
	
	$.post(window.location.protocol + "//" + window.location.host + "/comments/get_comments",
		   {char_id: pastebin_char_id,
		    page: page},
		   function(result) {
		    	pastebin.onCommentsLoaded(result);
		   });
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