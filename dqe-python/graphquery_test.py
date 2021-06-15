import sys
from os import path

import asyncio
from clients.graphql_client import FstGraphqlAuthorizationCodeClient

client = FstGraphqlAuthorizationCodeClient()


tpt_id_list = ["FD20RAP01DPR"]


def call_graphql_api(tpt_id_list):

    async def query_graphql():

        query = """ query getTrials($tds: [String]) {
                fieldtrials(filter: [{
                    tdKeys: $tds
                }],
                pagination: {
                    take: 5,
                    skip: 0
                }) {
            tdKeys
            crops {
            name
            }
            targets {
            name
            }
            fieldTestingType
            projectNumbers
            siteType
            plotArea
            experimentalSeason
            
            treatments {
            numberOfApplications
            applications {
                products {
                equipment {
                    method
                }
                }
            }
            assessmentMeanValues {
                partRated
                sampleSize
                sampleSizeUnit
                target {
                name
                }
                crop {
                name
                }
            }
            }
        }
    } """

        #variables = {"tds": ["FD20RAP01DPR"]}
        variables = {"tds": tpt_id_list }
        return await client.query(query, variables)


    queryResults = asyncio.run(query_graphql())
   # print(queryResults)
    print(type(queryResults))
    return queryResults


data = call_graphql_api(tpt_id_list)
print(data)