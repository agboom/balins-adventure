from base.perms import *
from .models import *
from base.models import Bestuur

def get_ht_bestuur(): return Bestuur.objects.get(status='ht')

PERMISSION_LOGICS = (
  (Courant, InGroupPermissionLogic(
    'courant.view_courant',
    get_ht_bestuur
  )),
)
