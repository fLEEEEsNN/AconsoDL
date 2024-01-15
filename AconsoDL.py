import configparser
import os
import contextlib
import time
import imaplib
import email
import re
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


script_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(script_dir, 'config.ini')

# Conf Logger
logging.basicConfig(filename=os.path.join(script_dir, 'AconsoDL.log'), level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
CONFIG_FILE = config_file_path

@contextlib.contextmanager
def suppress_output():
    new_stdout = open(os.devnull, 'w')
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = new_stdout, new_stdout

    try:
        yield
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr
        new_stdout.close()

def read_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    return config

def retrieve_script_settings(config):
    download_path = config.get("Script", "download_path")
    download_history_file = config.get("Script", "download_history_file")
    return download_path, download_history_file

def retrieve_employer_info(config):
    employer_login_url = config.get("employer", "login_url")
    employer_document_url_template = config.get("employer", "document_url_template")
    return employer_login_url, employer_document_url_template

def retrieve_email_credentials(config):
    username = config.get("Email", "username")
    password = config.get("Email", "password")
    imap_url = config.get("Email", "imap_url")
    sender = config.get("Email", "sender")
    subject = config.get("Email", "subject")
    return username, password, imap_url, sender, subject

def retrieve_portal_credentials(config):
    email_selector = config.get("Portal", "email_selector")
    password_selector = config.get("Portal", "password_selector")
    login_button_selector = config.get("Portal", "login_button_selector")
    portal_username = config.get("Portal", "portal_username")
    portal_password  = config.get("Portal", "portal_password")
    return email_selector, password_selector, login_button_selector, portal_username, portal_password

def is_file_already_downloaded(filename, document_index, download_history_file):
    if not os.path.exists(os.path.join(script_dir, download_history_file)):
        with open(os.path.join(script_dir, download_history_file), 'w') as file:
            pass
    with open(os.path.join(script_dir, download_history_file), "r") as file:
        lines = file.readlines()
        for line in lines:
            parts = line.strip().split()
            if len(parts) == 2 and parts[0] == filename and parts[1] == document_index:
                return True
    return False

def mark_file_as_downloaded(filename, document_index, download_history_file):
    if not os.path.exists(os.path.join(script_dir, download_history_file)):
        with open(os.path.join(script_dir, download_history_file), 'w') as file:
            file.write(f"{filename} {document_index}\n")
    else:
        with open(os.path.join(script_dir, download_history_file), "a") as file:
            file.write(f"{filename} {document_index}\n")

def main():
    config = read_config(CONFIG_FILE)
    email_username, email_password, email_imap_url, sender, subject = retrieve_email_credentials(config)
    portal_email_selector, portal_password_selector, portal_login_button_selector, portal_username, portal_password = retrieve_portal_credentials(config)
    employer_login_url, employer_document_url_template = retrieve_employer_info(config)
    download_path, download_history_file = retrieve_script_settings(config)

    # CONNECT
    mail = imaplib.IMAP4_SSL(email_imap_url)
    mail.login(email_username, email_password)
    mail.select("inbox")

    # SEARCH ACONSO MAIL
    status, messages = mail.search(None, '(FROM "{}")'.format(sender))

    # Prüfe, ob Nachrichten gefunden wurden
    if messages[0]:
        # Holen Sie sich die neueste Nachricht
        latest_email_id = messages[0].split()[-1]

        _, msg_data = mail.fetch(latest_email_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        # Prüfe den Betreff der neuesten E-Mail
        mail_subject = msg.get("Subject", "")

        if subject.lower() in mail_subject.lower():
            # ANALYSE BODY
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        body = part.get_payload(decode=True).decode()
                        # EXTRACT DOCUMENT INDEX
                        logging.info("Neuste Mail der HR Document Box eingelesen und verarbeitet")

                        # FIND TEXT
                        match = re.search(r'<b>(.*?)</b>', body)

                        if match:
                            document_name = match.group(1) + ".pdf"  # ADD EXTENSION .pdf
                            logging.info("Gefundener Dateiname: " + document_name)
                        else:
                            logging.info("Kein Dateiname im E-Mail-Body gefunden.")

                        match = re.search(r'/document/(\d+)/show', body)

                        if match:
                            document_index = match.group(1)
                            logging.info("Gefundener Dokumentenindex: " + document_index)
                        else:
                            logging.info("Kein Dokumentenindex im E-Mail-Body gefunden.")
                            break


        # DONT FORGET TO CLOSE CONNECTIONS FLEEEE....
        mail.close()
        mail.logout()


        # CHECK IF ITS A NEW FILE
        if not is_file_already_downloaded(document_name, document_index, download_history_file):
            logging.info("Neues Dokument! Fahre fort mit Downloadablauf...")
            mark_file_as_downloaded(document_name, document_index, download_history_file)
        else:
            logging.info("Datei wurde bereits heruntergeladen, überspringe den Download.")
            return

        firefox_options = Options()
        firefox_options.set_preference("browser.download.folderList", 2)
        firefox_options.set_preference("browser.download.dir", download_path)
        firefox_options.set_preference("browser.download.useDownloadDir", True)
        firefox_options.set_preference("pdfjs.disabled", True)
        firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")

        # WebDriver
        driver = webdriver.Firefox(options=firefox_options)
                  
        # NAVIGATE TO LOGIN PAGE
        driver.get(employer_login_url)

        time.sleep(10)  # SLEEP to ensure page is loaded correctly
        # GET USER AND PW FIELD
        # REPLACE 'email_selector', 'password_selector' and 'login_button_selector' for your needs in config
        email_field = driver.find_element(By.ID, portal_email_selector)
        password_field = driver.find_element(By.ID, portal_password_selector)
        login_button = driver.find_element(By.ID, portal_login_button_selector)

        # FILL IN USER DATA
        email_field.send_keys(portal_username)
        password_field.send_keys(portal_password)

        # CLICK LOGIN
        login_button.click()

        ## WAIT AGAIN
        time.sleep(10)

        # NAVIGATE TO DOCUMENT
        document_url =  employer_document_url_template.format(document_index=document_index)
        driver.get(document_url)

        time.sleep(10)

        logging.info("Im Portal eingeloggt und Datei geoeffnet")


        # DOWNLOAD BY CLICKING DL BUTTON
        try:
            download_button = driver.find_element(By.ID, 'download')
            download_button.click()
            logging.info("Download-Button wurde angeklickt.")
        except Exception as e:
            logging.info("Download-Button konnte nicht angeklickt werden:", e)

        time.sleep(10)
        driver.quit()

if __name__ == "__main__":
    main()
