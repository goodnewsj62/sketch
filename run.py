from main import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
    # app.run(debug=True,ssl_context="adhoc")