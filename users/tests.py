from django.test import TestCase
from django.core.urlresolvers import reverse

def create_test_account(test_case):
    """
    Creates user TestUser
    """
    test_case.client.post(reverse("users:register"), {"username": "TestUser",
                                                      "password": "password",
                                                      "confirm_password": "password"})
    
def login_test_account(test_case):
    """
    Logs in as TestUser. User must be created before logging in
    """
    test_case.client.post(reverse("users:login"), {"username": "TestUser",
                                                   "password": "password"})
    
def upload_test_paste(test_case):
    """
    Upload a test paste
    """
    test_case.client.post(reverse("pastes:submit_paste"), { "title": "Paste test title",
                                                            "text": "This is a test.",
                                                            "syntax_highlighting": "text",
                                                            "expiration": "never",
                                                            "visibility": "public"},
                        follow=True)

class UserTests(TestCase):
    def test_user_can_register(self):
        """
        Register with valid details
        """
        response = self.client.post(reverse("users:register"), {"username": "TestUser",
                                                                "password": "password",
                                                                "confirm_password": "password"})
        
        self.assertContains(response, "Registered!")
        
    def test_user_can_login(self):
        """
        Login after creating a test account
        """
        create_test_account(self)
        
        response = self.client.post(reverse("users:login"), {"username": "TestUser",
                                                             "password": "password"})
        
        self.assertContains(response, "Logged in!")
        
    def test_user_empty_profile_displayed_correctly(self):
        """
        Check that new user's profile page is displayed correctly
        """
        create_test_account(self)
        
        response = self.client.get(reverse("users:profile", kwargs={"username": "TestUser"}))
        
        self.assertContains(response, "This user hasn't added any favorites yet.")
        self.assertContains(response, "This user hasn't uploaded any pastes yet.")
        
        # Now login and check the same page again
        login_test_account(self)
        
        response = self.client.get(reverse("users:profile", kwargs={"username": "TestUser"}))
        
        self.assertContains(response, "You haven't uploaded any pastes yet.")
        self.assertContains(response, "You haven't added any favorites yet.")
        
    def test_user_can_upload_paste(self):
        """
        Upload a paste while logged in and check that the user is added as its
        uploader
        """
        create_test_account(self)
        login_test_account(self)
        
        response = self.client.post(reverse("pastes:submit_paste"), { "title": "Paste test title",
                                                                      "text": "This is a test.",
                                                                      "syntax_highlighting": "text",
                                                                      "expiration": "never",
                                                                      "visibility": "public"},
                                    follow=True)
        
        self.assertContains(response, "Delete paste")
        
    def test_user_uploaded_paste_displayed_in_profile(self):
        """
        Upload a paste as an user and check that it is displayed in the user's profile
        """
        create_test_account(self)
        login_test_account(self)
        upload_test_paste(self)
        
        response = self.client.get(reverse("users:profile", kwargs={"username": "TestUser"}))
        
        self.assertContains(response, "Paste test title")
        self.assertNotContains(response, "You haven't uploaded any pastes yet.")