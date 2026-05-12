# Adam's Goal Tracker App
#### Video Demo: https://www.youtube.com/watch?v=drehpYfWFf8

## Summary:
The goal of my CS50 final project was to create a web-based goal-tracking application using HTML, CSS, JavaScript, Python and SQL. There were many features I wanted the users to have access to such as, being able to log in to the site, create goals, schedule them for various days across the week, and monitor their progress of the goal on the current day. It was also important for the user to be able to see how many times they have completed the goal whilst being able to view a calendar of the current month where they can see all of the days they completed their goals as motivation for continuing.<br/>

As well as listing some of the features of my website, I am also going to break down what each file in my project does and outline any areas I found particularly challenging, as well as the decisions I made when designing the pages.<br/>
<br/>

## Key Features:
+ Create and edit goals.

+ Change when goals are scheduled.

+ If the user changed the day from the current day, this would be correctly recorded in the completion table.

+ Track the goal with a progression bar.

+ Retain progression state of the goal when user leaves the site.

+ Mark days as completed only when all scheduled goals are finished.

+ Provide a Calendar that visually keeps track of completed days.

+ Completion history recording when the goal was completed and the number of times the goal has been completed.

<br/>

## Key Pages and Files Breakdown

### Python Files:

### Main Python File - app.py:
Outside of the helpers.py file, the app.py file contains all the code for managing the data and structure of my application. I have included a citation for code copied from previous problem sets (the register, login, and logout routes), which I made small adjustments to. Apart from that, all the code after was written by me.<br/>

#### Schedule Route:
The first route is for the schedule page on my site. This route determines which database data applies to the current user, selects it, and passes it to the relevant HTML file via Jinja. This includes aspects such as determining if the user is new or not, as that will flag which HTML page to render, filtering the data selection based on what the current day is, and the days the user selected the goal to be scheduled on (more on day selection in the 'add_goal' route section).<br/>

This was a particularly challenging route to code, as it required making numerous SQL queries and keeping track of and updating many values in variables to not only determine which data to pass to HTML, but also assess which sections of the HTML to display.
<br/>
<br/>

#### Goal Route:
The goal route is responsible for sending the correct information to the Goal page on the app. The route first checks whether the user has any goals registered and conditions whether to display certain aspects of the Goals page. After checking whether the user has any registered goals, an empty list is created, then populated with only the essential data from the goals database, and finally passed to the HTML, where the information from the list is displayed. I decided to populate my own list with only the necessary information rather than using 'SELECT *', since the 'goals' table contained numerous columns that weren't needed for the information I wanted to display on the Goals page.<br/>
<br/>

#### Add Goal Route:
The 'add goal' route utilises both GET and POST methods. When accessing the page via GET, the page displays an empty form where the user can enter all the details about their goal (this will be explained further in the 'add goal' HTML section). When using POST, the route collects all the information from the user's submitted form. It then checks whether all the essential form fields are filled in. If not, it refreshes the same webpage and tells the user that they haven't filled out all the fields. If the form is successful, all the information is inserted into the goals table along with the user's ID, and the user is directed to a confirmation page to confirm that the goal was registered successfully.<br/>

One minor challenge with this section was sorting through which days the user chose to schedule their goal. Since I used a checkbox approach in the HTML, any checked boxes returned the string 'true' or nothing. As I set up my table to store Boolean values for each day of the week, I needed to write numerous conditionals to check which days were selected and set their status to either True or False, then finally insert all the data into the table.<br/>
<br/>

#### Goal Deletion Routes:
The delete route determines which goal the user wants to delete when they click the delete button. A small challenge of this section, though, was figuring out how to implement a system where, when a user clicks to delete a specific goal, I would then need to locate which goal they were referring to, then pass that information into app.py and filter through all the goals that specific user has and delete the correct goal. My approach was to first select all the goals associated with the user, then retrieve the goal name from the form and store that in a variable. I then set up a loop over all the goals in my list, generated by the select query, and checked whether the current goal name in the loop matched the name stored in the form variable. If it were a match, it would confirm which goal the user wanted to delete.<br/>

However, this route wouldn't actually be responsible for deleting the goal, as I wanted to have a safety measure in place for the user in case they accidentally click to delete the goal. This route just confirms the goal they want to delete and renders it on the web page, where they then click to confirm they want to delete it. This information is then passed to the delete confirmation route, and the page then provides feedback to the user to let them know the goal was successfully removed. It is also responsible for locating the goal in the table (using a similar process as above) and actually deleting all the relevant data associated with that goal, not just in the 'goals' table, but also the 'goals_completed' table.<br/>
<br/>

#### Goal Information Route:
This route follows a very similar structure to the add goal route. However, the main difference with this route is that users can go back and edit any information about their goal, and update the relevant data in the goal table. This difference applies to the GET section of the route, where I wanted the system to automatically populate all of the form's fields with the current data the user has about their goal. Otherwise, if they clicked to edit any information about their goal, the user would have to retype all the information, as none of the fields would contain any data.<br/>

This was more of a challenge on the HTML side, as I needed to learn which attributes to include in each input field tag and set up a system so that all the information passed through Jinja would become the value of those attributes, ensuring the information was displayed correctly. This was a key feature I wanted to include as, if a user only wanted to change the days the goal was scheduled on, I didn't want them to have to retype every other piece of information into the form just to change a day.<br/>
<br/>

#### Calendar Route:
The calendar route was complex to implement, but a vital aspect I wanted in my app. I wanted the calendar to show the user's goal completion streak by showing each day in the month as either a green completed box or a faded grey box if all the goals on that day weren't completed. I also wanted a history section below the calendar that showed the 14 most recent completed goals and provided a count of how many times each goal has been completed overall. This page was vital to get right, as this page was designed to motivate users to keep working on their goals and keep their completion streak going by providing stats and visual cues.<br/>

While providing the completion history was relatively simple, as I just needed to generate a list through a SQL query, the calendar was more complicated. I will talk more about how the visuals were created in the calendar HTML file, but as for the actual data, the idea was to create a list of all the days in the month, which were either marked as true or false, depending on whether all the goals on that current day were marked as completed. The first step was to create a loop that totalled the number of days in the current month, which was achieved by using datetime and conditions to determine the current month and therefore the number of days. I then created an empty list and iterated over each day, selecting the relevant data from the ‘goals completed’ table. If all the goals in the selection had a true completion status, the current day in the loop was marked as true and appended to the loop. If there were no goals to select or if one of the goals had a false completion status, the day was marked as false and added to the list. This resulted in a list of every day in the month, marked as true or false, which was used as the condition to determine which styling to apply to the calendar.<br/>
<br/>

#### Begin Day Route:
A fairly simple route. This is responsible for when a user clicks to begin their day. All the goals listed on the current day are inserted into the 'goals completed' table with a false completion status and the current day. This was essential for adding data to the completion table so the queries in the calendar route could identify which days had all their goals marked with the true completion status.<br/>
<br/>

#### Goal Progress Route:
The aim of this route was to track the user's progress toward the goal and store it in the goals database. This was a complicated route, as I needed to use JavaScript to send requests to my Python code in order to update my databases, but I will talk about that more in the HTML section.<br/>

This was an essential component as, originally, the user would click to increase the progress bar next to the goal, and the bar would increase. The button to increase the bar and ultimately record the goals as completed worked, but, if the user left the page at any point then returned, all the progress was reset and the button was reset to default even if they clicked to complete the goal. So this route made it so that when a user clicked to increase their progress, it would update the bar in real time using JavaScript and also send a request to update the database with the goal's current progress status. This ensured that progress was stored so that when a user closed the page and returned, the progress bar and the state of the completion button would reflect where the user left off.<br/>
<br/>

#### Progress Status Route:
This route is very similar to the route above. Instead of keeping track of how much progress the user has made and recording it in a database, this approach was developed to record the goal's completion state. For example, if the goal was still in progress, it was recorded as '1'. If the user has completed all their progress, the status is marked as '2', indicating that they need to click the button to register their goal as completed. This would then change the status to '3', which meant the goal has been registered as completed. This route essentially served to keep track of the button status next to each goal, so that if the user left the page and returned, the button status remained the same.<br/>
<br/>

#### Goal Completed Route:
This route is quite self-explanatory in that, when the user clicks the completion button next to their goal, it updates the goal in the 'goals completed' database to be marked as true in the completion status column. It would also determine the value in the 'days completed' column in the most recent instance of the goal, which was a key piece of data to keep track of, as I wanted the user to be able to see how many times they had completed that specific goal.<br/>
<br/>

#### Reset Progress Route:
The final route was also relatively simple to put together in Python, but a little more complicated in HTML, as it follows a similar approach to the process on the schedule page for using JavaScript and fetch to manage the progress bar state. This route's purpose was to allow the user to reset the goal's progress on the current day. This was more of a quality-of-life feature in case the user accidentally clicked to increase their progress too many times and wanted to reset the bar so they could put in the correct value. It would also reset the completion status of the goal in the 'goals completed' table back to false.<br/>
<br/>

### Helper Python File - helpers.py:
A very short file that defines the function for a login requirement. The code in this file was copied from the Finance problem set, where I wanted certain webpages in my app to be only accessible when the user has logged in. All citations of of where I copied the code from are in the file itself.<br/>
<br/>
<br/>
<hr/>

### Template Files:

#### Layout Page - layout.html:
A very simple HTML file. This file provides the framework for the rest of the pages in the application, including links to utilise Bootstrap styling across the site.<br/>
<br/>

#### Schedule Page - schedule.html:
This is the main page you are taken to after the user logs in. All pages include a navigation section at the top. This page displays all the goals the user has registered for today, a progress bar showing how much progress the user has made, a button to increase the progress value and mark the goal as completed. There is also a reset button to reset the goal's progress. The information that populates the table is determined in Python and then passed through Jinja. There are a few conditions in place, depending on the user's status, which dictate which parts of the HTML are displayed or hidden.<br/>

This page was quite challenging to put together because it required a fair bit of JavaScript, which I wasn't comfortable with. The parts in question were the ability to increase the progress bar in real time and to incorporate a reset button, whilst also sending the relevant information via fetch to my databases. This was a challenge as I wasn't sure how to write JS code in order to select specific data points in a table, edit that value depending on certain conditions, use these conditions to also change what CSS styling to apply to the buttons and then finally update the table to reflect which button the user clicked on.<br/>

It was also challenging to figure out how to send requests to my Python code to update specific information in my table based on which button was clicked and the goal's status. This is where I used ChatGPT to explore fetch's capabilities (I disclose the extent to which I used ChatGPT within the code, but, simply put, all the code was written by me). ChatGPT gave me a breakdown of what fetch is, gave examples using example code of how it is used and provided a link to the documentation about it. I then incorporated fetch into my own code to send requests to update my databases and dynamically change the button tags' classes so I could adjust the button's styling based on the goal's progress. This also applied to the reset function in my JS code, where I used fetch to request resetting specific data in my databases.<br/>
<br/>

#### Register/Login Pages - register.html and login.html:
Quite simple HTML files that contain a form where the user enters a username and password, which are then stored in the user database to record their user_id, which is then used in the other data tables in the application to select information relevant only to the current user.<br/>
<br/>

#### Goal Page - goals.html:
The goals page displays what goals the user has registered in their goals list. The purpose of this page is to allow the user to see all their current goals, the days on which they have scheduled each goal, and to edit or delete each goal.<br/>
<br/>

#### Add Goal Page - add_goal.html:
This page provides a form for the user to add a goal. This form is responsible for organising which data is passed into the databases, which, in turn, determines not only what information is displayed but also which days the goals should appear. I also decided to incorporate the SMART goal-setting framework to structure the form and give users greater clarity about what they want to achieve, which I believe would also help with motivation and accountability.<br/>
<br/>

#### Goal Info Page - goalinfo.html:
This page is very similar to the add goal page in both structure and content. This page was merely a tool that allowed users to view all the information they currently have about their goal and make any adjustments, such as changing the dates the goal was scheduled for and the information outlined in the SMART sections. This was particularly challenging to achieve, as I needed to figure out how to pass the original information the user had written before creating the goal, and use that data to fill out the input fields for them. Otherwise, the user would have to type everything again, even if they just wanted to change a minor detail about their goal.<br/>
<br/>

#### Delete Goal Pages - delete_goal.html:
The deleted pages are relatively straightforward. When the user clicks the delete button on the goals page, they are taken to this page first to confirm they want to delete the goal. Then, if they click the button, another page loads with a confirmation message indicating that the goal was deleted successfully. I wanted to have two separate pages and routes for this process, acting as a safety feature in case the user accidentally clicked the delete button.<br/>
<br/>

#### Apology Page - apology.html:
Another simple page. This page is used to inform the user of the error that has been caught, such as an incorrect username or password.<br/>
<br/>

#### Calendar Page - calendar.html:
The calendar page is the last page I will be describing, but it was quite a challenging page to put together due to the amount of information I wanted to include and how I wanted to display it. This was a crucial page to get right, as a key feature of my app was for the user to see the progress they have made through a visual streak pattern and to provide data on how many times they had completed the goal.<br/>

The history section was quite simple to put together. All I needed to do was run a 'select' query, then pass the resulting list through Jinja to populate a table with that information. I did modify the selection query slightly, though, as I wanted the information organised by the most recent date first, with the 14 most recent completed goals displayed. It was also important to display the number of times the goal had been completed in this table to help motivate users to keep going.<br/>

The trickier part was creating a calendar that would count the days in the current month, indicate when the user had completed all their goals, and display that information in an appealing way. Whilst the actual code in the HTML may look relatively simple, the challenge came from organising that data to be passed in the first place, as I described earlier in the Python section, and from utilising the many features and properties within CSS to achieve the style I wanted. I opted to use a table to organise the data, and, through extensive research into CSS and a fair bit of trial and error, I was able to achieve the look I wanted.<br/>

<br/>

## Closing Thoughts:
Overall, while this project was quite tough for me to put together, it was nonetheless a very enjoyable and challenging experience that required a lot of trial and error in order to produce this result, which I am very proud of.<br/>

Seeing as I had no prior coding experience at the start of the CS50 course, being able to produce this application whilst utilising numerous languages and tools was by no means a small feat for me. While I found the CSS and HTML sections to be relatively straightforward, the more challenging aspects came from how to utilise JavaScript to produce the responsive results I wanted and from managing and passing all the key data I wanted the user to see with Python, SQL, and Jinja. This was essential to my application, as a key part of achieving goals was providing visual feedback on how much the person has progressed, so I wanted to make sure that information was clearly displayed to any user in an appealing manner.<br/>

If I were to develop this project further, there are numerous features I would've liked to include, but don't have the capability to do so at the moment. These features include a chatbot on the goal creation page to provide further insight into creating an ambitious and achievable goal, with additional clarification. Or even a chatbot across the entire site that provided encouragement or advice if the user was struggling to complete their goal. Another feature would be to have the user provide an email address, which would then be used to send reminders if they have any goals yet to be completed today. Perhaps even a medal or achievement system in place where, if the user completed a certain number of goals, they would receive a medal, or if they completed a certain number of goals across a week, they would receive a trophy. Then there would be a page dedicated to displaying all the medals and trophies they received by completing their goals.<br/>

To conclude, whilst there were many ups and downs throughout this process, this was an extremely rewarding project to work on, and I am very happy with my goal-tracking application.<br/>

<br/>
<hr/>


