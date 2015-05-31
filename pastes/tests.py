from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils.html import escape

from pastes.models import Paste

class PasteTests(TestCase):
    def test_upload_paste(self):
        """
        Check that paste is submitted correctly and can be viewed
        """
        response = self.client.post(reverse("home:home"), { "title": "Paste test title",
                                                            "text": "This is a test.",
                                                            "syntax_highlighting": "text",
                                                            "expiration": "never",
                                                            "visibility": "public"},
                                    follow=True)
        
        self.assertContains(response, "Paste test title")
        self.assertContains(response, "This is a test.")
        
    def test_upload_encrypted_paste(self):
        """
        Upload an encrypted paste and check that it is shown correctly in the view
        """
        response = self.client.post(reverse("home:home"), {"title": "Encrypted paste",
                                                           "text": "This is not really encrypted",
                                                           "syntax_highlighting": "text",
                                                           "expiration": "never",
                                                           "visibility": "public",
                                                           "encrypted": True},
                                    follow=True)
        
        self.assertContains(response, "This paste is encrypted")
        
    def test_cant_upload_empty_paste(self):
        """
        Check that an empty paste can't be uploaded
        """
        response = self.client.post(reverse("home:home"), { "title": "Paste test title",
                                                            "text": "",
                                                            "syntax_highlighting": "text",
                                                            "expiration": "never",
                                                            "visibility": "public"},
                                    follow=True)
        
        # We should be redirected back to the front page on failure
        self.assertContains(response, "Upload a new paste")
        self.assertContains(response, escape("The paste can't be empty."))
        
    def test_raw_paste_displayed_correctly(self):
        """
        Create a paste and view it in raw format
        """
        text = """This is a raw paste.<b></b>>TEST TEST TEST     TEST"""
        
        paste = Paste()
        char_id = paste.add_paste(text)
        
        response = self.client.get(reverse("raw_paste", kwargs={"char_id": char_id}))
        
        # The response should contain the next text and nothing else
        self.assertContains(response, text)
        self.assertNotContains(response, "Untitled")
        
    def test_non_existent_paste_displays_error(self):
        """
        If user tries to view a non-existing paste a "paste not found" error should be displayed
        """
        response = self.client.get(reverse("show_paste", kwargs={"char_id": "420BlzIt"}))
        
        self.assertContains(response, "Paste not found", status_code=404)