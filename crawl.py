import conf
import code
import codechef_solution
import requests
from models import URL

with requests.Session() as s:
    code.codechef_login(s, URL.BASE)
    # Uncomment this line, if you want to fetch the ratingue
    # code.get_rating(s, conf.handle)
    codechef_solution.codechef_download(s, conf.handle)
    code.codechef_logout(s, URL.BASE + URL.LOGOUT)
