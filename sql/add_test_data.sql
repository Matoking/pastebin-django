INSERT INTO pastes (char_id, title, hash, hidden, submitted) VALUES
				   ('A5vSfcXu', 'Test paste', 'a2ee48bd00238c5a5f42d71cadf1d418d01827fda4acf90fd413debec5d2c5dc', false,
				    timestamp '2015-03-01 12:00:00'),
				   ('d5dAASXC', 'Another test paste', 'd4b1a4af2c8852b9df30097e075ca17be6174b8e7f29437257474e3314a39f5d', false,
				    timestamp '2015-03-01 12:00:00');
				    
INSERT INTO paste_content (hash, text, formatted_text) VALUES
				   ('a2ee48bd00238c5a5f42d71cadf1d418d01827fda4acf90fd413debec5d2c5dc',
				    'This is a test paste.',
				    'This is a test paste.'),
				   ('d4b1a4af2c8852b9df30097e075ca17be6174b8e7f29437257474e3314a39f5d',
				    'This is another test paste. Unfortunately, this one doesn''t have any interesting content either.',
				    'This is another test paste. Unfortunately, this one doesn''t have any interesting content either.');