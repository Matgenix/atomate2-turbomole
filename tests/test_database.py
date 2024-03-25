# # Part of turbomole package.
#
# """Tests of the database tools in the turbomole package."""
#
# import os
#
# import turbomole.database
# from turbomole.database import ResultsDatabase
#
#
# def test_database(mocker, test_files, mongo_collection):
#     mock = mocker.patch.object(turbomole.database, "MongoClient", autospec=True)
#     rdb = ResultsDatabase(
#         host="localhost",
#         port=1234,
#         database="results_db",
#         collection_name="projectA_results",
#         user="johndoe",
#         password="password",
#     )
#     mock.assert_called_once()
#     rdb.insert({"a": 1})
#     rdb.collection.insert_one.assert_called_once()
#     rdb.collection.insert_one.assert_called_with({"a": 1})
#
#     mock.reset_mock()
#     rdb = ResultsDatabase.from_db_file(
#         os.path.join(test_files, "misc", "results_db.yaml")
#     )
#     assert rdb.user == "testuser"
#     assert rdb.password == "testpassword"
#     assert rdb.host == "somehost"
#     assert rdb.port == 12345
#     assert rdb.database == "results"
#     rdb.db.__getitem__.assert_called_once()  # == 'projectA_results'
#     rdb.db.__getitem__.assert_called_with("projectA_results")
#
#     mocker.patch.object(turbomole.database, "ResultsDatabase", autospec=True)
#     rdb = ResultsDatabase(
#         host="localhost",
#         port=1234,
#         database="results_db",
#         collection_name="projectA_results",
#         user="johndoe",
#         password="password",
#     )
#     rdb.collection = mongo_collection
#     rdb.insert({"b": "b"})
#     assert rdb.collection.count_documents({}) == 1
#     rdb.insert({"c": "c"})
#     assert rdb.collection.count_documents({}) == 2
