
from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
from secret import API_SECRET_KEY
from werkzeug.exceptions import Unauthorized



app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = API_SECRET_KEY

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)


@app.errorhandler(404)
def not_found(e):
  return render_template("404.html")


@app.route("/")
def homepage():
    """Redirect to register page."""

    return redirect("/login")


@app.route("/secret")
def secret():
    """Example hidden page for logged-in users only."""

    if "username" not in session:
        flash("You must be logged in to view!")
        return redirect("/login")

    else:
        return '<h1> You made it to the members area!  </h1>'
    
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user: produce form & handle form submission."""
    
    form = RegisterForm()
    
    if form.validate_on_submit():
    
        username = form.username.data
        pwd = form.password.data
        email = form.email.data
        first = form.first_name.data
        last = form.last_name.data

        user = User.register(username, pwd, email, first, last)
        db.session.commit()

        session["username"] = user.username

        return redirect('/secret')
    
    else:
        return render_template("users/register.html", form=form)
    
@app.route("/login", methods=["GET", "POST"])
def login():
    '''Login user: produce form & handle submission.'''
    
    if "username" in session:
        username = session["username"]
        return redirect(f'users/{username}')
    
    form = LoginForm()
    
    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data
        
                # authenticate will return a user or False
        user = User.authenticate(name, pwd)

        if user:
            session["username"] = user.username  # keep logged in
            return redirect(f"/users/{user.username}")

        else:
            form.username.errors = ["Bad name/password"]

    return render_template("users/login.html", form=form)
# end-login 

@app.route("/logout", methods=['POST'])
# should be a POST REQUEST
def logout_user():
    session.pop("username")
    flash("Goodbye!")
    return redirect('/')

################
# USER ROUTES
###############
@app.route("/users/<username>")
def show_user(username):
    '''Show user information and feedback. Only accessible to authorized users.'''
    if "username" not in session or session["username"] != username:
        flash("You must be logged in and authorized to view!")
        return redirect("/login")   
        # raise Unauthorized()
    
    else:
        user = User.query.get(username)
        return render_template("users/show.html", user=user)     
    
@app.route("/users/<username>/delete", methods=['POST'])
def delete_user(username):
    '''Delete user from database.'''
    
    if "username" not in session or session["username"] != username:
        flash("Not authroized!")
        return redirect("/")      
    
    else:
        db.session.delete(username)
        db.session.commit()
        
        flash(f"User: {username} deleted!")
        return redirect('/')
 

################
# Feedback Routes
################

@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):
    '''Show new feedback form and handle submission.'''
    
    if "username" not in session or username != session["username"]:
        flash("Not authroized!")
        return redirect("/") 
        
    form = FeedbackForm()
    
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        
        new_feedback= Feedback(title=title, content=content, username=username)
        db.session.add(new_feedback)
        db.session.commit()
        
        flash('Feedback added!')
        return redirect('/')
    
    return render_template("/feedback/new.html", form=form, username=username)
    
@app.route("/feedback/<feedback_id>/edit", methods=["GET", "POST"])
def edit_feedback(feedback_id):
    '''Show edit feedback form and handle submission'''
    feedback = Feedback.query.get_or_404(feedback_id)

    if "username" not in session or feedback.username != session["username"]:
        flash("Not authroized!")
        return redirect("/")      

    form = FeedbackForm(obj=feedback)
    
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        
        db.session.add(feedback)
        db.session.commit()
        
        flash('Feedback edited!', 'success')
        return redirect('/')

    return render_template("/feedback/edit.html", form=form, feedback=feedback)


@app.route("/feedback/<feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    '''Delete feedback'''
    feedback = Feedback.query.get_or_404(feedback_id)

    if "username" not in session or feedback.username != session["username"]:
        flash("Not authroized!")
        return redirect("/")      
        
    db.session.delete(feedback)
    db.session.commit()
    
    flash('Feedback Deleted!', 'success')
    return redirect('/')
