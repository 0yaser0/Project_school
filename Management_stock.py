from DB import app, mysql
from ROUTES import bp

app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True)