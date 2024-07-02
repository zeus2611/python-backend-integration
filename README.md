# Python Backend Integrations

This project demonstrates a full-stack integration with HubSpot, Airtable, and Notion. It uses FastAPI for the backend to handle OAuth2 authentication and fetch data, and React for the frontend to display the data. This project is part of an assessment to showcase my backend and frontend development skills.

## Features

- OAuth2 authentication with HubSpot, Airtable, and Notion
- Secure storage and retrieval of access tokens using Redis
- Fetching and displaying data from HubSpot, Airtable, and Notion
- Full-stack implementation with FastAPI and React
- Detailed error handling and logging

## Technologies Used

- FastAPI
- Redis
- HTTPX (for async HTTP requests)
- Python 3.9+
- React
- Material-UI

## Setup and Installation

### Prerequisites

- Python 3.9+
- Node.js
- Redis server
- Developer Accounts for HubSpot, Airtable, and Notion (for client IDs and client secrets)

### Clone the Repository

```bash
git clone https://github.com/zeus2611/python-backend-integration.git
cd python-backend-integration
```

### Backend Setup

1. Navigate to the backend directory:

    ```bash
    cd backend
    ```

2. Install Dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the backend directory and add your credentials:

    ```env
    CLIENT_ID=your_hubspot_client_id
    CLIENT_SECRET=your_hubspot_client_secret
    REDIRECT_URI=http://localhost:8000/integrations/hubspot/oauth2callback
    SCOPE=crm.objects.contacts.read%20crm.objects.contacts.write%20crm.schemas.contacts.read%20crm.schemas.contacts.write
    ```

4. Start the Redis server:

    ```bash
    redis-server
    ```

5. Run the FastAPI application:

    ```bash
    uvicorn main:app --reload
    ```

### Frontend Setup

1. Navigate to the frontend directory:

    ```bash
    cd ../frontend
    ```

2. Install Dependencies:

    ```bash
    npm install
    ```

3. Run the React application:

    ```bash
    npm start
    ```

### Endpoints

#### Backend Endpoints

- **Initiate OAuth2 Flow for HubSpot**

    ```http
    GET /integrations/hubspot/authorize
    ```

- **OAuth2 Callback for HubSpot**

    ```http
    GET /integrations/hubspot/oauth2callback
    ```

- **Get HubSpot Contacts**

    ```http
    GET /integrations/hubspot/items
    ```

Similar endpoints exist for Airtable and Notion.

### Project Structure

```
.
├── backend
│   ├── integrations
│   │   ├── __init__.py
│   │   ├── airtable.py
│   │   ├── hubspot.py
│   │   ├── integration_item.py
│   │   └── notion.py
│   ├── redis_client.py
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
└── frontend
    ├── src
    │   ├── App.js
    │   ├── index.js
    │   ├── integrations
    │   │   ├── airtable.js
    │   │   ├── hubspot.js
    │   │   ├── notion.js
    │   └── ...
    ├── package.json
    └── README.md
```

- **backend/integrations/hubspot.py**: Contains the main logic for HubSpot integration including OAuth2 flow and fetching contacts.
- **backend/redis_client.py**: Utility functions for interacting with Redis.
- **backend/main.py**: FastAPI application setup and routing.
- **frontend/src/integrations**: Contains React components for Airtable, HubSpot, and Notion integrations.

## Improvements

- Implement pagination for fetching all HubSpot contacts.
- Enhance error handling and logging.
- Add unit tests for the integration.
- Expand the frontend to display data from Airtable and Notion as well.

## License

This project is licensed under the MIT License.

## Contact

For any questions or suggestions, feel free to reach out to me at [itsnischay2604@gmail.com].

---
