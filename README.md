# LittleLemon API

The LittleLemon API is a web service for managing a restaurant's menu items, orders, and user interactions. This project is a modification of the final project work for the API course offered by Meta on Coursera. This README provides an overview of the project, how to set it up, and the available endpoints.

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Authentication](#authentication)
  - [API Endpoints](#api-endpoints)
- [Permissions](#permissions)
- [Filters and Sorting](#filters-and-sorting)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

### Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7+
- Pipenv
- Django 4.2
- Django REST framework 3.12+
- Djoser
  

### Installation

1. Clone this repository: git clone https://github.com/aygalaxyworld/littlelemon-api.git
2. Unzip the folder and Open CMD to the folder path
3. Install dependencies using pipenv install
4. Migrate the tables using python manage.py migrate
5. Create an admin python manage.py createsuperuser
The API should now be accessible at http://localhost:8000/api/.

## Usage
### Authentication
To access most API endpoints, you need to authenticate. The API supports Token-based authentication, which can be obtained by creating an account or superuser account and then logging in.

### API Endpoints
Menu Items: /api/menu-items

Create, list, filter, and sort menu items.
Requires authentication.
Cart: /api/cart/menu-items

Create and list cart items.
Requires authentication.
Orders: /api/orders

Add users to Manager Groups
 group:  api/groups/manager/users
         api/groups/manager/users/<int:pk>
         api/groups/delivery-crew/users
         api/groups/delivery-crew/users/<int:pk>

Retrieve and update user profiles.
Requires authentication.
Admin Panel: /admin

Access the Django admin panel.
Requires admin permissions.

## Permissions
The API uses permissions to control access to various features:

IsAuthenticated: Users must be logged in to access most endpoints.
IsManagerOrReadOnly: Managers can edit menu items, others can only view.
IsAdminUser: Admins have full access to everything.
IsCustomer: Users without any specific group can access customer features.

## Filters and Sorting
You can filter and sort data on some endpoints using query parameters. For example, on the /api/menu-items endpoint, you can filter by name or price and sort by various criteria.

Example:

Filter menu items by name: /api/menu-items?name=burger
Sort menu items by price: /api/menu-items?ordering=price

## Contributing
Contributions are welcome! If you'd like to contribute to the project, please follow these steps:

Fork the project.
Create a new branch for your feature or bug fix.
Make your changes and test thoroughly.
Submit a pull request to the main repository.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

