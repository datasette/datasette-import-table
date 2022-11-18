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
    ds = Datasette([], memory=True)
    response = await ds.client.get("/-/plugins.json")
    assert response.status_code == 200
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

    ds = Datasette([db_path])
    cookies = {"ds_actor": ds.sign({"a": {"id": "root"}}, "actor")}
    response = await ds.client.get("/-/import-table", cookies=cookies)
    assert response.status_code == 200
    csrftoken = response.cookies["ds_csrftoken"]
    cookies["ds_csrftoken"] = csrftoken
    response = await ds.client.post(
        "/-/import-table",
        data={
            "url": "http://example/some/table",
            "csrftoken": csrftoken,
        },
        cookies=cookies,
    )
    assert response.status_code == 302
    assert response.headers["location"] == "/test/mytable?_import_expected_rows=1"


@pytest.mark.asyncio
async def test_import_table_multiple_databases(tmpdir):
    db_path1 = str(tmpdir / "test.db")
    db_path2 = str(tmpdir / "test2.db")
    ds = Datasette([db_path1, db_path2])
    cookies = {"ds_actor": ds.sign({"a": {"id": "root"}}, "actor")}
    response = await ds.client.get("/-/import-table", cookies=cookies)
    assert response.status_code == 200
    assert "<option>test</option>" in response.text
    assert "<option>test2</option>" in response.text
    response2 = await ds.client.get("/-/import-table?database=test2", cookies=cookies)
    assert response2.status_code == 200
    assert '<option selected="selected">test2</option>' in response2.text


@pytest.mark.asyncio
async def test_permissions(tmpdir):
    path = str(tmpdir / "test.db")
    ds = Datasette([path])
    response = await ds.client.get("/-/import-table")
    assert response.status_code == 403
    # Now try with a root actor
    response2 = await ds.client.get(
        "/-/import-table",
        cookies={"ds_actor": ds.sign({"a": {"id": "root"}}, "actor")},
    )
    assert response2.status_code != 403
