import os
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route
from starlette_admin.contrib.mongoengine import Admin as StarletteAdmin, ModelView
from mongoengine import connect, disconnect
from dotenv import load_dotenv

from models import User, Admin, Product, Event


load_dotenv()
MONGO_URL = os.environ["DATABASE_ADMIN_URL"]
print(MONGO_URL)

app = Starlette(
    routes=[
        Route(
            "/",
            lambda r: HTMLResponse('<a href="/admin/">Click me to get to Admin!</a>'),
        )
    ],
    on_startup=[lambda: connect(host=MONGO_URL)],
    on_shutdown=[lambda: disconnect()],
)

# Create admin
admin = StarletteAdmin(title="Winebot Admin")

admin.add_view(ModelView(User, icon="fa fa-users"))
admin.add_view(ModelView(Admin, icon="fa fa-users"))
admin.add_view(ModelView(Product, icon="fa fa-list"))
admin.add_view(ModelView(Event, icon="fa fa-list"))

# Mount admin to app
admin.mount_to(app)
