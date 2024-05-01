# CampusSwap Web App

Based on our second project, the new and revised CampusSwap implements several new features to makes the web app more complete and user friendly. CampusSwap allows users to create an account and make listings to other users, making trading items easier between students.

# New Features

- Adding Offers: Users can now create and recieve offers for items, as well as accept/decline offers
- Private Items: Items can now be set to private or public
- Profiles: Each user has a unique profile which displays the items sold
- Friends: Users can now add friends and view their friends list
- Pages: The marketplace will now have pagination features

# Contributors

- [Eleazer Neri](https://github.com/afknero)
- [Terry Qiu](https://github.com/TerryQtt)
- [Marc Etter](https://github.com/Morcupine)
- [Johan Gallardo](https://github.com/JohanGallardo)

# How to Run

Create and navigate to local repository. Then run command below, which removes any containers whose ports are needed.

    docker-compose down

To install the required dependencies and run the program, run the following command.

    docker-compose up --build

To open the app, open a web browser and navigate to [localhost:5001](http://localhost:5001/). Do not go to the address that the program tells you to navigate to.

# Additional Comments On Running

Developers should set a FLASK_PORT in a .env file as well as include mongodb configurations.
