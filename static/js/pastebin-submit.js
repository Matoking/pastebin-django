/**
 *  This script is responsible for submitting the paste as well as performing form validation
 */
if (typeof pastebin === 'undefined') {
	var pastebin = {};
	pastebin.urls = {};
}

pastebin.urls["submit_paste"] = window.location.protocol + "//" + window.location.host;

var pastebin_paste_encrypted = false;

/**
 * Called when the script is loaded
 */
pastebin.loadSubmitForm = function() {
	// Add event handlers
	$("#encryption-password").change(function() { pastebin.updateEncryptionTab(); });
	$("#encryption-password").keydown(function() { pastebin.updateEncryptionTab(); });
	$("#encryption-password").keyup(function() { pastebin.updateEncryptionTab(); });
	
	$("#encryption-confirm-password").change(function() { pastebin.updateEncryptionTab(); });
	$("#encryption-confirm-password").keydown(function() { pastebin.updateEncryptionTab(); });
	$("#encryption-confirm-password").keyup(function() { pastebin.updateEncryptionTab(); });
	
	$("#encryption-generate-password").click(function() { pastebin.generateRandomPassword(); });
	$("#encryption-encrypt").click(function() { pastebin.encryptPaste(); });
	
	$("#encryption-show-password").click(function() { pastebin.setPasswordVisible(this.checked); });
};

/**
 * Update the encryption tab
 */
pastebin.updateEncryptionTab = function() {
	if (pastebin_paste_encrypted) {
		$("#encryption-password").attr("disabled", true);
		$("#encryption-confirm-password").attr("disabled", true);
		$("#encryption-generate-password").attr("disabled", true);
		$("#encryption-encrypt").attr("disabled", true);
		return;
	}
	
	var password = $("#encryption-password").val();
	var confirmPassword = $("#encryption-confirm-password").val();
	
	if (password === confirmPassword && password != "") {
		$("#encryption-encrypt").attr("disabled", false);

		$("#encryption-password-group").removeClass("has-error");
		$("#encryption-confirm-password-group").removeClass("has-error");

		$("#encryption-password-group").addClass("has-success");
		$("#encryption-confirm-password-group").addClass("has-success");
	} else {
		$("#encryption-encrypt").attr("disabled", true);
		
		$("#encryption-password-group").addClass("has-error");
		$("#encryption-confirm-password-group").addClass("has-error");
		
		$("#encryption-password-group").removeClass("has-success");
		$("#encryption-confirm-password-group").removeClass("has-success");
	}
};

/**
 * Generates a random password
 */
pastebin.generateRandomPassword = function() {
	var chars="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
	
	var password = "";
	
	for (var i=0; i < 16; i++) {
		// Use random word generator provided courtesy of SJCL library
		var char = chars[(Math.abs(sjcl.random.randomWords(1))%chars.length)];
		password += char;
	}
	
	$("#encryption-password").val(password);
	$("#encryption-confirm-password").val(password);
	
	pastebin.setPasswordVisible(true);
	pastebin.updateEncryptionTab();
	
	$("#encryption-password").select();
};

/**
 * Set whether passwords should be visible or not
 */
pastebin.setPasswordVisible = function(visible) {
	if (visible) {
		$("#encryption-password").attr("type", "text");
		$("#encryption-confirm-password").attr("type", "text");
	} else {
		$("#encryption-password").attr("type", "password");
		$("#encryption-confirm-password").attr("type", "password");
	}
}

/**
 * Encrypt the paste and prevent it from being edited again
 */
pastebin.encryptPaste = function() {
	var text = $("[name='text']").val();
	var password = $("#encryption-password").val();
	
	text = sjcl.encrypt(password, text);
	
	$("[name='text']").val(text).attr("disabled", true);
	
	pastebin_paste_encrypted = true;
	
	pastebin.updateEncryptionTab();
};

pastebin.loadSubmitForm();