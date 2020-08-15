import googlemaps


with open("google_maps_key.txt", "r") as fkey:
    key = fkey.read()
gmaps = googlemaps.Client(key)


def output_interest(message, latitude, longitude, bot):
    json_places = get_places_info(latitude, longitude)
    right_limit = len(json_places["latitude"]) if len(json_places["latitude"]) != 10 else 10
    for number in range(right_limit):
        text = "{}. {}".format(number + 1, json_places["name"][number])
        bot.send_message(chat_id=message.chat.id, text=text)
        bot.send_location(
            chat_id=message.chat.id,
            latitude=json_places["latitude"][number],
            longitude=json_places["longitude"][number]
        )


def get_places_info(lat, lng):
    json_all = places_nearby(lat, lng)
    json_res = {"name": [], "latitude": [], "longitude": [], "photo": []}
    count = 0
    for place in json_all:
        if 'point_of_interest' in place["types"]:
            json_res["name"].append(place["name"])
            json_res["latitude"].append(float(place["geometry"]["location"]["lat"]))
            json_res["longitude"].append(float(place["geometry"]["location"]["lng"]))
            count += 1
        if count == 10:
            break
    return json_res


def places_nearby(lat, lng):
    return places_request(lat, lng)["results"]


def places_request(latitude, longitude, radius=100):
    result = gmaps.places_nearby(location=(latitude, longitude), language="ru", radius=radius)
    return result
