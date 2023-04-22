# Monitorman 🕵️‍♂️

Monitorman is a web application that allows you to create and schedule custom HTTP requests and monitor their expected results. With Monitorman, you can easily set up automated tests to monitor the availability, performance, and correctness of your web services, APIs, and websites.

## Features 🚀

- **Custom HTTP Requests**: Monitorman allows you to create custom HTTP requests with flexible options including URL, HTTP method (GET, POST, PUT, DELETE, etc.), headers, query parameters, request body, and authentication.

- **Expected Results**: You can define expected results for each HTTP request, specifying the expected response status code, response headers, response body, or any combination of these. Monitorman will automatically validate the responses against the expected results.

- **Schedule Monitoring**: Monitorman enables you to schedule monitoring tasks to run at specified intervals, such as every minute, hourly, daily, or custom intervals. You can configure multiple schedules for each HTTP request, allowing you to monitor different endpoints with different frequencies.

- **Dashboard and Reports**: Monitorman provides a user-friendly dashboard that displays the status of your monitoring tasks in real-time. You can view historical monitoring results and generate detailed reports to analyze the performance and availability of your web services over time.

## Getting Started 🚀

To get started with Monitorman, follow these steps:

1. Clone the Monitorman repository from GitHub.
2. Install Docker and Docker Compose on your system if you don't have them already.
3. Navigate to the cloned directory and run `docker-compose up -d` to start the application containers.
4. Access the Monitorman web application in your web browser at `http://localhost:8002`.
5. Create your custom HTTP requests by providing the necessary details such as URL, method, headers, query parameters, request body, and expected results.
6. Schedule your monitoring tasks by defining the monitoring intervals for each HTTP request.
7. Monitor the status of your monitoring tasks in the dashboard and analyze the reports to gain insights into the performance and availability of your web services.