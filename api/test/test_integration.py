from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


class TestIntegrationProviderServiceArea(TestCase):
    def setUp(self):
        self.api_client = APIClient()
        self.user = {'username': 'test', 'password': '123'}
        self.api_client.post(reverse('user-list'), self.user)
        response = self.api_client.post(reverse('token'), self.user, format='json')
        self.api_client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['token'])

        self.polygon = [
            {"lat": -10.947000, "lng": -37.074000},
            {"lat": -10.947000, "lng": -37.060000},
            {"lat": -10.933000, "lng": -37.060000},
            {"lat": -10.933000, "lng": -37.074000},
            {"lat": -10.947000, "lng": -37.074000}
        ]
        self.provider_data = {
            "email": "test@email.com",
            "name": "Provider Test",
            "phone_number": "799999999",
            "language": "PT",
            "currency": "REAL"
        }

    def test_create_provider_and_service_area_then_query_avaiable(self):
        """
        Create a provider and a service area, then query if point is inside
        """
        response_service_area = self.api_client.post(reverse('service-area-list'), {
            "price": "100.0",
            "name": "Test Area",
            "coordinates": self.polygon,
            "provider": self.provider_data
        }, format='json')
        self.assertEqual(response_service_area.status_code, status.HTTP_201_CREATED)

        response = self.api_client.get(
            reverse('service-area-avaiable'),
            {'lat': -10.940000, 'lng': -37.067000},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Test Area")
    
    def test_update_provider_reflects_in_service_area(self):
        """
        Update provider and check if the change is reflected in service area details
        """
        response_service_area = self.api_client.post(reverse('service-area-list'), {
            "price": "100.0",
            "name": "Test Area",
            "coordinates": [
                {"lat": -10.947000, "lng": -37.074000},
                {"lat": -10.947000, "lng": -37.060000},
                {"lat": -10.933000, "lng": -37.060000},
                {"lat": -10.933000, "lng": -37.074000},
                {"lat": -10.947000, "lng": -37.074000}
            ],
            "provider": {
                "email": "test@email.com",
                "name": "Provider Old",
                "phone_number": "799999999",
                "language": "PT",
                "currency": "REAL"
            }
        }, format='json')
        provider_id = response_service_area.data['provider']['id']

        self.api_client.put(reverse('provider-detail', args=[provider_id]), {
            "email": "test@email.com",
            "name": "Provider Updated",
            "phone_number": "799999999",
            "language": "PT",
            "currency": "REAL"
        }, format='json')

        response_get = self.api_client.get(
            reverse('service-area-detail', args=[response_service_area.data['id']]),
            format='json'
        )
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        self.assertEqual(response_get.data['provider']['name'], "Provider Updated")