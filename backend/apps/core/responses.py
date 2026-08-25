from rest_framework.response import Response


def api_success(data=None, message="success"):
    return Response({"code": 0, "message": message, "data": data})


def api_error(message, code=400):
    return Response({"code": code, "message": message, "data": None}, status=400)

