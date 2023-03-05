"""Run deployment tasks."""
from app import create_app, db
# from flask_migrate import upgrade, migrate, init, stamp

app = create_app('config.DevelopmentConfig')
app.app_context().push()
db.create_all()

# def migrate_app():
#     """Migrate database to latest revision"""
#     init()
#     stamp()
#     migrate()
#     upgrade()

def recreate_db():
    """
    Recreates a local database. You should not use this on production.
    """
    db.drop_all()
    db.create_all()
    db.session.commit()

if __name__ == "__main__":
    # recreate_db()
    app.run()
