/**
 *  This script is responsible for updating the favorite button and displaying the relevant information.
 *  This way the user can add/remove the paste from his favorites without having to refresh the page.
 */
if (typeof pastebin === 'undefined') {
	var pastebin = {};
	pastebin.urls = {};
}

// An object containing different URLs for easier access
pastebin.urls["change_paste_favorite"] = window.location.protocol + "//" + window.location.host + "/pastes/change_paste_favorite/";

pastebin.loadFavorites = function() {
	// We need to send a CSRF token with POST requests, so make sure it's included
	// with every request
	$.ajaxSetup({
	    beforeSend: function(xhr) {
	        xhr.setRequestHeader('X-CSRFToken', pastebin_csrf_token);
	    }
	});
	
	pastebin.updateFavoriteButton();
};
		
/**
 * Update the "add/remove favorite" button
 */
pastebin.updateFavoriteButton = function() {
	// Hide the button if user isn't logged in, he's not supposed to see it anyway
	if (!pastebin_logged_in) {
		$("#favorite-button").css("display", "none");
		return;
	}
	
	if (pastebin_paste_favorited) {
		$("#favorite-button").html("<span class='glyphicon glyphicon-remove'></span> Remove from favorites");
		$("#favorite-button").attr("onclick", "pastebin.removeFromFavorites()");
		$("#favorite-button").attr("class", "btn btn-warning btn-xs");
	} else {
		$("#favorite-button").html("<span class='glyphicon glyphicon-star'></span> Add to favorites");
		$("#favorite-button").attr("onclick", "pastebin.addToFavorites()");
		$("#favorite-button").attr("class", "btn btn-info btn-xs");
	}
};
		
/**
 * Called when user clicks "add to favorites"
 */
pastebin.addToFavorites = function() {
	if (pastebin_paste_favorited) {
		return;
	}
	
	$.post(pastebin.urls["change_paste_favorite"],
		   {char_id: pastebin_char_id,
		    action: "add"},
		   function(result) {
		    	pastebin.onFavoriteUpdated(result);
		   });
	
	$("#favorite-button").attr("disabled", true);
};

/**
 * Called when user clicks "remove from favorites"
 */
pastebin.removeFromFavorites = function() {
	if (!pastebin_paste_favorited) {
		return;
	}
	
	$.post(pastebin.urls["change_paste_favorite"],
		   {char_id: pastebin_char_id,
		    action: "remove"},
		   function(result) {
		    	pastebin.onFavoriteUpdated(result);
		   });
	
	$("#favorite-button").attr("disabled", true);
};
		
/**
 * Called when response is received to user's "add/remove favorite" request
 */
pastebin.onFavoriteUpdated = function(result) {
	result = JSON.parse(result);
	
	if ("status" in result && result["status"] === "success") {
		if (result["data"]["favorited"]) {
			pastebin_paste_favorited = true;
		} else {
			pastebin_paste_favorited = false;
		}
	}
	
	$("#favorite-button").attr("disabled", false);
	
	pastebin.updateFavoriteButton();
};

pastebin.loadFavorites();