class TosSettings(BaseSettings):
    """Environment-backed settings for TOS object storage."""

    access_key: str = Field(default="", validation_alias="TOS_ACCESS_KEY")
    secret_access_key: str = Field(
        default="",
        validation_alias="TOS_SECRET_ACCESS_KEY",
    )
    endpoint: str = Field(default="", validation_alias="TOS_ENDPOINT")
    region: str = Field(default="", validation_alias="TOS_REGION")
    bucket_name: str = Field(default="", validation_alias="TOS_BUCKET_NAME")

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=ENV_FILE,
        extra="ignore",
    )


tos_settings = TosSettings()
__all__ = ["TosSettings", "tos_settings"]
