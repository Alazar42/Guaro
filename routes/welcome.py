from guaro import Router

router = Router()

@router.get("/")
def welcome_user():
    return {"message" : "Welcome to Guaro backend framework."}