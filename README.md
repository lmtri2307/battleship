# BattleShip Game

Welcome to the BattleShip Game project! This project was developed as part of a Computer Networking course, showcasing the implementation of a multiplayer BattleShip game with client-server architecture.

## Demo Video

Check out the demo video of the BattleShip [here](https://www.youtube.com/watch?v=ciYIb-8J9tU).

## Project Description

The BattleShip Game allows clients to connect to a server using an IP address and port. After connecting, clients can either login or sign up to access the game. Once logged in, clients can invite other connected clients to a game of BattleShip. The game features a graphical user interface developed using Tkinter and utilizes Pygame for the BattleShip game mechanics.

## Technologies Used

- Python: The project was developed using the Python programming language.
- Socket: Socket programming was employed for the client-server communication.
- Tkinter: The Tkinter library was used to develop the graphical user interface for login, sign up, and game lobby screens.
- Pygame: Pygame library was utilized to design and implement the BattleShip game mechanics.

## Getting Started

To run the BattleShip Game locally, follow these steps:

1. Clone the repository: `git clone https://github.com/lmtri2307/battleship`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Run the server: 
    - Navigate to the server directory: `cd sever` 
    - Run the program: `python Sever.py`
4. Run the client:
    - Navigate to the client directory: `cd client` 
    - Run the program: `python Client.py`
    - Use the IP address `127.0.0.1` and port number `33000`
## Usage

Once the server and client are running, clients can follow the on-screen prompts to connect, login or sign up, and invite other connected clients to a game. The game interface will display the BattleShip grid and provide options for placing ships and making guesses.

## Contributing

Contributions to the BattleShip Game project are welcome! If you would like to contribute, please fork the repository, make your changes, and submit a pull request.

