import os
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(currentdir)
sys.path.append(parentdir)
sys.path.append('/opt/dagster/app')

from dagster import repository

try:
    from source.crawler import crawler_schedule, crawler_job
except:
    from crawler import crawler_schedule
    from crawler import crawler_job

@repository
def ckan_repository():

    return [
        crawler_schedule,
        crawler_job
            ]

