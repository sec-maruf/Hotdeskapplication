#solid.py
from solid.auth import Auth
from solid.solid_api import SolidAPI

def get_solid_api(idp, username, password):
    auth = Auth()
    api = SolidAPI(auth)
    try:
        auth.login(idp, username, password)
        print("Login successful to Solid POD at:", idp)  # Print success message
        return api
    except Exception as e:
        print("Failed to login to Solid POD at:", idp, "Error:", e)  # Print error message
        raise e  # Re-raise the exception to handle it further up the call stack