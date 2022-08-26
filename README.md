# Fashion Forecast
This repository is only for the backend component of the project.
## What this app does:
By inputting the clothes you have in your closet, this app is able to automatically generate an outfit for the day based on the weather of the day.

## What this repository does in the app:
I implemented routes that get the weather, clothes associated with the user, and basic user information. Users have the location attribute to specify the location of the user using zip code. I also implemented a POST route that allowed the user to upload their information, post the clothes to their information, and the photos of the clothes. For the clothes, it has the warmth attribute to gauge how warm each clothes are and the type of clothing attribute to categorize it into a top, bottom, jacket, or shoes. In order to get the information for the weather, I used the OpenWeather API to select the clothes based on the temperature of the location. I implemented a route that selects the clothes that match the temperature of the person’s location.

#### GET /
##### Response:
```
{
   "success": true,
   "data": {
       "coord": {
           "lon": -76.4837,
           "lat": 42.4474
       },
       "weather": [
           {
               "id": 803,
               "main": "Clouds",
               "description": "broken clouds",
               "icon": "04d"
           }
       ],
       "base": "stations",
       "main": {
           "temp": 1.87,
           "feels_like": 1.87,
           "temp_min": -0.58,
           "temp_max": 3.89,
           "pressure": 960,
           "humidity": 69
       },
       "visibility": 10000,
       "wind": {
           "speed": 0.89,
           "deg": 305,
           "gust": 1.79
       },
       "clouds": {
           "all": 75
       },
       "dt": 1638558880,
       "sys": {
           "type": 2,
           "id": 2012568,
           "country": "US",
           "sunrise": 1638533898,
           "sunset": 1638567228
       },
       "timezone": -18000,
       "id": 0,
       "name": "Ithaca",
       "cod": 200
   }
}
```

#### POST /user/
##### Request:
```
{
   "name": "Yuki Suwabe",
   "location": "14853"
}
```
##### Response:
```
{
   "success": true,
   "data": {
       "id": <ID>,
       "name": "Yuki Suwabe", 
       "location": "14853",
       "clothings": []
   }
}
```
#### GET /user/{user_id}
##### Response:
```
{
   "success": true,
   "data": {
       "id": <ID>,
       "name": <STORED NAME FOR USER {user_id}>,
       "location": <STORED ZIP CODE FOR USE {user_id}>,
       "clothings": [<SERIALIZED CLOTHING FOR USER {user_id}>]
   }
}
```
#### POST /{user_id}/clothing/
##### Request:
```
{
   "name": "Tennis Skirt",
   "warmth": 2,
   "typeOfClothes": "top" or “bottom” or “jacket” or “shoes”
}
```
##### Response:
```
{
   "success": true,
   "data": {
       "id": <ID>,
       "name": "Tennis Skirt",
       "warmth": 2,
       "typeOfClothes": "bottom",
       "users": {
           "id": <user_id>,
           "name": <STORED NAME FOR USER {user_id}>,
           "location": <STORED ZIP CODE FOR USER {user_id}>
       },
       "pictures": []
   }
}
```
#### POST /{clothing_id}/picture/
##### Request:
```
{
   "image_data": "<base64 form of image>"
}
```
###### Response:
```
{
   "success": true,
   "data": {
       "url": "https://fashionforecast.s3-us-east-2.amazonaws.com/OXJTKUUDWZWLSS8T.png",
       "description": {
           "id": <clothing_id>,
           "name": "<NAME OF CLOTHING {clothing_id}>,
           "warmth": <WARMTH LEVEL OF CLOTHING {clothing_id}>,
           "typeOfClothes": <CLOTHING TYPE OF CLOTHING{clothing_id}>
       }
   }
}
```
#### GET /{user_id}/clothing/
##### Response:
```
{
   "success": true,
   "data": {
       "clothes": [
           {
               "id": <ID>,
               "name": <STORED NAME OF CLOTHING {ID}>,
               "warmth": <STORED WARMTH LEVEL OF CLOTHING {ID}>,
               "typeOfClothes": <STORED TYPE OF CLOTHING CLOTHING {ID}>,
               "users": {
                   "id": <user_id>,
                   "name": <STORED NAME OF USER {user_id},
                   "location": <STORED ZIP CODE OF USER {user_id}>
               },
               "pictures": [
                   {
                       "url": <STORED URL OF PICTURES OF CLOTHING {ID}>
                   }
               ]
           }
       ]
   }
}
```
#### GET /{user_id}/weather/
##### Response:
```
{
   "success": true,
   "data": {
       "coord": {
           "lon": -76.4837,
           "lat": 42.4474
       },
       "weather": [
           {
               "id": 804,
               "main": "Clouds",
               "description": "overcast clouds",
               "icon": "04n"
           }
       ],
       "base": "stations",
       "main": {
           "temp": 5.04,
           "feels_like": 5.04,
           "temp_min": 4.06,
           "temp_max": 6.2,
           "pressure": 948,
           "humidity": 88
       },
       "visibility": 10000,
       "wind": {
           "speed": 0.45,
           "deg": 306,
           "gust": 1.79
       },
       "clouds": {
           "all": 90
       },
       "dt": 1638495108,
       "sys": {
           "type": 2,
           "id": 2012568,
           "country": "US",
           "sunrise": 1638447436,
           "sunset": 1638480843
       },
       "timezone": -18000,
       "id": 0,
       "name": "Ithaca",
       "cod": 200
   }
}
```

#### GET /{user_id}/{typeOfClothes}/select/
##### Response:
```
{
   "success": true,
   "data": {
       "id": <CLOTHING ID THAT WAS SELECTED>,
       "name": <NAME OF CLOTHING SELECTED>,
       "warmth": <WARMTH OF CLOTHING SELECTED>,
       "typeOfClothes": <TYPE OF CLOTHING SELECTED>,
       "users": {
           "id": <user_id>,
           "name": <NAME OF USER {user_id}>,
           "location": <ZIP CODE OF USER {user_id}>
       },
       "pictures": [<PICTURE OF THE CLOTHING SELECTED>]
   }
}
```
