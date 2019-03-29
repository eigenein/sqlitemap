import re
from typing import Pattern

table_name_re: Pattern = re.compile(r'^(?!sqlite_)([^"]|"")+')
