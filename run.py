from blog.models import *
from blog import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        appe.run(debug=True, port=8080)