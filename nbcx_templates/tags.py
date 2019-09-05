from enum import Enum


class Tags(Enum):
    DISCLOSURES = 'nbcx_disclosures'
    NBCONVERT_IGNORE = 'nbcx_ignore'
    PARAMETERS = 'parameters'  # for Papermill
    TITLE = 'nbcx_title'
