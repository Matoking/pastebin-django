from django.test import TestCase
from django.core.urlresolvers import reverse

class LatestPastesTests(TestCase):
    def test_latest_pastes_empty(self):
        """
        Test that latest pastes shows the "no pastes uploaded" message when no pastes
        have been uploaded
        """
        response = self.client.get(reverse("latest_pastes"))
        
        self.assertContains(response, "No pastes uploaded")
        
    def test_latest_pastes_with_pastes(self):
        """
        Upload two pastes and check that they're visible on the list
        """
        self.client.post(reverse("home:home"), { "title": "Paste",
                                                 "text": "This is a test.",
                                                 "syntax_highlighting": "text",
                                                 "expiration": "never",
                                                 "visibility": "public"},
                                                follow=True)
        
        self.client.post(reverse("home:home"), { "title": "Paste 2",
                                                 "text": "This is a test.",
                                                 "syntax_highlighting": "text",
                                                 "expiration": "never",
                                                 "visibility": "public"},
                                                follow=True)
        
        response = self.client.get(reverse("latest_pastes"))
        
        self.assertContains(response, "Paste")
        self.assertContains(response, "Paste 2")
        
    def test_latest_pastes_doesnt_show_hidden_pastes(self):
        """
        Upload a hidden paste and check that it isn't visible in the latest pastes
        """
        self.client.post(reverse("home:home"), {"title": "Paste paste",
                                                "text": "This is a test.",
                                                "syntax_highlighting": "text",
                                                "expiration": "never",
                                                "visibility": "hidden"},
                                                follow=True)
        
        response = self.client.get(reverse("latest_pastes"))
        
        self.assertContains(response, "No pastes uploaded")