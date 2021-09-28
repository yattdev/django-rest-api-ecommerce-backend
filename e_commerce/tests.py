from django.test import TestCase
from django.urls import reverse

# Create your tests here.


class HomePageTestCase(TestCase):
    def test_home_statucode_200(self):
        response = self.client.get(reverse('home'))

        return self.assertEqual(response.status_code, 200)
