from django.db import connection


def execute_query(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        data = cursor.fetchall()
    return data


def execute_query_with_description(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        data = cursor.fetchall()
        desc = cursor.description
        desc_result = [col[0] for col in desc]
    return {"data": data, "desc": desc_result}
