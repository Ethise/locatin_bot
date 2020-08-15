import googlemaps


with open("google_maps_key.txt", "r") as fkey:
    key = fkey.read()
gmaps = googlemaps.Client(key)


def get_places(latitude, longitude, radius=200):
    result = gmaps.places_nearby(location=(latitude, longitude), language="ru", radius=radius)
    return result


def potential_location(latitude, longitude):
    places = get_places(latitude, longitude)["results"]
    places_int = []
    for place in places:
        if 'point_of_interest' in place["types"]:
            places_int.append(place)
        else:
            print(place["types"])
    return places_int


def places_nearby10(latitude, longitude):
    return potential_location(latitude, longitude)[:10]


def get_bot_info(latitude, longitude):
    json10 = places_nearby10(latitude, longitude)
    json_res = {"name": [], "latitude": [], "longitude": [], "photo": []}
    for place in json10:
        json_res["name"].append(place["name"])
        json_res["latitude"].append(float(place["geometry"]["location"]["lng"]))
        json_res["longitude"].append(float(place["geometry"]["location"]["lat"]))
        try:
            json_res["photo"].append(place["photos"][0]["photo_reference"])
        except KeyError:
            json_res["photo"].append("без фотографии")
    return json_res


def output_place_map(message, latitude, longitude, bot):
    json_places = get_bot_info(latitude, longitude)
    right_limit = len(json_places["latitude"]) if len(json_places["latitude"]) != 10 else 10
    for number in range(right_limit):
        text = "{}. {}".format(number + 1, json_places["name"][number])
        if json_places["photo"] != "без фотографии":
            #bot.send_photo(chat_id=message.chat.id, photo=json_places["photo"][number], caption=text)
            print("here")
        else:
            bot.send_message(chat_id=message.chat.id, text=text + "\nбез фотографии")
        bot.send_location(
            chat_id=message.chat.id,
            latitude=json_places["latitude"][number],
            longitude=json_places["longitude"][number]
        )


k = potential_location(49.431297, 32.050445)
print("_________________________________________-")
for i in k:
    print(i)
