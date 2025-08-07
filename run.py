from app import create_app

app = create_app()

if __name__ == '__main__':
    print("Calling app.run", flush=True)
    app.run(debug=True)