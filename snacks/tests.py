from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Snack

class SnackTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="vaultdweller", email="dweller@email.com", password="pass"
        )
        self.snack = Snack.objects.create(
            title="Nuka-Cola", description="A refreshing drink from the wasteland.", purchaser=self.user,
        )

    def test_string_representation(self):
        self.assertEqual(str(self.snack), "Nuka-Cola")

    def test_snack_content(self):
        self.assertEqual(f"{self.snack.title}", "Nuka-Cola")
        self.assertEqual(f"{self.snack.purchaser}", "vaultdweller")
        self.assertEqual(f"{self.snack.description}", "A refreshing drink from the wasteland.")

    def test_snack_list_view(self):
        response = self.client.get(reverse("snack_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nuka-Cola")
        self.assertTemplateUsed(response, "snack_list.html")

    def test_snack_detail_view(self):
        response = self.client.get(reverse("snack_detail", args=[str(self.snack.id)]))
        no_response = self.client.get(reverse("snack_detail", args=["100000"]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(no_response.status_code, 404)
        self.assertContains(response, "Purchaser: vaultdweller")
        self.assertTemplateUsed(response, "snack_detail.html")

    def test_snack_create_view(self):
        response = self.client.post(
            reverse("snack_create"),
            {
                "title": "Sugar Bombs",
                "description": "A delicious cereal from before the war.",
                "purchaser": self.user.id,
            }, follow=True
        )
        new_snack = Snack.objects.get(title="Sugar Bombs")
        self.assertRedirects(response, reverse("snack_detail", args=[str(new_snack.id)]))
        self.assertContains(response, new_snack.title)
        self.assertContains(response, f"Purchaser: {self.user.username}")
        self.assertContains(response, new_snack.description)

    def test_snack_update_view_redirect(self):
        response = self.client.post(
            reverse("snack_update", args=[str(self.snack.id)]),
            {"title": "Slocum's BuzzBites", "description": "A sweet and caffeinated treat.", "purchaser": self.user.id}
        )
        self.assertRedirects(response, reverse("snack_detail", args=[str(self.snack.id)]))

    def test_snack_delete_view(self):
        response = self.client.get(reverse("snack_delete", args=[str(self.snack.id)]))
        self.assertEqual(response.status_code, 200)
