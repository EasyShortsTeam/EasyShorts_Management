from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "EasyShorts Management Admin Backend"
    app_env: str = "dev"

    host: str = "0.0.0.0"
    port: int = 8000

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"

    # Accept either JWT_SECRET (this repo) or SECRET_KEY (EasyShorts_backend)
    jwt_secret: str = Field(default="change-me", validation_alias=AliasChoices("JWT_SECRET", "SECRET_KEY"))

    # EasyShorts_backend DB
    database_url: str = Field(
        default="mysql+pymysql://root:password@localhost:3306/video_generator?charset=utf8mb4",
        validation_alias=AliasChoices("EASYSHORTS_DATABASE_URL", "DATABASE_URL"),
    )

    # AWS (optional; if set, assets endpoints can operate on S3)
    aws_access_key_id: str | None = Field(default=None, validation_alias=AliasChoices("AWS_ACCESS_KEY_ID"))
    aws_secret_access_key: str | None = Field(default=None, validation_alias=AliasChoices("AWS_SECRET_ACCESS_KEY"))
    aws_region: str | None = Field(default=None, validation_alias=AliasChoices("AWS_REGION", "AWS_DEFAULT_REGION"))

    s3_fonts_bucket: str | None = Field(default=None, validation_alias=AliasChoices("S3_FONTS_BUCKET"))
    s3_soundeffects_bucket: str | None = Field(default=None, validation_alias=AliasChoices("S3_SOUNDEFFECTS_BUCKET"))
    s3_userassets_bucket: str | None = Field(default=None, validation_alias=AliasChoices("S3_USERASSETS_BUCKET"))

    # For deleting episode outputs/story assets when URLs are not available
    s3_results_bucket: str | None = Field(default=None, validation_alias=AliasChoices("S3_RESULTS_BUCKET", "RESULTS_BUCKET"))
    s3_userbgm_bucket: str | None = Field(default=None, validation_alias=AliasChoices("S3_USERBGM_BUCKET"))

    kakao_client_id: str | None = None
    kakao_client_secret: str | None = None
    kakao_redirect_uri: str | None = None

    # Emergency bypass for admin lockout (comma-separated user_ids)
    superadmin_user_ids: str = Field(default="", validation_alias=AliasChoices("SUPERADMIN_USER_IDS"))

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def superadmin_ids(self) -> set[str]:
        return {x.strip() for x in (self.superadmin_user_ids or "").split(",") if x.strip()}


settings = Settings()
