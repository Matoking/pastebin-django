from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils.html import escape
from django.contrib.auth.models import User

from pastebin.testcase import CacheAwareTestCase
from pastebin import settings

from freezegun import freeze_time

from pastes.models import Paste, PasteReport, PasteContent

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
    
def upload_test_paste(test_case, username="TestUser", text="This is the test paste."):
    """
    Upload a test paste
    """
    paste = Paste()
    
    if username != None:
        test_user = User.objects.get(username=username)
    else:
        test_user = None
        
    return paste.add_paste(user=test_user,
                           text=text,
                           title="Test paste")

@freeze_time("2015-01-01")
class PasteTests(CacheAwareTestCase):
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
        
    def test_guest_can_upload_max_amount_of_pastes(self):
        """
        Upload as many pastes as possible as a guest and then try uploading one more
        """
        settings.MAX_PASTE_UPLOADS_PER_GUEST = 5
        guest_uploads = 5
        
        for i in range(0, guest_uploads):
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
        
        settings.MAX_PASTE_UPLOADS_PER_GUEST = -1
        
        response = self.client.post(reverse("home:home"), { "title": "Paste test title",
                                                            "text": "This is a test.",
                                                            "syntax_highlighting": "text",
                                                            "expiration": "never",
                                                            "visibility": "public"},
                                        follow=True)
        
        self.assertNotContains(response, "You can only upload")
        
    def test_expiring_paste_expires_correctly(self):
        """
        Upload a paste with an expiration time
        """
        with freeze_time("2015-01-01 12:00:00"):
            paste = Paste()
            char_id = paste.add_paste(text="This is a test paste",
                                      title="Expiring paste title",
                                      expiration=Paste.ONE_HOUR)
            
            response = self.client.post(reverse("show_paste", kwargs={"char_id": char_id}))
            
            self.assertContains(response, "Expiring paste title")
            self.assertNotContains(response, "The paste you tried to view has expired")
            
        with freeze_time("2015-01-01 13:00:01"):
            response = self.client.post(reverse("show_paste", kwargs={"char_id": char_id}))
            
            self.assertContains(response, "The paste you tried to view has expired", status_code=404)
            
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
        
    def test_paste_size_shown_correctly(self):
        """
        Submit a paste with a size of 8 bytes and check that it's shown correctly
        """
        response = self.client.post(reverse("home:home"), { "title": "Paste test title",
                                                            "text": "aaaaaaaa",
                                                            "syntax_highlighting": "text",
                                                            "expiration": "never",
                                                            "visibility": "public"},
                                    follow=True)
        
        # filesizeformat template tag uses a non-breakable space, thus the more verbose
        # check
        self.assertContains(response, '8\xc2\xa0bytes')
        
class PasteAdminTests(CacheAwareTestCase):
    def test_report_ignored_correctly(self):
        """
        Submit a paste report and ignore it
        """
        create_test_account(self)
        login_test_account(self)
        
        paste = upload_test_paste(self)
        
        user = User.objects.get(username="TestUser")
        user.is_staff = True
        user.is_superuser = True
        user.save()
        
        response = self.client.post(reverse("pastes:report_paste", kwargs={"char_id": paste}),
                                                                          {"text": "This is a report for the first paste",
                                                                           "reason": "illegal_content"})
        
        self.assertContains(response, "The paste report was sent successfully")
        
        report_id = PasteReport.objects.get(type="illegal_content").id
        
        response = self.client.post(reverse("admin:pastes_pastereport_process_report", kwargs={"report_ids": report_id}))
        
        self.assertContains(response, "TestUser -> Test paste")
        self.assertContains(response, "This is a report for the first paste")
        
        self.assertContains(response, "This is the test paste")
        
        response = self.client.post(reverse("admin:pastes_pastereport_process_report", kwargs={"report_ids": report_id}),
                                                                                              {"ignore": "true",
                                                                                               "removal_reason": ""})
        
        self.assertContains(response, "The reports were marked as checked")
        
    def test_report_removed_correctly(self):
        """
        Submit a paste report and remove the offending paste
        """
        create_test_account(self)
        login_test_account(self)
        
        paste = upload_test_paste(self)
        
        user = User.objects.get(username="TestUser")
        user.is_staff = True
        user.is_superuser = True
        user.save()
        
        response = self.client.post(reverse("pastes:report_paste", kwargs={"char_id": paste}),
                                                                          {"text": "This is a report for the first paste",
                                                                           "reason": "illegal_content"})
        
        report_id = PasteReport.objects.get(type="illegal_content").id
        
        response = self.client.post(reverse("admin:pastes_pastereport_process_report", kwargs={"report_ids": report_id}),
                                                                                              {"remove": "true",
                                                                                               "removal_reason": "This paste is illegal you know"})
        
        self.assertContains(response, "The paste(s) were removed.")
        
        response = self.client.get(reverse("show_paste", kwargs={"char_id": paste}))
        
        self.assertContains(response, "This paste is illegal you know", status_code=404)
        
        # The paste content should still exist
        paste_content = PasteContent.objects.get(hash="81e7fd17afe49f1ebdfbcec983c12377e63b90982eb2e50288a3f3b3b65a06cf",
                                                 format="none")
        
        self.assertEquals(paste_content.text, "This is the test paste.")
        
    def test_report_deleted_correctly(self):
        """
        Submit a paste report and remove the offending paste
        """
        create_test_account(self)
        login_test_account(self)
        
        paste = upload_test_paste(self)
        
        user = User.objects.get(username="TestUser")
        user.is_staff = True
        user.is_superuser = True
        user.save()
        
        response = self.client.post(reverse("pastes:report_paste", kwargs={"char_id": paste}),
                                                                          {"text": "This is a report for the first paste",
                                                                           "reason": "illegal_content"})
        
        report_id = PasteReport.objects.get(type="illegal_content").id
        
        response = self.client.post(reverse("admin:pastes_pastereport_process_report", kwargs={"report_ids": report_id}),
                                                                                              {"delete": "true",
                                                                                               "removal_reason": "This paste is illegal you know"})
        
        self.assertContains(response, "The paste(s) were deleted permanently")
        
        response = self.client.get(reverse("show_paste", kwargs={"char_id": paste}))
        
        self.assertContains(response, "This paste is illegal you know", status_code=404)
        
        # The paste content should've been removed as well
        self.assertEquals(PasteContent.objects.filter(hash="81e7fd17afe49f1ebdfbcec983c12377e63b90982eb2e50288a3f3b3b65a06cf",
                                                      format="none").exists(), False)
        
    def test_multiple_reports_handled_correctly(self):
        """
        Submit two pastes and two reports and remove them simultaneously
        """
        create_test_account(self)
        login_test_account(self)
        
        paste_one = upload_test_paste(self, username=None)
        
        paste_two = upload_test_paste(self, text="This is the second test paste.")
        
        user = User.objects.get(username="TestUser")
        user.is_staff = True
        user.is_superuser = True
        user.save()
        
        self.client.post(reverse("pastes:report_paste", kwargs={"char_id": paste_one}),
                                                               {"text": "This is a report for the first paste",
                                                                "reason": "illegal_content"})
        
        report_one_id = PasteReport.objects.get(type="illegal_content").id
        
        self.client.post(reverse("pastes:report_paste", kwargs={"char_id": paste_two}),
                                                               {"text": "This is a report for the second paste",
                                                                "reason": "spam"})
        
        report_two_id = PasteReport.objects.get(type="spam").id
        
        response = self.client.post(reverse("admin:pastes_pastereport_process_report", kwargs={"report_ids": "%d,%d" % (report_one_id, report_two_id)}))
        
        self.assertContains(response, "This is a report for the first paste")
        self.assertContains(response, "This is a report for the second paste")
               
        self.assertContains(response, "This is the test paste.")
        self.assertContains(response, "This is the second test paste.")
        
        response = self.client.post(reverse("admin:pastes_pastereport_process_report", kwargs={"report_ids": "%d,%d" % (report_one_id, report_two_id)}),
                                                                                              {"remove": "true",
                                                                                               "removal_reason": "Both are deleted"})

        self.assertContains(response, "The paste(s) were removed.")
        
        response = self.client.get(reverse("show_paste", kwargs={"char_id": paste_one}))
        
        self.assertContains(response, "Both are deleted", status_code=404)

        response = self.client.get(reverse("show_paste", kwargs={"char_id": paste_two}))
        
        self.assertContains(response, "Both are deleted", status_code=404)