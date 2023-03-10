import os.path
import tempfile
import time
import unittest
from unittest.mock import patch

from PyQt6.QtCore import Qt, QCoreApplication, QObject, QEventLoop, QEvent
from PyQt6.QtGui import QAction
from PyQt6.QtTest import QSignalSpy, QTest
from PyQt6.QtWidgets import QApplication, QLineEdit, QTextEdit, QPushButton, QMessageBox
from pypgpeed.run import run

from pypgpeed import make_key, encrypt_message, decrypt_message, encrypt_cleartext_message, verify_message as vf_msg, \
    PGP_Main

pass_user_one = "TeStPaSs1!"
pass_user_two = "TeStPaSs2!"

def wait_for_val(test, old_val, box):
    # wait for the field to change - also track times its checked
    times = 0
    while True:
        new_output_text = box.toPlainText()
        if times == 20:
            test.fail("Took 10 seconds with no output, thats an issue")
            return
        elif new_output_text != old_val:
            break
        time.sleep(0.5)
        times += 1
    return new_output_text

class MyWindowTest(unittest.TestCase):
    def setUp(self):
        """Sometimes we dont need these bits as they are creaton in the method"""
        if self._testMethodName != "test_run":
            temp_dir = tempfile.TemporaryDirectory()
            self.person_one_pri, self.person_one_pub = make_key("person1", "person1@test.com", pass_user_one, temp_dir.name)
            self.person_two_pri, self.person_two_pub = make_key("person2", "person2@test.com", pass_user_two, temp_dir.name)
            self.app = QApplication([])
            self.window = PGP_Main(True)

    def tearDown(self):
        """Sometimes we dont need these bits as they are creaton in the method"""
        if self._testMethodName != "test_run":
            self.window.close()
            self.window.dlg.close()
            self.app.quit()

    def test_blank(self):
        """Tests the the output box correctly displays error messages"""

        message = ""

        # get elements
        encrypt_button = self.window.findChild(QPushButton, "encrypt_button")
        encrypt_output_box = self.window.findChild(QTextEdit, "encrypt_output_box")
        encrypt_public_key_box = self.window.findChild(QTextEdit, "encrypt_public_key_box")
        encrypt_message_box = self.window.findChild(QTextEdit, "encrypt_message_box")

        # set the message to be encrypted
        encrypt_message_box.setText(message)
        # set the encryption box public key
        encrypt_public_key_box.setText(self.person_two_pub)
        #get the output text
        out_text = encrypt_output_box.toPlainText()
        #click the button to encrypt
        encrypt_button.click()
        #wait for the field to change - also track times its checked
        new_output_text = wait_for_val(self, out_text, encrypt_output_box)

        #get the new output text
        self.assertEqual(new_output_text, 'Message Blank')

    def test_key_error(self):
        """Tests the output box correctly displays error messages on invalid key"""

        message = "test"

        # get elements
        encrypt_button = self.window.findChild(QPushButton, "encrypt_button")
        encrypt_output_box = self.window.findChild(QTextEdit, "encrypt_output_box")
        encrypt_public_key_box = self.window.findChild(QTextEdit, "encrypt_public_key_box")
        encrypt_message_box = self.window.findChild(QTextEdit, "encrypt_message_box")

        # set the message to be encrypted
        encrypt_message_box.setText(message)
        # set the encryption box public key
        encrypt_public_key_box.setText("Not a valid key")
        # get the output text
        out_text = encrypt_output_box.toPlainText()
        # click the button to encrypt
        encrypt_button.click()
        # wait for the field to change - also track times its checked
        new_output_text = wait_for_val(self, out_text, encrypt_output_box)

        # get the new output text
        self.assertEqual(new_output_text.strip(), 'Key invalid - please enter a valid key')

    def test_key_blank(self):
        """Tests the output box correctly displays error messages on blank"""

        message = "test"

        # get elements
        encrypt_button = self.window.findChild(QPushButton, "encrypt_button")
        encrypt_output_box = self.window.findChild(QTextEdit, "encrypt_output_box")
        encrypt_public_key_box = self.window.findChild(QTextEdit, "encrypt_public_key_box")
        encrypt_message_box = self.window.findChild(QTextEdit, "encrypt_message_box")

        # set the message to be encrypted
        encrypt_message_box.setText(message)
        # set the encryption box public key
        encrypt_public_key_box.setText("")
        # get the output text
        out_text = encrypt_output_box.toPlainText()
        # click the button to encrypt
        encrypt_button.click()
        # wait for the field to change - also track times its checked
        new_output_text = wait_for_val(self, out_text, encrypt_output_box)

        # get the new output text
        self.assertEqual(new_output_text.strip(), 'Key blank - please enter a valid key')

    def test_encrypt(self):
        """Tests encrypting a message"""

        message = "Heyy"

        # get elements
        encrypt_button = self.window.findChild(QPushButton, "encrypt_button")
        copy_button_encrypt = self.window.findChild(QPushButton, "copy_button_encrypt")
        encrypt_output_box = self.window.findChild(QTextEdit, "encrypt_output_box")
        encrypt_public_key_box = self.window.findChild(QTextEdit, "encrypt_public_key_box")
        encrypt_message_box = self.window.findChild(QTextEdit, "encrypt_message_box")

        # set the message to be encrypted
        encrypt_message_box.setText(message)
        # set the encryption box public key
        encrypt_public_key_box.setText(self.person_two_pub)
        #get the output text
        out_text = encrypt_output_box.toPlainText()
        #click the button to encrypt
        encrypt_button.click()

        #wait for the field to change - also track times its checked
        new_output_text = wait_for_val(self, out_text, encrypt_output_box)
        #get the new output text
        self.assertEqual(new_output_text[:27], '-----BEGIN PGP MESSAGE-----')

        # check copy button works
        copy_button_encrypt.click()

        # Get the contents of the clipboard
        import pyperclip
        clipboard_text = pyperclip.paste()

        self.assertIn('-----BEGIN PGP MESSAGE-----', clipboard_text)

    def test_decrypt(self):
        """Tests decrypting a message"""

        # create a message to send
        send_message = 'This is a test!'
        #person1 encrypt message
        encrypted_message = encrypt_message(send_message, self.person_two_pub)
        # make sure the decrypted message is the same as the original message

        decrypt_button = self.window.findChild(QPushButton, "decrypt_button")
        copy_button_decrypt = self.window.findChild(QPushButton, "copy_button_decrypt")
        decrypt_pass_box = self.window.findChild(QTextEdit, "decrypt_pass_box")
        decrypt_output_box = self.window.findChild(QTextEdit, "decrypt_output_box")
        decrypt_private_key_box = self.window.findChild(QTextEdit, "decrypt_private_key_box")
        decrypt_message_box = self.window.findChild(QTextEdit, "decrypt_message_box")

        decrypt_message_box.setText(encrypted_message)
        decrypt_private_key_box.setText(self.person_two_pri)
        decrypt_pass_box.setText(pass_user_two)

        # get the output text
        out_text = decrypt_output_box.toPlainText()

        # check decrypts correctly
        # check decrypts correctly

        # click the button to encrypt
        decrypt_button.click()


        #wait for the field to change - also track times its checked
        new_output_text = wait_for_val(self, out_text, decrypt_output_box)
        # get the new output text
        self.assertEqual(new_output_text[:27], send_message)


        # check copy button works
        copy_button_decrypt.click()
        # Get the contents of the clipboard
        import pyperclip
        clipboard_text = pyperclip.paste()
        self.assertEqual(send_message, clipboard_text.strip())


        # check Fails decrypts on incorrect pass
        # check Fails decrypts on incorrect pass

        out_text = ""
        # set incorrect passphrase
        decrypt_pass_box.setText("TeStPaSs2!!!!")
        decrypt_button.click()
        #wait for the field to change - also track times its checked
        new_output_text = wait_for_val(self, out_text, decrypt_output_box)
        # get the new output text
        self.assertEqual(new_output_text, "Passphrase Error")

        # check Fails decrypts on no pass
        # check Fails decrypts on no pass

        out_text = ""
        # set incorrect passphrase
        decrypt_pass_box.setText("")
        decrypt_button.click()
        #wait for the field to change - also track times its checked
        new_output_text = wait_for_val(self, out_text, decrypt_output_box)
        # get the new output text
        self.assertEqual(new_output_text, "You have not supplied a passphrase")

        # check Fails decrypts on not PGP message
        # check Fails decrypts on not PGP message

        decrypt_pass_box.setText(pass_user_two)
        decrypt_private_key_box.setText(self.person_two_pri)
        decrypt_message_box.setText("Test Message")
        decrypt_button.click()

        out_text = ""

        #wait for the field to change - also track times its checked
        new_output_text = wait_for_val(self, out_text, decrypt_output_box)
        # get the new output text
        self.assertEqual(new_output_text, "Message not PGP error (possibly plain text)")

    def test_sign(self):
        """Tests signing a message"""

        message = "This is me"

        sign_message_box = self.window.findChild(QTextEdit, "sign_message_box")
        sign_private_key_box = self.window.findChild(QTextEdit, "sign_private_key_box")
        sign_output_box = self.window.findChild(QTextEdit, "sign_output_box")
        sign_passphrase_box = self.window.findChild(QTextEdit, "sign_passphrase_box")
        copy_button_sign = self.window.findChild(QPushButton, "copy_button_sign")
        sign_button = self.window.findChild(QPushButton, "sign_button")


        sign_message_box.setText(message)
        sign_private_key_box.setText(self.person_one_pri)
        sign_passphrase_box.setText(pass_user_one)


        out_text = sign_output_box.toPlainText()

        sign_button.click()

        #wait for the field to change - also track times its checked
        new_output_text = wait_for_val(self, out_text, sign_output_box)
        # get the new output text
        self.assertIn(new_output_text[:27], "-----BEGIN PGP SIGNED MESSA")


        # check copy button works
        copy_button_sign.click()
        # Get the contents of the clipboard
        import pyperclip
        clipboard_text = pyperclip.paste()
        self.assertEqual(sign_output_box.toPlainText().strip(), clipboard_text.strip())

    def test_verify(self):
        """Tests verifying a message"""

        message = "This is me"

        verify_message_box = self.window.findChild(QTextEdit, "verify_message_box")
        verify_public_key_box = self.window.findChild(QTextEdit, "verify_public_key_box")
        verify_output_box = self.window.findChild(QTextEdit, "verify_output_box")
        copy_button_verify = self.window.findChild(QPushButton, "copy_button_verify")
        verify_button = self.window.findChild(QPushButton, "verify_button")

        signed_mess = encrypt_cleartext_message(message, self.person_one_pri, pass_user_one)

        verify_message_box.setText(signed_mess)
        verify_public_key_box.setText(self.person_one_pub)

        out_text = verify_output_box.toPlainText()

        verify_button.click()

        # wait for the field to change - also track times its checked
        new_output_text = wait_for_val(self, out_text, verify_output_box)
        # get the new output text
        self.assertEqual(new_output_text, "Message verified... It was created by the owner of this public key.")

        # check copy button works
        copy_button_verify.click()
        # Get the contents of the clipboard
        import pyperclip
        clipboard_text = pyperclip.paste()
        self.assertEqual(new_output_text, clipboard_text.strip())

    def test_gpg_key_creation(self):
        "test creating PGP key"

        temp_directory = tempfile.TemporaryDirectory().name

        passphrase_box = self.window.dlg.findChild(QTextEdit, "gen_passphrase_box")
        name_box = self.window.dlg.findChild(QTextEdit, "gen_name_box")
        email_box = self.window.dlg.findChild(QTextEdit, "gen_email_box")
        output_location_box = self.window.dlg.findChild(QTextEdit, "gen_output_location_box")
        generate_button = self.window.dlg.findChild(QPushButton, "gen_generate_button")

        passphrase_box.setText("iuhsdf33aSDFFuisd!!")
        name_box.setText("testuser1")
        email_box.setText("testuser1@test.com")
        output_location_box.setText(temp_directory)
        generate_button.click()

        pri_exists = os.path.isfile(os.path.join(temp_directory, "pri_key.key"))
        pub_exists = os.path.isfile(os.path.join(temp_directory, "pub_key.key"))

        # check if the files were created
        self.assertTrue(pri_exists)
        self.assertTrue(pub_exists)

        #then have to do a bit of tweaking here pretend the window was open and what it does next.
        self.window._set_key(temp_directory)

        # check if the path to the keys has been update
        self.assertEqual(self.window.key_location,  temp_directory)

        #get the new keys
        with open(os.path.join(temp_directory, "pri_key.key"), "r") as f:
            pri_key = f.read()
        with open(os.path.join(temp_directory, "pub_key.key"), "r") as f:
            pub_key = f.read()

        # check all the relevant fields in the parent window have been updated with the new key
        for k, v in self.window.key_boxes.items():
            for el in v:
                if k == "private":
                    self.assertEqual(el.toPlainText().strip(), pri_key.strip())
                else:
                    self.assertEqual(el.toPlainText().strip(), pub_key.strip())

    def test_key_fail(self):
        """ checks to make sure the validation on the key creation is working correctly """

        passphrase_box = self.window.dlg.findChild(QTextEdit, "gen_passphrase_box")
        name_box = self.window.dlg.findChild(QTextEdit, "gen_name_box")
        email_box = self.window.dlg.findChild(QTextEdit, "gen_email_box")
        output_location_box = self.window.dlg.findChild(QTextEdit, "gen_output_location_box")

        # no name
        name_box.setText("")
        self.assertFalse(self.window.dlg.generate_key_validation(True))

        # short name
        name_box.setText("aa")
        self.assertFalse(self.window.dlg.generate_key_validation(True))

        # no email
        name_box.setText("testuser1")
        email_box.setText("")
        self.assertFalse(self.window.dlg.generate_key_validation(True))

        #invalid email
        email_box.setText("test.com")
        self.assertFalse(self.window.dlg.generate_key_validation(True))

        #short passwork
        email_box.setText("test@test.com")
        passphrase_box.setText("testp")
        self.assertFalse(self.window.dlg.generate_key_validation(True))


        #short password
        passphrase_box.setText("testp")
        self.assertFalse(self.window.dlg.generate_key_validation(True))

        #no upper
        passphrase_box.setText("testpassword")
        self.assertFalse(self.window.dlg.generate_key_validation(True))


        #no upper
        passphrase_box.setText("TESTPASSWORD")
        self.assertFalse(self.window.dlg.generate_key_validation(True))


        #no special
        passphrase_box.setText("TESTpassword")
        self.assertFalse(self.window.dlg.generate_key_validation(True))

        #no output location
        output_location_box.setText("")
        self.assertFalse(self.window.dlg.generate_key_validation(True))

        self.window.dlg.close()

    def test_copy(self):
        """ checks to make sure the button doesn't copy when its blank """

        self.error=False

        for textbox, button in self.window.copy_buttons:
            # click the moneykey patched button
            error = self.window.copy_text(textbox, button)
            # assert that the error dialog was opened and closed
            self.assertTrue(error)
            self.window.error_window.close()
    def test_run(self):
        """Test running the gui segment of the code"""

        #get new app etc
        window, app = run(True)
        #check enabled
        self.assertTrue(window.isEnabled())
        #check window
        self.assertTrue(window.isWindow())
        #check has PID
        self.assertTrue(app.applicationPid())

        #set these for the teardown
        window.close()
        window.dlg.close()
        app.quit()

    def test_setup_keys_incorrect(self):

        """checks to see if incorrect key location is handled correctly"""
        self.window.key_location = "/"
        run_ok = self.window.setup_keys(self.window.key_location)
        self.assertFalse(run_ok)
    def test_help_show(self):

        """checks to make sure the help window opened"""
        self.window.help_show()
        self.window.helpdlg
        self.assertTrue(self.window.helpdlg.isWindow())
        self.assertTrue(self.window.helpdlg.isEnabled())
        self.window.helpdlg.close()
if __name__ == '__main__':
    unittest.main()
