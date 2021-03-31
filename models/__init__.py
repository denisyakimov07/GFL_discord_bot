from datetime import datetime
from enum import Enum
from typing import Optional, Union, List, TypeVar, Generic, Any

from pydantic import BaseModel as BaseModelPydantic


class BaseModel(BaseModelPydantic):
    id: str
    createdAt: Optional[datetime]
    updatedAt: Optional[datetime]


class ModelOperationEnum(str, Enum):
    createOne = 'createOne'
    createMany = 'createMany'
    updateById = 'updateById'
    updateMany = 'updateMany'
    deleteById = 'deleteById'
    deleteMany = 'deleteMany'
    findById = 'findById'
    findMany = 'findMany'


class Client(BaseModel):
    name: str
    redirectUris: Optional[str]
    grants: Union[List[str], str]
    accessTokenLifetime: int
    refreshTokenLifetime: int
    scope: Union[List[str], str]


class DiscordRole(BaseModel):
    id: str
    guildId: str
    roleId: str
    name: str


class DiscordServerSettings(BaseModel):
    guildId: str
    name: str
    verificationRoles: List[str]
    roles: List[DiscordRole]
    botCommandChannelId: str


class DiscordUser(BaseModel):
    id: str
    memberName: str
    memberId: str
    memberNickname: Optional[str]
    verifiedByMemberId: Optional[str]
    verifiedAt: Optional[datetime]
    avatarUrl: Optional[str]
    coins: float
    notes: Union['DiscordUserNote', List[str]]


class DiscordUserNote(BaseModel):
    discordUser: Union['DiscordUser', str]
    text: str

    byUser: Optional[Union['User', str]]
    byDiscordUser: Optional[Union['DiscordUser', str]]


class DiscordVerificationRole(BaseModel):
    id: str
    discordRole: Union[DiscordRole, str]
    maxPerDay: int


TModel = TypeVar('TModel')


class Pagination(BaseModelPydantic, Generic[TModel]):
    totalCount: int
    totalPages: int
    resultsPerPage: int
    data: List[TModel]


class User(BaseModel):
    username: Optional[str]
    email: str
    roles: List[str]


class Token(BaseModel):
    accessToken: str

    accessTokenExpiresAt: Optional[datetime]
    grantType: str
    refreshToken: Optional[str]
    scope: Union[str, List[str]]
    refreshTokenExpiresAt: Optional[datetime]
    client: Union[Client, str]
    user: Union[Optional[User], Any]


class WebhookSubscription(BaseModel):
    url: str
    client: Union[Client, str]
    authorizationHeader: Optional[str]
    modelOperations: List[str]
    modelName: List[ModelOperationEnum]
