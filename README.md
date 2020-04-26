# Virtual Herbarium
Springboard Capstone 1 - Virtual Herbarium

Deployed at: [https://virtualherbarium.herokuapp.com/](https://virtualherbarium.herokuapp.com/)

About this project
-

The virtual herbarium is a website that allows users to upload images of plants to create a digital plant collection specimen. Users can edit, add to, and maintain plant collections online on the virtual herbarium.

In addition to uploading plant images, users are asked to submit species name information, details of when and where the plant was collected, and other notes the user would like to provide. Images are uploaded anonymously to imgur using the imgur API. The glocal biodiversity informational facility API is used when entering the species information of the specimen. This database takes the species name and auto-fills all of the taxonomic information for a given species from genus to kingdom.

Collections can also be created for users to add plant specimens to, if they would like to categorize their plants. For example, a user could create a collection called "My backyard" and add all the plants they collected from their backyard to it.

Technologies used for this project
- 
- HTML/CSS/Javascript  
- Bootstrap  
- Python  
- Flask  
- PostgreSQL
  
Flask Extensions and Libraries used:
-
- Flask-WTF  
- Flask-SQLAlchemy
- Flask-Login
- Flask-Bcrypt


APIs Utilized
-

[imgur API](https://apidocs.imgur.com/?version=latest)

[Global Biodiversity Informational Facility API](https://www.gbif.org/developer/summary)

