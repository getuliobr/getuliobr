import os
# query ($owner_affiliation: [RepositoryAffiliation], $cursor: String) {
#         user(login: "getuliobr") {
#             repositories(first: 100, after: $cursor, ownerAffiliations: $owner_affiliation) {
#             edges {
#                 node {
#                     ... on Repository {
#                         nameWithOwner
#                         }
#                     }
#                 }
#                 pageInfo {
#                     endCursor
#                     hasNextPage
#                 }
#             }
#         }
#     }

print(os.environ('teste'))