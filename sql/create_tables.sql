-- table of all the pastes
CREATE TABLE pastes (
	id SERIAL PRIMARY KEY,
	char_id CHAR(8) NOT NULL, -- 8-character identifier, used in the URL
	user_id INTEGER DEFAULT NULL REFERENCES auth_user(id), -- reference to registered user as defined by Django, can be NULL
	
	title VARCHAR(128) NOT NULL, -- Title of the paste
	format VARCHAR(32) NOT NULL, -- Formatting of the text (eg. "text" for plain text, "python" for Python code)
	hash CHAR(64) NOT NULL, -- Hash of the paste's text (SHA256, probably a bit overkill),
						 	-- which is then used as the identifier to the actual paste content
						 	-- This means duplicate pastes don't waste space
						 	 
	expiration_date TIMESTAMP DEFAULT NULL, -- Date after which the paste is considered expired
											-- NULL if paste doesn't have an expiration date
	hidden BOOLEAN NOT NULL,
											
	submitted TIMESTAMP NOT NULL -- Date when the paste was submitted
);

CREATE INDEX paste_id_index ON pastes(id);
CREATE INDEX char_id_index ON pastes(char_id);

-- Paste content is retrieved by a hash (SHA-256/MD5)
-- meaning no space is wasted by duplicate pastes
CREATE TABLE paste_content (
	id SERIAL PRIMARY KEY,
	hash CHAR(64) NOT NULL,
	format VARCHAR(32) NOT NULL, -- Formatting of the text. If "none", the text isn't formatted and is stored in its original form
	text TEXT NOT NULL
);

CREATE INDEX paste_content_id_index ON paste_content(id);
CREATE INDEX paste_content_hash_index ON paste_content(hash);

CREATE TABLE comments (
	id SERIAL PRIMARY KEY,
	paste_id INTEGER REFERENCES pastes(id),
	user_id INTEGER REFERENCES auth_user(id),
	
	text TEXT NOT NULL, -- the actual comment
	
	submitted TIMESTAMP NOT NULL,
	edited TIMESTAMP DEFAULT NULL
);

CREATE INDEX comment_id_index ON comments(id);
CREATE INDEX comment_paste_id_index ON comments(paste_id);

CREATE TABLE favorites (
	id SERIAL PRIMARY KEY,
	paste_id INTEGER REFERENCES pastes(id),
	user_id INTEGER REFERENCES auth_user(id),
	added TIMESTAMP NOT NULL
);