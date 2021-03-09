"""Test /feature_association."""
import json

from fastapi.testclient import TestClient
import pytest

from icees_api.app import APP

from ..util import load_data, do_verify_feature_matrix_response, escape_quotes

testclient = TestClient(APP)
table = "patient"
year = 2010
age_levels = [
    '0-2',
    '3-17',
    '18-34',
    '35-50',
    '51-69',
    '70-89',
]


@load_data(
    APP,
    """
        PatientId,year,AgeStudyStart,Albuterol,AvgDailyPM2.5Exposure,EstResidentialDensity,AsthmaDx
        varchar(255),int,varchar(255),varchar(255),int,int,int
        1,2010,0-2,0,1,0,1
        2,2010,0-2,1,1,0,1
        3,2010,0-2,>1,1,0,1
        4,2010,0-2,0,2,0,1
        5,2010,0-2,1,2,0,1
        6,2010,0-2,>1,2,0,1
        7,2010,0-2,0,3,0,1
        8,2010,0-2,1,3,0,1
        9,2010,0-2,>1,3,0,1
        10,2010,0-2,0,4,0,1
        11,2010,0-2,1,4,0,1
        12,2010,0-2,>1,4,0,1
    """,
    """
        cohort_id,size,features,table,year
        COHORT:1,12,"{}",patient,2010
    """
)
def test_feature_association():
    feature_variables = {}
    resp = testclient.post(
        f"/{table}/{year}/cohort",
        json=feature_variables,
    )
    resp_json = resp.json()
    cohort_id = resp_json["return value"]["cohort_id"]
    atafdata = {
        "feature_a": {
            "AgeStudyStart": {
                "operator": "=",
                "value": '0-2'
            }
        },
        "feature_b": {
            "AgeStudyStart": {
                "operator": "=",
                "value": '0-2'
            }
        }
    }
    resp = testclient.post(
        f"/{table}/{year}/cohort/{cohort_id}/feature_association",
        json=atafdata,
    )
    resp_json = resp.json()
    assert "return value" in resp_json
    do_verify_feature_matrix_response(resp_json["return value"])


@load_data(
    APP,
    """
        PatientId,year,AgeStudyStart,Albuterol,AvgDailyPM2.5Exposure,EstResidentialDensity,AsthmaDx
        varchar(255),int,varchar(255),varchar(255),int,int,int
        1,2010,0-2,0,1,0,1
        2,2010,0-2,1,1,0,1
        3,2010,0-2,>1,1,0,1
        4,2010,0-2,0,2,0,1
        5,2010,0-2,1,2,0,1
        6,2010,0-2,>1,2,0,1
        7,2010,0-2,0,3,0,1
        8,2010,0-2,1,3,0,1
        9,2010,0-2,>1,3,0,1
        10,2010,0-2,0,4,0,1
        11,2010,0-2,1,4,0,1
        12,2010,0-2,>1,4,0,1
    """,
    """
        cohort_id,size,features,table,year
        COHORT:1,12,"{}",patient,2010
    """
)
def test_feature_association_explicit():
    feature_variables = {}
    resp = testclient.post(
        f"/{table}/{year}/cohort",
        json=feature_variables,
    )
    resp_json = resp.json()
    cohort_id = resp_json["return value"]["cohort_id"]
    atafdata = {
        "feature_a": {
            "feature_name": "AgeStudyStart",
            "feature_qualifier": {
                "operator": "=",
                "value": '0-2'
            }
        },
        "feature_b": {
            "feature_name": "AgeStudyStart",
            "feature_qualifier": {
                "operator": "=",
                "value": '0-2'
            }
        }
    }
    resp = testclient.post(
        f"/{table}/{year}/cohort/{cohort_id}/feature_association",
        json=atafdata,
    )
    resp_json = resp.json()
    assert "return value" in resp_json
    do_verify_feature_matrix_response(resp_json["return value"])


@load_data(
    APP,
    """
        PatientId,year,AgeStudyStart,Albuterol,AvgDailyPM2.5Exposure,EstResidentialDensity,AsthmaDx
        varchar(255),int,varchar(255),varchar(255),int,int,int
        1,2010,0-2,0,1,0,1
        2,2010,3-17,1,1,0,1
        3,2010,18-34,>1,1,0,1
        4,2010,35-50,0,2,0,1
        5,2010,51-69,1,2,0,1
        6,2010,70-89,>1,2,0,1
        7,2010,0-2,0,3,0,1
        8,2010,0-2,1,3,0,1
        9,2010,0-2,>1,3,0,1
        10,2010,0-2,0,4,0,1
        11,2010,0-2,1,4,0,1
        12,2010,0-2,>1,4,0,1
    """,
    """
        cohort_id,size,features,table,year
        COHORT:1,12,"{}",patient,2010
    """
)
def test_feature_association2_explicit_check_coverage_is_full():
    feature_variables = {}
    resp = testclient.post(
        f"/{table}/{year}/cohort",
        json=feature_variables,
    )
    resp_json = resp.json()
    cohort_id = resp_json["return value"]["cohort_id"]
    atafdata = {
        "feature_a": {
            "feature_name": "AgeStudyStart",
            "feature_qualifiers": list(map(lambda x: {
                "operator": "=",
                "value": x
            }, age_levels))
        },
        "feature_b": {
            "feature_name": "AgeStudyStart",
            "feature_qualifiers": [{
                "operator": ">",
                "value": '0-2'
            }, {
                "operator": "<=",
                "value": '0-2'
            }]
        },
        "check_coverage_is_full": True
    }
    resp = testclient.post(
        f"/{table}/{year}/cohort/{cohort_id}/feature_association2",
        json=atafdata,
    )
    resp_json = resp.json()
    assert "return value" in resp_json
    do_verify_feature_matrix_response(resp_json["return value"])


@load_data(
    APP,
    """
        PatientId,year,AgeStudyStart,Albuterol,AvgDailyPM2.5Exposure,EstResidentialDensity,AsthmaDx
        varchar(255),int,varchar(255),varchar(255),int,int,int
        1,2010,0-2,0,1,0,1
        2,2010,0-2,1,1,0,1
        3,2010,0-2,>1,1,0,1
        4,2010,0-2,0,2,0,1
        5,2010,0-2,1,2,0,1
        6,2010,0-2,>1,2,0,1
        7,2010,0-2,0,3,0,1
        8,2010,0-2,1,3,0,1
        9,2010,0-2,>1,3,0,1
        10,2010,0-2,0,4,0,1
        11,2010,0-2,1,4,0,1
        12,2010,0-2,>1,4,0,1
    """,
    """
        cohort_id,size,features,table,year
        COHORT:1,12,"{}",patient,2010
    """
)
def test_feature_association_two_years():
    cohort_year = 2010
    year = 2011
    feature_variables = {}
    resp = testclient.post(
        f"/{table}/{cohort_year}/cohort",
        json=feature_variables,
    )
    resp_json = resp.json()
    cohort_id = resp_json["return value"]["cohort_id"]
    atafdata = {
        "feature_a": {
            "AgeStudyStart": {
                "operator": "=",
                "value": '0-2'
            }
        },
        "feature_b": {
            "AgeStudyStart": {
                "operator": "=",
                "value": '0-2'
            }
        }
    }
    resp = testclient.post(
        f"/{table}/{year}/cohort/{cohort_id}/feature_association",
        json=atafdata,
    )
    resp_json = resp.json()
    assert "return value" in resp_json
    do_verify_feature_matrix_response(resp_json["return value"])


feature_variables = [
    {
        "feature_name": "AgeStudyStart",
        "feature_qualifier": {
            "operator": "=",
            "value": "0-2"
        }
    },
    {
        "feature_name": "AvgDailyPM2.5Exposure",
        "feature_qualifier": {
            "operator": ">",
            "value": 1
        },
        "year": 2011
    }
]


@load_data(
    APP,
    """
        PatientId,year,AgeStudyStart,Albuterol,AvgDailyPM2.5Exposure,EstResidentialDensity,AsthmaDx
        varchar(255),int,varchar(255),varchar(255),int,int,int
        1,2010,0-2,0,1,0,1
        2,2010,0-2,1,1,0,1
        3,2010,0-2,>1,1,0,1
        4,2010,0-2,0,2,0,1
        5,2010,0-2,1,2,0,1
        6,2010,0-2,>1,2,0,1
        7,2010,0-2,0,3,0,1
        8,2010,0-2,1,3,0,1
        9,2010,0-2,>1,3,0,1
        10,2010,0-2,0,4,0,1
        11,2010,0-2,1,4,0,1
        12,2010,0-2,>1,4,0,1
    """,
    """
        cohort_id,size,features,table,year
        COHORT:1,12,"{0}",patient,2010
    """.format(escape_quotes(json.dumps(feature_variables, sort_keys=True)))
)
def test_feature_association_cohort_features_two_years():
    """
    See test/sql_example_2.txt for the SQL query this generates.
    It forms a cohort by finding rows matching each feature variable's
    conditions, then joining.
    This means that we get one row for _each time a patient was Male_ along
    with that patient's 2011 features (per the year parameter on the
    /feature_association call?)
    This seems like probably not the intended behavior? It's computing counts
    over _each time a patient was Male_ rather than over patients...

    Questions:
    1. What is this operation supposed to mean, in English?
    1. What is the cohort_year supposed to do?
    1. Can we include multiple years as distinct sets of columns rather than
       additional rows with duplicate patient ids? Then we could avoid joins
       entirely, I think, and this could be ~50x faster.
       * Possibly joins should not be as slow as they are. SQLite uses only
         nested-loop joins: O(NM).
    """
    cohort_year = 2010
    resp = testclient.post(
        f"/{table}/{cohort_year}/cohort",
        json=feature_variables,
    )
    year = 2011
    resp_json = resp.json()
    cohort_id = resp_json["return value"]["cohort_id"]
    atafdata = {
        "feature_a": {
            "AgeStudyStart": {
                "operator": "=",
                "value": '0-2'
            }
        },
        "feature_b": {
            "AgeStudyStart": {
                "operator": "=",
                "value": '0-2'
            }
        }
    }
    resp = testclient.post(
        f"/{table}/{year}/cohort/{cohort_id}/feature_association",
        json=atafdata,
    )
    resp_json = resp.json()
    assert "return value" in resp_json
    do_verify_feature_matrix_response(resp_json["return value"])
