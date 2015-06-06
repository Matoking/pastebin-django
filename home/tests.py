from pastebin.testcase import CacheAwareTestCase

from freezegun import freeze_time

from django.core.urlresolvers import reverse

@freeze_time("2015-01-01")
class LatestPastesTests(CacheAwareTestCase):
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
        
    def test_latest_pastes_doesnt_show_expired_pastes(self):
        """
        Upload an expiring paste and check that it isn't visible after it has expired
        """
        with freeze_time("2015-01-01 12:00:00"):
            self.client.post(reverse("home:home"), {"title": "Paste paste",
                                                    "text": "This is a test.",
                                                    "syntax_highlighting": "text",
                                                    "expiration": "1h",
                                                    "visibility": "public"},
                                                    follow=True)
            
            response = self.client.get(reverse("home:home"))
            
            self.assertContains(response, "Paste paste")
            
        with freeze_time("2015-01-01 13:00:01"):
            response = self.client.get(reverse("home:home"))
            
            self.assertContains(response, "No pastes have been submitted yet")
        
    def test_random_with_no_pastes_redirects_to_home(self):
        """
        Try going to a random paste when no pastes have been uploaded
        User should be redirect to home.
        """
        response = self.client.post(reverse("random_paste"), follow=True)
        
        self.assertContains(response, "Upload a new paste")
        
    def test_random_with_paste(self):
        """
        Upload one paste and go to a random paste
        """
        self.client.post(reverse("home:home"), { "title": "Test paste",
                                                 "text": "This is a test.",
                                                 "syntax_highlighting": "text",
                                                 "expiration": "never",
                                                 "visibility": "public"},
                                                follow=True)
        
        response = self.client.post(reverse("random_paste"), follow=True)
        
        self.assertContains(response, "Test paste")