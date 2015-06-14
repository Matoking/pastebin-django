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
        
    def test_latest_pastes_shows_correct_pastes(self):
        """
        Upload hidden and expiring paste and make sure hidden and expiring pastes
        aren't shown when they shouldn't be shown
        """
        with freeze_time("2015-01-01 12:00:00"):
            for i in range(0, 5):
                self.client.post(reverse("home:home"), {"title": "Normal paste %d" % i,
                                                        "text": "This is a test.",
                                                        "syntax_highlighting": "text",
                                                        "expiration": "never",
                                                        "visibility": "public"},
                                                        follow=True)
                
            for i in range(0, 5):
                self.client.post(reverse("home:home"), {"title": "Expiring paste %d" % i,
                                                        "text": "This is a test",
                                                        "syntax_highlighting": "text",
                                                        "expiration": "1h",
                                                        "visibility": "public"},
                                                        follow=True)
                
            self.client.post(reverse("home:home"), {"title": "Hidden paste",
                                                    "text": "This is a test",
                                                    "syntax_highlighting": "text",
                                                    "expiration": "1h",
                                                    "visibility": "hidden"},
                                                    follow=True)
            
            response = self.client.get(reverse("latest_pastes"))
            
            self.assertContains(response, "Normal paste", count=5)
            self.assertContains(response, "Expiring paste", count=5)
            self.assertNotContains(response, "Hidden paste")
            
        with freeze_time("2015-01-01 13:00:01"):
            self.clearCache()
            
            response = self.client.get(reverse("latest_pastes"))
            
            self.assertContains(response, "Normal paste", count=5)
            self.assertNotContains(response, "Expiring paste")
            self.assertNotContains(response, "Hidden paste")
            
    def test_latest_pastes_redirects_to_last_page(self):
        """
        Try checking a page of latest pastes which doesn't exist
        User should be redirected to the last page
        """
        self.client.post(reverse("home:home"), {"title": "Test paste",
                                                "text": "This is a test.",
                                                "syntax_highlighting": "text",
                                                "expiration": "never",
                                                "visibility": "public"},
                                                follow=True)
        
        response = self.client.get(reverse("latest_pastes", kwargs={"page": 2}))
        
        self.assertContains(response, "Test paste")
        self.assertContains(response, "1</span>")
        self.assertNotContains(response, "2</span>")
        
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
            
            self.clearCache()
            response = self.client.get(reverse("home:home"))
            
            self.assertContains(response, "Paste paste")
            
        with freeze_time("2015-01-01 13:00:01"):
            self.clearCache()
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