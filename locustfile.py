from locust import HttpUser, task, between


class QuickStartUser(HttpUser):
    wait_time = between(1, 5)
    host = 'http://localhost:5000'

    @task
    def index(self):
        self.client.get('/')

    @task
    def show_summary(self):
        self.client.post(
            '/showSummary',
            data={'email': 'test@email.co'}
        )

    @task
    def book(self):
        self.client.get('/book/Test competition 1/test 1')

    @task
    def purchase_places(self):
        self.client.post(
            '/purchasePlaces',
            data={
                'club_name': 'test 1',
                'competition_name': 'Test competition 1',
                'places': '10',
            },
        )
