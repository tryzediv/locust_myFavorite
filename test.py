import random
from locust import HttpUser, task, between


class SimpleFavoriteUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def create_and_use_favorite(self):
        """Создаём, используем и удаляем карточку за один раз"""
        # 1. Создаём
        create_data = {
            "title": f"Test_{random.randint(1000, 9999)}",
            "description": f"Test_{random.randint(1000, 9999)}"
        }
        create_resp = self.client.post("/favorites", json=create_data)

        favorite_id = create_resp.json().get("id")

        # 2. Обновляем
        update_data = {
            "title": f"Updated_{random.randint(1000, 9999)}",
            "description": f"Updated_{random.randint(1000, 9999)}"
        }
        self.client.put(f"/favorites/{favorite_id}", json=update_data)

        # 3. Лайкаем
        self.client.post(f"/favorites/{favorite_id}/like")

        # 4. Дизлайкаем (с вероятностью 50%)
        if random.choice([True, False]):
            self.client.post(f"/favorites/{favorite_id}/dislike")

        # 5. Удаляем
        self.client.delete(f"/favorites/{favorite_id}")

    @task(5)
    def just_look(self):
        """Просто смотрим на карточки"""
        skip = random.randint(0, 10)
        limit = random.choice([10, 25, 50])
        sort = random.choice(['new', 'az', 'za', 'rating'])
        self.client.get(f"/favorites?skip={skip}&limit={limit}&sort={sort}")
