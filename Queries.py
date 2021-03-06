import pprint

'''
Queries to run:
- Number of restaurants and fast food places
- Number of each type of fast food place
- Number of zipcodes
- List of top 5 top users
'''

def place_query():
    query = {"amenity" : "fast_food"}
    return query

def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db

def find_place(db, query):
    projection = {"id" : 1, "amenity" : 1, "name" : 1}
    place = db.Bellevue.find(query, projection)
    for p in place:
        pprint.pprint(p)


# Query 1: Finding the total number of fast food and restaurants
def food_count(db):
    fast_food_count = db.Bellevue.find({"amenity" : "fast_food"}).count()
    restaurant_count = db.Bellevue.find({"amenity" : "restaurant"}).count()
    total_count = fast_food_count + restaurant_count
    print "{} Total fast food establishments".format(fast_food_count)
    print "{} Total restaurants".format(restaurant_count)
    print "{} Total number of food establishments".format(total_count)

# Query 2: Finding the top 5 food establishments by number of locations
def food_analysis(db):
    result = db.Bellevue.aggregate([
                { "$match" : {"$or": [{"amenity" :"fast_food" }, {"amenity" : "restaurant"}]}},
                { "$group" : {"_id": "$name",
                              "count": {"$sum" : 1 }}},
                { "$sort" : {"count" : -1}},
                { "$limit" : 5}
            ])
    print "The top food establishments are:"
    pprint.pprint(list(result))


# Query 3: Finding the top 5 cuisines by number of establishments with that cuisine
def food_type_analysis(db):
    result = db.Bellevue.aggregate([
                { "$match" : {"$or": [{"amenity" :"fast_food" }, {"amenity" : "restaurant"}]}},
                { "$group" : {"_id": "$cuisine",
                              "count": {"$sum" : 1 }}},
                { "$sort" : {"count" : -1}},
                { "$limit" : 5}
            ])
    print "The top food cuisines are:"
    pprint.pprint(list(result))


# Query 4: Finding the number of zip codes in this map area
def zip_codes(db):
    result1 = db.Bellevue.distinct("tiger:zip_left")                    #zipcodes show up as 'tiger:' for ways and 'postcodes' for addresses
    result2 = db.Bellevue.distinct("tiger:zip_right")
    result3 = db.Bellevue.distinct("address.postcode")
    in_result1 = set(result1)
    in_result2 = set(result2)
    in_result3 = set(result3)
    in_second_but_not_in_first = in_result2 - in_result1
    in_third_but_not_in_others = in_result3 - in_second_but_not_in_first
    merged_result = result1 + list(in_second_but_not_in_first) + list(in_third_but_not_in_others)
    print "There are {} zip codes: ".format(len(merged_result))
    pprint.pprint(list(merged_result))


# Query 5: Finding the top 5 users by number of contributions
def top_user(db):
    user_result = db.Bellevue.aggregate([
        {"$match": {"created.user" : {"$exists" : True}}},
        {"$group" : {"_id":"$created.user",
                     "count": {"$sum" : 1}}},
        {"$sort" : {"count" : -1}},
        {"$limit" : 5}
    ])
    print "The top 5 contributors are:"
    pprint.pprint(list(user_result))


if __name__ == "__main__":
    db = get_db('project_2')
    query = place_query()
    count_of_food_establishments = food_count(db)
    top_food_establishments = food_analysis(db)
    top_cuisines = food_type_analysis(db)
    number_of_zipcodes = zip_codes(db)
    top_users =top_user(db)


