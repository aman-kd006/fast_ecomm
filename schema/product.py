from pydantic import (
    BaseModel,
    Field,
    AnyUrl,
    EmailStr,
    field_validator,
    model_validator,
    computed_field    
)
from uuid import UUID
from typing import List, Optional, Annotated, Literal
from datetime import datetime


class Seller(BaseModel):
    seller_id: UUID
    name: Annotated[str, Field(
        ...,
        min_length=1,
        max_length=50,
        description="The name of the seller"
    )]
    email: EmailStr
    website: AnyUrl

    @field_validator("email", mode = "after")
    @classmethod
    def validate_seller_email_domain(cls, value: EmailStr):
        allowed_domains = {
            "example.com", 
            "shop.com", 
            "dellexclusive.in"
            "ecommerce.com", 
            "mistore.in", 
            "realmeofficial.in", 
            "applestoreindia.in", 
            "samsungshop.in", 
            "oneplusstore.in", 
            "nokiaofficial.in", 
            "lgshop.in", 
            "sonyofficial.in", 
            "htcofficial.in",
            "motorolaofficial.in",
            "asusofficial.in",
            "dellstore.in",
            "hpstore.in",
            "lenovostore.in", 
            "acerstore.in",
            "microsoftstore.in",
            "xiaomiofficial.in",
            "realme.com",
            "apple.com",
            "samsung.com",
            "oneplus.com",
            "nokia.com",
            }
        domain = value.split("@")[-1]
        if domain not in allowed_domains:
            raise ValueError(f"Email domain '{domain}' is not allowed for sellers.")
        return value

class Dimensions_cm(BaseModel):
    length: Annotated[float, Field(
        ...,
        ge=0,
        description="The length of the product in centimeters"
    )]
    width: Annotated[float, Field(
        ...,
        ge=0,
        description="The width of the product in centimeters"
    )]
    height: Annotated[float, Field(
        ...,
        ge=0,
        description="The height of the product in centimeters"
    )]

class Product(BaseModel):
    id: UUID
    sku: Annotated[str, Field(
        ...,
        min_length=8,
        max_length=20,
        title="Stock Keeping Unit",
        description="A unique identifier for the product",
        examples=["SKU12345678", "PROD-0001"]
    )]
    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="The name of the product",
        examples=["Wireless Mouse", "Gaming Keyboard"]
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="The description of the product"
    )
    category: str = Field(
        ...,
        min_length=1,
        max_length=30,
        description="The category of the product"
    )
    brand: Optional[str] = Field(
        None,
        max_length=30,
        description="The brand of the product"
    )
    price: float = Field(
        ...,
        ge=0,
        description="The price of the product"
    )
    currency: Annotated[Literal["USD", "EUR", "INR", "GBP"], Field(
        ...,
        description="The currency of the product price",
        examples=["USD", "EUR", "INR", "GBP"]
    )]
    discount_percent: float = Field(
        None,
        ge=0,
        description="The discount percentage of the product(in %)"
    )
    stock: Annotated[int, Field(
        ...,
        ge=0,
        description="The available stock of the product"
    )]
    is_active: Annotated[bool, Field(
        default=True,
        description="Indicates if the product is active"
    )]
    rating: Annotated[Optional[float], Field(
        None,
        ge=0,
        le=5,
        description="The average rating of the product"
    )]
    tags: Optional[List[str]] = Field(
        None,
        description="A list of tags associated with the product"
    )
    image_url: Optional[AnyUrl] = Field(
        None,
        description="The URL of the product image"
    )
    dimensions_cm: Dimensions_cm
    seller: Seller
    created_at: datetime = Field(
        default_factory=datetime,
        description="The creation timestamp of the product"
    )

    @field_validator("tags", mode="before")
    @classmethod
    def split_tags(cls, v):
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(",")]
        return v
    
    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, v):
        if isinstance(v, str):
            try:
                return UUID(v)
            except ValueError:
                raise ValueError("Invalid UUID format")
        return v

    @model_validator(mode="after")
    def check_discount(self):
        if self.discount_percent is not None:
            if not (0 <= self.discount_percent <= 100):
                raise ValueError("discount_percent must be between 0 and 100")
        return self
        
    
    @computed_field
    @property
    def discounted_price(self) -> Optional[float]:
        if self.discount_percent is not None:
            discount_amount = (self.discount_percent / 100) * self.price
            return round(self.price - discount_amount, 2)
        return None
    
    @computed_field
    @property
    def volume_cm3(self) -> float:
        return round(
            self.dimensions_cm.length *
            self.dimensions_cm.width *
            self.dimensions_cm.height, 2
        )
    

class UpdateSeller(BaseModel):
    seller_id: Optional[UUID]
    name: Optional[str]= Field(
        ...,
        min_length=1,
        max_length=50,
        description="The name of the seller"
    )
    email: Optional[EmailStr]
    website: Optional[AnyUrl]

    @field_validator("email", mode = "after")
    @classmethod
    def validate_seller_email_domain(cls, value: EmailStr):
        allowed_domains = {
            "example.com", 
            "shop.com", 
            "dellexclusive.in"
            "ecommerce.com", 
            "mistore.in", 
            "realmeofficial.in", 
            "applestoreindia.in", 
            "samsungshop.in", 
            "oneplusstore.in", 
            "nokiaofficial.in", 
            "lgshop.in", 
            "sonyofficial.in", 
            "htcofficial.in",
            "motorolaofficial.in",
            "asusofficial.in",
            "dellstore.in",
            "hpstore.in",
            "lenovostore.in", 
            "acerstore.in",
            "microsoftstore.in",
            "xiaomiofficial.in",
            "realme.com",
            "apple.com",
            "samsung.com",
            "oneplus.com",
            "nokia.com",
            }
        domain = value.split("@")[-1]
        if domain not in allowed_domains:
            raise ValueError(f"Email domain '{domain}' is not allowed for sellers.")
        return value
    
class Update_Dimensions_cm(BaseModel):
    length: Optional[float] = Field(
        ...,
        ge=0,
        description="The length of the product in centimeters"
    )
    width: Optional[float]=Field(
        ...,
        ge=0,
        description="The width of the product in centimeters"
    )
    height: Optional[float]= Field(
        ...,
        ge=0,
        description="The height of the product in centimeters"
    )

class Update_Product(BaseModel):
    id: UUID
    # sku: Annotated[Optional[str], Field(
    #     ...,
    #     min_length=8,
    #     max_length=20,
    #     title="Stock Keeping Unit",
    #     description="A unique identifier for the product",
    #     examples=["SKU12345678", "PROD-0001"]
    # )]
    name: Optional[str] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="The name of the product",
        examples=["Wireless Mouse", "Gaming Keyboard"]
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="The description of the product"
    )
    category: Optional[str] = Field(
        ...,
        min_length=1,
        max_length=30,
        description="The category of the product"
    )
    brand: Optional[str] = Field(
        None,
        max_length=30,
        description="The brand of the product"
    )
    price: Optional[float] = Field(
        ...,
        ge=0,
        description="The price of the product"
    )
    currency: Annotated[Optional[Literal["USD", "EUR", "INR", "GBP"]], Field(
        ...,
        description="The currency of the product price",
        examples=["USD", "EUR", "INR", "GBP"]
    )]
    discount_percent: Optional[float] = Field(
        None,
        ge=0,
        description="The discount percentage of the product(in %)"
    )
    stock: Annotated[Optional[int], Field(
        ...,
        ge=0,
        description="The available stock of the product"
    )]
    is_active: Annotated[Optional[bool], Field(
        default=True,
        description="Indicates if the product is active"
    )]
    rating: Annotated[Optional[float], Field(
        None,
        ge=0,
        le=5,
        description="The average rating of the product"
    )]
    tags: Optional[List[str]] = Field(
        None,
        description="A list of tags associated with the product"
    )
    image_url: Optional[AnyUrl] = Field(
        None,
        description="The URL of the product image"
    )
    dimensions_cm: Optional[Dimensions_cm]
    seller: Optional[Seller]
    created_at: Optional[datetime] = Field(
        default_factory=datetime,
        description="The creation timestamp of the product"
    )

    @field_validator("tags", mode="before")
    @classmethod
    def split_tags(cls, v):
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(",")]
        return v
    
    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, v):
        if isinstance(v, str):
            try:
                return UUID(v)
            except ValueError:
                raise ValueError("Invalid UUID format")
        return v

    @model_validator(mode="after")
    def check_discount(self):
        if self.discount_percent is not None:
            if not (0 <= self.discount_percent <= 100):
                raise ValueError("discount_percent must be between 0 and 100")
        return self
        
    
    @computed_field
    @property
    def discounted_price(self) -> Optional[float]:
        if self.discount_percent is not None:
            discount_amount = (self.discount_percent / 100) * self.price
            return round(self.price - discount_amount, 2)
        return None
    
    @computed_field
    @property
    def volume_cm3(self) -> float:
        return round(
            self.dimensions_cm.length *
            self.dimensions_cm.width *
            self.dimensions_cm.height, 2
        )


class ProductListResponse(BaseModel):
    total: int = Field(
        ...,
        ge=0,
        description="The total number of products matching the query"
    )
    items: List[dict] = Field(
        ...,
        description="List of products"
    )
