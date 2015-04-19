/**
 *  This script is responsible for displaying the comments as well as uploading any comments submitted by
 *  the user
 */
if (typeof pastebin === 'undefined') {
	var pastebin = {};
	pastebin.urls = {};
}

pastebin.urls["get_comments"] = window.location.protocol + "//" + window.location.host + "/comments/get_comments/";
pastebin.urls["add_comment"] = window.location.protocol + "//" + window.location.host + "/comments/add_comment/";
pastebin.urls["edit_comment"] = window.location.protocol + "//" + window.location.host + "/comments/edit_comment/";
pastebin.urls["delete_comment"] = window.location.protocol + "//" + window.location.host + "/comments/delete_comment/";

pastebin.urls["user_profile"] = window.location.protocol + "//" + window.location.host + "/users/{USERNAME}/";

// Simple function to escape HTML
pastebin.escapeHtml = function(text) {
	return $("<div/>").text(text).html();
};

pastebin.loadComments = function() {
	// We need to send a CSRF token with POST requests, so make sure it's included
	// with every request
	$.ajaxSetup({
	    beforeSend: function(xhr) {
	        xhr.setRequestHeader('X-CSRFToken', pastebin_csrf_token);
	    }
	});
};

/**
 * Reset the layout of comments so that elements are not visible until they are
 * explicitly made visible when needed
 */
pastebin.resetComments= function() {
	$("#no-comments").css("display", "none");
}

/**
 * Scrolls the user's view to the comments section
 */
pastebin.scrollToComments = function() {
	$('html, body').animate({
        scrollTop: $("#comment-panel").offset().top
        }, 1000);
};

/**
 * Hide the comments section
 */
pastebin.hideComments = function() {
	pastebin_comment_visible = false;
	
	$("#comment-body").hide();
	
	pastebin.updateHeadingButton();
};

/**
 * Show comments
 * 
 * If a specific page isn't provided, display the first page
 */
pastebin.showComments = function(page) {
	page = typeof page !== 'undefined' ? page : 0;
	
	pastebin_comment_visible = true;
	
	pastebin.resetComments();
	
	// Display the comments section and change the panel button
	$("#comment-body").show();
	$("#comment-panel-button").attr("disabled", true);
	
	pastebin.updateHeadingButton();
	pastebin.getComments(page);
};

/**
 * Show the selected page of comments
 */
pastebin.selectPage = function(page) {
	pastebin.showComments(page);
};

/**
 * Show the form to edit the comment or hide it if it's already visible
 */
pastebin.toggleEditComment = function(id) {
	if ($("#comment-" + id).has(".comment-form").length === 0) {
		pastebin.hideDeleteComment(id);
		pastebin.showEditComment(id);
	} else {
		pastebin.hideEditComment(id);
	}
};

/**
 * Show the edit comment form
 */
pastebin.showEditComment = function(id) {
	// Clone the edit comment form if it doesn't exist yet
	if ($("#comment-" + id).has(".comment-form").length === 0) {
		$("#submit-comment-form").clone().appendTo("#comment-" + id);
	}
	
	// Hide the displayed comment as well as the header for the form
	$("#comment-" + id).find(".comment-text").hide();
	$("#comment-" + id).find(".page-header").hide();
	
	// Change the description
	$("#comment-" + id).find(".comment-form").attr("comment-form-" + id);
	$("#comment-" + id).find(".comment-form-title").text("Edit comment");
	$("#comment-" + id).find(".comment-form-description").html("You are editing your comment on paste <b>" + pastebin_paste_title + "</b>");
	
	$("#comment-" + id).find(".comment-text-field").val(pastebin_comments[id]["text"]);
	
	$("#comment-" + id).find(".comment-form-button").text("Update comment")
													.attr("onclick", "pastebin.updateComment(" + id + ")");
};

/**
 * Hide the edit comment form
 */
pastebin.hideEditComment = function(id) {
	// Delete the edit comment form and show the original comment
	$("#comment-" + id).find(".comment-form").detach();
	$("#comment-" + id).find(".comment-text").show();
}

/**
 * Show the dialog to delete a comment
 */
pastebin.toggleDeleteComment = function(id) {
	if ($("#comment-" + id).has(".delete-comment-form").length === 0) {
		pastebin.hideEditComment(id);
		pastebin.showDeleteComment(id);
	} else {
		pastebin.hideDeleteComment(id);
	}
};

/**
 * Show the delete comment form
 */
pastebin.showDeleteComment = function(id) {
	// Show the delete comment form
	if ($("#comment-" + id).has(".delete-comment-form").length === 0) {
		$("#delete-comment-form").clone().prependTo($("#comment-" + id).find(".comment-text")).show();
		$("#comment-" + id).find(".delete-comment-form").attr("id", "delete-comment-form-" + id);
	}
	
	$("#delete-comment-form-" + id).find(".delete-comment-button-yes").attr("onclick", "pastebin.deleteComment(" + id + ")");
	$("#delete-comment-form-" + id).find(".delete-comment-button-no").attr("onclick", "pastebin.toggleDeleteComment(" + id + ")");
};

/**
 * Hide the delete comment form
 */
pastebin.hideDeleteComment = function(id) {
	// Delete the comment deletion form
	$("#comment-" + id).find(".delete-comment-form").detach();
};

/**
 * Delete a comment
 */
pastebin.deleteComment = function(id) {
	var comment = pastebin_comments[id];
	
	var commentId = pastebin_comments[id]["id"];
	
	$("#delete-comment-form-" + id).find(".delete-comment-button-yes").attr("disabled", true);
	$("#delete-comment-form-" + id).find(".delete-comment-button-no").attr("disabled", true);
	
	$.post(pastebin.urls["delete_comment"],
		  {id: commentId,
		   char_id: pastebin_char_id,
		   page: pastebin_comment_page},
		  function(result) {
			   // The result only contains a page of comments,
			   // so we can use this handler instead
			   pastebin.onCommentsLoaded(result); 
		   });
};

/**
 * Update an existing comment
 */
pastebin.updateComment = function(id) {
	var comment = pastebin_comments[id];
	
	var commentId = pastebin_comments[id]["id"];
	var newText = $("#comment-" + id).find(".comment-text-field").val();
	
	$("#comment-" + id).find(".comment-form-errors").hide();
	$("#comment-" + id).find(".comment-form-button").attr("disabled", true);
	
	$.post(pastebin.urls["edit_comment"],
		   {id: commentId,
			char_id: pastebin_char_id,
			page: pastebin_comment_page,
		    text: newText},
		   function(result) {
		    	$("#comment-" + id).find(".comment-form-button").attr("disabled", false);
		    	
		    	pastebin.onCommentEdited(result, id);
		    });
};

/**
 * Get and update the comments for a specific page (first page if not defined)
 */
pastebin.getComments = function(page) {
	page = typeof page !== 'undefined' ? page : 0;
	
	$("#comment-spinner").show();
	$("#comment-list").hide();
	
	$.post(pastebin.urls["get_comments"],
		   {char_id: pastebin_char_id,
		    page: page},
		   function(result) {
		    	$("#comment-spinner").hide();
		    	$("#comment-panel-button").attr("disabled", false);
		    	
		    	pastebin.onCommentsLoaded(result);
		   }).fail(function() {
			   $("#comment-spinner").hide();
			   $("#comment-panel-button").attr("disabled", false);
		   });
};

/**
 * Submit a new comment
 */
pastebin.addComment = function() {
	var text = $("#submit-comment-form").find(".comment-text-field").val();
	
	if ($.trim(text) === "" || text.length > 2000) {
		return;
	}
	
	$("#submit-comment-form").find(".comment-form-button").attr("disabled", true);
	$("#submit-comment-form").find(".comment-form-errors").hide();
	
	$.post(pastebin.urls["add_comment"],
		   {char_id: pastebin_char_id,
		    text: text},
		    function(result) {
		    	$("#submit-comment-form").find(".comment-form-button").attr("disabled", false);
		    	
		    	pastebin.onCommentAdded(result);
		    });
};

/**
 * Response received to "get comments" request
 * 
 * Update the comments and open the correct page
 */
pastebin.onCommentsLoaded = function(result) {
	result = JSON.parse(result);
	
	if ("status" in result && result["status"] === "success") {
		pastebin_comment_page = result["data"]["page"];
		pastebin_comment_pages = result["data"]["pages"];
		pastebin_total_comment_count = result["data"]["total_comment_count"];
		pastebin_comments = result["data"]["comments"];
	}
	
	pastebin.updateComments();
	pastebin.updateCommentPaginator();
	pastebin.updateHeadingButton();
	pastebin.resetCommentForm();
};

/**
 * Response received to "add comments" request
 * 
 * Reload the shown comments or display an error message if necessary
 */
pastebin.onCommentAdded = function(result) {
	result = JSON.parse(result);
	
	if (!("status" in result)) {
		return;
	}
	
	if (result["status"] === "success") {
		pastebin_comment_page = result["data"]["page"];
		pastebin_comment_pages = result["data"]["pages"];
		pastebin_total_comment_count = result["data"]["total_comment_count"];
		pastebin_comments = result["data"]["comments"];
		
		pastebin.updateComments();
		pastebin.updateCommentPaginator();
		pastebin.updateHeadingButton();
		pastebin.resetCommentForm();
		
		// Scroll up to display the newest comment
		pastebin.scrollToComments();
	} else if (result["status"] === "fail") {
		// Get the error message
		var message = result["data"]["message"];
		
		var errorHtml = "The following error was returned when trying to submit a comment<br>" +
						"<strong>" + message + "</strong>";
		
		$("#submit-comment-form").find(".comment-form-errors").html(errorHtml)
															  .show();
	}
};

/**
 * Response received to "edit comment" request
 * 
 * Reload the shown comments or display an error message if necessary
 */
pastebin.onCommentEdited = function(result, id) {
	result = JSON.parse(result);
	
	if (!("status" in result)) {
		return;
	}
	
	if (result["status"] === "success") {
		pastebin_comment_page = result["data"]["page"];
		pastebin_comment_pages = result["data"]["pages"];
		pastebin_total_comment_count = result["data"]["total_comment_count"];
		pastebin_comments = result["data"]["comments"];
		
		pastebin.updateComments();
		pastebin.updateCommentPaginator();
		pastebin.updateHeadingButton();
		pastebin.resetCommentForm();
	} else if (result["status"] === "fail") {
		// Get the error message
		var message = result["data"]["message"];
		
		var errorHtml = "The following error was returned when trying to edit a comment<br>" +
						"<strong>" + message + "</strong>";
		
		$("comment-" + id).find(".comment-form-errors").html(errorHtml)
													   .show();
	}
};

/**
 * Update the show/hide comments button displayed on the panel heading
 */
pastebin.updateHeadingButton = function() {
	if (pastebin_comment_visible) {
		$("#comment-panel-button").text("Hide comments (" + pastebin_total_comment_count + ")")
								  .removeClass("btn-info")
								  .addClass("btn-warning")
								  .attr("onclick", "pastebin.hideComments()");
	} else {
		$("#comment-panel-button").text("Show comments (" + pastebin_total_comment_count + ")")
								  .removeClass("btn-warning")
								  .addClass("btn-info")
								  .attr("onclick", "pastebin.showComments()");
	}
}

/**
 * Update the displayed comments
 */
pastebin.updateComments = function() {
	if (pastebin_comments.length === 0) {
		$("#no-comments").css("display", "block");
	} else {
		$("#no-comments").css("display", "none");
	}
	
	// Clear the current listing of comments
	$("#comment-list").html("");
	
	// Add comments one by one
	for (var i=0; i < pastebin_comments.length; i++) {
		var comment = pastebin_comments[i];
		
		// Is the comment by the logged in user 
		var ownComment = comment["username"] === pastebin_current_username ? true : false;
		
		var commentHtml = "<div class=\"media\" id=\"{COMMENT_ID}\">" +
						  	"<div class=\"media-body\">" +
						  		"<h4 class=\"media-heading\">{COMMENT_DELETE}{COMMENT_EDIT}{COMMENT_USERNAME}</h4>" +
						  	"<div class=\"comment-text\">{COMMENT_TEXT}</div>" +
						  "</div></div>";
		
		commentHtml = commentHtml.replace("{COMMENT_ID}", "comment-" + i);
		commentHtml = commentHtml.replace("{COMMENT_TEXT}", pastebin.escapeHtml(comment["text"]).replace(/\r?\n/g, '<br />'));
		
		var userUrl = pastebin.urls["user_profile"];
		userUrl = userUrl.replace("{USERNAME}", comment["username"]);
		
		commentHtml = commentHtml.replace("{COMMENT_USERNAME}", "<a href=\"" + userUrl + "\">" + comment["username"] + "</a>");
		
		if (ownComment) {
			commentHtml = commentHtml.replace("{COMMENT_EDIT}", "<button onclick=\"pastebin.toggleEditComment(" + i + ")\" class=\"btn btn-xs btn-primary\">" +
																"<span class=\"glyphicon glyphicon-pencil\"></span></button> ");
			commentHtml = commentHtml.replace("{COMMENT_DELETE}", "<button onclick=\"pastebin.toggleDeleteComment(" + i + ")\" class=\"btn btn-xs btn-danger\">" +
																  "<span class=\"glyphicon glyphicon-remove\"></span></button> ");
		} else {
			commentHtml = commentHtml.replace("{COMMENT_EDIT}", "");
			commentHtml = commentHtml.replace("{COMMENT_DELETE}", "");
		}
		
		// Append the element into the list
		$("#comment-list").append(commentHtml);
	}
	
	$("#comment-list").show();
	
	// Limit each comment paragraph's height
	// This has to be done after the comments have been made visible
	$("#comment-list").find(".comment-text").each(function() {
		$(this).readmore();
	});
};

/**
 * Reset the form used to submit comments
 */
pastebin.resetCommentForm = function() {
	$("#submit-comment-form").find(".comment-form-errors").hide();
	$("#submit-comment-form").find(".comment-text-field").val("");
	$("#submit-comment-form").find(".comment-form-button").attr("disabled", false);
	
	// If the user is not logged in, don't show the form to submit comments
	if (!pastebin_logged_in) {
		$("#submit-comment-form").hide();
	}
};

/**
 * Get pages to be displayed in the paginator as a list
 */
pastebin.getPaginatorPages = function() {
	var pages = [];
	
	// Add the first page
	if (pastebin_comment_page !== 0) {
		pages.push("first");
		pages.push("previous");
	}
	
	// Add four pages before the current page
	for (var i=3; i >= 0; i--) {
		var page = pastebin_comment_page - i - 1;
		
		if (page >= 0) {
			pages.push(page);
		}
	}
	
	// Add the current page
	pages.push(pastebin_comment_page);
	
	// Add four pages after the current page
	for (var i=0; i < 4; i++) {
		var page = pastebin_comment_page + i + 1;
		
		if (page < pastebin_comment_pages) {
			pages.push(page);
		}
	}
	
	// Add the next and last page
	if (pastebin_comment_page + 1 != pastebin_comment_pages) {
		pages.push("next");
		pages.push("last");
	}
	
	return pages;
};

/**
 * Update the paginator
 */
pastebin.updateCommentPaginator = function() {
	var pages = pastebin.getPaginatorPages();
	
	// Clear the current paginator
	$("#comment-paginator").html("");
	
	for (var i=0; i < pages.length; i++) {
		var page = pages[i];
		
		var pageNumber = page;
		
		if (page === "first") {
			pageNumber = 0;
		} else if (page === "previous") {
			pageNumber = pastebin_comment_page - 1;
		} else if (page === "next") {
			pageNumber = pastebin_comment_page + 1;
		} else if (page === "last") {
			pageNumber = pastebin_comment_pages - 1;
		}
		
		var currentPage = pageNumber === pastebin_comment_page ? true : false;
		
		var pageHtml = "<li class=\"{ACTIVE_CLASS}\"><a href=\"javascript:void(0)\" onclick=\"{LINK_METHOD}\"><span aria-hidden=\"true\">{PAGE_SYMBOL}</span></a></li>";
		
		if (currentPage) {
			pageHtml = pageHtml.replace("{ACTIVE_CLASS}", "active");
			pageHtml = pageHtml.replace("{LINK_METHOD}", "");
		} else {
			pageHtml = pageHtml.replace("{ACTIVE_CLASS}", "");
			pageHtml = pageHtml.replace("{LINK_METHOD}", "pastebin.selectPage(" + pageNumber + ")");
		}
		
		// String to be displayed to represent the page
		pageSymbol = "";
		if (page === "first") {
			pageSymbol = "&laquo;";
		} else if (page === "previous") {
			pageSymbol = "&lt;";
		} else if (page === "next") {
			pageSymbol = "&gt;";
		} else if (page === "last") {
			pageSymbol = "&raquo;"; 
		} else {
			pageSymbol = pageNumber + 1;
		}
		
		pageHtml = pageHtml.replace("{PAGE_SYMBOL}", pageSymbol);
		
		$("#comment-paginator").append(pageHtml);
	}
	
	// If there is only one page there is no need to display the paginator
	if (pastebin_comment_pages === 1) {
		$("#comment-paginator").hide();
	} else {
		$("#comment-paginator").show();
	}
};

// Delay execution until the page and jQuery have loaded
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