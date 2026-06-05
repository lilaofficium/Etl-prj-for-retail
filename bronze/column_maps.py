
import pandas as pd
from utils.logger import get_logger

logger = get_logger("column_maps")

def rename_column_map(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    col_map = COLUMN_MAPS.get(source_name)

    if not col_map:
        raise ValueError(f"No column mapping found for source: {source_name}")
 
    available_cols = [col for col in col_map if col in df.columns]
 
    df = df[available_cols].rename(columns=col_map)

    return df



COLUMN_MAPS = {

    "fakestore_products": { 
        "id"             : "product_id",
        "title"          : "title",
        "price"          : "price",
        "description"    : "description",
        "category"       : "category",
        "image"          : "image_url",
        "rating"         : "rating", 
        "_source"        : "_source",
        "_ingested_at"   : "_ingested_at",
        "_pipeline_run"  : "_pipeline_run",
    },

    "dummyjson_products": {
        "id"                   : "product_id",
        "title"                : "title",
        "description"          : "description",
        "category"             : "category",
        "price"                : "price",
        "discountPercentage"   : "discount_percentage",  
        "rating"               : "rating",
        "stock"                : "stock",
        "brand"                : "brand",
        "sku"                  : "sku",
        "weight"               : "weight",
        "dimensions"           : "dimensions",
        "warrantyInformation"  : "warranty_information",
        "shippingInformation"  : "shipping_information",
        "availabilityStatus"   : "availability_status",
        "returnPolicy"         : "return_policy",
        "minimumOrderQuantity" : "minimum_order_quantity",
        "thumbnail"            : "thumbnail_url",
        "images"               : "images",
        "tags"                 : "tags",
        "reviews"              : "reviews",
        "meta"                 : "meta",
        "_source"              : "_source",
        "_ingested_at"         : "_ingested_at",
        "_pipeline_run"        : "_pipeline_run",
    },

    "dummyjson_users": {
        "id"          : "user_id",
        "firstName"   : "first_name",      
        "lastName"    : "last_name",
        "maidenName"  : "maiden_name",
        "age"         : "age",
        "gender"      : "gender",
        "email"       : "email",
        "phone"       : "phone",
        "username"    : "username",
        "password"    : "password",
        "birthDate"   : "birth_date",
        "image"       : "image_url",
        "bloodGroup"  : "blood_group",
        "height"      : "height",
        "weight"      : "weight",
        "eyeColor"    : "eye_color",
        "hair"        : "hair",
        "ip"          : "ip_address",
        "address"     : "address",
        "macAddress"  : "mac_address",
        "university"  : "university",
        "bank"        : "bank",
        "company"     : "company",
        "ein"         : "ein",
        "ssn"         : "ssn",
        "userAgent"   : "user_agent",
        "crypto"      : "crypto",
        "role"        : "role",
        "_source"     : "_source",
        "_ingested_at": "_ingested_at",
        "_pipeline_run": "_pipeline_run",
    },

    "dummyjson_carts": {
        "id"               : "cart_id",
        "userId"           : "user_id",    
        "products"         : "products",
        "total"            : "total",
        "discountedTotal"  : "discounted_total",
        "totalQuantity"    : "total_quantity",
        "_source"          : "_source",
        "_ingested_at"     : "_ingested_at",
        "_pipeline_run"    : "_pipeline_run",
    },

    "jsonplaceholder_posts": {
        "id"           : "post_id",
        "userId"       : "user_id",
        "title"        : "title",
        "body"         : "body",
        "_source"      : "_source",
        "_ingested_at" : "_ingested_at",
        "_pipeline_run": "_pipeline_run",
    },
}