# Shopping Cart Service

This is a simple Shopping Cart service implemented using Flask and PostgreSQL. The service allows users to:
- Register and log in.
- Add items to a shopping cart.
- View items in the cart.
- Remove items from the cart.
- Update the quantity of items in the cart.
- Checkout the cart.
- View order history.
- Logout.

## Getting Started

The Project can be deployed locally using Minikube for Kubernetes or using Docker Compose. Below are the instructions for both methods.

### Prerequisites

- Docker
- Docker Compose (for Docker deployment)
- Minikube (for Kubernetes deployment)
- kubectl (for Kubernetes deployment)
- Postman (for API testing)

## Deploy with Kubernetes

### Step 1: Clone the Repository

```sh
git clone https://github.com/kartike2001/ShoppingBackend.git
cd shopping-cart-backend
```

### Step 2: Build and Push Docker Image

Build and push the Docker image to your Docker Hub repository.

```sh
docker build -t kartike2001/shopping-cart-backend .
docker push kartike2001/shopping-cart-backend
```

### Step 3: Start Minikube
Start Minikube to create a local Kubernetes cluster.

```sh
minikube start
```

### Step 4: Apply Kubernetes Configurations

Apply the PostgreSQL deployment, backend deployment, and service configurations.

```sh
kubectl apply -f postgres-deployment.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

### Step 5: Verify Pods and Services

Check that all pods and services are running correctly.

```sh
kubectl get pods
kubectl get services
```

### Step 6: Get Minikube IP

Get the Minikube IP address to access your application.

```sh
minikube ip
```

Replace `<minikube-ip>` with the obtained IP address in the API endpoints below.

### API Endpoints and Testing with Postman

#### 1. Register a New User 

- **URL:** `http://<minikube-ip>:30008/users/create`
- **Method:** `POST`
- **Headers:** 
  - `Content-Type: application/json`
- **Body:**

To test on Postman, select raw JSON.

```json
{
    "name": "Kartike Chaurasia",
    "email": "kartike.chau@philips.com",
    "password": "password123"
}
```

#### 2. Log in as the User

- **URL:** `http://<minikube-ip>:30008/users/verify`
- **Method:** `POST`
- **Headers:**
  - `Content-Type: application/json`
- **Body:**

To test on Postman, select raw JSON.

```json
{
    "email": "kartike.chau@philips.com",
    "password": "password123"
}
```

#### 3. Add Items to the Cart

- **URL:** `http://<minikube-ip>:30008/cart/items`
- **Method:** `POST`
- **Headers:**
  - `Content-Type: application/json`
  - `Cookie: authToken=<your_auth_token>` (Replace `<your_auth_token>` with the token received in the login response)
- **Body:**

To test on Postman, select raw JSON.

```json
{
    "itemName": "IntelliVue MX400",
    "itemPrice": 9999.99,
    "itemQuantity": 10
}
```

#### 4. View Cart

- **URL:** `http://<minikube-ip>:30008/cart/items`
- **Method:** `GET`
- **Headers:**
  - `Cookie: authToken=<your_auth_token>` (Make sure header is checked)

#### 5. Update Cart Quantity

- **URL:** `http://<minikube-ip>:30008/cart/items`
- **Method:** `PUT`
- **Headers:**
  - `Content-Type: application/json`
  - `Cookie: authToken=<your_auth_token>` (Make sure header is checked)
- **Body:**

To test on Postman, select raw JSON.

```json
{
    "cart_id": 1,
    "itemQuantity": 5
}
```

#### 6. Remove Item from Cart

- **URL:** `http://<minikube-ip>:30008/cart/items`
- **Method:** `DELETE`
- **Headers:**
  - `Content-Type: application/json`
  - `Cookie: authToken=<your_auth_token>` (Make sure header is checked)
- **Body:**

To test on Postman, select raw JSON.

```json
{
    "cart_id": 1
}
```

#### 7. Checkout Cart

- **URL:** `http://<minikube-ip>:30008/cart/checkout`
- **Method:** `POST`
- **Headers:**
  - `Content-Type: application/json`
  - `Cookie: authToken=<your_auth_token>` (Make sure header is checked)

#### 8. View Order History

- **URL:** `http://<minikube-ip>:30008/users/orderHistory`
- **Method:** `GET`
- **Headers:**
  - `Cookie: authToken=<your_auth_token>` (Make sure header is checked)

#### 9. Logout

- **URL:** `http://<minikube-ip>:30008/users/logout`
- **Method:** `POST`
- **Headers:**
  - `Content-Type: application/json`
  - `Cookie: authToken=<your_auth_token>` (Make sure header is checked)

## Deploy with Docker Compose

### Step 1: Clone the Repository

```sh
git clone https://github.com/kartike2001/ShoppingBackend.git
cd shopping-cart-backend
```

### Step 2: Start the Docker Containers

Make sure Docker is running, then use Docker Compose to start the containers.

```sh
docker-compose up --build
```

This command will build the Docker images and start the containers for the Flask web server and the PostgreSQL database.

### API Endpoints

Replace `localhost` with the appropriate IP address when accessing the endpoints. The rest of the endpoints remain the same as listed above.

## Troubleshooting

If you encounter any issues, check the logs of the pods:

```sh
kubectl logs <pod-name>
```

Ensure that the Flask application is binding to `0.0.0.0` and running on port 80.