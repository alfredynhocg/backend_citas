from app import create_app
from app.seeder import seed_all

app = create_app()

with app.app_context():
    seed_all()
