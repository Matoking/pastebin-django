if (typeof pastebin === 'undefined') {
	var pastebin = {};
	pastebin.urls = {};
}

pastebin.currentFontSize = 2;
pastebin.fontSizes = [10, 12, 14, 16, 18];

pastebin.loadControls = function() {
	// Don't show controls unless user has decrypted the paste already
	if (!pastebin_paste_encrypted) {
		pastebin.showControls();
	}
};

/**
 * Show controls to change font size
 */
pastebin.showControls = function() {
	$("#paste-controls").show();
	pastebin.updateControls();
};

/**
 * Update the controls and paste's font size based on the current setting
 */
pastebin.updateControls = function() {
	if (!pastebin_paste_encrypted) {
		$(".code").css("font-size", pastebin.fontSizes[pastebin.currentFontSize] + "px");
	} else {
		$("#encrypted-text").css("font-size", pastebin.fontSizes[pastebin.currentFontSize] + "px");
	}
	
	$("#increase-font-size").attr("disabled", false);
	$("#decrease-font-size").attr("disabled", false);
	
	if (pastebin.currentFontSize === pastebin.fontSizes.length-1) {
		$("#increase-font-size").attr("disabled", true);
	} else if (pastebin.currentFontSize === 0) {
		$("#decrease-font-size").attr("disabled", true);
	}
}

/**
 * Increase paste's font size
 */
pastebin.increaseFontSize = function() {
	if (pastebin.currentFontSize >= pastebin.fontSizes.length-1) {
		return;
	}
	
	pastebin.currentFontSize += 1;
	pastebin.updateControls();
}

/**
 * Decrease paste's font size
 */
pastebin.decreaseFontSize = function() {
	if (pastebin.currentFontSize === 0) {
		return;
	}
	
	pastebin.currentFontSize -= 1;
	pastebin.updateControls();
}

pastebin.loadControls();