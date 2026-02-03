from fastapi import Response

async def remove_cookie(response: Response):
    response.delete_cookie("refresh_token")
    response.delete_cookie("access_token")
    return True