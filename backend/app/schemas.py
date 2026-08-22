from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2)
    email: str
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    name: str


class VehicleCreate(BaseModel):
    make: str
    model: str
    category: str
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)


class VehicleUpdate(VehicleCreate):
    pass


class RestockRequest(BaseModel):
    quantity: int = Field(gt=0)
