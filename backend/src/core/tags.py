class Tags:
    DIRECT_AUTH = "direct-auth"
    CLIENT_AUTH = "client-auth"
    FACE_AUTH = "face-auth"
    HEALTH = "health"
    REGISTRATION = "registration"
    CLIENTS = "clients"


tags_metadata = [
    {"name": Tags.DIRECT_AUTH, "description": "Direct user authentication operations (signup, signin)"},
    {"name": Tags.CLIENT_AUTH, "description": "Client/non-direct user authentication operations"},
    {"name": Tags.FACE_AUTH, "description": "Face recognition and biometric authentication"},
    {"name": Tags.HEALTH, "description": "API health checking endpoints"},
    {"name": Tags.REGISTRATION, "description": "User registration operations"},
]
