from django.test import TestCase

from django.core.urlresolvers import reverse

class PasteTests(TestCase):
    def test_upload_paste(self):
        """
        Check that paste is submitted correctly and can be viewed
        """
        response = self.client.post(reverse("pastes:submit_paste"), { "title": "Paste test title",
                                                                      "text": "This is a test.",
                                                                      "syntax_highlighting": "text",
                                                                      "expiration": "never",
                                                                      "visibility": "public"},
                                    follow=True)
        
        self.assertContains(response, "Paste test title")
        self.assertContains(response, "This is a test.")