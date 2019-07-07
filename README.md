# Meetup Flask API
---
This API implements two endpoints offering informtion extracted from the Meetup Long-Polling RSVP stream service. 

The information is locally stored by a listener (https://github.com/lorenamanita/listener-meetup) on a MariaDB RDMS databse running inside a container for simplicity of use.

This piece of software will run as a microservice, available on port 5000/TCP.

To invoke the different endpoints you must follow the instructionas below.

#### 1. Endpoints
---
The available end points for this API are the following:

* `/near`
* `/topCities`

#### `/near`
Given latitude, longitude, and N of a given location, this endpoint will return the N closest groups in distance [km]. The default query parameters are lat=0, lon=0, num=1.

Sample query:

http://<IP>:5000/near?lat=43&lon=-5&num=2

#### `/topCities`
Given a date in the ISO format (YYYYMMDD) return the top num cities sorted by the number of people attending the event on the given day. The defaulty query parameters are day=<today>, num=1.

Sample query:

http://<IP>:5000/topCities?day=20190708&num=4

#### 2. Functions
---
```python
1. near_groups()
```
Flask route for the `/near` endopoint.

`:param: none`
`:return: JSON string`

```python
2. top_cities()
```
Flask route for the `/topCities` endopoint.


`:param: none`
`:return: JSON string`



```python
3. get_near_groups(lat, lon, num)
```
This function will run the query to get the `num` closest items to the given location, compute the actual distance, and update the result as a sorted list of dicts.

`:param: (int) lat, lon, num`
`:return: list of dicts`

 valid ranges for latitude are [-90..90], and for longitude [180..-180].
 
```python
4. get_top_cities(date, num)
```
Run the query to collect data for the /near endpoint.

`:param: (int) lat, lon, num`
`:return: list of dicts`

