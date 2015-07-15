from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from autofixture import AutoFixture
from rest_framework import status

from base.models import Profiel, Bestuur, BestuursLid
from .models import CourantEntry, Courant

class CourantTests(APITestCase):

  def fixture(self):
    liduser = User.objects.create_user(username='Lid', password='Lid')
    ouduser = User.objects.create_user(username='OudLid', password='OudLid')
    bestuuruser = User.objects.create_user(username='Bestuur', password='Bestuur')

    AutoFixture(Profiel, generate_fk=True, field_values={
      'voornaam': 'LID',
      'status': Profiel.STATUS.LID,
      'user': liduser,
      'uid': '0001'
    }).create(1)

    AutoFixture(Profiel, generate_fk=True, field_values={
      'voornaam': 'OUDLID',
      'status': Profiel.STATUS.OUDLID,
      'user': ouduser,
      'uid': '0002'
    }).create(1)

    AutoFixture(Profiel, generate_fk=True, field_values={
      'voornaam': 'BESTUURSLID',
      'status': Profiel.STATUS.LID,
      'user': bestuuruser,
      'uid': '0003'
    }).create(1)

    AutoFixture(Bestuur, generate_fk=True, field_values={
      'naam': 'Groenenboom',
      'status': 'ht'
    }).create(1)

    AutoFixture(BestuursLid, field_values={
      'user': Profiel.objects.get(uid='0003'),
      'opmerking': 'Praeses Groenenboom',
      'groep_id': Bestuur.objects.get(status='ht')
    }).create(1)

    # unpublished courant
    AutoFixture(Courant, generate_fk=False, field_values={
      'publish_date': datetime.now() - timedelta(weeks=1),
      'date_created': datetime.now() - timedelta(weeks=1),
      'date_modified': datetime.now() - timedelta(weeks=1),
      'user': bestuuruser.profiel
    }).create(1)

    # published courant
    AutoFixture(Courant, generate_fk=False, field_values={
      'publish_date': datetime.now() + timedelta(weeks=1),
      'date_created': datetime.now() + timedelta(weeks=1),
      'date_modified': datetime.now() + timedelta(weeks=1),
      'user': bestuuruser.profiel
    }).create(1)

    AutoFixture(CourantEntry, generate_fk=True, field_values={
      'publish_date': datetime.now() + timedelta(weeks=1),
      'date_created': datetime.now() + timedelta(weeks=1),
      'date_modified': datetime.now() + timedelta(weeks=1),
      'user': bestuuruser.profiel
    }).create(1)

  def test_public_gets_public(self):
    self.fixture()
    response = self.client.get(reverse('courant-list'))
    self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
