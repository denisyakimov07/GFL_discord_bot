import json
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
    verification_roles: List[str] = Field(alias='verificationRoles')
    roles: List[DiscordRole]
    bot_command_channel_id: str = Field(alias='botCommandChannelId')


class DiscordUser(BaseModel):
    id: str
    member_name: str = Field(alias='memberName')
    member_id: str = Field(alias='memberId')
    member_nickname: Optional[str] = Field(alias='memberNickname')
    verified_by_member_id: Optional[str] = Field(alias='verifiedByMemberId')
    verified_at: Optional[datetime] = Field(alias='verifiedAt')
    avatar_url: Optional[str] = Field(alias='avatarUrl')
    coins: float
    notes: Union['DiscordUserNote', List[str]]


class DiscordUserNote(BaseModel):
    discord_user: Union['DiscordUser', str] = Field(alias='discordUser')
    text: str

    by_user: Optional[Union['User', str]] = Field(alias='byUser')
    by_discord_user: Optional[Union['DiscordUser', str]] = Field(alias='byDiscordUser')


class DiscordVerificationRole(BaseModel):
    id: str
    discord_role: Union[DiscordRole, str] = Field(alias='discordRole')
    max_per_day: int = Field(alias='maxPerDay')


TModel = TypeVar('TModel')


class Pagination(GenericModel, Generic[TModel]):
    total_count: int = Field(alias='totalCount')
    total_pages: int = Field(alias='totalPages')
    results_per_page: int = Field(alias='resultsPerPage')
    data: List[TModel]


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
    authorization_header: Optional[str] = Field(alias='authorizationHeader')
    model_operations: List[str] = Field(alias='modelOperations')
    model_name: str = Field(alias='modelName')


DiscordServerSettings.update_forward_refs()
DiscordUserNote.update_forward_refs()
DiscordUser.update_forward_refs()
