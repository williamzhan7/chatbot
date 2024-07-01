# Web Server-based Chatbot for Managing Meetings using Cal.com API
This project is a Flask-based web server that hosts a chatbot capable of handling various booking operations using the Cal.com API. The chatbot supports creating, finding, editing, and canceling bookings, as well as retrieving available bookable slots.

Currently a development server listening on port 5000

To use, start the webserver and curl a post request with a json header to the /query endpoint.

Example: curl -X POST -H "Content-Type: application/json" -d '{"query": "{your_query}"}' http://127.0.0.1:5000/query

