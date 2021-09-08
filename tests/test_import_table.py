from datasette.app import Datasette
import datasette_import_table
import pytest
import sqlite_utils
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
async def test_import_table(tmpdir, httpx_mock):
    db_path = str(tmpdir / "test.db")
    httpx_mock.add_response(
        url="http://example/some/table.json?_shape=objects&_size=max",
        json={
            "table": "mytable",
            "rows": [{"foo": "bar"}],
            "primary_keys": [],
            "filtered_table_rows_count": 1,
            "next_url": None,
        },
        headers={"content-type": "application/json"},
    )

    datasette = Datasette([db_path])
    cookies = {"ds_actor": datasette.sign({"a": {"id": "root"}}, "actor")}
    async with httpx.AsyncClient(app=datasette.app()) as client:
        response = await client.get("http://localhost/-/import-table", cookies=cookies)
        assert 200 == response.status_code
        csrftoken = response.cookies["ds_csrftoken"]
        cookies["ds_csrftoken"] = csrftoken
        response = await client.post(
            "http://localhost/-/import-table",
            data={
                "url": "http://example/some/table",
                "csrftoken": csrftoken,
            },
            allow_redirects=False,
            cookies=cookies,
        )
        assert response.status_code == 302
        assert response.headers["location"] == "/test/mytable?_import_expected_rows=1"


@pytest.mark.asyncio
async def test_import_table_multiple_databases(tmpdir):
    db_path1 = str(tmpdir / "test.db")
    db_path2 = str(tmpdir / "test2.db")
    datasette = Datasette([db_path1, db_path2])
    cookies = {"ds_actor": datasette.sign({"a": {"id": "root"}}, "actor")}
    async with httpx.AsyncClient(app=datasette.app()) as client:
        response = await client.get("http://localhost/-/import-table", cookies=cookies)
        assert response.status_code == 200
        assert "<option>test</option>" in response.text
        assert "<option>test2</option>" in response.text
        response2 = await client.get(
            "http://localhost/-/import-table?database=test2", cookies=cookies
        )
        assert response2.status_code == 200
        assert '<option selected="selected">test2</option>' in response2.text


@pytest.mark.asyncio
async def test_permissions(tmpdir):
    path = str(tmpdir / "test.db")
    ds = Datasette([path])
    app = ds.app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get("http://localhost/-/import-table")
        assert 403 == response.status_code
    # Now try with a root actor
    async with httpx.AsyncClient(app=app) as client2:
        response2 = await client2.get(
            "http://localhost/-/import-table",
            cookies={"ds_actor": ds.sign({"a": {"id": "root"}}, "actor")},
            allow_redirects=False,
        )
        assert 403 != response2.status_code
