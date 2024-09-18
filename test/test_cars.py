import copy

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response

from . import test_data


class TestCreateCar:
    REQUIRED_FIELDS: list[str] = ["brand", "model", "production_year"]

    @pytest.fixture
    def test_schema(self) -> dict[str, str]:
        return copy.deepcopy(test_data.CAR_SCHEMA)

    endpoint: str = "/cars"

    def test_valid_schema(
        self, client: TestClient, test_schema: dict[str, str]
    ) -> None:
        response: Response = client.post(self.endpoint, json=test_schema)

        expected_response_json: dict[str, str] = test_schema
        expected_response_json["id"] = 1

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == expected_response_json

    def test_empty_schema(self, client: TestClient) -> None:
        response: Response = client.post(self.endpoint, json={})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_no_schema(self, client: TestClient) -> None:
        response: Response = client.post(self.endpoint, json=None)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("missing_field", REQUIRED_FIELDS)
    def test_schema_missing_required_fields(
        self, client: TestClient, test_schema: dict[str, str], missing_field: str
    ) -> None:
        test_schema.pop(missing_field)

        response: Response = client.post(self.endpoint, json=test_schema)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_ids_are_incremented_per_created_car(
        self, client: TestClient, test_schema: dict[str, str]
    ) -> None:
        for expected_id in range(1, 11):
            response: Response = client.post(self.endpoint, json=test_schema)

            assert response.status_code == status.HTTP_201_CREATED
            assert response.json()["id"] == expected_id


class TestCreateRating:
    REQUIRED_FIELDS: list[str] = ["rating"]

    @pytest.fixture
    def test_schema(self) -> dict[str, str]:
        return copy.deepcopy(test_data.RATING_SCHEMA)

    @pytest.fixture(autouse=True)
    def create_test_car(self, client: TestClient) -> None:
        client.post("/cars", json=test_data.CAR_SCHEMA)

    TEST_CAR_ID: int = 1

    endpoint: str = f"/cars/{TEST_CAR_ID}/rate"

    def test_valid_schema(
        self, client: TestClient, test_schema: dict[str, str]
    ) -> None:
        response: Response = client.post(self.endpoint, json=test_schema)

        expected_response_json: dict[str, str] = test_schema
        expected_response_json["id"] = 1
        expected_response_json["car_id"] = 1

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == expected_response_json

    def test_no_schema(self, client: TestClient) -> None:
        response: Response = client.post(self.endpoint, json=None)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("missing_field", REQUIRED_FIELDS)
    def test_schema_missing_required_fields(
        self, client: TestClient, test_schema: dict[str, str], missing_field: str
    ) -> None:
        test_schema.pop(missing_field)

        response: Response = client.post(self.endpoint, json=test_schema)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_ids_are_incremented_per_created_rating(
        self, client: TestClient, test_schema: dict[str, str]
    ) -> None:
        for expected_id in range(1, 11):
            response: Response = client.post(self.endpoint, json=test_schema)

            assert response.status_code == status.HTTP_201_CREATED
            assert response.json()["id"] == expected_id

    def test_car_with_given_id_does_not_exist(
        self, client: TestClient, test_schema: dict[str, str]
    ) -> None:
        invalid_car_id = 2
        response: Response = client.post(
            f"/cars/{invalid_car_id}/rate", json=test_schema
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize("valid_rating", [1, 5])
    def test_valid_rating_boundries(
        self, client: TestClient, test_schema: dict[str, str], valid_rating: int
    ) -> None:
        test_schema["rating"] = valid_rating

        expected_response_json: dict[str, str] = test_schema
        expected_response_json["id"] = 1
        expected_response_json["car_id"] = 1

        response: Response = client.post(self.endpoint, json=test_schema)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == expected_response_json

    @pytest.mark.parametrize("invalid_rating", [0, 6])
    def test_invalid_rating_boundries(
        self, client: TestClient, test_schema: dict[str, str], invalid_rating: int
    ) -> None:
        test_schema["rating"] = invalid_rating

        response: Response = client.post(self.endpoint, json=test_schema)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestTop10:
    @pytest.fixture
    def create_test_cars(self, client: TestClient) -> None:
        for i in range(1, 16):
            client.post(
                "/cars",
                json={
                    "brand": f"Brand_{i}",
                    "model": f"Model_{i}",
                    "production_year": 2000 + i,
                },
            )

    @pytest.fixture(autouse=True)
    def create_test_ratings(self, client: TestClient, create_test_cars: None) -> None:
        car_ratings = {
            1: [5, 4, 5],  # Average: 4.67
            2: [5],  # Average: 5.0
            3: [3, 3, 4],  # Average: 3.33
            4: [1],  # Average: 1.0
            5: [2, 2],  # Average: 2.0
            6: [3],  # Average: 3.0
            7: [4, 4],  # Average: 4.0
            8: [5, 5],  # Average: 5.0
            9: [1, 1],  # Average: 1.0
            10: [5, 4],  # Average: 4.5
            11: [4],  # Average: 4.0
            12: [3],  # Average: 3.0
            13: [5, 5],  # Average: 5.0
            14: [4],  # Average: 4.0
            15: [2, 3],  # Average: 2.5
        }

        for car_id, ratings in car_ratings.items():
            for rating in ratings:
                client.post(f"/cars/{car_id}/rate", json={"rating": rating})

    def expected_response(self) -> list[dict[str, str]]:
        return [
            {
                "id": 2,
                "brand": "Brand_2",
                "model": "Model_2",
                "production_year": 2002,
                "average_rating": 5.0,
            },
            {
                "id": 8,
                "brand": "Brand_8",
                "model": "Model_8",
                "production_year": 2008,
                "average_rating": 5.0,
            },
            {
                "id": 13,
                "brand": "Brand_13",
                "model": "Model_13",
                "production_year": 2013,
                "average_rating": 5.0,
            },
            {
                "id": 1,
                "brand": "Brand_1",
                "model": "Model_1",
                "production_year": 2001,
                "average_rating": 4.67,
            },
            {
                "id": 10,
                "brand": "Brand_10",
                "model": "Model_10",
                "production_year": 2010,
                "average_rating": 4.5,
            },
            {
                "id": 7,
                "brand": "Brand_7",
                "model": "Model_7",
                "production_year": 2007,
                "average_rating": 4.0,
            },
            {
                "id": 11,
                "brand": "Brand_11",
                "model": "Model_11",
                "production_year": 2011,
                "average_rating": 4.0,
            },
            {
                "id": 14,
                "brand": "Brand_14",
                "model": "Model_14",
                "production_year": 2014,
                "average_rating": 4.0,
            },
            {
                "id": 3,
                "brand": "Brand_3",
                "model": "Model_3",
                "production_year": 2003,
                "average_rating": 3.33,
            },
            {
                "id": 6,
                "brand": "Brand_6",
                "model": "Model_6",
                "production_year": 2006,
                "average_rating": 3.0,
            },
        ]

    def test_get_top_10_cars(
        self, client: TestClient, create_test_ratings: None
    ) -> None:
        response: Response = client.get("/cars/top10")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == self.expected_response()
