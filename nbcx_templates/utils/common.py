import os
from functools import lru_cache


@lru_cache(None)
def in_nbconvert():
    '''helper function to check if running in nbcx context'''
    return True if os.environ.get('NBCX_NBCONVERT', '') else False


@lru_cache(None)
def nbconvert_context():
    '''get context in which nbcx is running, either 'pdf' or 'html' '''
    if in_nbconvert():
        if os.environ.get('NBCX_CONTEXT', ''):
            return 'html'
        return 'pdf'
    return 'html'
