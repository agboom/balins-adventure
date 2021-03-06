from base.models import *

class ProfielMiddleware(object):

  def process_request(self, request):
    if request.user.is_authenticated():
      request.profiel = request.user.profiel
    else:
      request.profiel = Profiel.objects.get(uid="x999")

  def process_response(self, request, response):
    return response
