from app import create_app

app = create_app()

if __name__ == "__main__":
    # Luister op poort 5001 i.p.v. standaard 5000
    app.run(debug=True, port=5002)

