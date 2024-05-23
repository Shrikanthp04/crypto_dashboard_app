from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

class QueryToSQL(APIView):
    def post(self, request):
        try:
            print(request.data)
            data = request.data
            query = data["query"]
            sql_query, df = util.sk_query(query)

            response = {"sql": sql_query, "df": df.to_json()}
            return Response(response)
        except Exception as e:
            raise Exception("Somthing Went Wrong")