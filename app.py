import datetime

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__)


# CODE BELOW WAS PROVIDED BY THE CS50 PROBLEM SET 9 - FINANCE - app.py

# SESSION CONFIGURATION MAKES IT SO THE SESSION USES INFORMATION FROM MY FILESYSTEM, RATHER THAN COOKIES

# db = SQL IS USED SO THE CS50 LIBRARY USES MY SQLite DATABASE NAMED "goaltracker.db"

# after_request IS A FUNCTION THAT ENSURES USER'S RESPONSES AREN'T CACHED BY THE BROWSER TO PREVENT DATA ERRORS

# CITED CODE BEGINS HERE

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///goaltracker.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# CITED CODE ENDS HERE


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register User"""
    if request.method == "POST":

        # Link for apologies
        previouspage = "/register"

        # Check user's inputs
        if not request.form.get("username"):
            apologytext = "Please provide a username."
            code = 400
            return render_template("apology.html", apologytext=apologytext, code=code, previouspage=previouspage)

        elif not request.form.get("password"):
            apologytext = "Please provide a password."
            code = 400
            return render_template("apology.html", apologytext=apologytext, code=code, previouspage=previouspage)

        elif not request.form.get("confirmationpassword"):
            apologytext = "Please provide your exact password twice for confirmation."
            code = 400
            return render_template("apology.html", apologytext=apologytext, code=code, previouspage=previouspage)

        elif request.form.get("password") != request.form.get("confirmationpassword"):
            apologytext = "Your password and confirmation password must match exactly."
            code = 400
            return render_template("apology.html", apologytext=apologytext, code=code, previouspage=previouspage)

        hash_password = generate_password_hash(request.form.get("password"))

        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
                       request.form.get("username"), hash_password)
        except ValueError:
            apologytext = "This username is already taken."
            code = 400
            return render_template("apology.html", apologytext=apologytext, code=code, previouspage=previouspage)

        return render_template("login.html")

    else:
        return render_template("register.html")


# CODE BELOW WAS PROVIDED BY THE CS50 PROBLEM SET 9 - FINANCE - app.py

# PROVIDES A LOGIN ROUTE AND FUNCTION TO LOG A USER IN AND LOG THEM OUT

# I ADDED IN A VARIATION TO THE APOLOGY SECTIONS AS MY APOLOGY HTML IS DIFFERENT

# CITED CODE BEGINS HERE

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log User In"""

    # Forget any user_id
    session.clear()

    previouspage = "/login"

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            apologytext = "Please provide a username."
            code = 400
            return render_template("apology.html", apologytext=apologytext, code=code, previouspage=previouspage)

        # Ensure password was submitted
        elif not request.form.get("password"):
            apologytext = "Please provide a password."
            code = 400
            return render_template("apology.html", apologytext=apologytext, code=code, previouspage=previouspage)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            apologytext = "Incorrect username and/or password."
            code = 400
            return render_template("apology.html", apologytext=apologytext, code=code, previouspage=previouspage)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log User Out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")

# CITED CODE ENDS HERE


@app.route("/")
@login_required
def schedule():
    """Show User's Schedule"""

    # If the user is new and doesn't have goals registered, render new_schedule page
    currentuserid = session["user_id"]
    currentuserinfo = db.execute("SELECT new_user FROM users WHERE id = ?", currentuserid)

    if currentuserinfo[0]["new_user"] == "yes":
        return render_template("newschedule.html")

    else:
        # If the user does have goals already, check if they have goals today
        date = datetime.datetime.now()
        weekday = datetime.datetime.now().strftime("%A")
        current_date = date.strftime("%Y/%m/%d")
        daybegun = True
        anyscheduledgoals = True

        # Check if the value of the most recent date_completed in the goal_completed table matches the current date. The value will be used in later condition
        most_recent_completed_goal = db.execute(
            "SELECT date_completed FROM goals_completed WHERE user_id = ? AND date_completed = ? LIMIT 1", currentuserid, current_date)

        # Do a count of goals to check if the user has any goals
        usersgoaltotal = db.execute(
            "SELECT COUNT(goal_title) FROM goals WHERE user_id = ?", currentuserid)

        # Or if any goals are registered to repeat on the current day of the week
        if weekday in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            goalstoday = db.execute(
                f"SELECT COUNT(goal_title) FROM goals WHERE user_id = ? AND {weekday} = TRUE", currentuserid)

            # If the user either has no goals today or none at all,
            if usersgoaltotal[0]['COUNT(goal_title)'] == 0 or goalstoday[0]['COUNT(goal_title)'] == 0:
                anyscheduledgoals = False
                return render_template("schedule.html", date=date, anyscheduledgoals=anyscheduledgoals)

            # If most_recent_completed_goal is None, it means they haven't clicked to start their day
            elif not most_recent_completed_goal:
                anyscheduledgoals = True
                daybegun = False
                return render_template("schedule.html", date=date, anyscheduledgoals=anyscheduledgoals, daygun=daybegun)

            # If not, compile a list of goals that are scheduled today using all relevant info from table
            else:
                scheduledgoalscheck = db.execute(
                    f"SELECT * FROM goals WHERE user_id = ? AND {weekday} = TRUE", currentuserid)

                # Loop through each goal scheduled today and check the last updated date and the progress value
                for goal in scheduledgoalscheck:

                    # Assign variables to store the current goal title, the progress value and the last updated date
                    goal_title = goal['goal_title']
                    progress_value = goal['progress_number']
                    last_update_date = goal['date_progress_last_updated']

                    # if the goals last updated date does not match the current date, update the progress value in the table to be 0 and update date last updated value to the current date
                    if last_update_date != current_date:
                        progress_value = 0

                        # run an update for the goals table to reset the progress value and update the last updated date
                        db.execute("UPDATE goals SET progress_number = ?, date_progress_last_updated = ? WHERE user_id = ? AND goal_title = ?",
                                   progress_value, current_date, currentuserid, goal_title)

                # Once the loop has completed checking all progress values and dates, reselect all from the table then send to the html
                scheduledgoals = db.execute(
                    f"SELECT * FROM goals WHERE user_id = ? AND {weekday} = TRUE", currentuserid)

                return render_template("schedule.html", date=date, anyscheduledgoals=anyscheduledgoals, daybegun=daybegun, scheduledgoals=scheduledgoals)

        else:
            # Error below only applies if for some reason datetime doesn't return the correct info
            previouspage = "/"
            apologytext = "Internal Server Error."
            code = 500
            print("datetime.datetime.now().strftime('%A') returned unexpected data")
            return render_template("apology.html", apologytext=apologytext, code=code, previouspage=previouspage)


@app.route("/goals")
@login_required
def goals():
    """Show User's Goals"""
    currentuserid = session["user_id"]
    usergoals = True

    # Do a sum of goals to check if the user has any goals
    usersgoaltotal = db.execute(
        "SELECT COUNT(goal_title) FROM goals WHERE user_id = ?", currentuserid)

    # Return specific section in goals html if the user has no current goals
    if usersgoaltotal[0]['COUNT(goal_title)'] == 0:
        usergoals = False
        return render_template("goals.html", usergoals=usergoals)

    elif usersgoaltotal[0]['COUNT(goal_title)'] == None:
        usergoals = False
        return render_template("goals.html", usergoals=usergoals)

    # If user has goals, show all of them in the table
    else:
        userscurrentgoals = []

        usersgoaldata = db.execute(
            "SELECT goal_title, length_of_goal, unit_type_of_length, monday, tuesday, wednesday, thursday, friday, saturday, sunday FROM goals WHERE user_id = ?", currentuserid)

        for goaldata in usersgoaldata:
            goal_title = goaldata["goal_title"]
            length_of_goal = goaldata["length_of_goal"]
            unit_type_of_length = goaldata["unit_type_of_length"]
            monday = goaldata["monday"]
            tuesday = goaldata["tuesday"]
            wednesday = goaldata["wednesday"]
            thursday = goaldata["thursday"]
            friday = goaldata["friday"]
            saturday = goaldata["saturday"]
            sunday = goaldata["sunday"]

            goaldatadict = {
                "goal_title": goal_title,
                "length_of_goal": length_of_goal,
                "unit_type_of_length": unit_type_of_length,
                "monday": monday,
                "tuesday": tuesday,
                "wednesday": wednesday,
                "thursday": thursday,
                "friday": friday,
                "saturday": saturday,
                "sunday": sunday,
            }

            userscurrentgoals.append(goaldatadict)

        return render_template("goals.html", usersgoals=usergoals, userscurrentgoals=userscurrentgoals)


@app.route("/add_goal", methods=["GET", "POST"])
@login_required
def add_goals():
    """Add a Goal"""
    # When the habit has been added, change the users new_user status needs to change from yes to no
    currentuserid = session["user_id"]
    missingfield = False
    current_time = datetime.datetime.now()
    currentdatestring = current_time.strftime("%Y/%m/%d")

    # Store all info from the form into variables
    if request.method == "POST":
        goal_name = request.form.get("title")
        goal_specific = request.form.get("specific")
        goal_measurable = request.form.get("measurable")
        goal_achievable = request.form.get("achievable")
        goal_realistic = request.form.get("realistic")
        goal_timely = request.form.get("timely")
        goal_length = request.form.get("length")
        goal_length_unit = request.form.get("length_unit")
        date_progress_last_updated = currentdatestring
        goal_monday = request.form.get("monday")
        goal_tuesday = request.form.get("tuesday")
        goal_wednesday = request.form.get("wednesday")
        goal_thursday = request.form.get("thursday")
        goal_friday = request.form.get("friday")
        goal_saturday = request.form.get("saturday")
        goal_sunday = request.form.get("sunday")

        # Check that all the input fields have been filled out. If they haven't, return template with error message.
        if not goal_name or not goal_specific or not goal_measurable or not goal_achievable or not goal_realistic or not goal_timely or not goal_length or not goal_length_unit:
            missingfield = True
            return render_template("add_goal.html", missingfield=missingfield)

        # Convert values of days from strings into boolean values depending on their value
        if goal_monday == 'True':
            goal_monday = True
        else:
            goal_monday = False

        if goal_tuesday == 'True':
            goal_tuesday = True
        else:
            goal_tuesday = False

        if goal_wednesday == 'True':
            goal_wednesday = True
        else:
            goal_wednesday = False

        if goal_thursday == 'True':
            goal_thursday = True
        else:
            goal_thursday = False

        if goal_friday == 'True':
            goal_friday = True
        else:
            goal_friday = False

        if goal_saturday == 'True':
            goal_saturday = True
        else:
            goal_saturday = False

        if goal_sunday == 'True':
            goal_sunday = True
        else:
            goal_sunday = False

        day = current_time.day
        month = current_time.month
        year = current_time.year

        # Store all the info in the database
        db.execute("INSERT INTO goals (user_id, goal_title, length_of_goal, unit_type_of_length, date_progress_last_updated, s_goal, m_goal, a_goal, r_goal, t_goal, monday, tuesday, wednesday, thursday, friday, saturday, sunday, day, month, year) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   currentuserid, goal_name, goal_length, goal_length_unit, date_progress_last_updated, goal_specific, goal_measurable, goal_achievable, goal_realistic, goal_timely, goal_monday, goal_tuesday, goal_wednesday, goal_thursday, goal_friday, goal_saturday, goal_sunday, day, month, year)

        # Change users new user info in database
        newusercheck = db.execute("SELECT new_user FROM users WHERE id = ?", currentuserid)

        # If the user has 'yes' in their database as a new user, change to 'no'
        if newusercheck[0]["new_user"] == 'yes':
            db.execute("UPDATE users SET new_user = 'no' WHERE id = ?", currentuserid)

        return render_template("goalconfirmed.html")

    else:
        return render_template("add_goal.html")


@app.route("/delete_goal")
@login_required
def delete_goal():
    """Message to Delete Goals"""
    currentuserid = session["user_id"]

    currentgoals = db.execute("SELECT goal_title FROM goals WHERE user_id = ?", currentuserid)
    goalfromform = request.args.get("goal_title")
    for goal in currentgoals:
        if goal["goal_title"] == goalfromform:
            goaltodelete = goalfromform
            return render_template("delete_goal.html", goaltodelete=goaltodelete)


@app.route("/deletionconfirmed", methods=["GET", "POST"])
@login_required
def deletionconfirmed():
    """Confirmation to say Goal is Deleted"""
    currentuserid = session["user_id"]

    if request.method == "POST":
        currentgoals = db.execute("SELECT goal_title FROM goals WHERE user_id = ?", currentuserid)
        formgoal = request.form.get("goal_title")
        for goal in currentgoals:
            if formgoal == goal["goal_title"]:
                goaltodelete = formgoal
                db.execute("DELETE FROM goals WHERE user_id = ? AND goal_title = ?",
                           currentuserid, goaltodelete)

                db.execute("DELETE FROM goals_completed WHERE user_id = ? AND goal_title = ?",
                           currentuserid, goaltodelete)

        return render_template("deletionconfirmed.html")


@app.route("/goalinfo", methods=["GET", "POST"])
@login_required
def goal_info():
    """Show Info About Goal"""
    # Give the user the ability to edit the existing information about their goal and update the database
    currentuserid = session["user_id"]
    missingfield = False
    currentdate = datetime.datetime.now()
    currentdatestring = currentdate.strftime("%Y/%m/%d")

    # Store all info from the form into variables
    if request.method == "POST":
        goal_name = request.form.get("title")
        goal_specific = request.form.get("specific")
        goal_measurable = request.form.get("measurable")
        goal_achievable = request.form.get("achievable")
        goal_realistic = request.form.get("realistic")
        goal_timely = request.form.get("timely")
        goal_length = request.form.get("length")
        goal_length_unit = request.form.get("length_unit")
        progress_number = request.form.get("progress_number")
        progress_state = request.form.get("progress_state")
        date_progress_last_updated = currentdatestring
        goal_monday = request.form.get("monday")
        goal_tuesday = request.form.get("tuesday")
        goal_wednesday = request.form.get("wednesday")
        goal_thursday = request.form.get("thursday")
        goal_friday = request.form.get("friday")
        goal_saturday = request.form.get("saturday")
        goal_sunday = request.form.get("sunday")

        # Check that all the input fields have been filled out. If they haven't, return template with error message.
        if not goal_specific or not goal_measurable or not goal_achievable or not goal_realistic or not goal_timely or not goal_length or not goal_length_unit:
            missingfield = True
            return render_template("goalinfo.html", missingfield=missingfield, goal_name=goal_name, goal_specific=goal_specific, goal_measurable=goal_measurable, goal_achievable=goal_achievable, goal_realistic=goal_realistic, goal_timely=goal_timely, goal_length=goal_length, goal_length_unit=goal_length_unit, goal_monday=goal_monday, goal_tuesday=goal_tuesday, goal_wednesday=goal_wednesday, goal_thursday=goal_thursday, goal_friday=goal_friday, goal_saturday=goal_saturday, goal_sunday=goal_sunday)

        # Convert values of days into boolean values depending on their value
        if goal_monday == 'True':
            goal_monday = True
        else:
            goal_monday = False

        if goal_tuesday == 'True':
            goal_tuesday = True
        else:
            goal_tuesday = False

        if goal_wednesday == 'True':
            goal_wednesday = True
        else:
            goal_wednesday = False

        if goal_thursday == 'True':
            goal_thursday = True
        else:
            goal_thursday = False

        if goal_friday == 'True':
            goal_friday = True
        else:
            goal_friday = False

        if goal_saturday == 'True':
            goal_saturday = True
        else:
            goal_saturday = False

        if goal_sunday == 'True':
            goal_sunday = True
        else:
            goal_sunday = False

        # Update the database with new info

        db.execute("UPDATE goals SET length_of_goal = ?, unit_type_of_length = ?, progress_number = ?, progress_state = ?, date_progress_last_updated = ?,  s_goal = ?, m_goal = ?, a_goal = ?, r_goal = ?, t_goal = ?, monday = ?, tuesday = ?, wednesday = ?, thursday = ?, friday = ?, saturday = ?, sunday = ?, day = ?, month = ?, year = ? WHERE user_id = ? AND goal_title = ?",
                   goal_length, goal_length_unit, progress_number, progress_state, date_progress_last_updated, goal_specific, goal_measurable, goal_achievable, goal_realistic, goal_timely, goal_monday, goal_tuesday, goal_wednesday, goal_thursday, goal_friday, goal_saturday, goal_sunday, currentdate.day, currentdate.month, currentdate.year, currentuserid, goal_name)

        # Check if the goal was added to the goals_completed table on the current day and remove it
        db.execute("DELETE FROM goals_completed WHERE user_id = ? AND goal_title = ? AND date_completed = ?",
                   currentuserid, goal_name, currentdatestring)

        return render_template("goalconfirmed.html")

    else:
        # When taken to the page, display all the current information the user has submitted
        goalfromform = request.args.get("goal_title")

        # Select all necessary fields from the database and store them in variables
        goaltoedit = db.execute(
            "SELECT * FROM goals WHERE user_id = ? AND goal_title = ?", currentuserid, goalfromform)

        goal_name = goaltoedit[0]["goal_title"]
        goal_specific = goaltoedit[0]["s_goal"]
        goal_measurable = goaltoedit[0]["m_goal"]
        goal_achievable = goaltoedit[0]["a_goal"]
        goal_realistic = goaltoedit[0]["r_goal"]
        goal_timely = goaltoedit[0]["t_goal"]
        goal_length = goaltoedit[0]["length_of_goal"]
        goal_length_unit = goaltoedit[0]["unit_type_of_length"]
        progress_number = goaltoedit[0]["progress_number"]
        progress_state = goaltoedit[0]["progress_state"]
        goal_monday = goaltoedit[0]["monday"]
        goal_tuesday = goaltoedit[0]["tuesday"]
        goal_wednesday = goaltoedit[0]["wednesday"]
        goal_thursday = goaltoedit[0]["thursday"]
        goal_friday = goaltoedit[0]["friday"]
        goal_saturday = goaltoedit[0]["saturday"]
        goal_sunday = goaltoedit[0]["sunday"]

        # Render the template with the variables and display them with Jinja
        return render_template("goalinfo.html", goal_name=goal_name, goal_specific=goal_specific, goal_measurable=goal_measurable, goal_achievable=goal_achievable, goal_realistic=goal_realistic, goal_timely=goal_timely, goal_length=goal_length, goal_length_unit=goal_length_unit, progress_number=progress_number, progress_state=progress_state, goal_monday=goal_monday, goal_tuesday=goal_tuesday, goal_wednesday=goal_wednesday, goal_thursday=goal_thursday, goal_friday=goal_friday, goal_saturday=goal_saturday, goal_sunday=goal_sunday)


@app.route("/calendar")
@login_required
def calendar():
    """Show History of Completed Goals"""
    currentuserid = session["user_id"]
    existing_goals = True
    currentdate = datetime.datetime.now()

    # Do a sum of goals to check if the user has any goal registered
    goalcheck = db.execute(
        "SELECT COUNT(goal_title) FROM goals WHERE user_id = ?", currentuserid)

    # If the goal count is zero, return the template with a prompt to view schedule
    if goalcheck[0]['COUNT(goal_title)'] == 0:
        existing_goals = False
        return render_template("calendar.html", currentdate=currentdate, existing_goals=existing_goals)

    else:
        # If the user has goals that have been completed, create a calendar and list of the completed goals and pass the info to the template
        # Create the calendar grid

        # Store number of days depending on the month (add 1 extra for stopping point)
        month = currentdate.month
        if month in [1, 3, 5, 7, 8, 10, 12]:
            daycounter = range(1, 32)

        elif month in [4, 6, 9, 11]:
            daycounter = range(1, 31)

        elif month == 2:
            daycounter = range(1, 30)

        # Create the list. Need to store all the day numbers and their status
        completed_days_in_month = []

        # Create the day, month and year string to check the days. Use the day value in the for loop below as the value for which day you're on
        year = str(currentdate.strftime("%Y"))
        month = str(currentdate.strftime("%m"))

        # Iterate through every day in the month and store true or false on each day
        for day in daycounter:

            # Create a YYYY/MM/DD string of the date to use as the check value in my table
            daytocheck = str(day)
            if int(daytocheck) < 10:
                daytocheck = f"0{day}"

            completiondate = f"{year}/{month}/{daytocheck}"

            daycompletioncheck = db.execute(
                "SELECT completion_status FROM goals_completed WHERE user_id = ? AND date_completed = ?", currentuserid, completiondate)

            # Go through the list from query above and check if any are false.
            daycompleted = True

            # If there was no data from the query, the for loop below is skipped meaning no completion
            if not daycompletioncheck:
                daycompleted = False

            else:
                for status in daycompletioncheck:
                    if status["completion_status"] == False:
                        daycompleted = False
                        continue

            # Add the current iteration of the loop to my list storing the day number and True or False depending on if all goals on the day were completed
            day = {
                "daynumber": int(day),
                "completion_state": daycompleted,
            }

            completed_days_in_month.append(day)

        # Calendar Done. Now Create a history list of the users completed goals
        completedgoalslist = db.execute(
            "SELECT * FROM goals_completed WHERE user_id = ? AND completion_status = TRUE ORDER BY date_completed DESC", currentuserid)

        completedgoalscount = db.execute(
            "SELECT COUNT(goal_title) FROM goals_completed WHERE user_id = ? AND completion_status = TRUE ORDER BY date_completed DESC", currentuserid)

        completedtotal = completedgoalscount[0]['COUNT(goal_title)']

        # Pass the calendar list and history list info onto the template then iterate through list
        return render_template("calendar.html", currentdate=currentdate, existing_goals=existing_goals, completed_days_in_month=completed_days_in_month, completedgoalslist=completedgoalslist, completedtotal=completedtotal)


@app.route("/begin_day", methods=["POST"])
@login_required
def begin_day():
    """Add Goals Scheduled on the Current Day to the Goal Completion Table"""
    currentuserid = session["user_id"]
    date = datetime.datetime.now()
    weekday = datetime.datetime.now().strftime("%A")
    current_date = date.strftime("%Y/%m/%d")

    # Select all the goals that are scheduled on the current day by checking which days are marked true for the corresponding weekday
    goalstoday = db.execute(
        f"SELECT goal_title FROM goals WHERE user_id = ? AND {weekday} = TRUE", currentuserid)

    # Go through the above list and, through each iteration, insert into the goals_completed table the user_id, the goal_title, and the current date
    for goal in goalstoday:
        goal_title = goal['goal_title']
        db.execute("INSERT INTO goals_completed (user_id, goal_title, date_completed) VALUES (?, ?, ?)",
                   currentuserid, goal_title, current_date)

        # Reset progress_number and progress_state in goals
        db.execute("UPDATE goals SET progress_number = 0, progress_state = 1, date_progress_last_updated = ? WHERE user_id = ? AND goal_title = ?",
                   current_date, currentuserid, goal_title)

    # Once all done, redirect back to the schedule page with the goals all rendered
    return redirect("/")


@app.route("/goal_progress", methods=["POST"])
@login_required
def goal_progress():
    """Update Database when User Clicks to Increase their Progress"""
    currentuserid = session["user_id"]
    currentdate = datetime.datetime.now()
    date_for_update = currentdate.strftime("%Y/%m/%d")

    # Retrieve the corresponding goal_title from the completion button that was pressed
    update_data = request.get_json()
    goal_title = update_data['goalname']

    # When the user has clicked add 1, update the progress value of the goal and the last updated date in the table

    # Get the current value
    progress_value_data = db.execute(
        "SELECT progress_number FROM goals WHERE user_id = ? AND goal_title = ?", currentuserid, goal_title)

    progress_value = progress_value_data[0]['progress_number']

    # Increase the value by 1
    progress_value += 1

    # Update data with new progress value and the updated date
    db.execute("UPDATE goals SET progress_number = ?, date_progress_last_updated = ? WHERE user_id = ? AND goal_title = ?",
               progress_value, date_for_update, currentuserid, goal_title)

    # Check also if the goal hasn't already been added to the goals_completed table
    goal_check_list = db.execute(
        "SELECT goal_title FROM goals_completed WHERE goal_title = ? AND user_id = ? AND date_completed = ?", goal_title, currentuserid, date_for_update)

    # If it hasn't, add it with the current date, completion status as false, the user_id and the goal_title. If it has, do nothing
    if not goal_check_list:
        db.execute("INSERT INTO goals_completed (user_id, goal_title, date_completed) VALUES (?, ?, ?)",
                   currentuserid, goal_title, date_for_update)

    # * Following on from the schedule.html JavaScript Section. CHatGPT explained how using fetch works and that, when making a fetch request, the python code needs to return success to signify the request was successful.
    return {"success": True}


@app.route("/progress_status", methods=["POST"])
@login_required
def progress_status():
    """Update the Progress State Type of the Goal"""
    currentuserid = session["user_id"]

    # Progress state is being saved so when a user refreshes the page or returns later, the button type reflects what stage of progress there goal is in

    # Retrieve the corresponding goal_title from the completion button that was pressed
    update_data = request.get_json()
    goal_title = update_data['goalname']

    # When the progress of the goal has reached it's maximum value, update the status of the button to complete the goal
    db.execute("UPDATE goals SET progress_state = 2 WHERE user_id = ? AND goal_title = ?",
               currentuserid, goal_title)

    return {"success": True}


@app.route("/goal_completed", methods=["POST"])
@login_required
def goal_completed():
    """Update Database when User Completes Goal"""
    currentuserid = session["user_id"]
    currentdate = datetime.datetime.now()
    date_completed = currentdate.strftime("%Y/%m/%d")

    # Retrieve the corresponding goal_title from the completion button that was pressed
    completed_data = request.get_json()
    goal_title = completed_data['goalname']

    # When the user has finished all scheduled events for their goal on the current day, update the goal in the table with a completed status and add 1 to the days_completed number
    current_days_completed = db.execute(
        "SELECT days_completed FROM goals_completed WHERE user_id = ? AND goal_title = ? AND completion_status = TRUE ORDER BY date_completed DESC LIMIT 1", currentuserid, goal_title)

    if not current_days_completed:
        updated_days_completed = 1

    elif current_days_completed[0]['days_completed'] == 0:
        updated_days_completed = 1

    else:
        updated_days_completed = current_days_completed[0]['days_completed'] + 1

    db.execute("UPDATE goals_completed SET completion_status = TRUE, days_completed = ? WHERE user_id = ? AND goal_title = ? AND date_completed = ?",
               updated_days_completed, currentuserid, goal_title, date_completed)

    # Update progress status
    db.execute("UPDATE goals SET progress_state = 3 WHERE user_id = ? AND goal_title = ?",
               currentuserid, goal_title)

    return {"success": True}


@app.route("/reset_progress", methods=["POST"])
@login_required
def reset_progress():
    """Reset Goal Progress"""
    currentuserid = session["user_id"]
    currentdate = datetime.datetime.now()
    currentdate_string = currentdate.strftime("%Y/%m/%d")

    # Retrieve the corresponding goal_title from the completion button that was pressed
    data = request.get_json()
    goal_title = data['goalname']

    # Reset completion_status in goals_completed
    db.execute("UPDATE goals_completed SET completion_status = FALSE, days_completed = 0 WHERE user_id = ? AND goal_title = ? AND date_completed = ?",
               currentuserid, goal_title, currentdate_string)

    # Reset progress_number and progress_state in goals
    db.execute("UPDATE goals SET progress_number = 0, progress_state = 1 WHERE user_id = ? AND goal_title = ? AND date_progress_last_updated = ?",
               currentuserid, goal_title, currentdate_string)

    return {"success": True}


# TO DO:

    # Complete the README
    # Record Video
    # Submit project
