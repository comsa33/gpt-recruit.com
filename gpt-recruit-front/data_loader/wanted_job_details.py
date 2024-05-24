from dotenv import dotenv_values
from pymongo import MongoClient
from icecream import ic

config = dotenv_values(".env")

mongo_uri = config["MONGO_URI"]
client = MongoClient(mongo_uri)
db = client["scrap"]
collection = db["wanted_job_details"]


def get_wanted_job_details(projection: dict = {}, filter: dict = {}) -> list:
    """
    원티드 채용공고 상세정보를 조회하는 함수

    Returns:
        list: 원티드 채용공고 상세정보 목록
    """
    return list(collection.find(filter, projection=projection))


def get_unique_industry_name(data: list) -> list:
    """
    중복을 제거한 industry_name 리스트를 생성하는 함수

    Args:
        data (list): 원티드 채용공고 상세정보 목록

    Returns:
        list: 중복을 제거한 industry_name 리스트
    """
    return list(set(map(lambda x: x["data"]["job"]["company"]["industry_name"], data)))


def get_unique_company_name(data: list) -> list:
    """
    중복을 제거한 company_name 리스트를 생성하는 함수

    Args:
        data (list): 원티드 채용공고 상세정보 목록

    Returns:
        list: 중복을 제거한 company_name 리스트
    """
    return list(set(map(lambda x: x["data"]["job"]["company"]["name"], data)))


def get_unique_position(data: list) -> list:
    """
    중복을 제거한 position 리스트를 생성하는 함수

    Args:
        data (list): 원티드 채용공고 상세정보 목록

    Returns:
        list: 중복을 제거한 position 리스트
    """
    return list(set(map(lambda x: x["data"]["job"]["detail"]["position"], data)))


all_data_projection = {
    "_id": 0,
    "data.job.id": 1,
    "data.job.company.industry_name": 1,
    "data.job.company.name": 1,
    "data.job.detail.position": 1
}
data = get_wanted_job_details(projection=all_data_projection)

industry_list = get_unique_industry_name(data)
company_list = get_unique_company_name(data)


if __name__ == "__main__":
    target_industry = industry_list[0]
    ic(target_industry)
    
    industry_name_filter = {
        "data.job.company.industry_name": target_industry
    }
    industry_data = get_wanted_job_details(
        filter=industry_name_filter,
        projection={"data.job.company.name": 1}
    )
    filtered_companies = get_unique_company_name(industry_data)
    ic(filtered_companies)

    target_company = filtered_companies[0]
    ic(target_company)

    company_name_filter = {
        "data.job.company.name": target_company
    }
    company_data = get_wanted_job_details(filter=company_name_filter)

    filtered_positions = get_unique_position(company_data)
    ic(filtered_positions)