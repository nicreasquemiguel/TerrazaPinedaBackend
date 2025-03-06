from datetime import datetime, timedelta

from django.test import TestCase
from django.contrib.auth import get_user_model

from pytz import UTC
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

# from blog.models import Post
from .models import Event, Package, Extra

class PostApiTestCase(TestCase):
  def setUp(self):
    self.client = get_user_model().objects.create_user(
        email="client@example.com", password="password"
    )


    self.admin = get_user_model().objects.create_user(
        email="admin@example.com", password="password"
    )


    events = [
            Event.objects.create(
                client = self.client,
                admin = self.admin,
                date = datetime.now() + timedelta(1), #tomorrow
                description = "Birthday party for my little girl with a princess show for the kids"
            ),
            Event.objects.create(
                client = self.client,
                admin = self.admin,
                date = datetime.now() + timedelta(7), #in a week
                description = "Adult pool party with alcoholic brevages, music band playing at night time"
            )
    ]
    
    

    

    # # let us look up the post info by ID
    self.event_lookup = {e.id: e for e in events}

    # override test client
    self.client = APIClient()
    token = Token.objects.create(user=self.client)
    self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

  def test_event_list(self):
    resp = self.client.get("/api/eventos/ocupados/")
    data = resp.json()["results"]
    self.assertEqual(len(data), 2)

    for event_dict in data:
        event_obj = self.event_lookup[event_dict["id"]]
        self.assertEqual(event_obj.description, event_dict["description"])
        self.assertEqual(event_obj.date, event_dict["date"])
        self.assertEqual(event_obj.client, event_dict["client"])
        self.assertEqual(event_obj.admin, event_dict["admin"])

  
