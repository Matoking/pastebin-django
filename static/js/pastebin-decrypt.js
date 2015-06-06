if (typeof pastebin === 'undefined') {
	var pastebin = {};
	pastebin.urls = {};
}

// List of languages prism.js can highlight
// The key is the format used by pastebin-django,
// the value is the format used in language-xxxx class by prism.js
pastebin.languages = {
	"text": "markup",
	"c": "c",
	"css": "css",
	"js": "javascript",
	"as": "actionscript",
	"apacheconf": "apacheconf",
	"aspx-cs": "aspnet",
	"ahk": "autohotkey",
	"bash": "bash",
	"csharp": "csharp",
	"cpp": "cpp",
	"coffee-script": "coffeescript",
	"dart": "dart",
	"eiffel": "eiffel",
	"erlang": "erlang",
	"fsharp": "fsharp",
	"fortran": "fortran",
	"cucumber": "gherkin",
	"go": "go",
	"groovy": "groovy",
	"haml": "haml",
	"handlebars": "handlebars",
	"haskell": "haskell",
	"http": "http",
	"ini": "ini",
	"jade": "jade",
	"java": "java",
	"julia": "julia",
	"matlab": "matlab",
	"nasm": "nasm",
	"nsis": "nsis",
	"objective-c": "objectivec",
	"perl": "perl",
	"php": "php",
	"powershell": "powershell",
	"python": "python",
	"rst": "rest",
	"rb": "ruby",
	"rust": "rust",
	"sass": "scss",
	"scala": "scala",
	"scheme": "scheme",
	"smalltalk": "smalltalk",
	"smarty": "smarty",
	"sql": "sql",
	"swift": "swift",
	"twig": "twig",
	"ts": "typescript",
	"yaml": "yaml"
};

pastebin.loadDecrypt = function() {
	$("#paste-decrypt").click(function() { pastebin.decryptPaste(); });
	
	$("#paste-password").keyup(function(evt) {
		if (evt.keyCode == 13) {
			$("#paste-decrypt").click().focus();
		}
	});
};

pastebin.decryptPaste = function() {
	var password = $("#paste-password").val();
	var text = $("#encrypted-text").text();
	
	try {
		text = sjcl.decrypt(password, text);
	} catch (err) {
		// Paste couldn't be decrypted
		window.alert("Paste couldn't be decrypted. Your password is probably incorrect.");
		$("#paste-decrypt-password").select();
		return;
	}
	
	$("#encrypted-text").find("code").text(text);
	pastebin.highlightPaste();
}

/**
 * Highlight the now decrypted paste using prism.js
 */
pastebin.highlightPaste = function() {
	// Check if prism.js supports the format of this paste
	// If it does, highlight it using that language
	// Otherwise, default to plain text
	var language = "markup";
	
	if (pastebin_paste_format in pastebin.languages) {
		language = pastebin.languages[pastebin_paste_format];
	}
	
	$("#encrypted-text").addClass("language-" + language + " line-numbers");
	$("#encrypted-text").show();
	$("#paste-decrypt-form").hide();
	
	Prism.highlightAll();
	
	$("#encrypted-text").addClass("pre-code");
};

pastebin.loadDecrypt();