import json
from os import path

import pytest

from chocs import Application, HttpMethod, HttpRequest, HttpResponse
from chocs.json_schema.errors import RequiredPropertyError, PropertyValueError
from chocs.middleware import OpenApiMiddleware


def test_pass_valid_request_with_body() -> None:
    app = _mockup_app()
    _add_create_pet_route(app)
    body = json.dumps({
        "name": "Bob",
        "tag": "test-tag",
    })
    app(HttpRequest(HttpMethod.POST, "/pets", body=body, headers={"content-type": "application/json"}))


def test_fail_request_with_missing_property() -> None:
    app = _mockup_app()
    _add_create_pet_route(app)
    body = json.dumps({
        "tag": "test-tag",
    })

    with pytest.raises(RequiredPropertyError):
        app(HttpRequest(HttpMethod.POST, "/pets", body=body, headers={"content-type": "application/json"}))


def test_fail_request_with_invalid_value() -> None:
    app = _mockup_app()
    _add_create_pet_route(app)
    body = json.dumps({
        "name": 11,
    })

    with pytest.raises(PropertyValueError):
        app(HttpRequest(HttpMethod.POST, "/pets", body=body, headers={"content-type": "application/json"}))


def test_pass_valid_request_with_query() -> None:
    app = _mockup_app()

    @app.get("/pets")
    def get_pets(request: HttpRequest) -> HttpResponse:
        return HttpResponse("OK")

    app(HttpRequest(HttpMethod.GET, "/pets", query_string="tags=bla&tags=bla2"))


def test_fail_request_with_query_invalid_type() -> None:
    app = _mockup_app()

    @app.get("/pets")
    def get_pets(request: HttpRequest) -> HttpResponse:
        return HttpResponse("OK")

    with pytest.raises(PropertyValueError):
        app(HttpRequest(HttpMethod.GET, "/pets", query_string="tags=1"))


def test_fail_request_with_query_missing_field() -> None:
    app = _mockup_app()

    @app.get("/pets")
    def get_pets(request: HttpRequest) -> HttpResponse:
        return HttpResponse("OK")

    with pytest.raises(RequiredPropertyError):
        app(HttpRequest(HttpMethod.GET, "/pets"))


def test_turn_off_query_validation() -> None:
    openapi_file = path.realpath(path.dirname(__file__) + "/../fixtures/openapi.yml")
    app = Application(OpenApiMiddleware(openapi_file, validate_query=False))
    @app.get("/pets")
    def get_pets(request: HttpRequest) -> HttpResponse:
        return HttpResponse("OK")

    assert app(HttpRequest(HttpMethod.GET, "/pets"))


def _mockup_app() -> Application:
    openapi_file = path.realpath(path.dirname(__file__) + "/../fixtures/openapi.yml")
    app = Application(OpenApiMiddleware(openapi_file))

    return app


def _add_create_pet_route(app: Application) -> None:
    @app.post("/pets")
    def create_pet(request: HttpRequest) -> HttpResponse:
        return HttpResponse("OK")


