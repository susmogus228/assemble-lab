import unittest
from contact_feedback import center_from_contacts
class ContactsTests(unittest.TestCase):
    def test_center_uses_both_fingertips(self):
        self.assertEqual(center_from_contacts([(.4,.08,.2)],[(.4,.12,.2)],(.4,.1,.2)),(.4,.1))
    def test_missing_or_distant_contacts_are_rejected(self):
        self.assertIsNone(center_from_contacts([],[(.4,.12,.2)],(.4,.1,.2)))
        self.assertIsNone(center_from_contacts([(2,2,2)],[(.4,.12,.2)],(.4,.1,.2)))
