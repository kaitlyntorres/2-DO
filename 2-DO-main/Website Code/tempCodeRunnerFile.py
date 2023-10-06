from website import create_app

app = create_app()

#Runs webserver if ONLY the main is run and not anywhere else website is imported
if __name__ == '__main__':
    app.run(debug=True) #This makes us not have to manually re-run flask webserver, turn off for production