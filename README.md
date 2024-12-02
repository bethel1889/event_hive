# EventLink

**EventLink** is a modern web application designed to enhance networking experiences at events. The platform provides users with the tools to create or join event-specific rooms, explore attendees' LinkedIn profiles, and foster meaningful connections.

---

## Table of Contents

1. [Features](#features)
2. [Technologies Used](#technologies-used)
3. [Getting Started](#getting-started)
   - [Requirements](#requirements)
   - [Installation](#installation)
   - [Database Setup](#database-setup)
4. [Usage](#usage)
   - [User Guide](#user-guide)
   - [Admin Features](#admin-features)
5. [Contributing](#contributing)
6. [License](#license)

---

## Features

- **Event Rooms**: Create or join unique event rooms with a secure key.
- **Networking**: Seamlessly connect with attendees via their LinkedIn profiles.
- **Personalized Connections**: Build meaningful, lasting relationships.
- **Role Management**: Admins can manage users and control room statuses.
- **User-Friendly Interface**: A clean and responsive design for all users.

---

## Technologies Used

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, Bootstrap
- **Session Management**: Flask-Session
- **Security**: Password hashing with `werkzeug.security`

---

## Getting Started

Follow these steps to set up and run the application locally.

### Requirements

Ensure you have the following installed:

- Python 3.x
- pip (Python package installer)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/EventLink.git
   cd EventLink
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Database Setup

1. Set up the database schema:

   ```bash
   python
   >>> from cs50 import SQL
   >>> db = SQL("sqlite:///database/eventlink.db")
   >>> exec(open("database/schema.sql").read())
   ```

2. Verify that the database tables have been created successfully.

---

## Usage

### User Guide

- **Registration**:
  - Navigate to the `/register` page to create a new account.
  - Provide your username, password, and LinkedIn profile link.
- **Login**:

  - Use your registered credentials to log in at `/login`.

- **Joining Event Rooms**:

  - Use a valid room key on the `/rooms` page to join a specific event.

- **Networking**:
  - View other attendees in your joined rooms and connect via their LinkedIn profiles.

### Admin Features

- **Manage Users**:
  - Admins can search for users and update their roles (e.g., toggle between Admin and User).
- **Control Rooms**:
  - Admins can toggle room statuses (e.g., Open or Closed).

---

## Contributing

We welcome contributions to EventLink! To contribute:

1. Fork this repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add new feature"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Open a Pull Request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Screenshots

![Homepage Screenshot](https://via.placeholder.com/800x400.png?text=EventLink+Homepage)  
_The EventLink homepage, showcasing event rooms and connection options._

---
