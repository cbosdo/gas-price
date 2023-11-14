# Building

```
cd api
go build

cd ../fetchers/fr
go build
```

# How to use


Run the following command in a daily cron job:

```
./fetchers/fr/fr data
```

Serve the API on port 8080 by running:

```
./api/api ./data
```

The data can now be queried using requests like:

```
curl http://localhost:8080/node/2098288113
curl http://localhost:8080/way/134088260
```

The prices will be returned in a json format like:

```
{
  "id": "78114001",
  "prices": [
    {
      "name": "diesel",
      "value": 1.829,
      "update": "2023-11-13T05:43:19Z"
    },
    {
      "name": "octane_95",
      "value": 1.859,
      "update": "2023-11-13T05:43:20Z"
    },
    {
      "name": "e85",
      "value": 0.959,
      "update": "2023-11-13T05:43:20Z"
    },
    {
      "name": "e10",
      "value": 1.819,
      "update": "2023-11-13T05:43:20Z"
    },
    {
      "name": "octane_98",
      "value": 1.889,
      "update": "2023-11-13T05:43:20Z"
    }
  ]
}
```

# Things to do 
* Use redis / couchdb as a possible data backend
* Run on Kubernetes with deployment and cronjob
* Implement fetcher for Germany
