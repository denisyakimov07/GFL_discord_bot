from datetime import datetime
from enum import Enum
from typing import Optional, Union, List, TypeVar, Generic, Any

from pydantic import BaseModel as BaseModelPydantic, Field
from pydantic.generics import GenericModel


class BaseModel(BaseModelPydantic):
    id: str
    created_at: Optional[datetime] = Field(alias='createdAt')
    updated_at: Optional[datetime] = Field(alias='updatedAt')


class ModelOperationEnum(str, Enum):
    create_one = 'createOne'
    create_many = 'createMany'
    update_by_id = 'updateById'
    update_many = 'updateMany'
    delete_by_id = 'deleteById'
    delete_many = 'deleteMany'
    find_by_id = 'findById'
    find_many = 'findMany'


class SpecialChannelEnum(str, Enum):
    audit_log_join = 'auditlogjoin',
    audit_log_voice = 'auditlogvoice',
    audit_log_event = 'auditlogevent',
    audit_log_roles = 'auditlogroles',
    audit_log_messages = 'auditlogmessages',
    audit_log_bans = 'auditlogbans',
    audit_log_admin = 'auditlogadmin',
    verify = 'verify',


class SpecialRoleEnum(str, Enum):
    verify = 'verify',


class Client(BaseModel):
    name: str
    redirect_uris: Optional[str] = Field(alias='redirectUris')
    grants: Union[List[str], str]
    access_token_lifetime: int = Field(alias='accessTokenLifetime')
    refresh_token_lifetime: int = Field(alias='refreshTokenLifetime')
    scope: Union[List[str], str]


class DiscordRole(BaseModel):
    id: str
    guild_id: str = Field(alias='guildId')
    role_id: str = Field(alias='roleId')
    name: str


class DiscordServerSettings(BaseModel):
    guild_id: str = Field(alias='guildId')
    name: str
    verification_roles: Optional[Union[List['DiscordVerificationRole'], List[str]]] = Field(alias='verificationRoles')
    special_channels: Optional[dict] = Field(alias='specialChannels')
    special_roles: Optional[dict] = Field(alias='specialRoles')

    def get_special_channel(self, key: SpecialChannelEnum) -> Union[None, str]:
        if self.special_channels is None:
            return None
        return self.special_channels[key]

    def get_special_role(self, key: SpecialRoleEnum) -> Union[None, str]:
        if self.special_roles is None:
            return None
        return self.special_roles[key]


TModel = TypeVar('TModel')


class Pagination(GenericModel, Generic[TModel]):
    total_count: int = Field(alias='totalCount')
    total_pages: int = Field(alias='totalPages')
    results_per_page: int = Field(alias='resultsPerPage')
    data: List[TModel]


class DiscordUser(BaseModel):
    id: str
    member_name: Optional[str] = Field(alias='memberName')
    member_id: Optional[str] = Field(alias='memberId')
    member_nickname: Optional[str] = Field(alias='memberNickname')
    verified_by_member_id: Optional[str] = Field(alias='verifiedByMemberId')
    verified_at: Optional[datetime] = Field(alias='verifiedAt')
    avatar_url: Optional[str] = Field(alias='avatarUrl')
    notes: Optional[Union[List['DiscordUserNote'], List[str]]]


class DiscordUserNote(BaseModel):
    discord_user: Optional[Union['DiscordUser', str]] = Field(alias='discordUser')
    text: Optional[str]

    by_user: Optional[Union['User', str]] = Field(alias='byUser')
    by_discord_user: Optional[Union['DiscordUser', str]] = Field(alias='byDiscordUser')


class DiscordVerificationRole(BaseModel):
    id: str
    discord_role_id: Union[DiscordRole, str] = Field(alias='discordRoleId')
    max_per_day: int = Field(alias='maxPerDay')


class User(BaseModel):
    username: Optional[str]
    email: str
    roles: List[str]


class Token(BaseModel):
    accessToken: str = Field(alias='accessToken')
    access_token_expires_at: Optional[datetime] = Field(alias='accessTokenExpiresAt')
    grant_type: str = Field(alias='grantType')
    refresh_token: Optional[str] = Field(alias='refreshToken')
    scope: Union[str, List[str]]
    refresh_token_expires_at: Optional[datetime] = Field(alias='refreshTokenExpiresAt')
    client: Union[Client, str]
    user: Union[Optional[User], Any]


class WebhookSubscription(BaseModel):
    url: str
    client: Union[Client, str]
    topic: str
    secret: str
    expires_at: datetime = Field(alias='expiresAt')


class DeleteResult(BaseModelPydantic):
    success: bool


class DeleteManyResult(BaseModelPydantic):
    n: Optional[int]
    ok: Optional[int]
    deleted_count: Optional[int] = Field(alias='deleted_count')


class UpdateManyResult(BaseModelPydantic):
    n: Optional[int]
    n_modified: Optional[int] = Field(alias='nModified')
    ok: Optional[int]


DiscordServerSettings.update_forward_refs()
DiscordUserNote.update_forward_refs()
DiscordUser.update_forward_refs()
