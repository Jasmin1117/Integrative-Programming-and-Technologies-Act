from django.test import TestCase

# Create your tests here.
def test_create_post(self):
    self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
    data = {
        "post_type": "status",
        "title": "Sample Title",
        "content": "Sample Content",
        "metadata": {},
        "privacy": "public"
    }
    response = self.client.post('/posts/manage/', data, format='json')
    self.assertEqual(response.status_code, 201)
