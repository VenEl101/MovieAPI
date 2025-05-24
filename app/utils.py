import random
import hashlib


def gen_ran_num():
    return random.randint(100000, 999999)



def generate_device_id(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    ip = request.META.get('REMOTE_ADDR', '')
    raw = f"{user_agent}-{ip}"
    return hashlib.sha256(raw.encode()).hexdigest()