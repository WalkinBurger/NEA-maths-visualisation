from website import *

init_db()
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)