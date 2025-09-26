from app import create_app

app = create_app()

if __name__ == "__main__":
    # Enable Flask's built-in development server when executing `python run.py`.
    app.run(debug=True)
