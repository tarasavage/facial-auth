from pydantic import BaseModel, ConfigDict


class CreateClient(BaseModel):
    domain: str
    login_redirect_url: str
    logout_redirect_url: str

    model_config = ConfigDict(from_attributes=True)


class ClientResponse(BaseModel):
    client_id: str
    domain: str
    login_redirect_url: str
    logout_redirect_url: str

    model_config = ConfigDict(from_attributes=True)
