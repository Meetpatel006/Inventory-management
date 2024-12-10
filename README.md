# Inventory Management System

A comprehensive inventory management system built with Python and Firebase. This application allows users to manage inventory efficiently, including product management, user authentication, and billing processes.
## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Project Structure](#project-structure)
- [Functionality Overview](#functionality-overview)
  - [Admin Functions](#admin-functions)
  - [User Functions](#user-functions)
  - [Billing System](#billing-system)
  - [Remember Me Functionality](#remember-me-functionality)
- [Usage](#usage)
- [Logging](#logging)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)
## Features

- **User Authentication**: Supports both Admin and Normal User roles to ensure secure access.
- **Product Management**: Admins can add, modify, and delete products in the inventory.
- **Cart and Billing System**: Users can add products to their cart, view their cart, and generate bills.
- **QR Code Generation**: Automatically generate QR codes for products for easy scanning.
- **Real-time Firebase Database Integration**: All data is stored and managed in a Firebase database, allowing for real-time updates.
- **Logging System**: Tracks user actions and system events for better monitoring and debugging.
- **Remember Me Functionality**: Allows users to save their login credentials for future sessions.
## Prerequisites

Before you begin, ensure you have met the following requirements:  

- Python 3.x installed on your machine.
- A Firebase project set up with Firestore enabled.
- Firebase Admin SDK credentials (JSON file).
## Setup

Follow these steps to set up the project on your local machine:
1. **Clone the Repository**:

   ```git clone https://github.com/Meetpatel006/inventory_management.git ```
```cd inventory_management```

2. **Install Dependencies**:

   Install the required Python packages using pip:
   ```pip install -r requirements.txt ``` 

3. **Configure Firebase**:

   - Place your Firebase credentials in the `src/config/credentials.json` file. You can obtain this file from your Firebase project settings.

4. **Run the Application**:

   Start the application by executing:
   ```bash
   python main.py
   ```
## Project Structure

The project is organized as follows:

```
inventory_management/

├── src/
│   ├── gui/          # GUI components for user interface
│   │   ├── admin_window.py  # Admin interface for managing products and users
│   │   ├── user_window.py   # User interface for shopping and billing
│   │   └── login_window.py   # Login interface for user authentication
│   ├── core/         # Core business logic and functionalities
│   │   ├── admin_functions.py  # Functions for admin operations
│   │   ├── user_functions.py   # Functions for user management
│   │   ├── product_functions.py # Functions for product management
│   │   ├── bill_functions.py    # Functions for bill generation and management
│   │   └── setup.py              # Setup functions for initializing the application
│   └── config/       # Configuration files, including Firebase credentials
│       └── credentials/  # Folder to store user credentials for "Remember Me" functionality
├── main.py            # The main file for running the application
├── requirements.txt  # List of project dependencies
└── README.md         # Project documentation

```
## Functionality Overview

### Admin Functions

The admin interface allows for comprehensive management of the inventory system:

- **User Management**: Admins can create, modify, and delete user accounts. This includes setting user roles (Admin or Normal User).
- **Product Management**: Admins can add new products, modify existing product details (name, price, quantity), and delete products that are no longer available.
- **View Logs**: Admins can view logs of user activities and system events for monitoring purposes.
### User Functions
  
The user interface provides a seamless shopping experience:

- **Product Browsing**: Users can view a list of available products, including details such as name, price, and quantity.
- **Cart Management**: Users can add products to their cart, update quantities, or remove items. The system checks for stock availability before allowing additions.
- **Checkout Process**: Users can proceed to checkout, where they can review their cart and generate a bill.
### Billing System

The billing system handles the generation and management of bills:

- **Bill Generation**: Each bill is generated with a unique identifier and includes details such as customer name, contact information, purchased items, total amount, and any applicable discounts.
- **Bill Storage**: Generated bills are saved in a designated directory for future reference.
### Remember Me Functionality

The "Remember Me" feature allows users to save their login credentials securely. When enabled, the application stores the user's username and password in the `src/config/credentials/` folder, allowing for automatic login in future sessions. This enhances user experience by reducing the need to enter credentials each time the application is launched.
## Usage

Once the application is running, you can access the user interface where you can:

1. **Login**: Users can log in as either Admin or Normal User.
2. **Admin Functions**:
   - Manage products: Add, edit, or delete products in the inventory.
   - View user activity and manage user accounts.
3. **User Functions**:
   - Browse products and add them to the cart.
   - View the cart and proceed to checkout.
   - Generate bills, which will be saved and can be viewed later.
### Example Workflow

1. **Admin Login**: Admin logs in to manage products.
2. **Product Management**: Admin can add new products, modify existing ones, or delete products that are no longer available.
3. **User Login**: Normal users log in to view products.
4. **Shopping**: Users can add products to their cart and proceed to checkout.
5. **Billing**: Users can generate bills, which will be saved and can be viewed later.
## Logging
  
The application includes a logging system that records important events, such as user login attempts, product modifications, and Firebase initialization. Logs can be found in the `ims-info/logs/` directory. This helps in monitoring the application and debugging issues.
## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please fork the repository and submit a pull request. Ensure to follow the coding standards and include tests for new features.
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
## Acknowledgments

- Thanks to the Firebase team for providing a robust database solution.
- Special thanks to the open-source community for their contributions and support.