from pastebin.testcase import CacheAwareTestCase

from pastes.models import Paste

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

import json

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

class CommentTests(CacheAwareTestCase):
    def test_comment_can_be_posted(self):
        """
        Post a comment to a paste and check that it is received
        """
        create_test_account(self)
        login_test_account(self)
        char_id = upload_test_paste(self)
        
        response = self.client.post(reverse("comments:add_comment"), {"char_id": char_id,
                                                                      "text": "This is a test comment"})
        response = json.loads(response.content)
        
        self.assertEqual(response["status"], "success")
        
        response = self.client.post(reverse("comments:get_comments"), {"char_id": char_id,
                                                                      "page": 0})
        response = json.loads(response.content)
        
        self.assertEqual(response["status"], "success")
        self.assertEqual(len(response["data"]["comments"]), 1)
        self.assertEqual(response["data"]["comments"][0]["text"], "This is a test comment")
        
    def test_comment_can_be_edited(self):
        """
        Post a comment and then try to edit it
        """
        create_test_account(self)
        login_test_account(self)
        char_id = upload_test_paste(self)
        
        response = self.client.post(reverse("comments:add_comment"), {"char_id": char_id,
                                                                      "text": "This is a test comment"})
        response = json.loads(response.content)
        
        self.assertEqual(response["status"], "success")
        
        comment_id = response["data"]["comments"][0]["id"]
        
        response = self.client.post(reverse("comments:edit_comment"), {"char_id": char_id,
                                                                       "text": "The new comment text",
                                                                       "id": comment_id,
                                                                       "page": 0})
        response = json.loads(response.content)
        
        self.assertEqual(response["status"], "success")
        
        response = self.client.post(reverse("comments:get_comments"), {"char_id": char_id,
                                                                       "page": 0})
        response = json.loads(response.content)
        
        self.assertEqual(response["status"], "success")
        
        self.assertEqual(response["data"]["comments"][0]["text"], "The new comment text")
        
    def test_comment_can_be_deleted(self):
        """
        Post a comment and then delete it
        """
        create_test_account(self)
        login_test_account(self)
        char_id = upload_test_paste(self)
        
        response = self.client.post(reverse("comments:add_comment"), {"char_id": char_id,
                                                                      "text": "This is a test comment"})
        response = json.loads(response.content)
        
        self.assertEqual(response["status"], "success")
        
        comment_id = response["data"]["comments"][0]["id"]
        
        response = self.client.post(reverse("comments:delete_comment"), {"char_id": char_id,
                                                                         "id": comment_id,
                                                                         "page": 0})
        response = json.loads(response.content)
        
        self.assertEqual(response["status"], "success")
        
        response = self.client.post(reverse("comments:get_comments"), {"char_id": char_id,
                                                                       "page": 0})
        response = json.loads(response.content)
        
        self.assertEqual(response["status"], "success")
        self.assertEqual(len(response["data"]["comments"]), 0)
        
    def test_user_cant_delete_other_comment(self):
        """
        Post a comment and try deleting it with an account other than the one that posted it
        """
        create_test_account(self)
        login_test_account(self)
        char_id = upload_test_paste(self)
        
        response = self.client.post(reverse("comments:add_comment"), {"char_id": char_id,
                                                                      "text": "This is a test comment"})
        response = json.loads(response.content)
        
        self.assertEqual(response["status"], "success")
        
        comment_id = response["data"]["comments"][0]["id"]
        
        logout(self)
        create_test_account(self, "TestUser2")
        login_test_account(self, "TestUser2")
        
        response = self.client.post(reverse("comments:delete_comment"), {"char_id": char_id,
                                                                         "id": comment_id,
                                                                         "page": 0})
        response = json.loads(response.content)
        
        self.assertEqual(response["status"], "fail")
        
    def test_user_cant_edit_other_comment(self):
        """
        Post a comment and try editing it with an account other than the one that posted it
        """
        create_test_account(self)
        login_test_account(self)
        char_id = upload_test_paste(self)
        
        response = self.client.post(reverse("comments:add_comment"), {"char_id": char_id,
                                                                      "text": "This is a test comment"})
        response = json.loads(response.content)
        
        self.assertEqual(response["status"], "success")
        
        comment_id = response["data"]["comments"][0]["id"]
        
        logout(self)
        create_test_account(self, "TestUser2")
        login_test_account(self, "TestUser2")
        
        response = self.client.post(reverse("comments:edit_comment"), {"char_id": char_id,
                                                                       "text": "Haha I'll edit you",
                                                                       "id": comment_id,
                                                                       "page": 0})
        response = json.loads(response.content)
        
        self.assertEqual(response["status"], "fail")