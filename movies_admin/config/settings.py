from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()

include(
    'components/auth.py',
    'components/common.py',
    'components/database.py',
    'components/internationalization.py',
    'components/templates.py',
    'components/web.py',
)
