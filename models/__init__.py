from datetime import datetime
from enum import Enum
from typing import Optional, Union, List, TypeVar, Generic, Any

import discord
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
    audit_log_join = 'auditlogjoin'
    audit_log_voice = 'auditlogvoice'
    audit_log_event = 'auditlogevent'
    audit_log_roles = 'auditlogroles'
    audit_log_messages = 'auditlogmessages'
    audit_log_bans = 'auditlogbans'
    audit_log_admin = 'auditlogadmin'
    verify = 'verify'
    video_submissions = 'videosubmissions'
    current_event = 'currentevent'


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
    welcome_message: Optional[str]
    guild_id: str = Field(alias='guildId')
    name: str
    verification_roles: Optional[Union[List['DiscordVerificationRole'], List[str]]] = Field(alias='verificationRoles')
    special_channels: Optional[dict] = Field(alias='specialChannels')
    special_roles: Optional[dict] = Field(alias='specialRoles')

    def get_special_channel(self, key: SpecialChannelEnum) -> Union[None, str]:
        """
        Returns the channel id (str) that was configured in the Management Portal
        :param key:
        :return:
        """
        if self.special_channels is None:
            return None
        return self.special_channels[key]

    def get_verification_role_by_role_id(self, role_id: Union[str, int]) -> Union['DiscordVerificationRole', None]:
        if isinstance(role_id, int):
            role_id = str(role_id)

        verification_roles_with_matching_role_id = list(
            filter(lambda x: x.discord_role_id == role_id, self.verification_roles)
        )
        if len(verification_roles_with_matching_role_id) == 0:
            return None
        return verification_roles_with_matching_role_id[0]

    def get_special_role(self, key: SpecialRoleEnum) -> Union[None, str]:
        if self.special_roles is None:
            return None
        return self.special_roles.get(key)

    def can_member_verify(self, member: discord.Member) -> bool:
        """
        Checks to see if verification_roles contains a role that the member has
        :param member:
        :return:
        """
        roles_allowed_to_verify = [int(verification_role.discord_role_id) for verification_role in
                                   self.verification_roles]

        user_roles_list = [role.id for role in member.roles]

        intersection_roles = set(user_roles_list) & set(roles_allowed_to_verify)
        return len(intersection_roles) > 0


TModel = TypeVar('TModel')


class Pagination(GenericModel, Generic[TModel]):
    total_count: int = Field(alias='totalCount')
    total_pages: int = Field(alias='totalPages')
    results_per_page: int = Field(alias='resultsPerPage')
    data: List[TModel]


# https://github.com/Gamers-4-Life/web-common-types/blob/main/src/interfaces/models/IDiscordUser.ts
class DiscordUser(BaseModel):
    id: str
    member_name: Optional[str] = Field(alias='memberName')
    member_id: Optional[str] = Field(alias='memberId')
    member_nickname: Optional[str] = Field(alias='memberNickname')
    verified_by_member_id: Optional[str] = Field(alias='verifiedBy')
    verified_at: Optional[datetime] = Field(alias='verifiedAt')
    avatar_url: Optional[str] = Field(alias='avatarUrl')
    notes: Optional[Union[List['DiscordUserNote'], List[str]]]


class User(BaseModel):
    discord_user: Optional[Union[str, DiscordUser]] = Field(alias='discordUser')
    email: str
    roles: Optional[List[str]]
    stars: Optional[int]
    username: str
    roles: List[str]


class DiscordUserNote(BaseModel):
    discord_user: Optional[Union['DiscordUser', str]] = Field(alias='discordUser')
    text: Optional[str]

    by_user: Optional[Union['User', str]] = Field(alias='byUser')
    by_discord_user: Optional[Union['DiscordUser', str]] = Field(alias='byDiscordUser')


class DiscordVerificationRole(BaseModel):
    discord_role_id: Union[DiscordRole, str] = Field(alias='discordRoleId')
    max_per_day: int = Field(alias='maxPerDay')


class DiscordOnlineStreamTimeLog(BaseModel):
    member_id: str = Field(alias='memberId')
    status: bool


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


# https://github.com/Gamers-4-Life/web-common-types/blob/4cdbb012b88add0ac8a46a9cf429c1380a272470/src/interfaces/models/IPostTag.ts#L3
class PostTag(BaseModel):
    tag: str
    color: Optional[str]
    slug: str
    posts: Optional[int]


# https://github.com/Gamers-4-Life/web-common-types/blob/4cdbb012b88add0ac8a46a9cf429c1380a272470/src/interfaces/models/IPost.ts#L6
class Post(BaseModel):
    type: int
    title: str
    text: Optional[str]
    html: Optional[str]
    published: bool
    publishedAt: Union[None, datetime, str]
    thumbnailUrl: Optional[str]
    authors: Union[None, User, str]
    expiresAt: Optional[datetime]
    tags: Union[None, PostTag, str]


# https://github.com/Gamers-4-Life/web-common-types/blob/4cdbb012b88add0ac8a46a9cf429c1380a272470/src/interfaces/models/IGameEvent.ts#L4
class GameEvent(BaseModel):
    title: str
    description: Optional[str]
    post: Union[None, Post, str]
    startsAt: datetime
    endsAt: datetime


# https://github.com/Gamers-4-Life/web-common-types/blob/main/src/interfaces/models/IGameEventProof.ts
class GameEventProof(BaseModel):
    pending: bool
    # category: Optional[Any]  # ???
    event: Union[GameEvent, str]
    user: Union[User, str]
    url: str
    accepted: Optional[bool]
    acceptedBy: Union[None, User, str]


DiscordServerSettings.update_forward_refs()
DiscordUserNote.update_forward_refs()
DiscordUser.update_forward_refs()
