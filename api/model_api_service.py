import json
import requests

from typing import TypeVar, Type, List, Union, Optional
from environment import get_env
from .access_token import AccessToken
from models import BaseModel, Pagination, DeleteResult, DeleteManyResult, UpdateManyResult, DiscordUser

TModel = TypeVar('TModel', bound=BaseModel)

SORT_TYPE = str
QUERY_TYPE = Union[dict, TModel]
UPDATE_QUERY_TYPE = Union[dict, TModel]
POPULATE_TYPE = Union[str, dict, List[str]]
SELECT_TYPE = List[str]


class __ModelApiService():
    accessToken: AccessToken

    def __init__(self):
        self.accessToken = AccessToken()

    def find_many(
            self,
            model_class: Type[TModel],
            limit: int = 100,
            page_index: int = 0,
            query: Optional[QUERY_TYPE] = None,
            sort: Optional[SORT_TYPE] = None,
            populate: Optional[POPULATE_TYPE] = None,
            select: Optional[SELECT_TYPE] = None
    ) -> Pagination[TModel]:
        """
        :param model_class: The model class you want to be returned to you. Ex: DiscordUser
        :param limit: The number of items to return per page
        :param page_index: The page index
        :param sort: Which property to sort by
        :param query: How you want to filter the object. You can filter by properties or by a Mongoose query. More Info: https://mongoosejs.com/docs/queries.html
        :param populate: Which references to populate. Such as for DiscordUser, you could populate with ['notes']
        :param select: Which properties to return. Helps performance
        :return:
        """

        params = {
            'l': limit,
            'p': page_index
        }

        if query is not None and not isinstance(query, dict):
            query = query.dict(exclude_unset=True, exclude_defaults=True, by_alias=True)

        if query is not None:
            params['q'] = json.dumps(query)
        if sort is not None:
            params['sort'] = sort
        if populate is not None:
            params['populate'] = json.dumps(populate)
        if select is not None:
            params['select'] = json.dumps(select)

        response = requests.get(
            self.get_model_url(model_class),
            headers=self.get_headers(),
            params=params
        )

        if response.status_code == 200:
            return Pagination[model_class].parse_raw(response.text)
        else:
            self.print_error(response)

    def find_one(
            self,
            model_class: Type[TModel],
            query: Optional[QUERY_TYPE] = None,
            sort: Optional[SORT_TYPE] = None,
            populate: Optional[POPULATE_TYPE] = None,
            select: Optional[SELECT_TYPE] = None,
    ) -> Union[TModel, None]:
        """
        Helper method of using find_many but when you need 1 result. Useful for when you want to find one model without id
        :param model_class: The model class you want to be returned to you. Ex: DiscordUser
        :param query: How you want to filter the object. You can filter by properties or by a Mongoose query. More Info: https://mongoosejs.com/docs/queries.html
        :param sort: Which property to sort by
        :param populate: Which references to populate. Such as for DiscordUser, you could populate with ['notes']
        :param select: Which properties to return. Helps performance
        :return:
        """
        pagination = self.find_many(model_class, limit=1, query=query, sort=sort, populate=populate, select=select)
        if pagination.total_count == 0:
            return None
        else:
            return pagination.data[0]

    def find_by_id(
            self,
            model_class: Type[TModel],
            model_id: str,
            populate: Optional[POPULATE_TYPE] = None,
    ) -> TModel:
        """
        :param model_class: The model class you want to be returned to you. Ex: DiscordUser
        :param model_id:
        :param populate: Which references to populate. Such as for DiscordUser, you could populate with ['notes']
        :return:
        """
        params = {}
        if populate is not None:
            params['populate'] = json.dumps(populate)

        response = requests.get(
            self.get_model_url(model_class, model_id),
            headers=self.get_headers(),
            params=params
        )

        if response.status_code == 200:
            response_body = model_class.parse_raw(response.text)
            return response_body
        else:
            self.print_error(response)

    def update_many(
            self,
            model_class: Type[TModel],
            model_ids: List[str],
            update_query: UPDATE_QUERY_TYPE
    ) -> UpdateManyResult:
        """
        :param model_class: The model class you want to be returned to you. Ex: DiscordUser
        :param model_ids: List of strings
        :param update_query: The set of properties you want to update TModel or Mongoose Update Query: More Info: https://mongoosejs.com/docs/queries.html
        :return:
        """
        request_body = update_query
        if not isinstance(update_query, dict):
            request_body = update_query.dict(exclude_defaults=True, exclude_unset=True, by_alias=True)

        response = requests.put(
            self.get_model_url(model_class),
            json=request_body,
            headers=self.get_headers(),
            params={
                'ids': model_ids
            }
        )

        if response.status_code == 200:
            return UpdateManyResult.parse_raw(response.text)
            return response_body
        else:
            self.print_error(response)

    def update_by_id(
            self,
            model_class: Type[TModel],
            model_id: str,
            update_query: UPDATE_QUERY_TYPE
    ) -> TModel:
        """
        :param model_class: The model class you want to be returned to you. Ex: DiscordUser
        :param model_id: The string id of the model you want to update
        :param update_query: The set of properties you want to update TModel or Mongoose Update Query: More Info: https://mongoosejs.com/docs/queries.html
        :return:
        """
        request_body = update_query
        if not isinstance(update_query, dict):
            request_body = update_query.dict(exclude_defaults=True, exclude_unset=True, by_alias=True)

        response = requests.put(
            self.get_model_url(model_class, model_id),
            json=request_body,
            headers=self.get_headers()
        )

        if response.status_code == 200:
            response_body = model_class.parse_raw(response.text)
            return response_body
        else:
            self.print_error(response)

    def create_one(
            self,
            model: TModel
    ) -> TModel:
        """
        :param model: The model to create. Do NOT include the id
        :return:
        """
        response = requests.post(
            self.get_model_url(model),
            json=model.dict(exclude_defaults=True, by_alias=True),
            headers=self.get_headers()
        )

        if response.status_code == 200:
            return model.parse_raw(response.text)
        else:
            self.print_error(response)

    def create_many(
            self,
            models: List[TModel]
    ) -> List[TModel]:
        """
        :param models: The many models you want to create. Throws an exception if len(models) is 0
        :return:
        """
        if len(models) == 0:
            raise Exception('Must be at least one model in create_many(models)')

        request_body = list(map(lambda x: x.dict(exclude_defaults=True, by_alias=True), models))

        response = requests.post(
            self.get_model_url(models[0]),
            json=request_body,
            headers=self.get_headers()
        )

        if response.status_code == 200:
            return list(map(lambda x: models[0].parse_raw(json.dumps(x)), response.json()))
        else:
            self.print_error(response)

    def delete_by_id(
            self,
            model_class: Type[TModel],
            model_id: str
    ) -> DeleteResult:
        """
        :param model_class: The model class you want to be returned to you. Ex: DiscordUser
        :param model_id: The id of the model you want to delete
        :return:
        """
        response = requests.delete(self.get_model_url(model_class, model_id), headers=self.get_headers())

        if response.status_code == 200:
            return DeleteResult.parse_raw(response.text)
        else:
            self.print_error(response)

    def delete_many(
            self, model_class: Type[TModel],
            model_ids: List[str]
    ) -> DeleteManyResult:
        """
        :param model_class: The model class you want to be returned to you. Ex: DiscordUser
        :param model_ids: List of string id's you want to delete
        :return:
        """
        response = requests.delete(
            self.get_model_url(model_class),
            headers=self.get_headers(),
            params={
                'ids': model_ids
            }
        )

        if response.status_code == 200:
            response_body = DeleteManyResult.parse_raw(response.text)
            return response_body
        else:
            self.print_error(response)

    @staticmethod
    def get_model_url(
            model_class_or_name: Union[str, Type[TModel], TModel],
            optional_model_id: Optional[str] = None
    ) -> str:
        model_name: str
        if isinstance(model_class_or_name, str):
            model_name = model_class_or_name
        elif isinstance(model_class_or_name, Type):
            model_name = model_class_or_name.__name__
        else:
            model_name = model_class_or_name.__class__.__name__

        url = f'{get_env().API_BASE_URL}/api/model/{model_name}'

        if optional_model_id is not None:
            url += f'/{optional_model_id}'

        return url

    def get_headers(self):
        return {
            'Authorization': f'{self.accessToken.token}',
        }

    @staticmethod
    def print_error(response: requests.Response):
        print(f'[{response.status_code}] Model API Request Failure', response.text)


model_api_service = __ModelApiService()
