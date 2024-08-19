# created by wl123
#
# run.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Run the flask app on host localhost and port 5000
    app.run(debug=True, host='localhost', port=5000)
