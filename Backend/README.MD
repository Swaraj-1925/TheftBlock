# Theft Block - Smart Inventory Tracking Backend

## Overview

Theft Block is a smart inventory tracking system designed to monitor and manage inventory using UHF RFID technology. Due to the unavailability of actual sensor access, dummy classes have been implemented to simulate sensor functionality. These classes can be found in the `src/dummy` directory. Once real sensors are available, their functionality should be integrated into these classes.

### Key Features:

- Suppliers attach a UHF RFID tag to each product.
- Products are tracked using a unique hashed ID.
- Shipment receipts are created by both suppliers and warehouse owners to cross-check potential theft.
- Each shelf in the warehouse has a unique reader and ID.
- Shelves are periodically scanned to detect missing products.
- If an expected product is missing from a shelf and is not marked as sold, it is flagged as stolen or missing.

---

## Installation and Setup

### Prerequisites:

- Python 3.13
- FastAPI
- Virtual Environment (recommended)
- PostgreSQL 17.4 (Database Setup Required)

### Database Setup:

Before starting the script, ensure that the required database is created by running the following commands:

```sh
psql -U postgres -h localhost
CREATE DATABASE "TheftBlock";
```

The database configuration should follow a setup similar to `Backend/src/config/Settings.py`.

### Steps to Set Up the Project:

1. Create a directory for the project and navigate into it:
   ```sh
   mkdir TheftBlock
   cd TheftBlock
   ```
2. Clone the repository:
   ```sh
   git clone https://github.com/Swaraj-1925/TheftBlock.git
   ```
3. Navigate to the cloned directory:
   ```sh
   cd TheftBlock
   ```

### Steps to Run the Backend:

1. Navigate to the backend directory:
   ```sh
   cd Backend
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Start the FastAPI development server: (NOTE: If Your running this on testing env 1st run `python -m Backend.main` )
   ```sh
    fastapi dev server.py
   ```
4. Access API documentation:
   Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser to explore available routes.

### Running Main Simulation:

To test the system without a frontend, navigate back one directory from `Backend` and run:

```sh
cd ..
python -m Backend.main
```

---

## Project Structure

```
Backend/
│-- app/                    # FastAPI-related modules
│   │-- services/           # Business logic and processing
│   │-- inventory_routes.py # API routes for inventory tracking
│   │-- res_models.py       # Response models
│-- dummy_data/             # Simulated JSON data for testing
│   │-- supplier_to_warehouse_recp.json
│   │-- warehouse_storage.json
│   │-- warehouse_to_customer.json
│-- src/                    # Core functionality
│   │-- config/             # Configuration settings
│   │-- Db/                 # Database models and schemas
│   │-- dummy/              # Dummy sensor classes
│   │-- manager/            # Supplier, warehouse, and theft detection managers
│   │-- ml/                 # Machine learning for anomaly detection (Not implemented yet)
│-- main.py                 # Testing script to simulate the process
│-- server.py               # Main FastAPI application entry point
```

---

## API Documentation

Once the server is running, FastAPI provides an interactive documentation interface where you can test API endpoints.

- Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for **Swagger UI**.
- Open [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) for **ReDoc**. [**Preferred**]

These endpoints will list all available API routes, expected request payloads, and responses.

---

## Future Enhancements

- Implement real sensor integration by updating the `src/dummy` classes.
- Enhance security features for preventing inventory theft.
- Develop real-time alerts for missing or misplaced products.
- Implement anomaly detection for sales inconsistencies.

---

## Contributing

If you want to contribute to Theft Block, feel free to fork the repository and submit a pull request. **Make sure you Star the repo**

### Author

Developed by **Team Ingenx**.

