from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from pastebin import settings
from pastebin.testcase import CacheAwareTestCase

from pastes.models import Paste

from freezegun import freeze_time

from django.utils.html import escape

def create_test_account(test_case, username="TestUser"):
    """
    Creates user TestUser
    """
    test_case.client.post(reverse("users:register"), {"username": username,
                                                      "password": "password",
                                                      "confirm_password": "password"})
    
def login_test_account(test_case, username="TestUser"):
    """
    Logs in as TestUser. User must be created before logging in
    """
    test_case.client.post(reverse("users:login"), {"username": username,
                                                   "password": "password"})
    
def logout(test_case):
    """
    Logout from the current user
    """
    test_case.client.post(reverse("users:logout"))
    
def upload_test_paste(test_case, username="TestUser"):
    """
    Upload a test paste
    """
    paste = Paste()
    
    test_user = User.objects.get(username=username)
    
    return paste.add_paste(user=test_user,
                           text="This is the test paste.",
                           title="Test paste")

@freeze_time("2015-01-01")
class UserTests(CacheAwareTestCase):
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
        
        response = self.client.post(reverse("home:home"), { "title": "Paste test title",
                                                            "text": "This is a test.",
                                                            "syntax_highlighting": "text",
                                                            "expiration": "never",
                                                            "visibility": "public"},
                                    follow=True)
        
        self.assertContains(response, "Remove")
        self.assertContains(response, "Edit")
        
    def test_user_can_upload_max_amount_of_pastes(self):
        """
        Upload as many pastes as allowed by settings and then try uploading one more paste
        """
        create_test_account(self)
        login_test_account(self)
        
        settings.MAX_PASTE_UPLOADS_PER_USER = 5
        user_uploads = 5
        
        for i in range(0, user_uploads):
            response = self.client.post(reverse("home:home"), { "title": "Paste test title",
                                                                "text": "This is a test.",
                                                                "syntax_highlighting": "text",
                                                                "expiration": "never",
                                                                "visibility": "public"},
                                        follow=True)
            
            self.assertNotContains(response, "You can only upload")
            
        response = self.client.post(reverse("home:home"), { "title": "Paste test title",
                                                            "text": "This is a test.",
                                                            "syntax_highlighting": "text",
                                                            "expiration": "never",
                                                            "visibility": "public"},
                                        follow=True)
        
        self.assertContains(response, "You can only upload")
        
        settings.MAX_PASTE_UPLOADS_PER_USER = -1
        
        response = self.client.post(reverse("home:home"), { "title": "Paste test title",
                                                            "text": "This is a test.",
                                                            "syntax_highlighting": "text",
                                                            "expiration": "never",
                                                            "visibility": "public"},
                                        follow=True)
        
        self.assertNotContains(response, "You can only upload")
        
    def test_user_can_edit_max_amount_of_times(self):
        """
        Upload a paste and edit it until the limit is reached and then try editing it again
        """
        create_test_account(self)
        login_test_account(self)
        
        settings.MAX_PASTE_EDITS_PER_USER = 5
        user_edits = 5
        
        char_id = upload_test_paste(self)
        
        for i in range(0, 5):
            response = self.client.post(reverse("pastes:edit_paste", kwargs={"char_id": char_id}),
                                                                            {"title": "New paste title",
                                                                             "text": "This is the new text",
                                                                             "syntax_highlighting": "text",
                                                                             "expiration": "never",
                                                                             "visibility": "public",
                                                                             "note": "Testing update note"},
                                               follow=True)
            
            self.assertNotContains(response, "You can only edit")
            
        response = self.client.post(reverse("pastes:edit_paste", kwargs={"char_id": char_id}),
                                                                        {"title": "New paste title",
                                                                         "text": "This is the new text",
                                                                         "syntax_highlighting": "text",
                                                                         "expiration": "never",
                                                                         "visibility": "public",
                                                                         "note": "Testing update note"},
                                               follow=True)
        
        self.assertContains(response, "You can only edit")
        
        settings.MAX_PASTE_EDITS_PER_USER = -1
        
        response = self.client.post(reverse("pastes:edit_paste", kwargs={"char_id": char_id}),
                                                                        {"title": "New paste title",
                                                                         "text": "This is the new text",
                                                                         "syntax_highlighting": "text",
                                                                         "expiration": "never",
                                                                         "visibility": "public",
                                                                         "note": "Testing update note"},
                                               follow=True)
        
        self.assertNotContains(response, "You can only edit")
        
    def test_user_can_edit_paste(self):
        """
        Upload a paste while logged in and edit it
        """
        create_test_account(self)
        login_test_account(self)
        
        test_user = User.objects.get(username="TestUser")
        
        paste = Paste()
        char_id = paste.add_paste(user=test_user,
                                  text="This is a test paste number one.",
                                  title="Tested paste")
        
        self.assertEquals(len(char_id), 8)
        
        # Edit the paste
        response = self.client.post(reverse("pastes:edit_paste", kwargs={"char_id": char_id}),
                                                                 {"title": "New paste title",
                                                                  "text": "This is the new text",
                                                                  "syntax_highlighting": "text",
                                                                  "expiration": "never",
                                                                  "visibility": "public"},
                                    follow=True)
        
        self.assertContains(response, "New paste title")
        self.assertContains(response, "This is the new text")
        
        self.assertNotContains(response, "This is a test paste number one.")
        
    def test_user_cant_edit_other_pastes(self):
        """
        Upload a paste on one account and try editing it on another account
        """
        create_test_account(self)
        login_test_account(self)
        
        char_id = upload_test_paste(self)
        
        response = self.client.get(reverse("pastes:edit_paste", kwargs={"char_id": char_id}))
        
        self.assertContains(response, "Note")
        self.assertContains(response, "Visibility")
        self.assertContains(response, "Update")
        
        logout(self)
        
        create_test_account(self, "TestUser2")
        login_test_account(self, "TestUser2")
        
        response = self.client.get(reverse("pastes:edit_paste", kwargs={"char_id": char_id}))
        
        self.assertContains(response, "You can't edit a paste")
    
    def test_user_cant_remove_other_pastes(self):
        """
        Upload a paste on one account and try removing it on another account
        """
        create_test_account(self)
        login_test_account(self)
        
        char_id = upload_test_paste(self)
        
        response = self.client.get(reverse("pastes:remove_paste", kwargs={"char_id": char_id}))
        
        self.assertContains(response, "You are removing the paste")
        
        logout(self)
        
        create_test_account(self, "TestUser2")
        login_test_account(self, "TestUser2")
        
        response = self.client.get(reverse("pastes:remove_paste", kwargs={"char_id": char_id}))
        
        self.assertContains(response, "You can't remove a paste")
        
    def test_paste_has_correct_history(self):
        """
        Upload a paste, update it and check that the paste history is displayed correctly
        """
        create_test_account(self)
        login_test_account(self)
        
        test_user = User.objects.get(username="TestUser")
        
        paste = Paste()
        char_id = paste.add_paste(user=test_user,
                                  text="This is a test paste number one.",
                                  title="Tested paste")
        
        self.client.post(reverse("pastes:edit_paste", kwargs={"char_id": char_id}),
                                                             {"title": "New paste title",
                                                              "text": "This is the new text",
                                                              "syntax_highlighting": "text",
                                                              "expiration": "never",
                                                              "visibility": "public",
                                                              "note": "Testing update note"},
                                follow=True)
        
        response = self.client.get(reverse("pastes:paste_history", kwargs={"char_id": char_id}))
        
        self.assertContains(response, "Testing update note")
        
    def test_paste_versions_can_be_viewed(self):
        """
        Upload a paste, update it twice and check that all versions can be viewed individually
        """
        ""
        create_test_account(self)
        login_test_account(self)
        
        test_user = User.objects.get(username="TestUser")
        
        paste = Paste()
        char_id = paste.add_paste(user=test_user,
                                  text="This is the version one.",
                                  title="Tested paste")
        
        self.client.post(reverse("pastes:edit_paste", kwargs={"char_id": char_id}),
                                                             {"title": "Second version title",
                                                              "text": "This is the version two",
                                                              "syntax_highlighting": "python",
                                                              "expiration": "never",
                                                              "visibility": "public",
                                                              "note": "Update two"},
                                follow=True)
        
        self.client.post(reverse("pastes:edit_paste", kwargs={"char_id": char_id}),
                                                             {"title": "Third version title",
                                                              "text": "This is the version three",
                                                              "syntax_highlighting": "php",
                                                              "expiration": "never",
                                                              "visibility": "public",
                                                              "note": "Testing update note"},
                                follow=True)
        
        # Test that the normal link has the newest version
        response = self.client.get(reverse("show_paste", kwargs={"char_id": char_id}))
        
        self.assertContains(response, "PHP")
        self.assertContains(response, "Third version title")
        
        # Test the first version
        response = self.client.get(reverse("show_paste", kwargs={"char_id": char_id,
                                                                 "version": 1}))
        
        self.assertContains(response, "Text only")
        self.assertContains(response, "Tested paste")
        
        # Test the second version
        response = self.client.get(reverse("show_paste", kwargs={"char_id": char_id,
                                                                 "version": 2}))
        
        self.assertContains(response, "Python")
        self.assertContains(response, "Second version title")
        
        # Test the third version
        response = self.client.get(reverse("show_paste", kwargs={"char_id": char_id,
                                                                 "version": 3}))
        
        self.assertContains(response, "PHP")
        self.assertContains(response, "Third version title")
        
    def test_user_uploaded_paste_displayed_in_profile(self):
        """
        Upload a paste as an user and check that it is displayed in the user's profile
        """
        create_test_account(self)
        login_test_account(self)
        upload_test_paste(self)
        
        response = self.client.get(reverse("users:profile", kwargs={"username": "TestUser"}))
        
        self.assertContains(response, "Test paste")
        self.assertNotContains(response, escape("You haven't uploaded any pastes yet."))
        
    def test_user_can_change_password(self):
        """
        Change user's password and login again with the new password
        """
        create_test_account(self)
        login_test_account(self)
        
        response = self.client.post(reverse("users:change_password", kwargs={"username": "TestUser"}),
                                                                    {"current_password": "password",
                                                                     "new_password": "newPassword",
                                                                     "confirm_new_password": "newPassword"})
        
        self.assertContains(response, "Password changed!")
        
        self.client.get(reverse("users:logout"))
        
        response = self.client.post(reverse("users:login"), {"username": "TestUser",
                                                             "password": "newPassword"})
        
        self.assertContains(response, "Logged in!")
        
    def test_user_can_delete_account(self):
        """
        Delete user's account and check that it can't be accessed again
        """
        create_test_account(self)
        login_test_account(self)
        upload_test_paste(self)
        
        response = self.client.post(reverse("users:delete_account", kwargs={"username": "TestUser"}),
                                                                    {"password": "password"})
        
        self.assertContains(response, "Your account has been deleted.")
        
        response = self.client.get(reverse("users:profile", kwargs={"username": "TestUser"}))
        
        self.assertContains(response, "User not found", status_code=404)