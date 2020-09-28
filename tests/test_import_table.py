from datasette.app import Datasette
import datasette_import_table
import pytest
import json
import httpx


@pytest.fixture
def non_mocked_hosts():
    return ["localhost"]


@pytest.mark.asyncio
async def test_plugin_is_installed():
    app = Datasette([], memory=True).app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get("http://localhost/-/plugins.json")
        assert 200 == response.status_code
        installed_plugins = {p["name"] for p in response.json()}
        assert "datasette-import-table" in installed_plugins


@pytest.mark.asyncio
async def test_import_table(tmp_path_factory, httpx_mock):
    db_directory = tmp_path_factory.mktemp("dbs")
    db_path = db_directory / "test.db"
    httpx_mock.add_response(
        url="http://example/some/table.json?_shape=objects",
        json={
            "table": "mytable",
            "rows": [{"foo": "bar"}],
            "primary_keys": [],
            "filtered_table_rows_count": 1,
            "next_url": None,
        },
        headers={"content-type": "application/json"},
    )

    app = Datasette([str(db_path)], memory=True).app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get("http://localhost/-/import-table")
        assert 200 == response.status_code
        csrftoken = response.cookies["ds_csrftoken"]
        response = await client.post(
            "http://localhost/-/import-table",
            data={
                "url": "http://example/some/table",
                "csrftoken": csrftoken,
            },
            allow_redirects=False,
        )
        assert response.status_code == 302
        assert (
            response.headers["location"] == "/:memory:/mytable?_import_expected_rows=1"
        )
