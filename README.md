# AconsoDL

## Getting Started

Download a copy of this project.
In the root folder (same as AconsoDL.py) you need a config.ini e.g:

```
[Script]
download_path = [YOUR_DL_PATH]
download_history_file = [YOUR_DL_HISTORY_FILE] #e.g dl_history.txt

[Email]
username = [YOUR_MAIL]
password = [YOUR_MAIL_PW]
imap_url = [IMAP_URL_OF_YOUR_MAIL_PROVIDER] #e.g imap.gmail.com or imap-mail.outlook.com etc.
sender = [SENDER_MAIL_ADDRESS_TO_CHECK] #noreply@youremployerportal.com

[Portal]
email_selector = [mail_box_element_selector] #e.g __xmlview0--_Login-Input-Email_-inner
password_selector = [mail_box_element_selector] #e.g __xmlview0--_Login-Input-Password_-inner
login_button_selector = [login_button_element_selector] #e.g __xmlview0--_Login-Button-Login_-inner
portal_username = [YOUR_MAIL]
portal_password = [YOUR_PORTAL_PW]

[employer]
login_url = [YOUR_ACONSO_PORTAL_URL]
document_url_template = [YOUR_ACONSO_PORTAL_WEBVEIWER_URL_WITH_FILE] #e.g https:/youremployerportal.com/ui5/apps/documentboxui5/resources/external/nabi/m/thirdparty/pdfjs/web/viewer.html?file=%%2Fapi%%2Fv1%%2Finternal%%2Fdocuments%%2F{document_index}%%2Fpdf

```

Install dependecies like shown below under "Prerequisites".
Change "config.ini" to your needs.
Enjoy!

### Prerequisites

Things you need to install to run this script
```
pip install selenium
pip install webdrivermanager
webdrivermanager firefox --linkpath /usr/local/bin
```

## Authors

* **fLEEEEsNN** - *Initial work* - [fLEEEEsNN](https://github.com/fLEEEEsNN)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
