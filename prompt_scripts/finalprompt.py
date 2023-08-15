def prompt(category, plan_type, plan_timing, location, number_of_people,budget):

    str=f"You are a {category} planner, guiding me through the process of planning a {category}.You should provide consistent and reliable advice and suggestions every time I make a request.\n\n I have {plan_type} marriage going on.List down the events for a basic one having budget of {budget}.Assign each event a key and also plan the best optimized budget for each events.give me the response in json having following format"
    print(str)

# store every record for passing it to db
category = input("Enter the category of event: ")
plan_type = input("Enter the plan type: ")
plan_timing = input("Enter the plan timing: ")
location = input("Enter the location: ")
number_of_people = input("Enter the number of people: ")
budget = input("Enter your budget: ")
# if needed store the prompt or directly throw the prompt
event_output = prompt(category, plan_type, plan_timing, location, number_of_people,budget)
print(event_output)

# category can be wedding , birthday etc.
# For wedding the plan type can be indian/american/greek etc
# For birthday the type can be indoor/outdoor/theme_based etc/
