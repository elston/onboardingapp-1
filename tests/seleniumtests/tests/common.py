from ..page_objects.service_mailinator import MailinatorHomePage


# TODO access inbox to fetch sent mails
def help_access_mailinator(self, email):
    (
        MailinatorHomePage(self)
            .start()
            .assert_page()
            .access_inbox(email)
    )
