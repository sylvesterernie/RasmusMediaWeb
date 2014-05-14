import os
import sys


etcdir = os.path.join(sys.prefix, 'etc', 'rasmusmediaweb')
default_sql_url = 'sqlite:///' + os.path.join(etcdir, 'data.db')
