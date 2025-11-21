

import random
import string

ALPHABET = string.ascii_uppercase + string.digits



def generate_family_code(length=12, max_attempts=100):
    from .models import Family # Import here to avoid circular imports
    for _ in range(max_attempts):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if not Family.objects.filter(code=code).exists():
            return code  
    raise RuntimeError('Could not generate unique family code after 100 attempts')

