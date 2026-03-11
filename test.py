import random
from locust import HttpUser, task, between


class MyFavoriteUser(HttpUser):
    wait_time = between(1, 3)
    favorites_ids = []  # Кэш ID карточек

    def on_start(self):
        """Выполняется один раз при старте пользователя."""
        self.refresh_favorites_cache()

    def refresh_favorites_cache(self):
        """Обновляет список ID из /favorites."""
        try:
            response = self.client.get(
                "/favorites?skip=0&limit=50&sort=new",
                name="/favorites (cache)"
            )
            if response.status_code == 200:
                data = response.json()
                self.favorites_ids = [item["id"] for item in data if isinstance(item.get("id"), int)]
            else:
                self.favorites_ids = []
        except Exception:
            self.favorites_ids = []

    def _get_random_favorite_id(self, refresh_probability=0.2):
        """
        Вспомогательный метод для получения случайного ID.
        :param refresh_probability: вероятность принудительного обновления кэша (0.0–1.0)
        :return: int ID или None, если нет доступных карточек
        """
        # Обновляем кэш, если он пуст или с заданной вероятностью
        if not self.favorites_ids or random.random() < refresh_probability:
            self.refresh_favorites_cache()

        return random.choice(self.favorites_ids) if self.favorites_ids else None

    @task(3)
    def get_favorites(self):
        skip = random.randint(0, 10)
        limit = random.choice([10, 25, 50])
        sort = random.choice(['new', 'az', 'za', 'rating'])
        self.client.get(f"/favorites?skip={skip}&limit={limit}&sort={sort}")

    @task(1)
    def add_favorite(self):
        headers = {"Content-Type": "application/json"}
        favorite_data = {
            "title": f"TestFavoriteTitle_{random.randint(100, 999)}",
            "description": f"TestFavoriteDescription_{random.randint(100, 999)}"
        }
        response = self.client.post("/favorites", json=favorite_data, headers=headers)
        # Добавляем новый ID в кэш при успешном создании (200 или 201)
        if response.status_code in (200, 201):
            try:
                new_id = response.json().get("id")
                if isinstance(new_id, int):
                    self.favorites_ids.append(new_id)
            except Exception:
                pass

    @task(1)
    def update_favorite(self):
        favorite_id = self._get_random_favorite_id()
        if not favorite_id:
            return

        headers = {"Content-Type": "application/json"}
        favorite_data = {
            "title": f"UpdatedTitle_{random.randint(100, 999)}",
            "description": f"UpdatedDesc_{random.randint(100, 999)}"
        }
        self.client.put(f"/favorites/{favorite_id}", json=favorite_data, headers=headers)

    @task(1)
    def like_favorite(self):
        favorite_id = self._get_random_favorite_id()
        if not favorite_id:
            return

        self.client.post(f"/favorites/{favorite_id}/like", headers={"Content-Type": "application/json"})

    @task(1)
    def dislike_favorite(self):  # Исправлено имя метода (было дублирование like_favorite)
        favorite_id = self._get_random_favorite_id()
        if not favorite_id:
            return

        self.client.post(f"/favorites/{favorite_id}/dislike", headers={"Content-Type": "application/json"})

    @task(1)
    def delete_favorite(self):
        favorite_id = self._get_random_favorite_id(refresh_probability=0.5)  # Чаще обновляем кэш перед удалением
        if not favorite_id:
            return

        response = self.client.delete(
            f"/favorites/{favorite_id}",
            headers={"Content-Type": "application/json"}
        )
        # Удаляем ID из кэша при успешном удалении
        if response.status_code == 200 and favorite_id in self.favorites_ids:
            self.favorites_ids.remove(favorite_id)
