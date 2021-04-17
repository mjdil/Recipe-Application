import json
import argparse
import mysql.connector
import random
import config

def createUser(req):
  authenticate()
  data = req["payload"]
  newUserID = random.randint(100000,99999999)
  createUser = "INSERT INTO User (user_id, username, password) Values ('{}', '{}', '{}')".format(newUserID,userName, passWord)
  cursorObject.execute(createUser)
  ret = {"user_id": newUserID}
  print(json.dumps(ret, indent=4))
  dataBase.commit()

def createRecipe(req):
  authenticate()
  if not userID:
    print(json.dumps({"error": "invalid authentification!"}, indent=4))
    return
  add_recipe = """
  INSERT INTO Recipe 
  (recipe_name, cook_time, user_id, description, calories, fat, sugar, sodium, protein, saturated_fat, carbohydrates)
  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
  """

  data = req["payload"]

  data_recipe = (data["recipe_name"], 
  data["cook_time"], 
  userID, 
  data["description"], 
  data["calories"], 
  data["fat"], 
  data["sugar"], 
  data["sodium"], 
  data["protein"], 
  data["saturated_fat"], 
  data["carbohydrates"])

  cursorObject.execute(add_recipe, data_recipe)
  dataBase.commit()

  recipeID = cursorObject.lastrowid

  for ingredient in data["ingredients"]:
    searchIngredient = "SELECT * FROM Ingredient WHERE ingredient_name='{}'".format(ingredient)
    cursorObject.execute(searchIngredient)
    res = cursorObject.fetchall()
    if len(res) == 0:
      insertIngredient = "INSERT INTO Ingredient (ingredient_name) VALUES ('{}')".format(ingredient)
      cursorObject.execute(insertIngredient)
      dataBase.commit()
    insertRecipeIngredient = "INSERT INTO RecipeIngredient (recipe_id, ingredient_name) VALUES ('{}', '{}')".format(recipeID, ingredient)
    cursorObject.execute(insertRecipeIngredient)
    dataBase.commit()
  
  for i in range(len(data["instructions"])):
    instruction = data["instructions"][i]
    insertInstruction = "INSERT INTO Instruction (recipe_id, step, instruction) VALUES ('{}', '{}', '{}')".format(recipeID, i+1, instruction)
    cursorObject.execute(insertInstruction)


  insertPhoto = "INSERT INTO Photo (recipe_id, photo_URL) VALUES ('{}', '{}')".format(recipeID, data["photo"])
  cursorObject.execute(insertPhoto)

  print(json.dumps({"status": "success","recipe_id": recipeID}, indent=4))
  dataBase.commit()

def getRecipe(req):
  data = req["payload"]
  getRecipe = ""
  for field in data:
    if field == "ingredients" or field == "rating": 
      continue 
    if isinstance(data[field], str):
      getRecipe += "Recipe."+field + "=" + "\"" + data[field] + "\"" + " AND "
    else:
      getRecipe += "Recipe."+field + "=" + str(data[field]) + " AND "
  if len(getRecipe)>4:
    getRecipe = getRecipe[:-4]

  if "ingredients" in data:
    if getRecipe != "":
      getRecipe+="AND "
    getRecipe+="("
    for ing in data["ingredients"]:
      getRecipe += "RecipeIngredient.ingredient_name="+ "\"" + ing + "\"" + " OR "
    getRecipe = getRecipe[:-4]
    getRecipe+=")"


  if "rating" in data:
    if getRecipe != "":
      getRecipe+="AND "
    getRecipe += "Review.rating="+ str(data["rating"])

  getRecipe = "SELECT DISTINCT Recipe.recipe_id FROM Recipe LEFT JOIN RecipeIngredient ON Recipe.recipe_id = RecipeIngredient.recipe_id LEFT JOIN Review ON Review.recipe_id = Recipe.recipe_id WHERE " + getRecipe
  cursorObject.execute(getRecipe)
  ret = []

  res = cursorObject.fetchall()

  for rec in res:
    query = "Select * From Recipe Where recipe_id="+str(rec["recipe_id"])
    cursorObject.execute(query)
    ret.append(cursorObject.fetchone())

  print(json.dumps(ret, indent=4, default=str))
  
  
def updateRecipe(req):
  authenticate()
  data = req["payload"]
  recipeID = data["recipe_id"]
  del(data["recipe_id"])
  query = "Select * From Recipe Where recipe_id="+str(recipeID)
  cursorObject.execute(query)
  recipe = cursorObject.fetchone()
  if recipe["user_id"] != userID and not isAdmin:
    print(json.dumps({"error": "You cannot update someone elses recipe!"}, indent=4))
    return

  updateRecipe = ""
  for field in data:
    if isinstance(data[field], str):
      updateRecipe += field + "=" + "\"" + data[field] + "\"" + ", "
    else:
      updateRecipe += field + "=" + str(data[field]) + ", "
  updateRecipe = updateRecipe[:-2]
  updateRecipe = "UPDATE Recipe SET " + updateRecipe + " WHERE recipe_id=" + str(recipeID)
  cursorObject.execute(updateRecipe)
  dataBase.commit()
  print(json.dumps({"status": "success"}, indent=4))


def deleteRecipe(req):
  authenticate()
  data = req["payload"]
  if isAdmin:
    deleteRecipe = "DELETE FROM Recipe WHERE recipe_id = '{}'".format(data["recipe_id"])
  else:
    deleteRecipe = "DELETE FROM Recipe WHERE recipe_id = '{}' AND user_id = '{}'".format(data["recipe_id"], userID)
  cursorObject.execute(deleteRecipe)
  dataBase.commit()

  if (cursorObject.rowcount == 0):
    print(json.dumps({"message": "Could not delete Recipe"}, indent=4))
    return 
  print(json.dumps({"status": "success"}, indent=4))


def createIngredient(req):
  authenticate()
  data = req["payload"]
  addIngredient = "INSERT INTO Ingredient (ingredient_name) VALUES ('{}')".format(data["ingredient_name"])
  cursorObject.execute(addIngredient)
  dataBase.commit()
  print(json.dumps({"status": "success"}, indent=4))

def getIngredient(req):
  data = req["payload"]
  getIng = "SELECT ingredient_name FROM Ingredient WHERE ingredient_name = '{}'".format(data["ingredient_name"])
  cursorObject.execute(getIng)
  res = cursorObject.fetchone()
  if res == None:
    print(json.dumps({"error": "Could not find Ingredient"}, indent=4))
  else:  
    print(json.dumps(res, indent=4))

def deleteIngredient(req):
  authenticate()
  if not isAdmin:
    print(json.dumps({"error": "You must be an admin to delete an ingredient!"}, indent=4))
    return
  data = req["payload"]
  deleteIng = "DELETE FROM Ingredient WHERE ingredient_name = '{}'".format(data["ingredient_name"])
  cursorObject.execute(deleteIng)
  dataBase.commit()
  print(json.dumps({"status": "success"}, indent=4))

def createReview(req):
  authenticate()
  if not userID:
    print(json.dumps({"error": "invalid authentification!"}, indent=4))
    return

  data = req["payload"]
  createReview  = "INSERT INTO Review (recipe_id, user_id, rating, comment) VALUES ('{}', '{}', '{}', '{}')".format(data["recipe_id"], 
  userID, data["rating"], data["comment"])
  cursorObject.execute(createReview)
  dataBase.commit()
  print(json.dumps({"status": "success"}, indent=4))


def getReview(req):
  data = req["payload"]
  getReviews = "SELECT * FROM Review WHERE recipe_id = '{}'".format(data["recipe_id"])
  cursorObject.execute(getReviews)
  res = cursorObject.fetchall()
  if len(res) == 0:
    print(json.dumps({"message": "There are no reviews for this recipe"}, indent=4, default=str))
  else:
    print(json.dumps(res, indent=4, default=str))
  



def updateReview(req):
  authenticate()
  data = req["payload"]
  recipeID = data["recipe_id"]
  del(data["recipe_id"])

  updateReview = ""
  for field in data:
    if isinstance(data[field], str):
      updateReview += field + "=" + "\"" + data[field] + "\"" + ", "
    else:
      updateReview += field + "=" + str(data[field]) + ", "
  updateReview = updateReview[:-2]
  if "user_id" in data: 
    if isAdmin:
      updateReview = "UPDATE Review SET " + updateReview + " WHERE recipe_id=" + str(recipeID) + " AND user_id=" + str(data["user_id"])
    else:
      if data["user_id"] != userID:
        print(json.dumps({"error": "You cannot update someone elses review!"}, indent=4))
        return
  else:
    updateReview = "UPDATE Review SET " + updateReview + " WHERE recipe_id=" + str(recipeID) + " AND user_id=" + str(userID)
  cursorObject.execute(updateReview)
  dataBase.commit()
  print(json.dumps({"status": "success!"}, indent=4))
  return 

def deleteReview(req):
  authenticate()
  data = req["payload"]
  if "user_id" in data:
    if isAdmin:
      deleteRev = "DELETE FROM Review WHERE recipe_id = '{}' AND user_id = '{}'".format(data["recipe_id"], data["user_id"])
    else:
      if data["user_id"] != userID:
        print(json.dumps({"error": "You cannot delete someone elses review!"}, indent=4))
        return
  else:
    deleteRev = "DELETE FROM Review WHERE recipe_id = '{}' AND user_id = '{}'".format(data["recipe_id"], userID)
  cursorObject.execute(deleteRev)
  print(json.dumps({"status": "success!"}, indent=4))
  dataBase.commit()

def authenticate():
  global userID
  global isAdmin
  global userName
  global passWord
  userName = input("Enter your username : ")
  passWord = input("Enter your password : ")
  getUser = "SELECT * FROM User WHERE username = '{}' AND password = '{}'".format(userName, passWord)
  cursorObject.execute(getUser)
  res = cursorObject.fetchone()
  if res:
    userID = res["user_id"]
    isAdmin = res["is_admin"]
    return True
  return False


def requestMux(req):
  command = req["request"]
  if command == "create_recipe":
    try:
      createRecipe(req)
    except:
      print({"error": "Failed to create Recipe"})
  elif command == "get_recipe":
    try:
      getRecipe(req)
    except:
      print({"error": "Failed to get Recipe"})
  elif command == "update_recipe":
    try:
      updateRecipe(req)
    except:
      print({"error": "Failed to update Recipe"})
  elif command == "delete_recipe":
    try:
      deleteRecipe(req)
    except:
      print({"error": "Failed to delete Recipe"})
  elif command == "create_ingredient":
    try:
      createIngredient(req)
    except:
      print({"error": "Failed to add Ingredient"})
  elif command == "get_ingredient":
    try:
      getIngredient(req)
    except:
      print({"error": "Failed to get Ingredient"})
  elif command == "delete_ingredient":
    try:
      deleteIngredient(req)
    except:
      print({"error": "Failed to delete Ingredient"})
  elif command == "create_review":
    try:
      createReview(req)
    except:
      print({"error": "Failed to create Review"})
  elif command == "get_review":
    try:
      getReview(req)
    except:
      print({"error": "Failed to get Review"})
  elif command == "update_review":
    try:
      updateReview(req)
    except:
      print({"error": "Failed to update Review"})
  elif command == "delete_review":
    try:
      deleteReview(req)
    except:
      print({"error": "Failed to delete Review"})
  elif command == "create_user":
    try:
      createUser(req)
    except:
      print({"error": "Failed to create User"})


dataBase = mysql.connector.connect(
  host =config.host,
  user =config.user,
  passwd =config.passwd,
  database =config.database
)
 
# preparing a cursor object
cursorObject = dataBase.cursor(dictionary=True)
parser = argparse.ArgumentParser()
parser.add_argument('--infile', nargs=1,
                    help="JSON file to be processed",
                    type=argparse.FileType('r'))
arguments = parser.parse_args()

# Loading a JSON object returns a dict.
d = json.load(arguments.infile[0])

userName = ""
passWord = ""
userID, isAdmin = None, None

requestMux(d)

dataBase.close()
