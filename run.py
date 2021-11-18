from main import create_app,db
from main.models import User,Post,Notification,Category

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {"db":db,"User":User,"Post":Post,"Notification":Notification,"Category":Category}
if __name__ == "__main__":
    if app.config.get('DEBUG'):
        app.run(debug=True)
        # app.run(debug=True, ssl_context="adhoc")
    else:
        app.run(debug=False)
