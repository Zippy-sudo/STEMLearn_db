from config import app, db, api

@app.route('/')
def main():
    return '<h1>Welcome to STEMLearn</h1>'

if __name__ == '__main__':
    app.run(port=5555, debug=True)