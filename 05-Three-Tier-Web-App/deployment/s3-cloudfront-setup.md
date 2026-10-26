# S3 and CloudFront Frontend Deployment

This document describes how the React frontend was deployed using Amazon S3 and Amazon CloudFront.

## Frontend Build

The frontend is built using React and Vite.

From the frontend project directory:

```bash
npm install
npm run build
```

The production build is generated in:

```text
dist/
```

Example build structure:

```text
dist/
├── index.html
├── favicon.svg
├── icons.svg
└── assets/
    ├── index-xxxxx.css
    └── index-xxxxx.js
```

The contents of `dist/` are uploaded to Amazon S3.

## S3 Bucket

A General Purpose S3 bucket was created for the React frontend.

Example:

```text
ecommerce-frontend-v1-2026
```

Configuration:

```text
Bucket type: General purpose
Region: ap-southeast-2
Block all public access: Enabled
Object ownership: ACLs disabled
Default encryption: SSE-S3
Static website hosting: Disabled
```

The bucket remains private.

CloudFront is responsible for serving the frontend to users.

## Upload React Build

The contents of the `dist/` directory are uploaded to the root of the S3 bucket.

Correct structure:

```text
S3 bucket root
├── index.html
├── favicon.svg
├── icons.svg
└── assets/
    ├── index-xxxxx.css
    └── index-xxxxx.js
```

The `assets` directory structure must be preserved because Vite references JavaScript and CSS files using paths under `/assets/`.

## CloudFront Distribution

A CloudFront distribution was created for the frontend.

Example distribution name:

```text
ecommerce-frontend-cloudfront
```

CloudFront provides HTTPS access to the application.

The default root object is:

```text
index.html
```

## Private S3 Origin

The S3 bucket is configured as the default CloudFront origin.

Origin Access Control is enabled so that CloudFront can access the private bucket without making S3 publicly accessible.

Architecture:

```text
Browser
   |
   | HTTPS
   v
CloudFront
   |
   v
Private S3 Bucket
   |
   v
React Application
```

## CloudFront Default Behavior

The default behavior handles frontend requests.

Example:

```text
Path pattern: Default (*)
Origin: S3 frontend
Viewer protocol policy: Redirect HTTP to HTTPS
Allowed methods: GET, HEAD
```

Static frontend content can use CloudFront caching.

## EC2 Backend Origin

A second CloudFront origin was added for the Spring Boot backend.

The EC2 public DNS name is used instead of the raw public IP address.

Example:

```text
ec2-<public-ip>.ap-southeast-2.compute.amazonaws.com
```

Backend origin settings:

```text
Protocol: HTTP only
HTTP port: 8080
Origin path: blank
```

CloudFront communicates with Spring Boot over port `8080`.

## API Behavior

A separate CloudFront behavior routes API traffic to EC2.

Configuration:

```text
Path pattern: /api/*
Origin: EC2 backend
Viewer protocol policy: Redirect HTTP to HTTPS
```

Allowed methods:

```text
GET
HEAD
OPTIONS
PUT
POST
PATCH
DELETE
```

Cache policy:

```text
CachingDisabled
```

Origin request policy:

```text
AllViewerExceptHostHeader
```

This allows dynamic API requests to reach Spring Boot without CloudFront caching API responses.

## Request Flow

Frontend request:

```text
https://<cloudfront-domain>/shop/products
          |
          v
      CloudFront
          |
          v
         S3
          |
          v
       React
```

API request:

```text
https://<cloudfront-domain>/api/products
          |
          v
      CloudFront
          |
          v
      EC2 :8080
          |
          v
    Spring Boot
          |
          v
      RDS MySQL
```

Using the same CloudFront domain for both frontend and API requests allows the React application to continue using relative API paths such as:

```javascript
fetch("/api/products")
```

This avoids browser mixed-content problems and simplifies CORS configuration.

## EC2 Security Group for CloudFront

The EC2 security group allows port `8080` from the AWS-managed CloudFront origin-facing prefix list.

Example:

```text
Type: Custom TCP
Port: 8080
Source: com.amazonaws.global.cloudfront.origin-facing
```

This is preferable to allowing port `8080` from the entire internet.

During deployment testing, access from the developer's current IP may also be temporarily allowed.

## React SPA Routing Problem

React Router uses client-side routes such as:

```text
/shop
/shop/products
/shop/cart
/shop/orders
```

When navigating inside the application, React handles these routes.

However, directly refreshing a route such as:

```text
/shop/products
```

causes CloudFront to request `/shop/products` from S3.

Because S3 contains only static build files and does not contain an object named `/shop/products`, the request can return an S3 `AccessDenied` or `404` response.

## CloudFront Function for SPA Routing

A CloudFront Function named:

```text
ecommerce-spa-router
```

was created to rewrite React routes to `/index.html`.

Example function:

```javascript
function handler(event) {
    var request = event.request;
    var uri = request.uri;

    if (uri.startsWith('/api/')) {
        return request;
    }

    if (uri.includes('.')) {
        return request;
    }

    request.uri = '/index.html';

    return request;
}
```

The function is associated with:

```text
Default (*) behavior
Event type: Viewer request
```

It is not associated with the `/api/*` behavior.

## SPA Rewrite Logic

Requests without file extensions are treated as React routes.

Examples:

```text
/shop
/shop/products
/shop/cart
/shop/orders
```

These are internally rewritten to:

```text
/index.html
```

Static assets remain unchanged:

```text
/assets/index-xxxxx.js
/assets/index-xxxxx.css
/favicon.svg
/icons.svg
```

API requests also remain unchanged:

```text
/api/products
/api/orders
/api/customers
```

## Final CloudFront Architecture

```text
                   Browser
                      |
                      | HTTPS
                      v
                 CloudFront
                  /       \
                 /         \
                /           \
        Default (*)        /api/*
             |                |
             v                v
        Private S3         EC2 :8080
             |                |
             v                v
           React          Spring Boot
                              |
                              v
                           RDS MySQL
```

## Deployment Verification

Frontend:

```text
https://<cloudfront-domain>/
```

React route:

```text
https://<cloudfront-domain>/shop/products
```

API:

```text
https://<cloudfront-domain>/api/products
```

The React route should continue working even after refreshing the browser.

The API should return JSON from the Spring Boot backend.

## Updating the Frontend

After modifying React code:

```bash
npm run build
```

Upload the new `dist/` contents to the same S3 bucket.

Because CloudFront may cache previous static files, a CloudFront invalidation can be created when necessary.

Example invalidation path:

```text
/*
```

For larger production systems, cache invalidation strategies and versioned static assets should be used carefully to control cost and performance.

## Security Notes

- S3 public access remains blocked.
- CloudFront accesses S3 through Origin Access Control.
- Browser traffic uses HTTPS.
- API traffic reaches the backend through CloudFront.
- EC2 port `8080` is restricted to CloudFront origin-facing infrastructure.
- RDS remains private and is never exposed through CloudFront.

## Result

The frontend deployment now provides:

- HTTPS access through CloudFront
- private S3 hosting
- React SPA route support
- `/api/*` routing to Spring Boot
- reduced direct exposure of the EC2 backend
- one public application entry point for both frontend and API traffic
